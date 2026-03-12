"""
MR-05: Value Chain & Whitespace
Covers master table inputs 51-59, 116-121, 123.
"""
from market_research.base import MRBaseCategory


class MR05ValueChain(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-05"

    @property
    def category_name(self) -> str:
        return "Value Chain & Whitespace"

    def build_query(self) -> str:
        ctx = self._market_context_block()
        geo = self.context.geography
        solution = self.context.solution_category
        industry = self.context.industry_vertical

        return f"""Research the value chain structure, whitespace, and economics for:

{ctx}

Search for: "{industry} value chain", "{industry} supply chain map", "{industry} profit pool", "gatekeepers in {industry}", "underserved workflows in {industry}", "{industry} gross margin benchmarks", "supplier power in {industry}", "{industry} ecosystem participants".

Research and report on ALL of the following. Cite specific sources for every data point.

**A. Value Chain Structure**
1. **Stage-by-stage value chain map**: The main stages from upstream inputs through fulfillment, delivery, and ongoing value capture. Draw the full chain for this market.
2. **Actor roles at each stage**: The participant types present at each stage and their responsibilities.
3. **Economic value flow and profit-pool distribution**: Where revenue, margin, or bargaining power concentrates across the chain. Which stages capture the most value?
4. **Physical or operational flow structure**: How products, services, data, or work actually move through the chain in practice.
5. **Control points and gatekeepers**: Where one actor controls access, standards, distribution, or customer relationships. These are the power nodes in the chain.

**B. Whitespace Analysis**
6. **Underserved stages or workflows**: Stages where current offerings appear weak, fragmented, or incomplete. Support claims with evidence from review sites, analyst gap analyses, or trade commentary.
7. **Workflow friction points**: Observable inefficiencies, delays, manual workarounds, or coordination failures in existing workflows.
8. **Current solution coverage by stage**: Which parts of the chain are already well served and which remain thinly covered.
9. **Profit-pool vs solution-coverage mismatch**: Whether high-value stages are underserved relative to their economics. This is where real whitespace lives.

**C. Market Economics**
10. **Key suppliers**: Dominant suppliers of critical components, data, inputs, or enabling services upstream.
11. **Distributor / reseller margin norms**: Typical markups or commission structures for channel partners.
12. **Gross margin benchmarks**: Typical gross margins for comparable companies in this category.
13. **Operating margin benchmarks**: Typical operating margin range for mature or scaled companies.
14. **Cost structure benchmarks**: Typical mix of R&D, sales & marketing, services, G&A, and infrastructure costs.
15. **Supplier power indicators**: Evidence that upstream suppliers have leverage via concentration, scarcity, or standards control.
16. **Intermediary roles**: How brokers, marketplaces, and aggregators create, capture, or tax value.

Structure the report as a clear value chain narrative. For economic data, always cite the source, year, and methodology."""
