"""
EC-09: Industry Analyst & Expert Coverage

Deep research category for analyst reports, trade publication coverage,
conference themes, and expert commentary on the problem domain.
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from config.settings import GPTR_CONFIG_DIR


class EC09AnalystCoverage(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-09"

    @property
    def category_name(self) -> str:
        return "Industry Analyst & Expert Coverage"

    def get_report_type(self) -> str:
        return "deep"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "deep_landscape.json"

    def build_query(self) -> str:
        problem_kw = ", ".join(self.context.problem_keywords[:5])

        query = f"""Research industry analyst and expert coverage of the following problem domain and solution category:

**Solution category:** {self.context.solution_category}
**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Problem domain:** {self.context.problem_summary}
**Industry terms:** {', '.join(self.context.industry_terms[:5])}

Search for:
- "Gartner {self.context.solution_category} 2025 2026"
- "Forrester {self.context.solution_category} 2025 2026"
- "{self.context.solution_category} analyst report 2025 2026"
- "{problem_kw} industry report"
- "{self.context.industry_vertical} {problem_kw} conference 2025 2026"
- "{self.context.solution_category} market trends expert analysis"
- "IDC {self.context.solution_category}"
- "McKinsey {self.context.industry_vertical} {problem_kw}"

Research and report on:

1. **Analyst Coverage**: Reports from major analyst firms (Gartner, Forrester, IDC, McKinsey, BCG, Deloitte) covering this problem domain or solution category. For each: analyst firm, report title (paraphrased), date, key findings relevant to the venture, and source URL.

2. **Market Narrative**: What is the analyst consensus about this space? What do analysts broadly agree on? Where do they disagree? How do they classify the market maturity?

3. **Priority Rankings**: Does this problem or solution category appear in any analyst priority lists (e.g., Gartner Top 10 Strategic Technology Trends, Forrester top priorities)? If so, what year and what ranking/inclusion?

4. **Magic Quadrant / Wave / Market Guide**: Does a Gartner Magic Quadrant, Forrester Wave, or similar competitive analysis exist for this category? If so, when was it last published and who are the leaders?

5. **Conference Coverage**: Is this topic featured at major industry conferences? Which conferences, how central is the topic, and what are the key themes?

6. **Expert Commentary**: Notable thought leadership, expert blogs, or influential commentary on this space. What are recognized experts saying?

7. **Coverage Assessment**: Overall volume of coverage (heavy/moderate/light/absent), trend direction (increasing/stable/decreasing), and what the coverage level implies about market maturity.

Focus on analyst coverage from the last 24 months. Note if coverage is concentrated in certain geographies or sub-segments. If no analyst coverage is found for the specific sub-category, note the closest available coverage and what the absence of coverage might indicate."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
        }
