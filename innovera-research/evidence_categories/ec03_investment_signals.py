"""
EC-03: Investment & Financial Signals

Targeted lookup category for VC funding, M&A activity, IPOs,
and public company moves in the solution space.
Uses competitor list from EC-02 (Phase 2 dependency).
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from config.settings import GPTR_CONFIG_DIR


class EC03InvestmentSignals(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-03"

    @property
    def category_name(self) -> str:
        return "Investment & Financial Signals"

    def get_report_type(self) -> str:
        return "custom_report"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "targeted_lookup.json"

    def build_query(self) -> str:
        # Competitor funding queries
        competitor_block = ""
        if self.context.named_competitors:
            comp_queries = []
            for comp in self.context.named_competitors[:10]:
                comp_queries.append(f'- "{comp} funding raised investors"')
                comp_queries.append(f'- "{comp} acquisition"')
            competitor_block = "\n**Research funding for each known competitor:**\n" + "\n".join(comp_queries)

        # Parent company block
        parent_block = ""
        if self.context.parent_company:
            parent_block = f"""
**Corporate Parent Activity:**
- Search for "{self.context.parent_company} venture investments {self.context.industry_vertical}"
- Search for "{self.context.parent_company} competitors innovation"
"""

        query = f"""Research venture capital investment, M&A activity, and financial signals in the following space:

**Solution category:** {self.context.solution_category}
**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Geography:** {self.context.geography}
**Problem domain:** {self.context.problem_summary}

Search for: "{self.context.solution_category} funding rounds 2025 2026", "{self.context.solution_category} venture capital investment", "{self.context.solution_category} acquisitions mergers", "{self.context.industry_vertical} technology investment trends".

Find and report:

1. **Funding Activity**: Recent venture capital rounds in this space. For each round: company name, round type (Seed/A/B/C+), amount raised, date, lead investor, and source URL. Search Crunchbase, PitchBook, and TechCrunch.

2. **M&A Activity**: Acquisitions and mergers in the space. For each: acquirer, target, amount (or "undisclosed"), date, strategic rationale, and source.

3. **Aggregate Investment Signals**:
   - Total funding in the space over the last 24 months
   - Funding trend direction (accelerating / stable / decelerating)
   - Largest round in the space
   - Investor quality signal (Tier 1 VCs active? Mostly seed-stage? Corporate strategic only?)
   - Public company interest (any public companies entering this space?)

4. **Corporate Venture Activity**: Are major corporations investing strategically in this space? Any corporate venture arms active?

5. **Public Company Earnings References**: Any public company earnings calls or investor presentations referencing the problem domain ({self.context.industry_vertical}, {', '.join(self.context.problem_keywords[:3])})?
{competitor_block}
{parent_block}
For every data point, cite the specific source and date. Note where funding data may be incomplete (non-US companies, stealth-mode startups, undisclosed rounds)."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
        }
