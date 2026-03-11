"""
EC-13: Proxy Market Trajectories

Deep research category for analogous market adoption histories,
inflection points, and comparable technology adoption curves.
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from config.settings import GPTR_CONFIG_DIR


class EC13ProxyMarkets(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-13"

    @property
    def category_name(self) -> str:
        return "Proxy Market Trajectories"

    def get_report_type(self) -> str:
        return "deep"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "deep_landscape.json"

    def build_query(self) -> str:
        tech_stack = ", ".join(self.context.technology_stack[:3]) if self.context.technology_stack else self.context.solution_category
        problem_kw = ", ".join(self.context.problem_keywords[:3])

        # Venture-stated analogies
        analogy_block = ""
        if self.context.analogies_mentioned:
            analogy_queries = []
            for analogy in self.context.analogies_mentioned:
                analogy_queries.append(f'- Search "{analogy} market adoption history trajectory"')
                analogy_queries.append(f'- Search "{analogy} market inflection point"')
                analogy_queries.append(f'- Search "{analogy} early market growth"')
            analogy_block = "\n**Research Venture-Stated Analogies:**\n" + "\n".join(analogy_queries)

        query = f"""Identify and research analogous markets and comparable adoption trajectories for the following venture:

**Solution category:** {self.context.solution_category}
**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Technology stack:** {tech_stack}
**Problem:** {self.context.problem_summary}
**Geography:** {self.context.geography}
**Venture stage:** {self.context.stage}
{analogy_block}

Search for: "{self.context.solution_category} comparable markets adoption", "{problem_kw} solved in other industries", "{tech_stack} adoption curve similar vertical".

Conduct a deep research mission: "Identify 2-3 analogous markets or comparable adoption trajectories for {self.context.solution_category} in {self.context.industry_vertical}. For each analogue: describe the problem similarity, adoption timeline, inflection points, and what lessons apply to the target market."

Research and report on:

1. **Analogous Markets**: Identify 2-4 markets or product categories that solved a structurally similar problem in a different vertical or geography. For each analogue:
   - Name and description of the analogous market
   - Why this is a valid comparison (similarity basis)
   - Adoption timeline: early adoption phase (period, characteristics), inflection point (when and what triggered acceleration), mainstream adoption (period, scale achieved)
   - Key lessons for the target venture
   - Where the analogy breaks down (limitations)
   - Sources

2. **Technology Adoption Curves**: How have similar technologies ({tech_stack}) been adopted in comparable industries? What was the adoption pattern and what drove acceleration?

3. **Trajectory Synthesis**:
   - Where does the target market sit on the adoption curve based on proxy evidence?
   - Confidence level (high/moderate/low)
   - Key caveat: the most important way the target market differs from the analogues

4. **Timing Implications**: What do the proxy trajectories suggest about timing for the venture? Is this market pre-inflection, at inflection, or post-inflection?

Prioritize analogies that share structural similarities (problem type, buyer type, technology dependency) over surface-level similarities. Note that proxy market analysis is inherently approximate — structural differences should be explicitly stated."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
        }
