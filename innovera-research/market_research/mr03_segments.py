"""
MR-03: Segments & Concentration
Covers master table inputs 29-40, 122.
"""
from market_research.base import MRBaseCategory


class MR03Segments(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-03"

    @property
    def category_name(self) -> str:
        return "Segments & Concentration"

    def build_query(self) -> str:
        ctx = self._market_context_block()
        geo = self.context.geography
        solution = self.context.solution_category
        industry = self.context.industry_vertical

        return f"""Research market segmentation, concentration, and buyer dynamics for:

{ctx}

Search for: "{industry} market segmentation", "{solution} customer segments", "{industry} market share concentration", "{industry} buyer segments", "{solution} market by company size", "{industry} competitive intensity by segment", "{industry} M&A consolidation".

Research and report on ALL of the following. Cite specific sources for every data point.

**A. Segment Taxonomy**
1. **Segment taxonomy**: The usable segmentation scheme supported by public data — by industry vertical, company size, region, and use case. Document which segmentation frameworks public sources actually support with data.
2. **Addressable revenue by subsegment**: Public estimates of market spend or size for each major subsegment. This is needed to score segment size and focus the beachhead.
3. **Growth rate by subsegment**: Public growth rates for relevant verticals, buyer cohorts, regions, or use cases. Identify which pockets are growing fastest.
4. **Demand concentration by top segments**: Which segments account for the largest share of overall demand? Quantify the top-3 to top-5 segments by spend share.
5. **Primary customer segment descriptors**: Real-world attributes that make the leading segment identifiable and list-buildable — firmographic criteria, operational characteristics, buying signals.

**B. Buyer & User Roles**
6. **Buyer role titles by segment**: Common buyer titles or functions in each important segment. Who signs the check?
7. **User role titles by segment**: End-user or operator roles involved in the workflow. Who uses the product day-to-day?

**C. Competitive Intensity & Structure**
8. **Competitive intensity by subsegment**: How crowded each subsegment is and how strong incumbents appear. Search review sites, market maps, analyst landscapes.
9. **Fragmentation and consolidation indicators**: Vendor counts, share dispersion, HHI proxies, roll-up patterns, M&A consolidation signals. Is the market fragmenting or consolidating?
10. **Competitive layer structure**: Evidence for distinct layers — enterprise vs SMB, premium vs mass market, platform vs specialist.

**D. Concentration Risk**
11. **Buyer concentration indicators**: Whether demand is concentrated among a small number of large buyers, or broadly distributed.
12. **Whale-versus-long-tail demand pattern**: Does category spend appear dominated by large accounts or broadly distributed across many smaller buyers?
13. **Buyer power indicators**: Evidence that buyers have leverage via concentration, procurement sophistication, or volume-based negotiating power.

Structure the report with clear sections. For each segment claim, cite the source and note whether the data is directly reported or inferred."""
