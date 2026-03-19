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
from market_research.registry import (
    MRPhase, MR_CATEGORY_REGISTRY, get_mr_categories_by_phase
)
from orchestrator.phases import get_execution_plan, get_mr_execution_plan
from orchestrator.progress import ProgressTracker
from config.settings import MAX_CONCURRENT_CATEGORIES, CATEGORY_TIMEOUT_SECONDS, CONSULTANT_PRIMER_ENABLED
from orchestrator.checkpoints import load_checkpoint, mark_checkpoint_error, is_resumable

# Import all EC category classes
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

# Import all MR category classes
from market_research.mr01a_market_boundaries import MR01aMarketBoundaries
from market_research.mr01b_market_sizing import MR01bMarketSizing
from market_research.mr02_sam_som import MR02SamSom
from market_research.mr03_segments import MR03Segments
from market_research.mr04_trends import MR04Trends
from market_research.mr05_value_chain import MR05ValueChain
from market_research.mr06a_competitor_identification import MR06aCompetitorIdentification
from market_research.mr06b_competitive_intelligence import MR06bCompetitiveIntelligence
from market_research.mr07_buying_process import MR07BuyingProcess
from market_research.mr08_adoption_dynamics import MR08AdoptionDynamics
from market_research.mr09_regulation_platform import MR09RegulationPlatform
from market_research.mr10_barriers_ecosystem import MR10BarriersEcosystem

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

MR_CATEGORY_CLASSES = {
    "MR-01a": MR01aMarketBoundaries,
    "MR-01b": MR01bMarketSizing,
    "MR-02": MR02SamSom,
    "MR-03": MR03Segments,
    "MR-04": MR04Trends,
    "MR-05": MR05ValueChain,
    "MR-06a": MR06aCompetitorIdentification,
    "MR-06b": MR06bCompetitiveIntelligence,
    "MR-07": MR07BuyingProcess,
    "MR-08": MR08AdoptionDynamics,
    "MR-09": MR09RegulationPlatform,
    "MR-10": MR10BarriersEcosystem,
}


class ResearchRunner:
    """Orchestrates the phased execution of all evidence categories."""

    def __init__(
        self,
        context: ContextSignals,
        venture_docs_dir: Path,
        progress: Optional[ProgressTracker] = None,
        only_categories: Optional[list[str]] = None,
        research_mode: str = "demand_validation",
        run_id: Optional[str] = None,
        competitive_table=None,
    ):
        self.context = context
        self.venture_docs_dir = venture_docs_dir
        self.progress = progress or ProgressTracker()
        self.results: dict[str, CategoryResult] = {}
        self.competitor_list: list[str] = []
        self.only_categories = set(only_categories) if only_categories else None
        self.research_mode = research_mode
        self.run_id = run_id
        self.competitive_table = competitive_table
        self.competitive_table_status = "complete" if competitive_table else None
        self.consultant_context = None  # Populated by _run_consultant_primer()

        # Select the correct category classes and registry based on mode
        if self.research_mode == "market_research":
            self._category_classes = MR_CATEGORY_CLASSES
            self._category_registry = MR_CATEGORY_REGISTRY
        else:
            self._category_classes = CATEGORY_CLASSES
            self._category_registry = CATEGORY_REGISTRY

    def _should_run(self, category_id: str) -> bool:
        """Check if a category should run based on --only filter."""
        if self.only_categories is None:
            return category_id in self._category_classes
        return category_id in self.only_categories and category_id in self._category_classes

    async def run_all(self) -> dict[str, CategoryResult]:
        """Execute all phases in order."""
        if self.research_mode == "market_research":
            plan = get_mr_execution_plan()
        else:
            plan = get_execution_plan()

        total_start = time.time()

        # Pre-Phase: Consultant Primer (before everything else)
        await self._run_consultant_primer()

        # Phase 0: Build Competitive Table (before category phases)
        await self._build_competitive_table()

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
                    cat_meta = self._category_registry.get(cid)
                    cat_name = cat_meta.category_name if cat_meta else cid
                    self.results[cid] = CategoryResult(
                        category_id=cid,
                        category_name=cat_name,
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

            # Phase summary log
            phase_succeeded = sum(1 for cid in runnable if self.results.get(cid) and self.results[cid].status == "success")
            phase_failed = len(runnable) - phase_succeeded
            phase_sources = sum(len(self.results[cid].sources) for cid in runnable if self.results.get(cid))
            if hasattr(self.progress, 'emit_log_detail'):
                self.progress.emit_log_detail(
                    f"{phase_name}: {phase_succeeded}/{len(runnable)} categories succeeded, {phase_sources} sources collected",
                    "success" if phase_failed == 0 else "warning",
                )

            # Post-phase extraction hooks
            if self.research_mode == "demand_validation" and phase_info["phase"] == Phase.FOUNDATION:
                self._extract_competitor_list()
            elif self.research_mode == "market_research" and phase_info["phase"] == MRPhase.FOUNDATION:
                self._extract_market_research_context()

            self.progress.end_phase(phase_name)

        total_elapsed = time.time() - total_start
        self.progress.complete(total_elapsed)

        return self.results

    async def _run_category(self, category_id: str) -> CategoryResult:
        """Run a single category with timeout and checkpoint-aware recovery."""
        self.progress.start_category(category_id)

        category_class = self._category_classes[category_id]
        category = category_class(
            context=self.context,
            venture_docs_dir=self.venture_docs_dir,
            run_id=self.run_id,
            research_mode=self.research_mode,
            consultant_context=self.consultant_context,
        )

        # Demand validation: inject competitor list for Phase 2 categories
        if self.research_mode == "demand_validation":
            if category_id in ["EC-03", "EC-04", "EC-11"] and self.competitor_list:
                all_competitors = list(set(
                    self.context.named_competitors + self.competitor_list
                ))
                self.context.named_competitors = all_competitors

        # Market research: inject Phase 1 context into Phase 2/3 categories
        if self.research_mode == "market_research":
            if hasattr(category, 'inject_phase1_results'):
                category.inject_phase1_results(
                    market_terms=self.context.market_definition_terms,
                    competitors=self.context.named_competitors,
                    segments=getattr(self.context, 'buyer_segments', []),
                )
            # Inject competitive table if available
            if self.competitive_table and hasattr(category, 'inject_competitive_table'):
                category.inject_competitive_table(self.competitive_table)

        try:
            result = await asyncio.wait_for(
                category.execute(),
                timeout=CATEGORY_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            cat_meta = self._category_registry.get(category_id)
            cat_name = cat_meta.category_name if cat_meta else category_id

            # Check if checkpoint has resumable progress
            checkpoint = load_checkpoint(self.run_id, category_id) if self.run_id else None
            can_resume = checkpoint and is_resumable(checkpoint)

            if checkpoint and self.run_id:
                mark_checkpoint_error(self.run_id, category_id, "Timeout", CATEGORY_TIMEOUT_SECONDS)

            # Build a result that reflects checkpoint state
            raw_report = (checkpoint or {}).get("raw_report", "")
            source_urls = (checkpoint or {}).get("source_urls", [])
            structured = (checkpoint or {}).get("structured_findings", {})
            stage = (checkpoint or {}).get("stage", "")

            timeout_msg = f"Category timed out after {CATEGORY_TIMEOUT_SECONDS}s"
            if can_resume:
                timeout_msg += f" — checkpoint saved at {stage}"

            result = CategoryResult(
                category_id=category_id,
                category_name=cat_name,
                status="failed",
                raw_report=raw_report,
                structured_findings=structured,
                sources=[{"url": s} for s in source_urls],
                gaps=[timeout_msg],
                execution_time_seconds=CATEGORY_TIMEOUT_SECONDS,
                error="Timeout",
            )

        self.progress.end_category(
            category_id,
            result.status,
            error=result.error,
            source_count=len(result.sources),
            gap_count=len(result.gaps),
        )
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

    def _extract_market_research_context(self):
        """After MR Phase 1, extract market terms from MR-01a/MR-01b and competitors from MR-06a."""
        market_terms = []
        for mr_id in ("MR-01a", "MR-01b"):
            result = self.results.get(mr_id)
            if result and result.structured_findings:
                market_terms.extend(result.structured_findings.get("market_terms_extracted", []))

        competitor_terms = []
        mr06a_result = self.results.get("MR-06a")
        if mr06a_result and mr06a_result.structured_findings:
            competitor_terms = mr06a_result.structured_findings.get("competitor_names_extracted", [])

        self.context.market_definition_terms = list(set(
            self.context.market_definition_terms + market_terms
        ))
        self.context.named_competitors = list(set(
            self.context.named_competitors + competitor_terms
        ))

        # Also store competitor list for progress reporting
        if competitor_terms:
            self.competitor_list = list(set(self.context.named_competitors))

        self.progress.log(
            f"Extracted {len(self.context.market_definition_terms)} market terms and "
            f"{len(self.context.named_competitors)} competitor names from Phase 1"
        )

    def _filter_by_priority(self, category_ids: list[str]) -> list[str]:
        """Optionally filter out low-priority categories. V1: run everything."""
        return category_ids

    async def _run_consultant_primer(self):
        """Pre-Phase: Search consulting firm domains and extract insights."""
        import json as _json
        import logging

        _logger = logging.getLogger(__name__)

        if not CONSULTANT_PRIMER_ENABLED:
            self.progress.log("Consultant primer disabled, skipping")
            return

        # Check for existing checkpoint
        if self.run_id:
            cp = load_checkpoint(self.run_id, "CONSULTANT-PRIMER")
            if cp and cp.get("stage") == "completed":
                try:
                    from consultant_primer.models import ConsultantContext
                    self.consultant_context = ConsultantContext.model_validate(
                        cp.get("payload", {})
                    )
                    self.progress.log(
                        f"Consultant primer loaded from checkpoint: "
                        f"{self.consultant_context.coverage_summary}"
                    )
                    return
                except Exception as exc:
                    _logger.warning("Failed to load consultant primer checkpoint: %s", exc)

        try:
            from consultant_primer.primer import run_consultant_primer
            from consultant_primer.models import ConsultantContext

            self.consultant_context = await run_consultant_primer(
                context=self.context,
                progress=self.progress,
            )

            # Save checkpoint
            if self.run_id:
                self._save_ct_checkpoint("CONSULTANT-PRIMER", {
                    "stage": "completed",
                    "payload": self.consultant_context.model_dump(),
                })

        except Exception as exc:
            _logger.warning("Consultant primer failed (non-blocking): %s", exc, exc_info=True)
            if hasattr(self.progress, 'emit_log_detail'):
                self.progress.emit_log_detail(
                    f"Consultant primer failed (non-blocking): {exc}", "warning"
                )
            else:
                self.progress.log(f"Consultant primer failed (non-blocking): {exc}")
            # Graceful degradation: continue without consultant context

    async def _build_competitive_table(self):
        """Phase 0: Build the Competitive Table before category phases."""
        import json
        import logging
        from datetime import datetime, timezone
        from config.settings import OUTPUT_DIR, GPTR_CONFIG_DIR, CATEGORY_TIMEOUT_SECONDS

        logger = logging.getLogger(__name__)

        if self.competitive_table is not None:
            self.competitive_table_status = "complete"
            self._enrich_context_from_table()
            self.progress.log("Competitive table pre-loaded (skipping rebuild)")
            if hasattr(self.progress, 'emit_competitive_table_status'):
                ct = self.competitive_table
                self.progress.emit_competitive_table_status(
                    "complete", "done",
                    competitors=len(ct.competitors),
                    attributes=len(ct.attributes),
                    coverage=ct.metadata.coverage_percent if ct.metadata else None,
                )
            return

        self.competitive_table_status = "pending"

        # Check for existing completed table checkpoint
        if self.run_id:
            from orchestrator.checkpoints import load_checkpoint
            ct_checkpoint = load_checkpoint(self.run_id, "CT-complete")
            if ct_checkpoint and ct_checkpoint.get("stage") == "finalized":
                try:
                    from competitive_table.models import CompetitiveTable
                    table_path = OUTPUT_DIR / self.run_id / "competitive_table.json"
                    if table_path.exists():
                        table_data = json.loads(table_path.read_text(encoding="utf-8"))
                        self.competitive_table = CompetitiveTable.model_validate(table_data)
                        self.competitive_table_status = "complete"
                        self._enrich_context_from_table()
                        self.progress.log("Competitive table loaded from checkpoint")
                        return
                except Exception as exc:
                    logger.warning("Failed to load table from checkpoint: %s", exc)

        try:
            self.competitive_table_status = "building"

            from competitive_table.models import CompetitiveTable, CompetitiveTableSchema
            from competitive_table.schema_generator import generate_table_schema
            from competitive_table.competitor_discovery import discover_competitors
            from competitive_table.table_populator import populate_table, populate_venture_column
            from competitive_table.table_validator import compute_metadata, validate_and_summarize

            config_path = str(GPTR_CONFIG_DIR / "deep_landscape.json")
            table_start = time.time()

            # Emit progress
            if hasattr(self.progress, 'emit_competitive_table_status'):
                self.progress.emit_competitive_table_status("building", "schema_generation")
            if hasattr(self.progress, 'emit_log_detail'):
                self.progress.emit_log_detail(
                    f"Generating competitive framework for {self.context.industry_vertical}...", "info"
                )

            # Step 1: Schema generation
            schema = generate_table_schema(self.context)
            self._save_ct_checkpoint("CT-schema", schema.model_dump())

            if hasattr(self.progress, 'emit_competitive_table_status'):
                self.progress.emit_competitive_table_status("building", "competitor_discovery")
            if hasattr(self.progress, 'emit_log_detail'):
                self.progress.emit_log_detail(
                    f"Discovering competitors in {self.context.industry_vertical}...", "info"
                )

            # Step 2: Competitor discovery
            competitors = await asyncio.wait_for(
                discover_competitors(self.context, schema, config_path),
                timeout=CATEGORY_TIMEOUT_SECONDS,
            )
            self._save_ct_checkpoint("CT-discovery", {
                "competitors": [c.model_dump() for c in competitors],
            })

            if hasattr(self.progress, 'emit_competitive_table_status'):
                self.progress.emit_competitive_table_status(
                    "building", "competitor_discovery", found=len(competitors)
                )
            if hasattr(self.progress, 'emit_log_detail'):
                tier_counts = {}
                for c in competitors:
                    tier_counts[c.tier] = tier_counts.get(c.tier, 0) + 1
                tier_str = ", ".join(f"Tier {t}: {n}" for t, n in sorted(tier_counts.items()))
                self.progress.emit_log_detail(
                    f"Found {len(competitors)} competitors ({tier_str})", "info"
                )

            # Step 3: Table population
            def progress_callback(step, completed, total):
                if hasattr(self.progress, 'emit_competitive_table_status'):
                    self.progress.emit_competitive_table_status(
                        "building", step, completed=completed, total=total
                    )

            populated = await populate_table(
                competitors, schema.attributes, self.context, config_path,
                progress_callback=progress_callback,
                run_id=self.run_id,
            )

            # Step 4: Venture column
            if hasattr(self.progress, 'emit_log_detail'):
                self.progress.emit_log_detail("Populating venture column from brief...", "info")

            venture_brief_text = ""
            brief_path = self.venture_docs_dir / "venture_brief.md"
            if brief_path.exists():
                venture_brief_text = brief_path.read_text(encoding="utf-8")

            venture_entry = await populate_venture_column(
                self.context, schema.attributes, venture_brief_text
            )

            # Build the table
            research_time = time.time() - table_start
            table = CompetitiveTable(
                table_id=self.run_id or "local",
                venture_name=self.context.venture_name,
                industry=self.context.industry_vertical,
                geography=self.context.geography,
                generated_at=datetime.now(timezone.utc).isoformat(),
                attributes=schema.attributes,
                competitors=populated,
                venture_entry=venture_entry,
                attribute_groups=schema.attribute_groups,
                metadata=compute_metadata(
                    CompetitiveTable(
                        table_id=self.run_id or "local",
                        venture_name=self.context.venture_name,
                        industry=self.context.industry_vertical,
                        geography=self.context.geography,
                        attributes=schema.attributes,
                        competitors=populated,
                        venture_entry=venture_entry,
                        attribute_groups=schema.attribute_groups,
                    ),
                    research_time,
                ),
            )
            table.metadata.rationale = schema.rationale

            # Step 5: Validation & summary
            if hasattr(self.progress, 'emit_log_detail'):
                self.progress.emit_log_detail("Validating competitive table...", "info")

            await validate_and_summarize(table)

            # Save table to disk
            if self.run_id:
                table_dir = OUTPUT_DIR / self.run_id
                table_dir.mkdir(parents=True, exist_ok=True)
                table_path = table_dir / "competitive_table.json"
                table_path.write_text(
                    table.model_dump_json(indent=2),
                    encoding="utf-8",
                )
                self._save_ct_checkpoint("CT-complete", {"stage": "finalized"})

            self.competitive_table = table
            self.competitive_table_status = "complete"
            self._enrich_context_from_table()

            if hasattr(self.progress, 'emit_competitive_table_status'):
                self.progress.emit_competitive_table_status(
                    "complete", "done",
                    competitors=len(table.competitors),
                    attributes=len(table.attributes),
                    coverage=table.metadata.coverage_percent,
                )
            if hasattr(self.progress, 'emit_log_detail'):
                self.progress.emit_log_detail(
                    f"Competitive table complete: {len(table.competitors)} competitors, "
                    f"{len(table.attributes)} attributes, {table.metadata.coverage_percent:.0f}% coverage",
                    "success",
                )

        except Exception as exc:
            self.competitive_table_status = "failed"
            logger.warning("Competitive table construction failed: %s", exc, exc_info=True)
            if hasattr(self.progress, 'emit_competitive_table_status'):
                self.progress.emit_competitive_table_status("failed", "error")
            if hasattr(self.progress, 'emit_log_detail'):
                self.progress.emit_log_detail(
                    f"Competitive table failed (non-blocking): {exc}", "warning"
                )
            # Non-blocking: existing pipeline continues without the table

    def _enrich_context_from_table(self):
        """Update ContextSignals with competitor names from the table."""
        if not self.competitive_table:
            return
        table_names = [c.name for c in self.competitive_table.competitors]
        self.context.named_competitors = list(set(
            self.context.named_competitors + table_names
        ))
        self.competitor_list = list(self.context.named_competitors)

    def _save_ct_checkpoint(self, checkpoint_id: str, data: dict):
        """Save a competitive table checkpoint."""
        if not self.run_id:
            return
        try:
            import json
            from config.settings import OUTPUT_DIR
            cp_dir = OUTPUT_DIR / self.run_id / "checkpoints"
            cp_dir.mkdir(parents=True, exist_ok=True)
            cp_path = cp_dir / f"{checkpoint_id}.json"
            cp_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        except Exception:
            pass
