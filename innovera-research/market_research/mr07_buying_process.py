"""
MR-07: Buying Process, Budget & Pricing
Covers master table inputs 65-78, 102, 108-115, 124.
"""
from market_research.base import MRBaseCategory


class MR07BuyingProcess(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-07"

    @property
    def category_name(self) -> str:
        return "Buying Process, Budget & Pricing"

    def build_query(self) -> str:
        ctx = self._market_context_block()
        geo = self.context.geography
        solution = self.context.solution_category
        industry = self.context.industry_vertical

        return f"""Research the buying process, budget dynamics, and pricing landscape for:

{ctx}

Search for: "average sales cycle {industry}", "DMU size {industry}", "who buys {solution}", "{solution} pricing", "average deal size {industry}", "budget structure {industry}", "jobs to be done {solution}", "common objections {solution}", "CAC benchmarks {industry}", "churn rate {industry}".

Research and report on ALL of the following. Cite specific sources for every data point.

**A. Buying Process & Decision-Making Unit**
1. **Typical buying cycle length by segment**: Time-to-close, procurement duration, or evaluation cycle length. Note how this varies by segment (enterprise vs SMB, etc.).
2. **DMU size and role composition**: How many people are typically involved in a buying decision and which roles recur.
3. **Typical initiator / champion titles**: Who usually identifies the problem and starts the buying motion.
4. **Typical evaluator / blocker titles**: Who evaluates compliance, security, legal, or technical fit and can stop the deal.
5. **Budget-holder and executive-approver titles**: Who owns the budget and gives final sign-off.
6. **Approval chain stages and common failure points**: The formal and informal review steps, where decisions stall, and why.

**B. Budget Structure & Commercial Reality**
7. **Budget structure norms**: Whether spend typically lands as OPEX or CAPEX, centralized or distributed, recurring or project-based.
8. **Budget ownership norms by function**: Which departments or leaders usually control the relevant spend category.
9. **ACV, ARPA, or spend benchmarks by segment**: Public benchmarks for spend per account, contract value, or recurring revenue by segment.
10. **Budget-range or line-item benchmarks**: Typical budget bands or line items from which similar purchases are funded.
11. **Replacement cycle / refresh cadence**: Typical time before customers replace, renew, or materially upgrade the incumbent solution.
12. **Churn benchmarks**: Typical logo or revenue churn for vendors in the category. Flag if data is sparse.
13. **CAC benchmarks**: Typical customer acquisition cost or payback benchmarks, if public.
14. **LTV benchmarks**: Typical customer lifetime value benchmarks or implied lifetime value from retention patterns.
15. **Payment terms and DSO norms**: Net-30, net-60, annual prepay, milestone billing, or other common payment structures.

**C. Use Cases, Pricing, and Selection Dynamics**
16. **Dominant jobs-to-be-done by segment**: The use cases that most commonly drive evaluation and spend.
17. **Core vs nice-to-have use case split**: Which use cases are mission-critical versus discretionary.
18. **Pain frequency and ROI evidence**: How often the problem occurs and what value a fix creates.
19. **Pricing models and reference price anchors**: Dominant pricing models and public price points buyers already see in the market.
20. **Preferred purchase channels by buyer type**: Direct, partner, marketplace, reseller, distributor, or self-serve.
21. **Seasonality of buying**: Periods when evaluations, purchases, or renewals cluster during the year.
22. **Top purchase criteria**: The ranked criteria buyers use to compare vendors.
23. **NPS or customer satisfaction benchmarks**: Any public satisfaction benchmarks for the category.
24. **Common objections and lost-deal reasons**: The recurring reasons buyers say no, stall, or choose alternatives.

Structure the report with separate sections for buying process, budget/pricing, and use-case dynamics. Where benchmarks are missing, say that clearly rather than inferring."""
