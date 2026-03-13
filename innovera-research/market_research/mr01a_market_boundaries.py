"""
MR-01a: Market Definition & Boundaries
Covers master table inputs 1-7 (market boundary definition).
Split from MR-01 to avoid timeout on deep research.
"""
from market_research.base import MRBaseCategory


class MR01aMarketBoundaries(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-01a"

    @property
    def category_name(self) -> str:
        return "Market Definition & Boundaries"

    @property
    def extraction_schema(self) -> dict | None:
        return {
            "market_terms_extracted": "List of canonical market labels and search terms discovered",
            "market_boundaries": "Description of what is included and excluded from this market",
            "adjacent_markets": "List of adjacent or overlapping markets",
            "market_maturity": "Stage of market development (nascent, emerging, growing, mature, declining)",
        }

    def build_query(self) -> str:
        ctx = self._market_context_block()
        geo = self.context.geography
        solution = self.context.solution_category
        industry = self.context.industry_vertical
        sub = self.context.sub_vertical or ""

        verification_block = ""
        if self.context.market_size_claims:
            claims = "\n".join(f"  - {c}" for c in self.context.market_size_claims)
            verification_block = f"""
**Venture Claims to Verify:**
{claims}
"""

        return f"""Conduct comprehensive market definition and boundary research for this market:

{ctx}
{verification_block}

Search for: "{solution} market definition", "{industry} {sub} market scope", "{solution} NAICS code", "{solution} market classification", "{solution} market taxonomy".

Research and report on ALL of the following. For every data point, cite the specific source and publication date.

**A. Market Boundary Definition**
1. **Canonical market definition**: The main category name used by analysts, regulators, and trade bodies. Search for NAICS codes, Gartner/IDC definitions, trade association classifications.
2. **Alternate labels and synonyms**: Adjacent labels, legacy names, and nearby category terms. Test whether different labels imply different market boundaries.
3. **Product-type inclusion rules**: Which product forms or solution types third-party sources explicitly include in their market totals. Reference methodology notes from major reports.
4. **Product-type exclusion rules**: Which adjacent offerings sources explicitly exclude, and why. Document the edges of the market.
5. **Geographic scope conventions**: How sources define region-level scope (global, North America, EU, APAC). Note any differences in regional definitions across sources.
6. **Customer-segment boundaries**: How sources split the market by enterprise size, industry vertical, buyer type, or operating model.
7. **Use-case boundaries**: How sources separate the market by application, workflow, or job-to-be-done.

Prioritize data from the last 24 months. If only older data exists, note this explicitly. Distinguish between primary research, analyst estimates, and government statistics."""

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
            "market_terms_extracted": self._extract_market_terms(raw_report),
        }

    def _extract_market_terms(self, report: str) -> list[str]:
        """Extract market definition terms from the report for downstream injection."""
        import re
        terms = []
        # Look for NAICS codes
        naics = re.findall(r'NAICS\s*(?:code)?\s*(\d{4,6})', report, re.IGNORECASE)
        terms.extend([f"NAICS {n}" for n in naics])
        # Look for bold defined terms
        bold_terms = re.findall(r'\*\*([A-Z][A-Za-z0-9\s&\.\-/]+?)\*\*', report)
        skip = {"canonical market definition", "alternate labels", "product-type",
                "geographic scope", "customer-segment", "use-case", "search for",
                "research and report", "venture claims", "market boundary"}
        for t in bold_terms:
            t_clean = t.strip()
            if (3 < len(t_clean) < 60
                    and t_clean.lower() not in skip
                    and not any(s in t_clean.lower() for s in skip)
                    and t_clean not in terms):
                terms.append(t_clean)
        return terms[:20]
