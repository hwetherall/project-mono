"""
Main orchestration runner.
Executes evidence categories in phased order with parallel execution within phases.
"""
import asyncio
import time
from pathlib import Path
from typing import Optional

from context_extraction.models import ContextSignals
from evidence_categories.base import CategoryResult
from evidence_categories.registry import (
    Phase, CATEGORY_REGISTRY, get_categories_by_phase
)
from orchestrator.phases import get_execution_plan
from orchestrator.progress import ProgressTracker
from config.settings import MAX_CONCURRENT_CATEGORIES, CATEGORY_TIMEOUT_SECONDS

# Import all category classes
from evidence_categories.ec01_market_sizing import EC01MarketSizing
from evidence_categories.ec02_competitor_landscape import EC02CompetitorLandscape
from evidence_categories.ec03_investment_signals import EC03InvestmentSignals
from evidence_categories.ec04_alt_failures_reviews import EC04AltFailuresReviews
from evidence_categories.ec05_problem_prevalence import EC05ProblemPrevalence
from evidence_categories.ec06_regulatory_compliance import EC06RegulatoryCompliance
from evidence_categories.ec07_enabling_tech import EC07EnablingTech
from evidence_categories.ec08_urgency_forcing import EC08UrgencyForcing
from evidence_categories.ec09_analyst_coverage import EC09AnalystCoverage
from evidence_categories.ec10_voice_of_market import EC10VoiceOfMarket
from evidence_categories.ec11_search_hiring_trends import EC11SearchHiringTrends
from evidence_categories.ec12_budget_procurement import EC12BudgetProcurement
from evidence_categories.ec13_proxy_markets import EC13ProxyMarkets

# Map category IDs to their implementation classes
CATEGORY_CLASSES = {
    "EC-01": EC01MarketSizing,
    "EC-02": EC02CompetitorLandscape,
    "EC-03": EC03InvestmentSignals,
    "EC-04": EC04AltFailuresReviews,
    "EC-05": EC05ProblemPrevalence,
    "EC-06": EC06RegulatoryCompliance,
    "EC-07": EC07EnablingTech,
    "EC-08": EC08UrgencyForcing,
    "EC-09": EC09AnalystCoverage,
    "EC-10": EC10VoiceOfMarket,
    "EC-11": EC11SearchHiringTrends,
    "EC-12": EC12BudgetProcurement,
    "EC-13": EC13ProxyMarkets,
}


class ResearchRunner:
    """Orchestrates the phased execution of all evidence categories."""

    def __init__(
        self,
        context: ContextSignals,
        venture_docs_dir: Path,
        progress: Optional[ProgressTracker] = None,
        only_categories: Optional[list[str]] = None,
    ):
        self.context = context
        self.venture_docs_dir = venture_docs_dir
        self.progress = progress or ProgressTracker()
        self.results: dict[str, CategoryResult] = {}
        self.competitor_list: list[str] = []
        self.only_categories = set(only_categories) if only_categories else None

    def _should_run(self, category_id: str) -> bool:
        """Check if a category should run based on --only filter."""
        if self.only_categories is None:
            return category_id in CATEGORY_CLASSES
        return category_id in self.only_categories and category_id in CATEGORY_CLASSES

    async def run_all(self) -> dict[str, CategoryResult]:
        """Execute all phases in order."""
        plan = get_execution_plan()
        total_start = time.time()

        for phase_info in plan:
            phase_name = phase_info["phase_name"]
            category_ids = phase_info["categories"]

            runnable = [cid for cid in category_ids if self._should_run(cid)]

            if not runnable:
                if self.only_categories:
                    continue
                self.progress.start_phase(phase_name, category_ids)
                self.progress.log(f"Phase {phase_name}: no categories to run, skipping")
                self.progress.end_phase(phase_name)
                continue

            self.progress.start_phase(phase_name, runnable)
            runnable = self._filter_by_priority(runnable)

            semaphore = asyncio.Semaphore(MAX_CONCURRENT_CATEGORIES)

            async def run_with_semaphore(cid: str):
                async with semaphore:
                    return await self._run_category(cid)

            phase_results = await asyncio.gather(
                *[run_with_semaphore(cid) for cid in runnable],
                return_exceptions=True,
            )

            for cid, result in zip(runnable, phase_results):
                if isinstance(result, Exception):
                    self.results[cid] = CategoryResult(
                        category_id=cid,
                        category_name=CATEGORY_REGISTRY[cid].category_name,
                        status="failed",
                        raw_report="",
                        structured_findings={},
                        sources=[],
                        gaps=[f"Unhandled exception: {str(result)}"],
                        execution_time_seconds=0,
                        error=str(result),
                    )
                else:
                    self.results[cid] = result

            if phase_info["phase"] == Phase.FOUNDATION:
                self._extract_competitor_list()

            self.progress.end_phase(phase_name)

        total_elapsed = time.time() - total_start
        self.progress.complete(total_elapsed)

        return self.results

    async def _run_category(self, category_id: str) -> CategoryResult:
        """Run a single category with timeout."""
        self.progress.start_category(category_id)

        category_class = CATEGORY_CLASSES[category_id]
        category = category_class(
            context=self.context,
            venture_docs_dir=self.venture_docs_dir,
        )

        # If this is a Phase 2 category, inject competitor list into context
        if category_id in ["EC-03", "EC-04", "EC-11"] and self.competitor_list:
            all_competitors = list(set(
                self.context.named_competitors + self.competitor_list
            ))
            self.context.named_competitors = all_competitors

        try:
            result = await asyncio.wait_for(
                category.execute(),
                timeout=CATEGORY_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            result = CategoryResult(
                category_id=category_id,
                category_name=CATEGORY_REGISTRY[category_id].category_name,
                status="failed",
                raw_report="",
                structured_findings={},
                sources=[],
                gaps=[f"Category timed out after {CATEGORY_TIMEOUT_SECONDS}s"],
                execution_time_seconds=CATEGORY_TIMEOUT_SECONDS,
                error="Timeout",
            )

        self.progress.end_category(category_id, result.status)
        return result

    def _extract_competitor_list(self):
        """After Phase 1, pull the competitor list from EC-02's results."""
        ec02_result = self.results.get("EC-02")
        if ec02_result and ec02_result.status == "success":
            ec02_instance = EC02CompetitorLandscape(
                context=self.context,
                venture_docs_dir=self.venture_docs_dir,
            )
            self.competitor_list = ec02_instance.get_competitor_list(ec02_result)
            self.progress.log(
                f"Extracted {len(self.competitor_list)} competitors from EC-02: "
                f"{', '.join(self.competitor_list[:5])}{'...' if len(self.competitor_list) > 5 else ''}"
            )

    def _filter_by_priority(self, category_ids: list[str]) -> list[str]:
        """Optionally filter out low-priority categories. V1: run everything."""
        return category_ids
