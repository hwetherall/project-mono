"""
MR-01b: Market Sizing & Methodology
Covers master table inputs 8-18, 101.
Split from MR-01 to avoid timeout on deep research.
"""
from market_research.base import MRBaseCategory


class MR01bMarketSizing(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-01b"

    @property
    def category_name(self) -> str:
        return "Market Sizing & Methodology"

    @property
    def extraction_schema(self) -> dict | None:
        return {
            "tam_estimate": "Total addressable market size with currency and year",
            "sam_estimate": "Serviceable addressable market size if mentioned",
            "growth_rate": "Market CAGR or annual growth rate",
            "market_terms_extracted": "List of market category labels found in report",
            "key_sources": "List of analyst firms or data sources cited for sizing",
            "methodology": "Bottom-up vs top-down methodology used",
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

        return f"""Conduct comprehensive market sizing and methodology research for this market:

{ctx}
{verification_block}

Search for: "{solution} market size {geo}", "{industry} {sub} TAM", "{solution} market growth forecast", "{solution} market methodology", "{solution} CAGR", "{solution} market revenue".

Research and report on ALL of the following. For every data point, cite the specific source and publication date.

**A. Market Sizing Data**
1. **Named TAM estimates**: Individual market-size figures from named third-party sources with year, scope, and source attached. Report ALL estimates found, not just one.
2. **TAM range**: Synthesize the low, midpoint, and high estimates from all sources found. Make uncertainty explicit.
3. **Historical market size series**: At least 3-5 years of historical data. Note data gaps.
4. **Projected market size series**: Forward estimates with forecast horizon. Include multiple projections if available.
5. **Historical CAGR by geography or segment**: Where available, break out growth rates by region or subsegment.
6. **Projected CAGR by geography or segment**: Forecast growth rates by region or subsegment. Identify where future demand concentrates.

**B. Sizing Methodology & Confidence**
7. **Sizing methodology per source**: Whether each source uses top-down, bottom-up, value-based, shipment-based, or spend-based methods. Compare rigor across sources.
8. **Bottom-up demand-unit proxies**: Public counts for buyers, users, seats, facilities, transactions, or assets that can anchor bottom-up sizing. Search for government censuses, industry directories, public databases.
9. **Unit price / spend / value-per-unit proxies**: Benchmarks for spend per account, per seat, per transaction that convert volume into dollar market size.
10. **Hard-data anchor points**: Official data from SEC filings, government statistics, regulator databases, or standards bodies that serve as high-confidence anchors.
11. **Source credibility metadata**: For each source, note recency, independence, transparency, sample quality, potential sponsor bias, and methodological caveats.
12. **Pricing trend / ASP trajectory**: Average selling price trends over time — is pricing rising, falling, or compressing by segment?

Prioritize data from the last 24 months. If only older data exists, note this explicitly. Distinguish between primary research, analyst estimates, and government statistics. Flag significant variance between sources."""

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
            "market_terms_extracted": self._extract_sizing_terms(raw_report),
        }

    def _extract_sizing_terms(self, report: str) -> list[str]:
        """Extract market sizing terms (TAM values, CAGRs) for downstream context."""
        import re
        terms = []
        # Look for TAM/market size values
        tam_patterns = re.findall(
            r'(?:TAM|market size|market value|market revenue)[^\n]*?(\$[\d,\.]+\s*(?:billion|million|B|M|trillion|T))',
            report, re.IGNORECASE
        )
        terms.extend(tam_patterns[:5])
        # Look for CAGR values
        cagr_patterns = re.findall(
            r'CAGR[^\n]*?([\d\.]+\s*%)', report, re.IGNORECASE
        )
        terms.extend([f"CAGR {c}" for c in cagr_patterns[:5]])
        return terms
