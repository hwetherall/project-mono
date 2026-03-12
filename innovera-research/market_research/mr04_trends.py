"""
MR-04: Trends & Growth Quality
Covers master table inputs 41-50.
"""
from market_research.base import MRBaseCategory


class MR04Trends(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-04"

    @property
    def category_name(self) -> str:
        return "Trends & Growth Quality"

    def build_query(self) -> str:
        ctx = self._market_context_block()
        geo = self.context.geography
        solution = self.context.solution_category
        industry = self.context.industry_vertical

        return f"""Research structural trends, growth quality, and downside scenarios for:

{ctx}

Search for: "drivers of growth in {industry}", "headwinds for {industry}", "{industry} market trends", "{solution} adoption trends", "structural vs cyclical growth {industry}", "downside scenarios for {industry}", "macro drivers {industry}".

Research and report on ALL of the following. Cite specific sources for every data point.

**A. Structural Opportunity Trends**
1. **Top structural opportunity trends**: The few enduring trends creating new opportunity in this market. These should be durable forces, not news cycles. For each trend, name it, describe the mechanism, and cite evidence of its impact.
2. **Top structural threat trends**: The few enduring trends that could compress spend, reduce access, or shift value away. Include commoditization risk, substitution threats, and regulatory headwinds.
3. **Trend-to-mechanism evidence**: For each major trend, document the concrete mechanism through which it changes behavior, spend, or market structure. Keep this market-specific, not generic macro commentary.
4. **Trend persistence evidence**: For each trend, provide evidence showing whether it is structural (multi-year), seasonal, cyclical, or tied to a temporary shock. This is central to growth-quality analysis.
5. **Trend-ranking signals**: Observable signals that help rank trends by importance — search trends, venture funding data, deployment counts, policy timelines.

**B. Macro Context**
6. **Macro drivers affecting market behavior**: Major macro forces shaping this market — AI adoption, digitization, sustainability mandates, labor shortages, regulation shifts. For each, trace the causal chain to market behavior.
7. **Observable buyer behavior changes**: Public evidence that buyers are changing workflows, budget priorities, or evaluation behavior. Search for survey data, buyer research, and case studies.

**C. Growth Quality & Downside**
8. **Structural versus cyclical demand indicators**: Evidence separating durable tailwinds from temporary spending conditions. Is growth driven by structural need or cyclical budget availability?
9. **Named downside scenarios**: At least 3-5 specific scenarios that could slow growth, reduce spending, or delay adoption. Make these concrete — not "recession" but "enterprise IT budget freeze triggered by macro uncertainty reducing discretionary spend by 15-20%."
10. **Historical slowdown analogues**: Prior periods where similar markets slowed, stalled, or reversed. Document what happened, why, and how long it lasted. Search for "[industry] historical slowdown" and "[industry] recession impact".

For each trend, explicitly label it as opportunity or threat, and rate persistence (structural / cyclical / episodic)."""
