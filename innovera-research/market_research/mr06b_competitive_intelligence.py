"""
MR-06b: Competitive Intelligence
Covers master table inputs 103-107.
Split from MR-06 to avoid timeout on deep research.
"""
from market_research.base import MRBaseCategory


class MR06bCompetitiveIntelligence(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-06b"

    @property
    def category_name(self) -> str:
        return "Competitive Intelligence"

    def build_query(self) -> str:
        ctx = self._market_context_block()
        solution = self.context.solution_category
        industry = self.context.industry_vertical

        competitor_seed = ""
        if self.context.named_competitors:
            names = ", ".join(self.context.named_competitors)
            competitor_seed = f"\n**Known competitors to investigate:** {names}"

        return f"""Conduct a comprehensive competitive intelligence analysis for major players in this market:

{ctx}
{competitor_seed}

Search for: "G2 reviews {solution}", "Capterra {solution}", "{industry} competitor partnerships", "{industry} acquisitions", "{solution} competitor reviews", "{industry} litigation patents".

Research and report on ALL of the following. Cite specific sources for every data point.

**A. Competitive Intelligence**
1. **Review-site sentiment and recurring complaints**: Common strengths, weaknesses, complaints, and delight points visible on G2, Capterra, app stores, Reddit, and forums. Search for actual reviews and synthesize patterns.
2. **Competitor geographic footprint**: Where major competitors are strongest or weakest by region. Note any geographic gaps.
3. **Competitor partnerships and ecosystem integrations**: Key technology, channel, OEM, reseller, data, and services partners attached to major competitors.
4. **Litigation, IP dispute, or antitrust history**: Material lawsuits, IP disputes, or regulatory enforcement involving major vendors.
5. **Competitor acquisition history**: Acquisitions made by leading vendors — what capabilities they bought and why. Include dates and deal sizes where public.

For each competitor, use a consistent format with the company name in bold. Be specific — name companies, cite sources, provide concrete details."""
