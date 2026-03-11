"""
EC-12: Budget & Procurement Context

Deep research (hybrid) category for enterprise IT budget data,
procurement processes, compliance requirements, and deal mechanics.
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from config.settings import GPTR_CONFIG_DIR


class EC12BudgetProcurement(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-12"

    @property
    def category_name(self) -> str:
        return "Budget & Procurement Context"

    def get_report_type(self) -> str:
        return "deep"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "hybrid_mission.json"

    def _use_hybrid(self) -> bool:
        return True

    def build_query(self) -> str:
        geo = self.context.geography

        # Government procurement block
        gov_block = ""
        if self.context.target_buyer_type.lower() in ["government", "public sector", "municipal", "federal"]:
            gov_block = f"""
**Government Procurement Requirements:**
- Search "{geo} government procurement requirements technology"
- Search "{geo} public tender process requirements"
- Search "FedRAMP GovCloud requirements" (if applicable)
"""

        # SaaS procurement block
        saas_block = ""
        if "saas" in self.context.business_model_type.lower():
            saas_block = f"""
**SaaS Procurement Requirements:**
- Search "enterprise SaaS procurement requirements {self.context.industry_vertical}"
- Search "SOC 2 ISO 27001 requirement {self.context.industry_vertical}"
"""

        # Data security block
        data_block = ""
        if any(t.lower() in ["saas", "cloud", "data", "ai", "ml", "iot"] for t in self.context.technology_stack):
            data_block = f"""
**Data Security Requirements:**
- Search "data security requirements {self.context.industry_vertical} {geo}"
"""

        query = f"""Research budget, procurement, and buying process context for the following:

**Solution category:** {self.context.solution_category}
**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Target buyer type:** {self.context.target_buyer_type}
**Business model:** {self.context.business_model_type}
**Geography:** {geo}

Search for: "{self.context.industry_vertical} IT technology budget 2025 2026", "{self.context.industry_vertical} technology spending forecast", "{self.context.solution_category} typical deal size pricing", "{self.context.target_buyer_type} procurement process timeline".

Also conduct a deep synthesis: "What does the typical procurement process look like for {self.context.solution_category} in {self.context.industry_vertical}? Include: approval steps, required certifications, typical timelines, common deal-killers, and budget ownership."

Research and report on:

1. **Budget Data**: Enterprise IT/technology budget data for {self.context.industry_vertical}. Average IT spend as % of revenue, technology budget trends, and budget growth forecasts. Source: Gartner, Flexera, Deloitte surveys.

2. **Budget Ownership**: Which department or function typically owns the budget for {self.context.solution_category}? Is this OpEx or CapEx? What evidence supports this determination?

3. **Procurement Process**: Typical procurement steps from first meeting to signed contract. How many stakeholders are involved? What approvals are required? What is the typical timeline?

4. **Required Certifications**: Security and compliance certifications needed to sell to {self.context.target_buyer_type} in {self.context.industry_vertical}. SOC 2, ISO 27001, FedRAMP, industry-specific certifications. How long does achieving each take?

5. **Common Deal-Killers**: What typically causes deals to stall or fail in this procurement environment? Technical requirements, legal/compliance hurdles, integration requirements, or pricing model mismatches?

6. **Implementation Benchmarks**: Typical time from contract to first use (time-to-live) and time from first use to measurable ROI (time-to-value) for similar solutions.

7. **Variability Drivers**: What makes procurement faster or slower? Organization size, existing infrastructure, regulatory environment?
{gov_block}{saas_block}{data_block}
Cite specific sources for all budget data and procurement benchmarks. Note where data is based on {self.context.industry_vertical} specifically vs. broader enterprise averages."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
        }
