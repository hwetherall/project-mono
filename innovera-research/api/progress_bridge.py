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

    def end_category(self, category_id: str, status: str):
        self.category_statuses[category_id] = status
        start_time = self._category_start_times.get(category_id, time.time())
        elapsed = time.time() - start_time
        self._emit_sync({
            "type": "category_end",
            "category_id": category_id,
            "status": status,
            "elapsed_seconds": round(elapsed, 1),
            "source_count": 0,
            "gap_count": 0,
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

    def _get_category_name(self, category_id: str) -> str:
        try:
            from evidence_categories.registry import CATEGORY_REGISTRY
            meta = CATEGORY_REGISTRY.get(category_id)
            return meta.category_name if meta else category_id
        except ImportError:
            return category_id
