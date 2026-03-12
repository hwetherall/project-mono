"""
MR-10: Barriers, Saturation & Ecosystem Power
Covers master table inputs 91-100, 130.
"""
from market_research.base import MRBaseCategory


class MR10BarriersEcosystem(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-10"

    @property
    def category_name(self) -> str:
        return "Barriers, Saturation & Ecosystem Power"

    def build_query(self) -> str:
        ctx = self._market_context_block()
        solution = self.context.solution_category
        industry = self.context.industry_vertical

        return f"""Research entry barriers, saturation, and ecosystem power for:

{ctx}

Search for: "barriers to entry {industry}", "vendor saturation {industry}", "switching costs {industry}", "network effects {industry}", "ecosystem dependencies {industry}", "gatekeeper power {industry}", "talent shortage {industry}".

Research and report on ALL of the following. Cite specific sources for every data point.

1. **Capital barriers to entry**: Upfront investment, minimum viable scale, or capital intensity required to compete.
2. **Regulatory barriers to entry**: Licensing, approvals, certification, or legal hurdles entrants must clear.
3. **Technology, IP, data, or network-effect barriers**: Technical assets, data scale, IP base, or network thresholds that favor incumbents.
4. **Distribution and switching-cost barriers**: Channel lock-in, partner control, customer retraining, integration burden, or contract stickiness.
5. **Brand, reputation, or trust barriers**: Evidence that buyers require known brands, references, certifications, or reputational proof.
6. **Solution density and vendor saturation by segment**: How many vendors meaningfully serve each segment, and whether density varies across the market.
7. **Feature coverage versus buyer-need gaps**: Where current solutions over-serve, under-serve, or miss important needs.
8. **Ecosystem dependency map**: The platforms, partners, integrators, data providers, or standards bodies the market depends on.
9. **Gatekeeper power indicators**: Which ecosystem players can materially enable, delay, or block market entry and adoption.
10. **User-side and buyer-side adoption barriers by stage**: Friction across awareness, evaluation, purchase, onboarding, and expansion.
11. **Talent scarcity / skill bottlenecks**: Whether scarce talent materially slows supply, implementation, or customer adoption.

End with a practical market-entry difficulty assessment: low / moderate / high / extreme, with the top reasons why."""
