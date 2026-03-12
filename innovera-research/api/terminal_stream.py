"""
Tee-style stdout/stderr capture that mirrors research pipeline output
into the WebSocket Activity Stream via the progress bridge.

Usage:
    with TerminalTee(progress_bridge):
        await runner.run_all()

Normal terminal output continues unchanged. Selected lines are also emitted
as `terminal_line` websocket events.
"""
import io
import logging
import re
import sys

logger = logging.getLogger(__name__)

# Patterns that indicate research-relevant output worth mirroring.
_INCLUDE_PATTERNS = [
    re.compile(r"DEEP RESEARCH", re.IGNORECASE),
    re.compile(r"Generating\b", re.IGNORECASE),
    re.compile(r"rate.?limit", re.IGNORECASE),
    re.compile(r"Error:", re.IGNORECASE),
    re.compile(r"\bEC-\d{2}\b"),
    re.compile(r"\bMR-\d{2}[ab]?\b"),
    re.compile(r"search quer", re.IGNORECASE),
    re.compile(r"Tavily", re.IGNORECASE),
    re.compile(r"scraping|fetching|crawling", re.IGNORECASE),
    re.compile(r"report.*generat", re.IGNORECASE),
    re.compile(r"source[s]?\s+found", re.IGNORECASE),
    re.compile(r"research.*complet", re.IGNORECASE),
    re.compile(r"writing report", re.IGNORECASE),
    re.compile(r"breadth|depth|concurrency", re.IGNORECASE),
]

# Patterns to suppress (noise).
_EXCLUDE_PATTERNS = [
    re.compile(r"^INFO:\s+uvicorn", re.IGNORECASE),
    re.compile(r"^INFO:\s+\d+\.\d+\.\d+\.\d+:\d+", re.IGNORECASE),
    re.compile(r"HTTP/\d\.\d", re.IGNORECASE),
    re.compile(r"WebSocket.*connect", re.IGNORECASE),
    re.compile(r"^\s*$"),
]


def _classify_line(line: str) -> tuple[bool, str]:
    """Decide whether a line should be mirrored and at what level.

    Returns (should_mirror, level).
    """
    stripped = line.strip()
    if not stripped:
        return False, "info"

    # Exclude noise first
    for pat in _EXCLUDE_PATTERNS:
        if pat.search(stripped):
            return False, "info"

    # Check for error indicators
    level = "info"
    if re.search(r"error|exception|traceback|failed", stripped, re.IGNORECASE):
        level = "error"
    elif re.search(r"warn|rate.?limit", stripped, re.IGNORECASE):
        level = "warning"

    # Include if it matches a research-relevant pattern
    for pat in _INCLUDE_PATTERNS:
        if pat.search(stripped):
            return True, level

    # Conservative default: include lines that look substantive (>20 chars)
    # but not HTTP logs or pure whitespace
    if len(stripped) > 20 and not stripped.startswith(("INFO:", "DEBUG:", "WARNING:")):
        return True, level

    return False, "info"


class _TeeStream:
    """Wraps an original stream, forwarding writes to both the original
    and the progress bridge as terminal_line events."""

    def __init__(self, original, bridge, recent_messages):
        self._original = original
        self._bridge = bridge
        self._recent = recent_messages
        self._buffer = ""

    def write(self, data):
        # Always write to the real terminal first
        if self._original:
            try:
                self._original.write(data)
            except Exception:
                pass

        # Buffer partial writes, emit on newlines
        self._buffer += data
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self._emit_line(line)

    def _emit_line(self, line: str):
        stripped = line.strip()
        if not stripped:
            return

        should_mirror, level = _classify_line(stripped)
        if not should_mirror:
            return

        # Simple dedup: skip if this exact message was emitted recently
        if stripped in self._recent:
            return
        self._recent.add(stripped)
        # Cap the recent set
        if len(self._recent) > 200:
            # Remove oldest entries (sets aren't ordered, but this prevents unbounded growth)
            to_remove = list(self._recent)[:100]
            for item in to_remove:
                self._recent.discard(item)

        try:
            self._bridge.emit_terminal_line(stripped, level)
        except Exception:
            pass  # Never let telemetry break the run

    def flush(self):
        if self._original:
            try:
                self._original.flush()
            except Exception:
                pass

    def fileno(self):
        if self._original:
            return self._original.fileno()
        raise io.UnsupportedOperation("fileno")

    def isatty(self):
        if self._original:
            return self._original.isatty()
        return False

    @property
    def encoding(self):
        return getattr(self._original, "encoding", "utf-8")

    @property
    def errors(self):
        return getattr(self._original, "errors", "replace")

    def writable(self):
        return True

    def readable(self):
        return False

    def seekable(self):
        return False


class TerminalTee:
    """Context manager that tees stdout/stderr to the progress bridge."""

    def __init__(self, bridge):
        self._bridge = bridge
        self._original_stdout = None
        self._original_stderr = None
        self._recent_messages = set()

    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = _TeeStream(self._original_stdout, self._bridge, self._recent_messages)
        sys.stderr = _TeeStream(self._original_stderr, self._bridge, self._recent_messages)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Flush any remaining buffer
        if isinstance(sys.stdout, _TeeStream) and sys.stdout._buffer.strip():
            sys.stdout._emit_line(sys.stdout._buffer)
        if isinstance(sys.stderr, _TeeStream) and sys.stderr._buffer.strip():
            sys.stderr._emit_line(sys.stderr._buffer)

        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        return False
