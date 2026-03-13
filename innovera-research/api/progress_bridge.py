"""
WebSocket progress bridge - drop-in replacement for ProgressTracker.
Pushes JSON events to an asyncio queue instead of printing to terminal.
"""
import asyncio
import json
import time


class WebSocketProgressBridge:
    """Drop-in replacement for ProgressTracker that pushes events to a queue."""

    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.current_phase: str = ""
        self.category_statuses: dict[str, str] = {}
        self._category_start_times: dict[str, float] = {}

    async def _emit(self, event: dict):
        await self.queue.put(json.dumps(event))

    def _emit_sync(self, event: dict):
        """Fire-and-forget emit for sync callers."""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._emit(event))
        except RuntimeError:
            pass

    def start_phase(self, phase_name: str, category_ids: list[str]):
        self.current_phase = phase_name
        for cid in category_ids:
            self.category_statuses[cid] = "pending"
        self._emit_sync({
            "type": "phase_start",
            "phase": phase_name,
            "categories": category_ids,
        })

    def start_category(self, category_id: str):
        self.category_statuses[category_id] = "running"
        self._category_start_times[category_id] = time.time()
        self._emit_sync({
            "type": "category_start",
            "category_id": category_id,
            "category_name": self._get_category_name(category_id),
        })

    def end_category(self, category_id: str, status: str, error: str | None = None,
                     source_count: int = 0, gap_count: int = 0):
        self.category_statuses[category_id] = status
        start_time = self._category_start_times.get(category_id, time.time())
        elapsed = time.time() - start_time
        self._emit_sync({
            "type": "category_end",
            "category_id": category_id,
            "status": status,
            "elapsed_seconds": round(elapsed, 1),
            "source_count": source_count,
            "gap_count": gap_count,
            "error": error,
        })

    def end_phase(self, phase_name: str):
        self._emit_sync({
            "type": "phase_end",
            "phase": phase_name,
        })

    def log(self, message: str):
        self._emit_sync({
            "type": "log",
            "message": message,
        })

    def complete(self, total_seconds: float):
        succeeded = sum(1 for s in self.category_statuses.values() if s == "success")
        failed = sum(1 for s in self.category_statuses.values() if s == "failed")
        self._emit_sync({
            "type": "run_complete",
            "elapsed_seconds": round(total_seconds, 1),
            "succeeded": succeeded,
            "failed": failed,
        })

    def emit_context_ready(self, venture_name: str, industry: str,
                           competitor_count: int, keyword_count: int):
        self._emit_sync({
            "type": "context_ready",
            "venture_name": venture_name,
            "industry": industry,
            "competitor_count": competitor_count,
            "keyword_count": keyword_count,
        })

    def emit_competitor_list(self, competitors: list[str]):
        self._emit_sync({
            "type": "competitor_list",
            "competitors": competitors,
            "count": len(competitors),
        })

    def emit_run_error(self, error: str):
        self._emit_sync({
            "type": "run_error",
            "error": error,
        })

    def emit_rate_limit(self, category_id: str, attempt: int,
                        max_attempts: int, wait_seconds: float):
        self._emit_sync({
            "type": "rate_limit",
            "category_id": category_id,
            "attempt": attempt,
            "max_attempts": max_attempts,
            "wait_seconds": round(wait_seconds, 0),
        })

    def emit_log_detail(self, message: str, level: str = "info"):
        """Emit a detailed log message for the activity stream."""
        self._emit_sync({
            "type": "log_detail",
            "level": level,
            "message": message,
        })

    def emit_terminal_line(self, message: str, level: str = "info"):
        """Emit a mirrored terminal line for the activity stream."""
        self._emit_sync({
            "type": "terminal_line",
            "level": level,
            "message": message,
        })

    def emit_competitive_table_status(
        self, status: str, step: str,
        found: int | None = None,
        completed: int | None = None,
        total: int | None = None,
        competitors: int | None = None,
        attributes: int | None = None,
        coverage: float | None = None,
    ):
        """Emit a competitive table construction progress event."""
        event = {
            "type": "competitive_table_status",
            "status": status,
            "step": step,
        }
        if found is not None:
            event["found"] = found
        if completed is not None:
            event["completed"] = completed
        if total is not None:
            event["total"] = total
        if competitors is not None:
            event["competitors"] = competitors
        if attributes is not None:
            event["attributes"] = attributes
        if coverage is not None:
            event["coverage"] = coverage
        self._emit_sync(event)

    def _get_category_name(self, category_id: str) -> str:
        try:
            from evidence_categories.registry import CATEGORY_REGISTRY
            from market_research.registry import MR_CATEGORY_REGISTRY

            if category_id in CATEGORY_REGISTRY:
                return CATEGORY_REGISTRY[category_id].category_name
            if category_id in MR_CATEGORY_REGISTRY:
                return MR_CATEGORY_REGISTRY[category_id].category_name
            return category_id
        except ImportError:
            return category_id
