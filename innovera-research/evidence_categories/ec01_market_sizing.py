"""
EC-01: Market Sizing & Growth

Targeted lookup category for market size, growth rates, and structure data.
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from config.settings import GPTR_CONFIG_DIR


class EC01MarketSizing(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-01"

    @property
    def category_name(self) -> str:
        return "Market Sizing & Growth"

    def get_report_type(self) -> str:
        return "custom_report"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "targeted_lookup.json"

    def build_query(self) -> str:
        geo = self.context.geography

        # Build verification block for venture-claimed market sizes
        verification_block = ""
        if self.context.market_size_claims:
            claims = "\n".join(f"  - {c}" for c in self.context.market_size_claims)
            verification_block = f"""
6. **Venture Claims Verification**: The venture has made these market size claims. Verify, challenge, or contextualize each:
{claims}
"""

        # Conditional: hardware installed base
        hardware_block = ""
        if "hardware" in self.context.business_model_type.lower():
            hardware_block = f"""
7. **Installed Base**: Search for "{self.context.solution_category} installed base {geo}" to find the existing hardware/device installed base relevant to this market.
"""

        # Conditional: non-US geography
        geo_block = ""
        if geo.lower() not in ["united states", "us", "usa", "north america"]:
            geo_block = f"""
- **Regional Focus**: Specifically search for "{self.context.solution_category} market {geo} growth" as market data may be concentrated in US/EU reports.
"""

        query = f"""Research and report on market sizing data for the following:

**Solution category:** {self.context.solution_category}
**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Geography:** {geo}
**Problem:** {self.context.problem_summary}

Search for: "{self.context.solution_category} market size {geo}", "{self.context.solution_category} market growth rate forecast", "{self.context.industry_vertical} {self.context.sub_vertical or ''} market size", "{self.context.industry_vertical} technology spending".

Find and report:

1. **Total Addressable Market (TAM)**: The total global or regional market size for {self.context.solution_category}. Include the dollar value, the year of the estimate, and the source. If multiple estimates exist, report all and note the range.

2. **Market Growth Rate**: CAGR or annual growth rate forecasts. Include the forecast period and source.

3. **Serviceable Addressable Market (SAM)**: The subset relevant to {self.context.industry_vertical} in {geo}. If this specific segment isn't broken out in reports, note the closest available segmentation.

4. **Market Structure**: Is this market fragmented or consolidated? Emerging or mature? Who are the largest players by revenue or market share?

5. **Industry Revenue/Volume Data**: Any statistics on the size of the {self.context.industry_vertical} industry in {geo} that contextualizes the opportunity (e.g., total infrastructure spending, number of target organizations, etc.).
{verification_block}{hardware_block}{geo_block}
For every data point, cite the specific source and publication date. Distinguish between: primary research (from market research firms), analyst estimates, and government statistics. Flag any significant variance between sources.

Prioritize data from the last 24 months. If only older data exists, note this explicitly."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
        }
