"""
EC-04: Alternative Solution Failures & Reviews

Deep research category for third-party reviews, recurring complaints,
workaround evidence, and shadow spend on existing solutions.
Uses competitor list from EC-02 (Phase 2 dependency).
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from config.settings import GPTR_CONFIG_DIR


class EC04AltFailuresReviews(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-04"

    @property
    def category_name(self) -> str:
        return "Alternative Solution Failures & Reviews"

    def get_report_type(self) -> str:
        return "deep"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "deep_landscape.json"

    def build_query(self) -> str:
        problem_kw = ", ".join(self.context.problem_keywords[:5])

        # Competitor review queries
        competitor_block = ""
        if self.context.named_competitors:
            comp_queries = []
            for comp in self.context.named_competitors[:8]:
                comp_queries.append(f'- Search "{comp} reviews complaints"')
                comp_queries.append(f'- Search "{comp} limitations problems"')
                comp_queries.append(f'- Search "{comp} vs alternatives"')
            competitor_block = "\n**Research reviews for each known competitor:**\n" + "\n".join(comp_queries)

        # Workaround queries
        workaround_block = ""
        if self.context.workaround_mentions:
            wa_queries = []
            for wa in self.context.workaround_mentions[:5]:
                wa_queries.append(f'- Search "{wa} limitations problems"')
            workaround_block = "\n**Research known workarounds:**\n" + "\n".join(wa_queries)

        # Customer role frustration queries
        role_block = ""
        if self.context.customer_roles:
            role_queries = [f'- Search "{role} {problem_kw} frustration"' for role in self.context.customer_roles[:3]]
            role_block = "\n**Role-specific frustration:**\n" + "\n".join(role_queries)

        query = f"""Research third-party reviews, failure patterns, and workaround evidence for existing solutions to the following problem:

**Problem:** {self.context.problem_summary}
**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Target customer:** {self.context.target_customer_summary}
**Solution category:** {self.context.solution_category}

**Workaround Evidence Queries:**
- Search "{problem_kw} workaround manual process"
- Search "{problem_kw} Excel spreadsheet tracking"
- Search "{problem_kw} internal tool built"
- Search "{self.context.industry_vertical} {problem_kw} consulting services"
{competitor_block}
{workaround_block}
{role_block}
Research and report on:

1. **Reviews by Competitor**: For each identified competitor or existing solution, find reviews on G2, Capterra, TrustRadius, and other platforms. Report: average rating, review count, top 3 complaint themes (with frequency and representative language), top praise themes, and source URLs.

2. **Workaround Evidence**: What do customers currently do without a dedicated product? Search for manual processes, spreadsheet-based tracking, internal tools, outsourced services, and consulting engagements. For each workaround: describe the approach, estimate prevalence (based on forum threads, job postings, etc.), and estimate cost (dedicated FTE, hours/week, consulting spend).

3. **Shadow Spend**: Evidence of organizations spending on consultants, extra staff, or ad-hoc services to patch gaps in existing solutions.

4. **Failure Pattern Synthesis**:
   - What are the dominant failure modes across existing solutions?
   - What is the single biggest underserved need?
   - How prevalent are workarounds (high / moderate / low / unknown)?

Focus on substance of failures, not just sentiment. Cite specific review platforms and note the recency and volume of reviews. If a competitor has fewer than 20 reviews, flag this as limited data."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
        }
