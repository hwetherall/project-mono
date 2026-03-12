"""
Base class for all evidence categories.
"""
import asyncio
import json
import logging
import random
import time
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from gpt_researcher import GPTResearcher
from context_extraction.models import ContextSignals, PriorityLevel
from config.settings import RATE_LIMIT_MAX_RETRIES, RATE_LIMIT_BASE_DELAY

logger = logging.getLogger(__name__)


def _stringify_context_item(item) -> str:
    """Convert mixed GPT Researcher context objects into stable strings."""
    if item is None:
        return ""
    if isinstance(item, str):
        return item
    if isinstance(item, (bytes, bytearray)):
        return item.decode("utf-8", errors="replace")
    if isinstance(item, dict):
        preferred_fields = []
        for key in ("content", "text", "summary", "snippet", "body", "markdown", "page_content"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                preferred_fields.append(value.strip())

        if preferred_fields:
            meta = []
            title = item.get("title") or item.get("Title")
            source = item.get("url") or item.get("source") or item.get("Source")
            if title:
                meta.append(f"Title: {title}")
            if source:
                meta.append(f"Source: {source}")

            body = preferred_fields[0]
            return f"{chr(10).join(meta)}{chr(10) if meta else ''}{body}"

        return json.dumps(item, ensure_ascii=False, default=str)
    if isinstance(item, (list, tuple, set)):
        normalized = [_stringify_context_item(entry) for entry in item]
        return "\n".join(part for part in normalized if part)
    return str(item)


def _normalize_context_value(value):
    """Preserve list context shape, but guarantee string entries."""
    if isinstance(value, list):
        normalized = [_stringify_context_item(item) for item in value]
        return [item for item in normalized if item]
    if isinstance(value, tuple):
        normalized = [_stringify_context_item(item) for item in value]
        return [item for item in normalized if item]
    if isinstance(value, (dict, set)):
        return _stringify_context_item(value)
    return value


_ORIGINAL_GPTR_CONDUCT_RESEARCH = GPTResearcher.conduct_research
_ORIGINAL_GPTR_WRITE_REPORT = GPTResearcher.write_report


async def _patched_conduct_research(self, *args, **kwargs):
    context = await _ORIGINAL_GPTR_CONDUCT_RESEARCH(self, *args, **kwargs)
    normalized = _normalize_context_value(context)
    self.context = normalized
    return normalized


async def _patched_write_report(self, *args, **kwargs):
    if "ext_context" in kwargs and kwargs["ext_context"] is not None:
        kwargs["ext_context"] = _normalize_context_value(kwargs["ext_context"])
    self.context = _normalize_context_value(self.context)
    return await _ORIGINAL_GPTR_WRITE_REPORT(self, *args, **kwargs)


if not getattr(GPTResearcher, "_innovera_context_patch_applied", False):
    GPTResearcher.conduct_research = _patched_conduct_research
    GPTResearcher.write_report = _patched_write_report
    GPTResearcher._innovera_context_patch_applied = True


@dataclass
class CategoryResult:
    """Output from a single evidence category execution."""
    category_id: str
    category_name: str
    status: str  # "success" | "partial" | "failed"
    raw_report: str
    structured_findings: dict
    sources: list[dict]
    gaps: list[str]
    execution_time_seconds: float
    error: Optional[str] = None


def _is_rate_limit_error(exc: Exception) -> bool:
    """Check if an exception is a rate-limit (429) error from any provider."""
    msg = str(exc).lower()
    return "429" in msg or "rate limit" in msg or "rate_limit" in msg


class BaseCategory(ABC):
    """
    Abstract base class for evidence categories.

    Each category must implement:
    - build_query(): Constructs the GPT Researcher query from context signals
    - get_report_type(): Returns "deep" or "custom_report"
    - get_config_path(): Returns path to the appropriate GPTR config
    - parse_report(): Extracts structured findings from GPT Researcher's raw report
    """

    def __init__(self, context: ContextSignals, venture_docs_dir: Path):
        self.context = context
        self.venture_docs_dir = venture_docs_dir

    @property
    @abstractmethod
    def category_id(self) -> str:
        pass

    @property
    @abstractmethod
    def category_name(self) -> str:
        pass

    @abstractmethod
    def build_query(self) -> str:
        pass

    @abstractmethod
    def get_report_type(self) -> str:
        pass

    @abstractmethod
    def get_config_path(self) -> Path:
        pass

    @abstractmethod
    def parse_report(self, raw_report: str) -> dict:
        pass

    def get_priority(self) -> PriorityLevel:
        """Look up this category's priority from the context signals."""
        for cp in self.context.category_priorities:
            if cp.category_id == self.category_id:
                return cp.priority
        return PriorityLevel.MEDIUM

    async def execute(self) -> CategoryResult:
        """Run the GPT Researcher mission with retry on rate-limit errors."""
        start_time = time.time()
        last_error: Optional[Exception] = None

        for attempt in range(RATE_LIMIT_MAX_RETRIES + 1):
            try:
                result = await self._execute_once()
                result.execution_time_seconds = time.time() - start_time
                return result

            except Exception as e:
                last_error = e
                if _is_rate_limit_error(e) and attempt < RATE_LIMIT_MAX_RETRIES:
                    delay = RATE_LIMIT_BASE_DELAY * (2 ** attempt) + random.uniform(0, 3)
                    logger.warning(
                        f"{self.category_id}: Rate limited (attempt {attempt + 1}/{RATE_LIMIT_MAX_RETRIES + 1}), "
                        f"retrying in {delay:.0f}s..."
                    )
                    print(
                        f"  [rate-limit] {self.category_id}: waiting {delay:.0f}s "
                        f"(attempt {attempt + 1}/{RATE_LIMIT_MAX_RETRIES + 1})..."
                    )
                    await asyncio.sleep(delay)
                    continue
                break

        elapsed = time.time() - start_time
        return CategoryResult(
            category_id=self.category_id,
            category_name=self.category_name,
            status="failed",
            raw_report="",
            structured_findings={},
            sources=[],
            gaps=[f"Category execution failed: {str(last_error)}"],
            execution_time_seconds=elapsed,
            error=str(last_error),
        )

    async def _execute_once(self) -> CategoryResult:
        """Single attempt to run the GPT Researcher mission."""
        query = self.build_query()
        report_type = self.get_report_type()
        config_path = str(self.get_config_path())

        researcher_kwargs = {
            "query": query,
            "report_type": report_type,
            "config_path": config_path,
        }

        if self.get_report_type() == "deep" and self._use_hybrid():
            import os
            os.environ["DOC_PATH"] = str(self.venture_docs_dir)
            researcher_kwargs["report_source"] = "hybrid"

        researcher = GPTResearcher(**researcher_kwargs)
        await researcher.conduct_research()
        raw_report = await researcher.write_report()
        sources = self._extract_sources(researcher)
        structured = self.parse_report(raw_report)
        gaps = self._identify_gaps(structured)

        return CategoryResult(
            category_id=self.category_id,
            category_name=self.category_name,
            status="success",
            raw_report=raw_report,
            structured_findings=structured,
            sources=[{"url": s} for s in sources],
            gaps=gaps,
            execution_time_seconds=0,  # filled by caller
        )

    def _use_hybrid(self) -> bool:
        """Override in subclasses that should use hybrid (web + local docs) mode."""
        return False

    def _extract_sources(self, researcher: GPTResearcher) -> list[str]:
        """Extract source URLs from the researcher's results."""
        try:
            return list(researcher.get_source_urls()) if hasattr(researcher, 'get_source_urls') else []
        except Exception:
            return []

    def _identify_gaps(self, structured: dict) -> list[str]:
        """Default gap identification."""
        gaps = []
        if not structured:
            gaps.append(f"No structured findings could be extracted for {self.category_name}")
            return gaps

        for key, value in structured.items():
            if key == "raw_report_text":
                continue
            if value is None or value == "" or value == []:
                gaps.append(f"No data found for: {key}")
            elif isinstance(value, str) and any(marker in value.lower() for marker in
                ["not found", "no data", "unavailable", "insufficient", "could not find"]):
                gaps.append(f"Gap in {key}: {value[:100]}")

        return gaps
