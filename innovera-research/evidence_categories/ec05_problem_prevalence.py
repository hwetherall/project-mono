"""
EC-05: Problem Prevalence & Cost Data

Deep research (hybrid) category for statistical evidence of problem
prevalence, cost-of-problem figures, and frequency data.
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from config.settings import GPTR_CONFIG_DIR


class EC05ProblemPrevalence(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-05"

    @property
    def category_name(self) -> str:
        return "Problem Prevalence & Cost Data"

    def get_report_type(self) -> str:
        return "deep"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "hybrid_mission.json"

    def _use_hybrid(self) -> bool:
        return True

    def build_query(self) -> str:
        problem_kw = ", ".join(self.context.problem_keywords[:5])
        geo = self.context.geography

        # Conditional queries based on pain drivers
        compliance_block = ""
        if any(d in " ".join(self.context.pain_drivers).lower() for d in ["compliance", "regulatory"]):
            regs = ", ".join(self.context.named_regulations[:3]) if self.context.named_regulations else self.context.industry_vertical
            compliance_block = f"""
- Search for "{self.context.industry_vertical} compliance failure cost penalty"
- Search for "{regs} non-compliance cost statistics"
"""

        safety_block = ""
        if any(d in " ".join(self.context.pain_drivers).lower() for d in ["safety", "risk", "incident"]):
            safety_block = f"""
- Search for "{problem_kw} incident rate accident statistics"
- Search for "{problem_kw} liability claims cost"
"""

        query = f"""Synthesize available data on the cost and prevalence of the following problem:

**Problem:** {self.context.problem_summary}
**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Geography:** {geo}
**Target customer type:** {self.context.target_customer_summary}
**Known pain drivers:** {', '.join(self.context.pain_drivers)}

Research and report on:

1. **Prevalence Data**: How widespread is this problem? Search for "{problem_kw} statistics {geo}", "{self.context.industry_vertical} failure rate statistics". What percentage of target organizations are affected? How many organizations/individuals experience this problem?

2. **Per-Incident Cost**: What does each occurrence of the problem cost? Search for "{problem_kw} cost per incident", "{problem_kw} annual cost industry". Include direct costs (repair, downtime, penalties) and indirect costs (lost productivity, reputation, safety).

3. **Annual Cost Per Organization**: What does a typical {self.context.target_buyer_type} organization spend dealing with this problem annually? Search for "{problem_kw} benchmark study report".

4. **Industry-Wide Cost**: What is the total cost of this problem across the {self.context.industry_vertical} industry in {geo}?

5. **Frequency Data**: How often does the problem occur? What's the failure rate, incident rate, or frequency of occurrence?

6. **Trend Direction**: Is the problem getting worse, staying stable, or improving? What data supports the trend assessment?

7. **Cost-of-Problem Synthesis**: Calculate a per-customer annual cost estimate using: frequency x cost-per-incident = annual cost. Show the math and note what's sourced vs. estimated.
{compliance_block}{safety_block}
For every data point, cite the specific source and publication date. Distinguish between: government statistics, academic studies, industry benchmarks, consulting firm estimates, and insurance/actuarial data. Note data quality and recency for each source. Prioritize data from the last 24 months. If only older data exists, note this explicitly.

Focus on {geo} data where available, with global data as fallback."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
        }
