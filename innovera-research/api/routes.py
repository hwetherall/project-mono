"""
REST API endpoints for the Innovera Research web UI.
"""
import asyncio
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from api.models import ResearchRequest, ResearchResponse, RunStatus, CategoryStatus
from api.progress_bridge import WebSocketProgressBridge
from config.settings import VENTURE_DOCS_DIR, OUTPUT_DIR, MAX_CONCURRENT_CATEGORIES

router = APIRouter(prefix="/api")

# In-memory store of active and completed runs
active_runs: dict[str, dict] = {}


def _is_any_run_active() -> bool:
    return any(r["status"] == "running" for r in active_runs.values())


def _build_venture_brief(request: ResearchRequest) -> str:
    """Assemble the combined venture brief markdown document."""
    criteria_lines = "\n".join(
        f"{i+1}. {c}" for i, c in enumerate(request.success_criteria)
    )

    parts = [f"# Venture Brief\n\n{request.document_text}"]

    if request.additional_context.strip():
        parts.append(f"---\n\n## Additional Context\n\n{request.additional_context}")

    parts.append(f"---\n\n## Core Strategic Question\n\n{request.core_question}")
    parts.append(f"---\n\n## Success Criteria\n\n{criteria_lines}")

    return "\n\n".join(parts)


@router.post("/research/start")
async def start_research(request: ResearchRequest):
    # Enforce single concurrent run
    if _is_any_run_active():
        raise HTTPException(
            status_code=409,
            detail="A research run is already in progress. Please wait for it to complete."
        )

    run_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)

    # Create venture docs directory for this run
    run_docs_dir = VENTURE_DOCS_DIR / run_id
    run_docs_dir.mkdir(parents=True, exist_ok=True)

    # Write the combined venture brief
    brief_content = _build_venture_brief(request)
    brief_path = run_docs_dir / "venture_brief.md"
    brief_path.write_text(brief_content, encoding="utf-8")

    # Build metadata
    metadata = {
        "core_question": request.core_question,
        "success_criteria": request.success_criteria,
        "venture_name_override": request.venture_name or None,
    }

    # Create progress bridge
    progress = WebSocketProgressBridge()

    # Determine category filter
    only_categories = request.categories_to_run if request.categories_to_run else None

    # Store run info
    active_runs[run_id] = {
        "task": None,
        "progress": progress,
        "status": "running",
        "request": request,
        "started_at": started_at,
        "results": None,
        "context": None,
        "output_dir": None,
        "yaml_path": None,
        "markdown_path": None,
        "error": None,
    }

    # Launch the pipeline as a background task
    async def run_pipeline():
        try:
            from context_extraction.extractor import ContextExtractor
            from orchestrator.runner import ResearchRunner
            from output.package_assembler import PackageAssembler

            # Step 1: Context extraction
            extractor = ContextExtractor()
            context = extractor.extract(run_docs_dir, metadata)

            active_runs[run_id]["context"] = context

            # Emit context ready event
            progress.emit_context_ready(
                venture_name=context.venture_name,
                industry=context.industry_vertical,
                competitor_count=len(context.named_competitors),
                keyword_count=len(context.problem_keywords),
            )

            # Step 2: Research execution
            max_conc = request.max_concurrent or MAX_CONCURRENT_CATEGORIES

            # Temporarily override max concurrent in settings
            import config.settings as settings
            original_max = settings.MAX_CONCURRENT_CATEGORIES
            settings.MAX_CONCURRENT_CATEGORIES = max_conc

            try:
                runner = ResearchRunner(
                    context=context,
                    venture_docs_dir=run_docs_dir,
                    progress=progress,
                    only_categories=only_categories,
                )
                results = await runner.run_all()
            finally:
                settings.MAX_CONCURRENT_CATEGORIES = original_max

            active_runs[run_id]["results"] = results

            # Emit competitor list if available
            if runner.competitor_list:
                progress.emit_competitor_list(runner.competitor_list)

            # Step 3: Package assembly
            run_output_dir = OUTPUT_DIR / run_id
            run_output_dir.mkdir(parents=True, exist_ok=True)
            assembler = PackageAssembler(context, results, run_output_dir)
            yaml_path, md_path = assembler.assemble()

            active_runs[run_id]["output_dir"] = run_output_dir
            active_runs[run_id]["yaml_path"] = yaml_path
            active_runs[run_id]["markdown_path"] = md_path
            active_runs[run_id]["status"] = "completed"

            # Save run metadata
            run_meta = {
                "run_id": run_id,
                "started_at": started_at.isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "status": "completed",
                "venture_name": context.venture_name,
                "categories_succeeded": sum(1 for r in results.values() if r.status == "success"),
                "categories_failed": sum(1 for r in results.values() if r.status == "failed"),
                "total_sources": sum(len(r.sources) for r in results.values()),
                "request": request.model_dump(),
            }
            meta_path = run_output_dir / "run_meta.json"
            meta_path.write_text(json.dumps(run_meta, indent=2, default=str), encoding="utf-8")

        except Exception as e:
            active_runs[run_id]["status"] = "failed"
            active_runs[run_id]["error"] = str(e)
            progress.emit_run_error(str(e))

    task = asyncio.create_task(run_pipeline())
    active_runs[run_id]["task"] = task

    return ResearchResponse(
        run_id=run_id,
        status="started",
        message="Research pipeline started"
    )


@router.get("/research/{run_id}/status")
async def get_run_status(run_id: str):
    run = active_runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    progress = run["progress"]
    elapsed = (datetime.now(timezone.utc) - run["started_at"]).total_seconds()

    # Build category statuses from progress bridge
    categories = {}
    for cid, status in progress.category_statuses.items():
        from evidence_categories.registry import CATEGORY_REGISTRY
        meta = CATEGORY_REGISTRY.get(cid)
        cat_name = meta.category_name if meta else cid

        cat_elapsed = 0
        if cid in progress._category_start_times:
            cat_elapsed = time.time() - progress._category_start_times[cid]

        source_count = 0
        gap_count = 0
        error = None
        if run["results"] and cid in run["results"]:
            result = run["results"][cid]
            source_count = len(result.sources)
            gap_count = len(result.gaps)
            error = result.error

        categories[cid] = CategoryStatus(
            category_id=cid,
            category_name=cat_name,
            status=status,
            elapsed_seconds=round(cat_elapsed, 1),
            error=error,
            gap_count=gap_count,
            source_count=source_count,
        )

    output_files = []
    if run["yaml_path"]:
        output_files.append(str(run["yaml_path"]))
    if run["markdown_path"]:
        output_files.append(str(run["markdown_path"]))

    return RunStatus(
        run_id=run_id,
        status=run["status"],
        phase=progress.current_phase,
        categories=categories,
        elapsed_seconds=round(elapsed, 1),
        output_files=output_files,
        error=run.get("error"),
    )


@router.get("/research/{run_id}/output/yaml")
async def get_yaml_output(run_id: str):
    run = active_runs.get(run_id)
    if not run or not run.get("yaml_path"):
        raise HTTPException(status_code=404, detail="YAML output not available")
    return FileResponse(
        run["yaml_path"],
        media_type="application/x-yaml",
        filename=run["yaml_path"].name,
    )


@router.get("/research/{run_id}/output/markdown")
async def get_markdown_output(run_id: str):
    run = active_runs.get(run_id)
    if not run or not run.get("markdown_path"):
        raise HTTPException(status_code=404, detail="Markdown output not available")
    return FileResponse(
        run["markdown_path"],
        media_type="text/markdown",
        filename=run["markdown_path"].name,
    )


@router.get("/research/{run_id}/output/raw/{category_id}")
async def get_raw_report(run_id: str, category_id: str):
    run = active_runs.get(run_id)
    if not run or not run.get("output_dir"):
        raise HTTPException(status_code=404, detail="Output not available")

    # Find the raw report file
    raw_dir = run["output_dir"] / "raw_reports"
    if not raw_dir.exists():
        raise HTTPException(status_code=404, detail="Raw reports not available")

    # Find matching file
    matches = list(raw_dir.glob(f"{category_id}_*.md"))
    if not matches:
        raise HTTPException(status_code=404, detail=f"Raw report for {category_id} not found")

    return FileResponse(
        matches[0],
        media_type="text/markdown",
        filename=matches[0].name,
    )


@router.post("/research/{run_id}/retry/{category_id}")
async def retry_category(run_id: str, category_id: str):
    run = active_runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    if not run.get("context"):
        raise HTTPException(status_code=400, detail="Run context not available")
    if not run.get("results") or category_id not in run["results"]:
        raise HTTPException(status_code=400, detail=f"Category {category_id} not found in results")

    from orchestrator.runner import ResearchRunner, CATEGORY_CLASSES
    from evidence_categories.registry import CATEGORY_REGISTRY

    if category_id not in CATEGORY_CLASSES:
        raise HTTPException(status_code=400, detail=f"Unknown category: {category_id}")

    progress = run["progress"]
    context = run["context"]
    run_docs_dir = VENTURE_DOCS_DIR / run_id

    progress.start_category(category_id)

    async def do_retry():
        try:
            category_class = CATEGORY_CLASSES[category_id]
            category = category_class(context=context, venture_docs_dir=run_docs_dir)
            result = await category.execute()
            run["results"][category_id] = result
            progress.end_category(category_id, result.status)

            # Re-assemble output
            if run.get("output_dir"):
                from output.package_assembler import PackageAssembler
                assembler = PackageAssembler(context, run["results"], run["output_dir"])
                yaml_path, md_path = assembler.assemble()
                run["yaml_path"] = yaml_path
                run["markdown_path"] = md_path

        except Exception as e:
            progress.end_category(category_id, "failed")

    asyncio.create_task(do_retry())
    return {"status": "retrying", "category_id": category_id}


@router.get("/runs")
async def list_runs():
    """List recent runs from output_packages/ directory."""
    runs = []
    output_base = OUTPUT_DIR

    if not output_base.exists():
        return {"runs": []}

    # Check subdirectories that contain run_meta.json
    for entry in sorted(output_base.iterdir(), reverse=True):
        if entry.is_dir():
            meta_path = entry / "run_meta.json"
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                    runs.append(meta)
                except Exception:
                    pass
        if len(runs) >= 20:
            break

    # Also include active in-memory runs not yet on disk
    for run_id, run in active_runs.items():
        if not any(r.get("run_id") == run_id for r in runs):
            runs.append({
                "run_id": run_id,
                "status": run["status"],
                "started_at": run["started_at"].isoformat(),
            })

    return {"runs": runs}
