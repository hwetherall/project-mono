"""
EC-07: Enabling Technology Trends

Deep research category for technology shifts, cost curves,
and infrastructure readiness that make the venture's solution
feasible or economically viable now.
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from config.settings import GPTR_CONFIG_DIR


class EC07EnablingTech(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-07"

    @property
    def category_name(self) -> str:
        return "Enabling Technology Trends"

    def get_report_type(self) -> str:
        return "deep"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "deep_landscape.json"

    def build_query(self) -> str:
        tech_stack = ", ".join(self.context.technology_stack) if self.context.technology_stack else self.context.solution_category
        geo = self.context.geography

        # IoT-specific queries
        iot_block = ""
        if any("iot" in t.lower() for t in self.context.technology_stack):
            iot_block = f"""
**IoT-Specific Research:**
- Search "IoT sensor cost reduction trends"
- Search "IoT connectivity infrastructure {geo}"
- Search "industrial IoT adoption rate {self.context.industry_vertical}"
"""

        # AI/ML-specific queries
        ai_block = ""
        if any(t.lower() in ["ai", "ml", "machine learning", "artificial intelligence", "llm", "deep learning"] for t in self.context.technology_stack):
            ai_block = f"""
**AI/ML-Specific Research:**
- Search "AI {self.context.industry_vertical} adoption readiness"
- Search "foundation model cost per token trends"
- Search "AI implementation cost {self.context.industry_vertical}"
"""

        # Cloud-specific queries
        cloud_block = ""
        if any(t.lower() in ["cloud", "saas", "aws", "azure", "gcp"] for t in self.context.technology_stack):
            cloud_block = f"""
**Cloud-Specific Research:**
- Search "cloud adoption {self.context.industry_vertical} {geo}"
- Search "edge computing {self.context.industry_vertical}"
"""

        query = f"""Research enabling technology trends that make the following venture's solution feasible or economically viable now:

**Solution:** {self.context.solution_summary}
**Technology stack:** {tech_stack}
**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Geography:** {geo}
**Problem being solved:** {self.context.problem_summary}

Search for: "{tech_stack} cost trends 2025 2026", "{tech_stack} adoption rate enterprise", "{self.context.solution_category} technology enablers", "{tech_stack} maturity enterprise readiness".

Research and report on:

1. **Enabling Technology Shifts**: What technology changes have occurred in the last 3-5 years that make this solution possible or practical? For each shift: what changed, when, how it enables the venture's solution, maturity level (emerging/maturing/mature), and specific evidence/data points.

2. **Cost Curves**: How have costs changed for key enabling technologies? For each: technology name, cost trajectory (e.g., "dropped X% over Y years"), current cost per unit, projected future cost, and source.

3. **Infrastructure Readiness**: Is the necessary infrastructure in place for this solution to work? Key dependencies, geographic variation in readiness, and any significant gaps in {geo} specifically.

4. **Platform & API Ecosystem**: Are there new platforms, APIs, or services that reduce the build cost or time for this type of solution? What didn't exist 3-5 years ago that exists now?

5. **Technical Feasibility Assessment**: Based on technology readiness, is this solution technically feasible today at scale? What are the remaining technical risks or dependencies?
{iot_block}{ai_block}{cloud_block}
For each technology trend, cite specific sources with dates. Distinguish between: established trends with hard data, emerging trends with directional evidence, and speculative forecasts. Note where {geo}-specific data differs from global trends."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
        }
