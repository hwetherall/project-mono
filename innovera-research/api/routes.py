"""
REST API endpoints for the Innovera Research web UI.
"""
import asyncio
import json
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml
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


def _resolve_saved_brief_path(source: str) -> Path:
    """Resolve a saved venture brief by run ID or path."""
    candidate = source.strip()
    if not candidate:
        raise HTTPException(status_code=400, detail="A run ID or venture_brief.md path is required.")

    if len(candidate) == 36 and candidate.count("-") == 4:
        brief_path = VENTURE_DOCS_DIR / candidate / "venture_brief.md"
    else:
        raw_path = Path(candidate)
        brief_path = raw_path if raw_path.is_absolute() else (VENTURE_DOCS_DIR / raw_path)

    try:
        resolved = brief_path.resolve(strict=False)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid brief path: {exc}") from exc

    allowed_root = VENTURE_DOCS_DIR.resolve()
    if allowed_root not in resolved.parents:
        raise HTTPException(status_code=400, detail="Saved brief path must live under venture_docs.")

    if resolved.name.lower() != "venture_brief.md":
        raise HTTPException(status_code=400, detail="Only venture_brief.md can be preloaded.")

    if not resolved.exists():
        raise HTTPException(status_code=404, detail=f"Saved brief not found: {resolved}")

    return resolved


def _find_run_output_dir(run_id: str) -> Path | None:
    """Find the output directory for a run on disk."""
    run_dir = OUTPUT_DIR / run_id
    if run_dir.exists() and (run_dir / "run_meta.json").exists():
        return run_dir
    return None


def _load_run_meta(run_id: str) -> dict | None:
    """Load run_meta.json from disk for a historical run."""
    run_dir = _find_run_output_dir(run_id)
    if not run_dir:
        return None
    meta_path = run_dir / "run_meta.json"
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _find_file_by_glob(directory: Path, pattern: str) -> Path | None:
    """Find a single file matching a glob pattern."""
    matches = list(directory.glob(pattern))
    return matches[0] if matches else None


@router.get("/venture-brief/load")
async def load_saved_venture_brief(source: str):
    brief_path = _resolve_saved_brief_path(source)
    try:
        content = brief_path.read_text(encoding="utf-8")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read saved brief: {exc}") from exc

    return {
        "source": source,
        "resolved_path": str(brief_path),
        "content": content,
    }


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
        "research_mode": request.research_mode,
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
            mode_label = "Market Research" if request.research_mode == "market_research" else "Demand Validation"
            progress.emit_log_detail(f"Extracting context signals for {mode_label}...", "info")
            extractor = ContextExtractor()
            context = extractor.extract(run_docs_dir, metadata, research_mode=request.research_mode)

            active_runs[run_id]["context"] = context

            # Emit context ready event
            progress.emit_context_ready(
                venture_name=context.venture_name,
                industry=context.industry_vertical,
                competitor_count=len(context.named_competitors),
                keyword_count=len(context.problem_keywords),
            )
            progress.emit_log_detail(
                f"Context ready — {context.venture_name} ({context.industry_vertical})", "success"
            )

            # Step 2: Research execution
            max_conc = request.max_concurrent or MAX_CONCURRENT_CATEGORIES

            # Temporarily override max concurrent in settings
            import config.settings as settings
            original_max = settings.MAX_CONCURRENT_CATEGORIES
            settings.MAX_CONCURRENT_CATEGORIES = max_conc

            progress.emit_log_detail(f"Starting {mode_label} with max {max_conc} concurrent categories...", "info")

            try:
                runner = ResearchRunner(
                    context=context,
                    venture_docs_dir=run_docs_dir,
                    progress=progress,
                    only_categories=only_categories,
                    research_mode=request.research_mode,
                )
                results = await runner.run_all()
            finally:
                settings.MAX_CONCURRENT_CATEGORIES = original_max

            active_runs[run_id]["results"] = results

            # Emit competitor list if available
            if runner.competitor_list:
                progress.emit_competitor_list(runner.competitor_list)
                source_cat = "MR-06a" if request.research_mode == "market_research" else "EC-02"
                progress.emit_log_detail(
                    f"Extracted {len(runner.competitor_list)} competitors from {source_cat}", "info"
                )

            # Step 3: Package assembly
            progress.emit_log_detail("Assembling evidence package...", "info")
            run_output_dir = OUTPUT_DIR / run_id
            run_output_dir.mkdir(parents=True, exist_ok=True)
            assembler = PackageAssembler(context, results, run_output_dir)

            progress.emit_log_detail("Writing YAML output...", "info")
            yaml_path, md_path = assembler.assemble()
            progress.emit_log_detail("Writing Markdown report...", "info")

            active_runs[run_id]["output_dir"] = run_output_dir
            active_runs[run_id]["yaml_path"] = yaml_path
            active_runs[run_id]["markdown_path"] = md_path
            active_runs[run_id]["status"] = "completed"

            # Save run metadata
            succeeded = sum(1 for r in results.values() if r.status == "success")
            failed_count = sum(1 for r in results.values() if r.status == "failed")
            total_sources = sum(len(r.sources) for r in results.values())

            run_meta = {
                "run_id": run_id,
                "started_at": started_at.isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "status": "completed",
                "venture_name": context.venture_name,
                "research_mode": request.research_mode,
                "categories_succeeded": succeeded,
                "categories_failed": failed_count,
                "total_sources": total_sources,
                "request": request.model_dump(),
            }
            meta_path = run_output_dir / "run_meta.json"
            meta_path.write_text(json.dumps(run_meta, indent=2, default=str), encoding="utf-8")

            progress.emit_log_detail(
                f"Evidence package complete — {succeeded} categories, {total_sources} sources", "success"
            )

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
        from market_research.registry import MR_CATEGORY_REGISTRY
        meta = CATEGORY_REGISTRY.get(cid) or MR_CATEGORY_REGISTRY.get(cid)
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
    # Check in-memory first
    run = active_runs.get(run_id)
    if run and run.get("yaml_path"):
        return FileResponse(
            run["yaml_path"],
            media_type="application/x-yaml",
            filename=run["yaml_path"].name,
        )

    # Fallback to disk
    run_dir = _find_run_output_dir(run_id)
    if run_dir:
        yaml_file = _find_file_by_glob(run_dir, "*.yaml")
        if yaml_file:
            return FileResponse(yaml_file, media_type="application/x-yaml", filename=yaml_file.name)

    raise HTTPException(status_code=404, detail="YAML output not available")


@router.get("/research/{run_id}/output/markdown")
async def get_markdown_output(run_id: str):
    # Check in-memory first
    run = active_runs.get(run_id)
    if run and run.get("markdown_path"):
        return FileResponse(
            run["markdown_path"],
            media_type="text/markdown",
            filename=run["markdown_path"].name,
        )

    # Fallback to disk
    run_dir = _find_run_output_dir(run_id)
    if run_dir:
        md_file = _find_file_by_glob(run_dir, "*.md")
        # Exclude run_meta.json related files — find actual report .md
        md_files = [f for f in run_dir.glob("*.md") if f.name != "run_meta.md"]
        if md_files:
            return FileResponse(md_files[0], media_type="text/markdown", filename=md_files[0].name)

    raise HTTPException(status_code=404, detail="Markdown output not available")


@router.get("/research/{run_id}/output/raw/{category_id}")
async def get_raw_report(run_id: str, category_id: str):
    # Check in-memory first
    run = active_runs.get(run_id)
    output_dir = run["output_dir"] if run and run.get("output_dir") else None

    # Fallback to disk
    if not output_dir:
        output_dir = _find_run_output_dir(run_id)

    if not output_dir:
        raise HTTPException(status_code=404, detail="Output not available")

    raw_dir = output_dir / "raw_reports"
    if not raw_dir.exists():
        raise HTTPException(status_code=404, detail="Raw reports not available")

    matches = list(raw_dir.glob(f"{category_id}_*.md"))
    if not matches:
        raise HTTPException(status_code=404, detail=f"Raw report for {category_id} not found")

    return FileResponse(
        matches[0],
        media_type="text/markdown",
        filename=matches[0].name,
    )


@router.get("/research/{run_id}/output/structured")
async def get_structured_output(run_id: str):
    """Return a structured JSON representation of the evidence package for the frontend."""
    # Try to build from in-memory data first
    run = active_runs.get(run_id)
    output_dir = run["output_dir"] if run and run.get("output_dir") else _find_run_output_dir(run_id)

    if not output_dir:
        raise HTTPException(status_code=404, detail="Output not available")

    # Load run metadata
    meta = _load_run_meta(run_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Run metadata not available")

    # Load YAML evidence package
    yaml_file = _find_file_by_glob(output_dir, "*.yaml")
    evidence_data = None
    if yaml_file:
        try:
            evidence_data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Build structured categories
    categories = []
    raw_dir = output_dir / "raw_reports"

    # Get category info from evidence data
    pkg = evidence_data.get("research_package", {}) if evidence_data else {}
    # The YAML uses "evidence" key; fallback to "evidence_categories" for compat
    evidence_categories_data = pkg.get("evidence", {}) or pkg.get("evidence_categories", {})
    gap_summary = pkg.get("gap_summary", {})
    context_signals = pkg.get("context_signals", {})

    for cid in sorted(evidence_categories_data.keys()):
        cat_data = evidence_categories_data[cid]
        # Load raw report from disk
        raw_report_md = ""
        if raw_dir.exists():
            raw_matches = list(raw_dir.glob(f"{cid}_*.md"))
            if raw_matches:
                try:
                    raw_report_md = raw_matches[0].read_text(encoding="utf-8")
                except Exception:
                    pass

        sources = cat_data.get("sources", [])
        gaps = cat_data.get("gaps", [])

        categories.append({
            "category_id": cid,
            "category_name": cat_data.get("category_name", cid),
            "status": cat_data.get("status", "unknown"),
            "execution_time_seconds": cat_data.get("execution_time_seconds", 0),
            "source_count": len(sources),
            "gap_count": len(gaps),
            "gaps": gaps,
            "sources": sources,
            "raw_report_markdown": raw_report_md,
        })

    return {
        "run_id": run_id,
        "venture_name": meta.get("venture_name", "Unknown"),
        "research_mode": meta.get("research_mode", meta.get("request", {}).get("research_mode", "demand_validation")),
        "metadata": {
            "generated_at": meta.get("completed_at", ""),
            "started_at": meta.get("started_at", ""),
            "industry": context_signals.get("industry_vertical", ""),
            "sub_vertical": context_signals.get("sub_vertical", ""),
            "geography": context_signals.get("geography", ""),
            "stage": context_signals.get("stage", ""),
            "research_mode": meta.get("research_mode", "demand_validation"),
        },
        "context_signals": context_signals,
        "categories": categories,
        "gap_inventory": {
            "critical": gap_summary.get("critical_gaps", []),
            "moderate": gap_summary.get("moderate_gaps", []),
        },
        "request": meta.get("request", {}),
    }


@router.get("/research/{run_id}/full")
async def get_full_run(run_id: str):
    """Return everything needed to render the output viewer for a past run."""
    # Check in-memory first
    run = active_runs.get(run_id)
    if run and run.get("results"):
        results = run["results"]
        context = run["context"]
        request = run["request"]
        started_at = run["started_at"].isoformat()
        completed_at = None
        status = run["status"]

        cats = {}
        for cid, result in results.items():
            cats[cid] = {
                "category_id": cid,
                "category_name": result.category_name,
                "status": result.status,
                "source_count": len(result.sources),
                "gap_count": len(result.gaps),
                "elapsed_seconds": result.execution_time_seconds,
            }

        return {
            "run_id": run_id,
            "venture_name": context.venture_name if context else "",
            "research_mode": request.research_mode if request else "demand_validation",
            "started_at": started_at,
            "completed_at": completed_at,
            "status": status,
            "categories_succeeded": sum(1 for r in results.values() if r.status == "success"),
            "categories_failed": sum(1 for r in results.values() if r.status == "failed"),
            "total_sources": sum(len(r.sources) for r in results.values()),
            "request": request.model_dump() if request else {},
            "categories": cats,
        }

    # Fallback to disk
    meta = _load_run_meta(run_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    # Build category info from YAML evidence package
    output_dir = _find_run_output_dir(run_id)
    cats = {}

    if output_dir:
        yaml_file = _find_file_by_glob(output_dir, "*.yaml")
        if yaml_file:
            try:
                evidence = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
                pkg = evidence.get("research_package", {})
                evidence_data = pkg.get("evidence", {}) or pkg.get("evidence_categories", {})
                for cid, cat_data in evidence_data.items():
                    cats[cid] = {
                        "category_id": cid,
                        "category_name": cat_data.get("category_name", cid),
                        "status": cat_data.get("status", "unknown"),
                        "source_count": len(cat_data.get("sources", [])),
                        "gap_count": len(cat_data.get("gaps", [])),
                        "elapsed_seconds": cat_data.get("execution_time_seconds", 0),
                    }
            except Exception:
                pass

    return {
        "run_id": meta["run_id"],
        "venture_name": meta.get("venture_name", "Unknown"),
        "research_mode": meta.get("research_mode", meta.get("request", {}).get("research_mode", "demand_validation")),
        "started_at": meta.get("started_at", ""),
        "completed_at": meta.get("completed_at", ""),
        "status": meta.get("status", "unknown"),
        "categories_succeeded": meta.get("categories_succeeded", 0),
        "categories_failed": meta.get("categories_failed", 0),
        "total_sources": meta.get("total_sources", 0),
        "request": meta.get("request", {}),
        "categories": cats,
    }


@router.delete("/research/{run_id}")
async def delete_run(run_id: str):
    """Delete a run's output directory from disk."""
    # Remove from active_runs if present
    if run_id in active_runs:
        run = active_runs[run_id]
        if run["status"] == "running":
            raise HTTPException(status_code=409, detail="Cannot delete a running run")
        del active_runs[run_id]

    # Remove from disk
    run_dir = OUTPUT_DIR / run_id
    if run_dir.exists():
        shutil.rmtree(run_dir)
        return {"status": "deleted", "run_id": run_id}

    raise HTTPException(status_code=404, detail=f"Run {run_id} not found")


@router.post("/research/{run_id}/retry/{category_id}")
async def retry_category(run_id: str, category_id: str):
    run = active_runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    if not run.get("context"):
        raise HTTPException(status_code=400, detail="Run context not available")
    if not run.get("results") or category_id not in run["results"]:
        raise HTTPException(status_code=400, detail=f"Category {category_id} not found in results")

    from orchestrator.runner import ResearchRunner, CATEGORY_CLASSES, MR_CATEGORY_CLASSES
    from evidence_categories.registry import CATEGORY_REGISTRY
    from market_research.registry import MR_CATEGORY_REGISTRY

    all_classes = {**CATEGORY_CLASSES, **MR_CATEGORY_CLASSES}
    if category_id not in all_classes:
        raise HTTPException(status_code=400, detail=f"Unknown category: {category_id}")

    progress = run["progress"]
    context = run["context"]
    run_docs_dir = VENTURE_DOCS_DIR / run_id

    progress.start_category(category_id)

    async def do_retry():
        try:
            category_class = all_classes[category_id]
            category = category_class(context=context, venture_docs_dir=run_docs_dir)
            result = await category.execute()
            run["results"][category_id] = result
            progress.end_category(
                category_id,
                result.status,
                error=result.error,
                source_count=len(result.sources),
                gap_count=len(result.gaps),
            )

            # Re-assemble output
            if run.get("output_dir"):
                from output.package_assembler import PackageAssembler
                assembler = PackageAssembler(context, run["results"], run["output_dir"])
                yaml_path, md_path = assembler.assemble()
                run["yaml_path"] = yaml_path
                run["markdown_path"] = md_path

        except Exception as e:
            progress.end_category(category_id, "failed", error=str(e))

    asyncio.create_task(do_retry())
    return {"status": "retrying", "category_id": category_id}


@router.get("/runs")
async def list_runs():
    """List recent runs from output_packages/ directory with rich metadata."""
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
                    # Enrich with duration if both timestamps present
                    if meta.get("started_at") and meta.get("completed_at"):
                        try:
                            start = datetime.fromisoformat(meta["started_at"])
                            end = datetime.fromisoformat(meta["completed_at"])
                            meta["duration_seconds"] = (end - start).total_seconds()
                        except Exception:
                            pass
                    runs.append(meta)
                except Exception:
                    pass
        if len(runs) >= 50:
            break

    # Also include active in-memory runs not yet on disk
    for run_id, run in active_runs.items():
        if not any(r.get("run_id") == run_id for r in runs):
            runs.append({
                "run_id": run_id,
                "status": run["status"],
                "started_at": run["started_at"].isoformat(),
                "venture_name": run.get("context", {}).venture_name if run.get("context") else "In Progress...",
            })

    return {"runs": runs}
