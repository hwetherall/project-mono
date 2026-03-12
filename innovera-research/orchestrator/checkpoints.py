"""
Per-category checkpoint persistence for resume-after-timeout.

Checkpoints are stored as JSON files under:
    output_packages/<run_id>/checkpoints/<category_id>.json

Each checkpoint records the last completed stage and all intermediate data
needed to resume from that point.
"""
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config.settings import OUTPUT_DIR, CATEGORY_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)

# Ordered list of checkpoint stages (each stage implies all prior stages completed).
STAGES = [
    "research_started",
    "research_completed",
    "report_started",
    "report_completed",
    "parsed",
    "finalized",
]

# Stages from which true resume (skipping earlier work) is possible.
_RESUMABLE_FROM = {"research_completed", "report_completed", "parsed"}


def _checkpoints_dir(run_id: str) -> Path:
    return OUTPUT_DIR / run_id / "checkpoints"


def save_checkpoint(
    run_id: str,
    category_id: str,
    category_name: str,
    research_mode: str,
    stage: str,
    *,
    query: str = "",
    config_path: str = "",
    report_type: str = "",
    started_at: Optional[str] = None,
    elapsed_seconds: float = 0,
    error: Optional[str] = None,
    source_urls: Optional[list[str]] = None,
    research_context: Optional[list[str]] = None,
    researcher_agent: Optional[str] = None,
    researcher_role: Optional[str] = None,
    raw_report: Optional[str] = None,
    structured_findings: Optional[dict] = None,
) -> Path:
    """Write or update a checkpoint file for a category."""
    cp_dir = _checkpoints_dir(run_id)
    cp_dir.mkdir(parents=True, exist_ok=True)
    cp_path = cp_dir / f"{category_id}.json"

    can_resume = stage in _RESUMABLE_FROM and error is None
    resume_reason = _resume_reason(stage) if can_resume else None

    data = {
        "run_id": run_id,
        "category_id": category_id,
        "category_name": category_name,
        "research_mode": research_mode,
        "stage": stage,
        "status": "error" if error else ("finalized" if stage == "finalized" else "in_progress"),
        "query": query,
        "config_path": config_path,
        "report_type": report_type,
        "started_at": started_at or datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed_seconds,
        "error": error,
        "timeout_seconds": CATEGORY_TIMEOUT_SECONDS,
        "can_resume": can_resume,
        "resume_reason": resume_reason,
        "source_urls": source_urls or [],
        "research_context": research_context or [],
        "researcher_agent": researcher_agent,
        "researcher_role": researcher_role,
        "raw_report": raw_report or "",
        "structured_findings": structured_findings or {},
    }

    cp_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    logger.debug("Checkpoint saved: %s stage=%s can_resume=%s", category_id, stage, can_resume)
    return cp_path


def load_checkpoint(run_id: str, category_id: str) -> Optional[dict]:
    """Load a checkpoint from disk. Returns None if not found."""
    cp_path = _checkpoints_dir(run_id) / f"{category_id}.json"
    if not cp_path.exists():
        return None
    try:
        return json.loads(cp_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Failed to load checkpoint %s/%s: %s", run_id, category_id, exc)
        return None


def load_all_checkpoints(run_id: str) -> dict[str, dict]:
    """Load all checkpoints for a run. Returns {category_id: checkpoint_data}."""
    cp_dir = _checkpoints_dir(run_id)
    if not cp_dir.exists():
        return {}
    result = {}
    for cp_file in cp_dir.glob("*.json"):
        try:
            data = json.loads(cp_file.read_text(encoding="utf-8"))
            result[data["category_id"]] = data
        except Exception:
            pass
    return result


def delete_checkpoint(run_id: str, category_id: str):
    """Remove a checkpoint file."""
    cp_path = _checkpoints_dir(run_id) / f"{category_id}.json"
    if cp_path.exists():
        cp_path.unlink()


def is_resumable(checkpoint: dict) -> bool:
    """Check if a checkpoint supports true resume (not just retry)."""
    return checkpoint.get("can_resume", False) and checkpoint.get("stage") in _RESUMABLE_FROM


def mark_checkpoint_error(run_id: str, category_id: str, error: str, elapsed: float):
    """Update an existing checkpoint with error info while preserving progress data."""
    existing = load_checkpoint(run_id, category_id)
    if not existing:
        return

    stage = existing["stage"]
    can_resume = stage in _RESUMABLE_FROM
    resume_reason = _resume_reason(stage) if can_resume else None

    existing["error"] = error
    existing["elapsed_seconds"] = elapsed
    existing["updated_at"] = datetime.now(timezone.utc).isoformat()
    existing["can_resume"] = can_resume
    existing["resume_reason"] = resume_reason
    existing["status"] = "error"

    cp_path = _checkpoints_dir(run_id) / f"{category_id}.json"
    cp_path.write_text(json.dumps(existing, indent=2, default=str), encoding="utf-8")
    logger.info(
        "Checkpoint error recorded: %s stage=%s can_resume=%s error=%s",
        category_id, stage, can_resume, error,
    )


def _resume_reason(stage: str) -> str:
    if stage == "research_completed":
        return "Web research completed; can resume from report generation"
    if stage == "report_completed":
        return "Report written; can resume from parsing"
    if stage == "parsed":
        return "Report parsed; can resume from finalization"
    return ""
