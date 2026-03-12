"""
MR-02: SAM / SOM / Reachability
Covers master table inputs 19-28.
"""
from market_research.base import MRBaseCategory


class MR02SamSom(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-02"

    @property
    def category_name(self) -> str:
        return "SAM / SOM / Reachability"

    def build_query(self) -> str:
        ctx = self._market_context_block()
        geo = self.context.geography
        solution = self.context.solution_category
        industry = self.context.industry_vertical

        return f"""Research the serviceable addressable market (SAM), serviceable obtainable market (SOM), and market reachability for:

{ctx}

Search for: "{solution} route to market", "{solution} channel partners", "{industry} licensing requirements", "{solution} adoption rate", "{industry} market penetration", "{solution} compliance requirements {geo}".

Research and report on ALL of the following. Cite specific sources for every data point.

**A. Route-to-Market & Channel Structure**
1. **Dominant route-to-market types**: The main commercial routes used in this market — direct sales, channel partners, marketplaces, OEM, resale, self-serve. Which routes dominate and why?
2. **Channel share and segment coverage**: How much of the market each route serves, and which customer segments each route reaches best. Quantify where possible.
3. **Marketplace or platform access requirements**: Public requirements for listing, integration, certification, or participation on key platforms and marketplaces in this category.

**B. Access & Compliance Gates**
4. **Jurisdiction-specific licensing or compliance requirements**: Publicly documented legal, certification, or compliance requirements that gate access to target geographies or segments in {geo}. These are the filters between theoretical demand and serviceable demand.
5. **Time and cost to satisfy access requirements**: Typical duration, fees, audits, or approval effort needed to meet these access requirements.
6. **Reachable ICP counts by subsegment**: Public counts of organizations or buyers matching the relevant firmographic and use-case profile. Search industry directories, public databases, trade associations.

**C. Adoption & Obtainability**
7. **Analogous adoption-ramp benchmarks**: How quickly similar products or categories reached meaningful adoption. Include time-to-X-customers benchmarks from comparable markets.
8. **Typical switching timelines**: How long it takes buyers to replace incumbent tools, manual processes, or vendors in this category. Include implementation timelines and procurement cycles.
9. **Public penetration and attach-rate benchmarks**: Comparable rates for adoption, seat penetration, attach, or conversion in adjacent categories. Search for "[category] market penetration rate" and "percentage of companies using [technology]".
10. **Evidence-backed versus speculative markers**: Which assumptions in public sizing are sourced versus inferred. Help separate robust inputs from guesswork.

For each finding, note whether it applies globally or is specific to {geo}. Distinguish between hard data and analyst inference."""
