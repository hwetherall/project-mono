"""
EC-10: Voice of Market (Pain Language & Community)

Deep research category for practitioner language, community discussions,
pain patterns, and vocabulary alignment analysis.
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from config.settings import GPTR_CONFIG_DIR


class EC10VoiceOfMarket(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-10"

    @property
    def category_name(self) -> str:
        return "Voice of Market (Pain Language & Community)"

    def get_report_type(self) -> str:
        return "deep"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "deep_landscape.json"

    def build_query(self) -> str:
        problem_kw = ", ".join(self.context.problem_keywords[:5])
        roles = ", ".join(self.context.customer_roles[:3]) if self.context.customer_roles else "practitioners"

        # Technical community block
        tech_block = ""
        if any(t.lower() in ["software", "api", "cloud", "saas", "devops", "iot"] for t in self.context.technology_stack):
            tech_block = f"""
- Search "Stack Overflow {problem_kw}" and "{problem_kw} GitHub issues discussions"
- Search "Hacker News {problem_kw}"
"""

        # Non-English gap note
        language_note = ""
        if self.context.geography.lower() not in ["united states", "us", "usa", "uk", "united kingdom", "canada", "australia"]:
            language_note = f"\n**Note:** Community language analysis may be limited to English-language sources. Pain language in {self.context.geography}'s native language forums may differ significantly."

        query = f"""Research how practitioners and target customers actually talk about the following problem in their own words:

**Problem:** {self.context.problem_summary}
**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Target customer roles:** {roles}
**Venture's framing of the problem:** {self.context.solution_summary}
**Geography:** {self.context.geography}

Search across community platforms for authentic practitioner language:
- Search "{problem_kw} Reddit {self.context.industry_vertical}"
- Search "{problem_kw} forum discussion"
- Search "{self.context.industry_vertical} {problem_kw} frustration complaints"
- Search "{roles} challenges {problem_kw}"
- Search "{problem_kw} LinkedIn discussion"
{tech_block}
Research and report on:

1. **Pain Language Patterns**: What recurring phrases, complaints, and descriptions do practitioners use when discussing this problem? Group by theme (e.g., "cost frustration," "reliability complaints," "workflow friction"). For each theme, include: frequency signal, representative phrases (paraphrased), sentiment intensity (high/moderate/mild), and source context.

2. **Vocabulary Analysis**: Compare how the venture describes the problem ("{self.context.solution_category}") vs. how practitioners describe it. Is there strong alignment, moderate overlap, or a significant gap between venture framing and market language?

3. **Community Activity**: How much discussion is there about this problem? Is discussion volume high, moderate, low, or absent? Is it growing, stable, or declining? Which communities are most active?

4. **Escalation Signals**: Is the problem discussed at leadership/executive level, or only at practitioner level? Evidence of the problem escalating to budget-holder attention.

5. **Pain Intensity Assessment**: Based on language patterns and discussion volume, how intense is the experienced pain? Are people mildly annoyed or genuinely suffering?
{language_note}

Focus on authentic practitioner voices — forum posts, community discussions, social media threads, review comments — not marketing content or press releases. Paraphrase rather than quote directly. Note the recency of discussions."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
        }
