"""
EC-08: Urgency Drivers & Forcing Functions

Deep research (hybrid) category for external events, deadlines,
and pressures creating near-term decision urgency.
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from config.settings import GPTR_CONFIG_DIR


class EC08UrgencyForcing(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-08"

    @property
    def category_name(self) -> str:
        return "Urgency Drivers & Forcing Functions"

    def get_report_type(self) -> str:
        return "deep"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "hybrid_mission.json"

    def _use_hybrid(self) -> bool:
        return True

    def build_query(self) -> str:
        problem_kw = ", ".join(self.context.problem_keywords[:5])
        geo = self.context.geography

        # Verify venture-stated urgency signals
        urgency_verify_block = ""
        if self.context.urgency_signals:
            verify_queries = [f'- Verify: "{signal} timeline details"' for signal in self.context.urgency_signals]
            urgency_verify_block = "\n**Verify Venture-Stated Urgency Signals:**\n" + "\n".join(verify_queries)

        # Regulatory deadline queries
        reg_block = ""
        if self.context.named_regulations:
            reg_queries = [f'- Search "{reg} compliance deadline enforcement date"' for reg in self.context.named_regulations[:5]]
            reg_block = "\n**Regulatory Deadlines:**\n" + "\n".join(reg_queries)

        query = f"""Research external forces creating urgency for target customers to address the following problem:

**Problem:** {self.context.problem_summary}
**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Geography:** {geo}
**Target customer:** {self.context.target_customer_summary}
**Known urgency signals from venture:** {', '.join(self.context.urgency_signals) if self.context.urgency_signals else 'None stated'}

Search for: "{self.context.industry_vertical} regulatory deadline 2025 2026", "{self.context.industry_vertical} technology migration deadline", "{self.context.industry_vertical} budget cycle fiscal year", "{problem_kw} getting worse trend".

Also conduct a deep synthesis: "What external forces are creating urgency for {self.context.industry_vertical} organizations to address {problem_kw}? Include regulatory deadlines, technology shifts, competitive pressures, and cost trends."

Research and report on:

1. **Forcing Functions**: External events with specific deadlines or triggers. For each: name, type (regulatory_deadline / technology_sunset / cost_escalation / competitive_pressure / budget_cycle), description of what's happening, timeline (when pressure peaks), which customer segments feel it most, strength (hard_deadline / strong_pressure / moderate / weak), and source.

2. **Trend Urgency**: Is the problem getting worse over time? Data showing the trajectory of the problem — increasing frequency, rising costs, growing regulatory pressure. Include specific metrics and timeframes.

3. **Trigger Events**: Observable events that cause organizations to start looking for a solution. For each: what the trigger is, why it causes action, how predictable it is, and how frequently it occurs.

4. **Budget & Procurement Timing**: When do target organizations typically make purchasing decisions? Fiscal year cycles, budget planning windows, procurement timelines.

5. **Urgency Synthesis**: Overall urgency assessment (high/moderate/low), strongest forcing function, when urgency peaks, and which customer segments feel urgency most acutely.
{urgency_verify_block}
{reg_block}
Cite specific sources and dates for all deadlines and events. Distinguish between hard deadlines (regulatory mandates with enforcement dates) and soft pressure (trends, competitive dynamics). Note any uncertainty in timelines."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
        }
