"""
Base class for all market research categories.
Extends the demand-validation BaseCategory with MR-specific helpers.
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from context_extraction.models import ContextSignals
from config.settings import GPTR_CONFIG_DIR


class MRBaseCategory(BaseCategory):
    """
    Base for market research categories.
    All MR categories use deep research mode.
    """

    def __init__(self, context: ContextSignals, venture_docs_dir: Path,
                 run_id: str | None = None, research_mode: str = "market_research"):
        super().__init__(context, venture_docs_dir, run_id=run_id, research_mode=research_mode)
        self.market_definition_terms: list[str] = []
        self.known_competitors: list[str] = []
        self.known_segments: list[str] = []
        self.competitive_table = None

    def inject_phase1_results(
        self,
        market_terms: list[str] | None = None,
        competitors: list[str] | None = None,
        segments: list[str] | None = None,
    ):
        """Inject extracted data from Phase 1 results for Phase 2/3 queries."""
        if market_terms:
            self.market_definition_terms = market_terms
        if competitors:
            self.known_competitors = competitors
        if segments:
            self.known_segments = segments

    def inject_competitive_table(self, table):
        """Make the competitive table available to this category's query builder."""
        self.competitive_table = table
        # Also update known competitors from the table
        if table and table.competitors:
            table_names = [c.name for c in table.competitors]
            self.known_competitors = list(set(self.known_competitors + table_names))

    def get_report_type(self) -> str:
        return "deep"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "deep_landscape.json"

    def _market_context_block(self) -> str:
        """Standard context block used by all MR queries."""
        geo = self.context.geography
        industry = self.context.industry_vertical
        sub = self.context.sub_vertical or "General"
        solution = self.context.solution_category

        block = f"""**Industry:** {industry} / {sub}
**Solution Category:** {solution}
**Geography:** {geo}
**Business Model:** {self.context.business_model_type}
**Target Buyer:** {self.context.target_buyer_type}
**Problem Context:** {self.context.problem_summary}"""

        if self.market_definition_terms:
            block += f"\n**Market Terms:** {', '.join(self.market_definition_terms)}"
        if self.known_competitors:
            block += f"\n**Known Competitors:** {', '.join(self.known_competitors[:10])}"
        if self.known_segments:
            block += f"\n**Known Segments:** {', '.join(self.known_segments[:8])}"

        return block

    def parse_report(self, raw_report: str) -> dict:
        return {"raw_report_text": raw_report}
