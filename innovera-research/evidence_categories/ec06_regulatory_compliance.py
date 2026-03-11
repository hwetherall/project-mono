"""
EC-06: Regulatory & Compliance Environment

Deep research category for regulations, standards, mandates, enforcement,
and compliance requirements affecting the problem or solution space.
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from config.settings import GPTR_CONFIG_DIR


class EC06RegulatoryCompliance(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-06"

    @property
    def category_name(self) -> str:
        return "Regulatory & Compliance Environment"

    def get_report_type(self) -> str:
        return "deep"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "deep_landscape.json"

    def build_query(self) -> str:
        geo = self.context.geography
        problem_kw = ", ".join(self.context.problem_keywords[:5])

        # Named regulations block
        reg_block = ""
        if self.context.named_regulations:
            reg_queries = []
            for reg in self.context.named_regulations:
                reg_queries.append(f'- Research "{reg} requirements timeline enforcement"')
                reg_queries.append(f'- Research "{reg} compliance cost"')
                reg_queries.append(f'- Research "{reg} penalties non-compliance"')
            reg_block = "\n**Named Regulations to Research in Detail:**\n" + "\n".join(reg_queries)

        # Government buyer block
        gov_block = ""
        if self.context.target_buyer_type.lower() in ["government", "public sector", "municipal"]:
            gov_block = f"""
**Government/Public Sector Procurement Regulations:**
- Search for "{geo} government procurement regulations {self.context.solution_category}"
- Search for "{geo} public sector technology requirements"
"""

        # Compliance-driven pain block
        compliance_block = ""
        if any("compliance" in d.lower() for d in self.context.pain_drivers):
            compliance_block = f"""
**Compliance Audit Requirements:**
- Search for "{self.context.industry_vertical} compliance audit requirements frequency"
- Search for "{self.context.industry_vertical} compliance technology mandates"
"""

        # Data privacy block
        data_block = ""
        if any(t.lower() in ["saas", "cloud", "data", "ai", "ml"] for t in self.context.technology_stack):
            data_block = f"""
**Data Privacy & Security Regulations:**
- Search for "{geo} data privacy regulations {self.context.industry_vertical}"
- Search for "data residency requirements {geo}"
"""

        query = f"""Research and map the regulatory and compliance environment for the following:

**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Geography:** {geo}
**Problem domain:** {self.context.problem_summary}
**Solution category:** {self.context.solution_category}
**Target buyer type:** {self.context.target_buyer_type}

Search for: "{self.context.industry_vertical} regulations compliance requirements", "{self.context.industry_vertical} regulatory changes 2025 2026", "{problem_kw} regulatory requirements".

Research and report on:

1. **Current Regulations**: What regulations, standards, and mandates currently affect the problem or solution space? For each, include: name, jurisdiction, key requirements, enforcement status (active/pending/lax), compliance cost if quantified, and source.

2. **Pending Regulatory Changes**: What regulations are proposed, in progress, or expected? Include expected timeline and impact on the venture's problem/solution.

3. **Enforcement Actions**: Recent fines, penalties, or enforcement actions related to non-compliance in this domain. What are the consequences of non-compliance?

4. **Compliance as Buying Friction**: What compliance requirements affect buying decisions for solutions in this category? Security certifications (SOC 2, ISO 27001), data residency, audit requirements? How long do these add to procurement timelines?

5. **Regulatory Urgency Signal**: Is regulation creating urgency to act (mandates with deadlines), or creating friction that slows adoption (complex approval requirements)?
{reg_block}
{gov_block}{compliance_block}{data_block}
For each regulation or standard, cite the specific regulatory body, publication, and date. Distinguish between binding regulations, voluntary standards, and industry best practices.

Focus primarily on {geo} but note any relevant international standards or regulations from other jurisdictions that influence this market."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
        }
