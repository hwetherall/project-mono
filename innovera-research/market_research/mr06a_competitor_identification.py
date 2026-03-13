"""
MR-06a: Competitor Identification
Covers master table inputs 60-64.
Split from MR-06 to avoid timeout on deep research.
"""
import re
from market_research.base import MRBaseCategory
from evidence_categories.base import CategoryResult


class MR06aCompetitorIdentification(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-06a"

    @property
    def category_name(self) -> str:
        return "Competitor Identification"

    def build_query(self) -> str:
        ctx = self._market_context_block()
        geo = self.context.geography
        solution = self.context.solution_category
        industry = self.context.industry_vertical

        competitor_seed = ""
        if self.context.named_competitors:
            names = ", ".join(self.context.named_competitors)
            competitor_seed = f"\n**Known competitors to start with (search for more):** {names}"

        return f"""Conduct a comprehensive competitor identification and market share analysis for:

{ctx}
{competitor_seed}

Search for: "top companies in {industry}", "market leaders {industry}", "{solution} alternatives", "{solution} competitors comparison", "{solution} pricing", "{industry} market share".

Research and report on ALL of the following. Cite specific sources for every data point.

**A. Competitor Identification**
1. **Direct competitor list**: Named direct competitors currently serving this market. For each, include: what they do, who they target, positioning, pricing model (if public), funding stage, estimated revenue or scale indicators.
2. **Substitute and workaround list**: Named substitute products, adjacent vendors, manual workflows, or outsourcing options buyers use instead. These are the real competitive alternatives.
3. **Competitor revenue or market-share estimates**: Public share figures or revenue estimates for relevant competitors. Note the basis for each estimate (filings, analyst reports, traffic analysis, etc.).
4. **Public inputs supporting share estimates**: Visible assumptions behind share estimates — customer counts, pricing, traffic, segment exposure.
5. **Distribution route mix and channel power**: The relative importance of direct, partner, marketplace, OEM, or distributor-led routes, and who holds leverage in each.

For each competitor, use a consistent format with the company name in bold. Be specific — name companies, cite sources, provide concrete details. If pricing is not public, say so."""

    @property
    def extraction_schema(self) -> dict | None:
        return {
            "competitors": "List of competitor objects with name, type (direct/substitute/adjacent), positioning, and pricing model",
            "market_share_estimates": "List of competitors with estimated market share percentages or revenue",
            "distribution_channels": "Key distribution routes and their relative importance",
            "competitive_dynamics": "Summary of competitive intensity and key dynamics",
        }

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
            "competitor_names_extracted": self._extract_competitor_names(raw_report),
        }

    def _extract_competitor_names(self, report: str) -> list[str]:
        """Extract competitor names from bold text patterns in the report."""
        names = []
        bold_pattern = re.findall(r'\*\*([A-Z][A-Za-z0-9\s&\.\-]+?)\*\*', report)
        skip_phrases = {
            "direct competitor", "substitute", "workaround", "competitor",
            "distribution", "channel", "review", "partnership", "litigation",
            "acquisition", "search for", "research and report", "note",
            "important", "summary", "conclusion", "sources", "known competitors",
            "industry", "geography", "solution", "business model", "target buyer",
            "problem context", "market terms",
        }
        for name in bold_pattern:
            name_clean = name.strip()
            if (
                len(name_clean) > 2
                and len(name_clean) < 50
                and name_clean.lower() not in skip_phrases
                and not any(skip in name_clean.lower() for skip in skip_phrases)
                and name_clean not in names
            ):
                names.append(name_clean)
        return names

    def get_competitor_list(self, result: CategoryResult) -> list[str]:
        """Public method for Phase 2/3 to get competitor list from MR-06a results."""
        if result and result.structured_findings:
            names = result.structured_findings.get("competitor_names_extracted", [])
            return list(set(names + self.context.named_competitors))
        return self.context.named_competitors
