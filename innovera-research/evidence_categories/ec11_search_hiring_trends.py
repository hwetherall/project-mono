"""
EC-11: Search & Hiring Trends

Targeted lookup category for Google Trends data, search volumes,
job posting trends, and competitor hiring patterns.
Uses competitor list from EC-02 (Phase 2 dependency).
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from config.settings import GPTR_CONFIG_DIR


class EC11SearchHiringTrends(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-11"

    @property
    def category_name(self) -> str:
        return "Search & Hiring Trends"

    def get_report_type(self) -> str:
        return "custom_report"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "targeted_lookup.json"

    def build_query(self) -> str:
        problem_kw = ", ".join(self.context.problem_keywords[:5])
        geo = self.context.geography

        # Competitor hiring queries
        competitor_block = ""
        if self.context.named_competitors:
            comp_queries = []
            for comp in self.context.named_competitors[:8]:
                comp_queries.append(f'- Search "{comp} hiring growth headcount"')
                comp_queries.append(f'- Search "{comp} job openings"')
            competitor_block = "\n**Competitor Hiring Analysis:**\n" + "\n".join(comp_queries)

        # New vs established term comparison
        term_block = ""
        if self.context.solution_category != self.context.industry_vertical:
            term_block = f"""
**Term Comparison**: Compare search interest in the newer term "{self.context.solution_category}" vs. established equivalents in {self.context.industry_vertical}. Is the new category term gaining search traction?
"""

        query = f"""Research search trends, keyword volumes, and job posting data for the following problem and solution space:

**Problem keywords:** {problem_kw}
**Solution category:** {self.context.solution_category}
**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Geography:** {geo}

Search for: "{problem_kw} Google Trends interest", "{self.context.solution_category} search volume growth", "{problem_kw} job postings {geo}", "{problem_kw} hiring trends {self.context.industry_vertical}".

Find and report:

1. **Search Trends**: Google Trends data for problem-related and solution-related search terms. For each term: trend direction (growing/stable/declining), growth rate over past 12-24 months, current relative volume, and geographic concentration. Use Google Trends, SEMrush, or Ahrefs data.

2. **Job Posting Trends**: Are organizations hiring people to manually solve this problem? Search Indeed, LinkedIn Jobs, and Glassdoor for roles related to {problem_kw}. Report: posting volume, trend direction, types of employers posting, and what this indicates about internal investment in the problem area.

3. **Problem-Related Hiring**: Roles that indicate organizations are investing in solving the problem internally (e.g., hiring specialists, creating new teams). What job titles are appearing?

4. **Solution-Category Growth Signals**: Is there growing search interest in the solution category itself? Are more companies looking for this type of product?
{competitor_block}
{term_block}
For each data point, cite the specific source and timeframe. Note limitations: Google Trends may not capture B2B-specific search behavior well; job posting data may skew toward certain geographies or industries."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
        }
