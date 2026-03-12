"""
MR-09: Regulation & Platform Shifts
Covers master table inputs 85-90, 125-129.
"""
from market_research.base import MRBaseCategory


class MR09RegulationPlatform(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-09"

    @property
    def category_name(self) -> str:
        return "Regulation & Platform Shifts"

    def build_query(self) -> str:
        ctx = self._market_context_block()
        industry = self.context.industry_vertical
        geo = self.context.geography

        return f"""Research the regulatory and platform-policy landscape for:

{ctx}

Search for: "key regulations for {industry}", "{industry} compliance requirements {geo}", "upcoming regulations {industry}", "platform policy changes {industry}", "regulatory bodies for {industry}", "compliance cost {industry}".

Research and report on ALL of the following. Cite sources, enacting bodies, dates, and jurisdictions.

**A. Regulatory Landscape**
1. **Named regulatory regimes affecting the market**: The specific laws, standards, or regulatory domains that materially shape the category.
2. **Key regulatory agencies and oversight bodies**: The regulators, standards bodies, or supervisory agencies that formally govern the category.
3. **Regulatory shifts with enacting body and effective date**: Specific policy changes, who enacted them, when they took effect, and where they apply.
4. **Demand-side effects of policy shifts**: Which shifts create, accelerate, suppress, or redirect customer demand.
5. **Access-side effects of policy shifts**: Which shifts open or close market access, raise compliance burden, or alter reachability.
6. **Compliance cost benchmarks**: Estimated direct and indirect cost to comply with major regulations or certification requirements.
7. **Data privacy and cybersecurity requirements**: Specific data handling, residency, security, and privacy rules shaping category access and product design.

**B. Platform Dynamics**
8. **Named platform policies or rule changes affecting the market**: Public platform-level rules that shape access, economics, integration, or distribution.
9. **Platform changes with owner and effective date**: Specific platform rule or program changes, who controls them, and when they changed.

**C. Broader Policy Exposure**
10. **Environmental, trade, and labor rule exposure**: Non-core but potentially decisive policy risks.
11. **Subsidies, grants, and public incentives**: Government financial support, tax credits, or grants that create or accelerate demand.

End with a short policy-shift ledger that separates demand creation, access friction, and neutral/background regulation."""
