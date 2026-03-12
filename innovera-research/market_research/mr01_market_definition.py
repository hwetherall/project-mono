"""
MR-01: Market Definition & Sizing
Covers master table inputs 1-18, 101.
"""
from market_research.base import MRBaseCategory


class MR01MarketDefinition(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-01"

    @property
    def category_name(self) -> str:
        return "Market Definition & Sizing"

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

        return f"""Conduct comprehensive market definition and sizing research for this market:

{ctx}
{verification_block}

Search for: "{solution} market size {geo}", "{solution} market definition", "{industry} {sub} TAM", "{solution} NAICS code", "{solution} market growth forecast", "{solution} market methodology".

Research and report on ALL of the following. For every data point, cite the specific source and publication date.

**A. Market Boundary Definition**
1. **Canonical market definition**: The main category name used by analysts, regulators, and trade bodies. Search for NAICS codes, Gartner/IDC definitions, trade association classifications.
2. **Alternate labels and synonyms**: Adjacent labels, legacy names, and nearby category terms. Test whether different labels imply different market boundaries.
3. **Product-type inclusion rules**: Which product forms or solution types third-party sources explicitly include in their market totals. Reference methodology notes from major reports.
4. **Product-type exclusion rules**: Which adjacent offerings sources explicitly exclude, and why. Document the edges of the market.
5. **Geographic scope conventions**: How sources define region-level scope (global, North America, EU, APAC). Note any differences in regional definitions across sources.
6. **Customer-segment boundaries**: How sources split the market by enterprise size, industry vertical, buyer type, or operating model.
7. **Use-case boundaries**: How sources separate the market by application, workflow, or job-to-be-done.

**B. Market Sizing Data**
8. **Named TAM estimates**: Individual market-size figures from named third-party sources with year, scope, and source attached. Report ALL estimates found, not just one.
9. **TAM range**: Synthesize the low, midpoint, and high estimates from all sources found. Make uncertainty explicit.
10. **Historical market size series**: At least 3-5 years of historical data. Note data gaps.
11. **Projected market size series**: Forward estimates with forecast horizon. Include multiple projections if available.
12. **Historical CAGR by geography or segment**: Where available, break out growth rates by region or subsegment.
13. **Projected CAGR by geography or segment**: Forecast growth rates by region or subsegment. Identify where future demand concentrates.

**C. Sizing Methodology & Confidence**
14. **Sizing methodology per source**: Whether each source uses top-down, bottom-up, value-based, shipment-based, or spend-based methods. Compare rigor across sources.
15. **Bottom-up demand-unit proxies**: Public counts for buyers, users, seats, facilities, transactions, or assets that can anchor bottom-up sizing. Search for government censuses, industry directories, public databases.
16. **Unit price / spend / value-per-unit proxies**: Benchmarks for spend per account, per seat, per transaction that convert volume into dollar market size.
17. **Hard-data anchor points**: Official data from SEC filings, government statistics, regulator databases, or standards bodies that serve as high-confidence anchors.
18. **Source credibility metadata**: For each source, note recency, independence, transparency, sample quality, potential sponsor bias, and methodological caveats.
19. **Pricing trend / ASP trajectory**: Average selling price trends over time — is pricing rising, falling, or compressing by segment?

Prioritize data from the last 24 months. If only older data exists, note this explicitly. Distinguish between primary research, analyst estimates, and government statistics. Flag significant variance between sources."""
