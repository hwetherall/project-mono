"""
MR-08: Adoption & Expansion Dynamics
Covers master table inputs 79-84.
"""
from market_research.base import MRBaseCategory


class MR08AdoptionDynamics(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-08"

    @property
    def category_name(self) -> str:
        return "Adoption & Expansion Dynamics"

    def build_query(self) -> str:
        ctx = self._market_context_block()
        solution = self.context.solution_category
        industry = self.context.industry_vertical

        return f"""Research adoption maturity and expansion dynamics for:

{ctx}

Search for: "adoption stage of {solution}", "market maturity indicators {industry}", "land and expand {solution}", "adoption path {industry} software", "buyer familiarity {solution}", "expansion blockers {industry}".

Research and report on ALL of the following. Cite specific sources for every data point.

1. **Adoption-stage markers for analogous solutions**: Observable signs that the market is early, mainstream, or late in adopting similar solutions.
2. **Segment-by-segment adoption maturity differences**: Whether adoption stage varies materially by geography, company size, vertical, or buyer type.
3. **Adoption friction versus familiarity indicators**: Evidence showing whether buyers already understand the category or still require education, trust-building, and process change.
4. **Typical adoption path patterns**: Whether comparable solutions spread via land-and-expand, team-level bottoms-up adoption, or centralized top-down purchase.
5. **Buying-behavior compatibility with expansion**: Whether the market's buying norms support expansion after initial entry or force one-shot decisions.
6. **Path dependencies that block expansion**: Integrations, approvals, architecture choices, procurement resets, or other dependencies that can stall expansion.

Conclude with an overall maturity assessment for the market and a short explanation of whether expansion-led go-to-market motions fit this market well."""
