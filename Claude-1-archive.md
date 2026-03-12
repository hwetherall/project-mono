# Innovera Research — Market Research Pipeline Build Spec

## Overview

This spec adds a **Market Research** pipeline alongside the existing **Demand Validation** pipeline. The user selects the mode from the input form. Each mode runs a different set of research categories with different queries, phasing, and context extraction prompts — but they share the same orchestrator infrastructure, output packaging, progress system, and frontend shell.

**The existing Demand Validation pipeline (EC-01 through EC-13) must remain completely unchanged.** All changes are additive. The Market Research pipeline introduces 10 new categories (MR-01 through MR-10) derived from a 130-input master table (`market-research-inputs/market-research-master-table.csv`).

---

## Current Architecture (unchanged)

```
innovera-research/
├── api/
│   ├── app.py
│   ├── routes.py           # Add research_mode branching
│   ├── models.py           # Add research_mode field
│   ├── websocket.py
│   └── progress_bridge.py  # Add MR category name resolution
├── config/
│   ├── settings.py
│   └── gptr_configs/
│       ├── targeted_lookup.json
│       ├── deep_landscape.json
│       └── hybrid_mission.json
├── context_extraction/
│   ├── extractor.py        # Add mode-aware prompt selection
│   ├── models.py           # Extend ContextSignals for MR
│   └── prompts.py          # Add MR extraction prompts
├── evidence_categories/    # Existing EC-01..EC-13 untouched
│   ├── base.py
│   ├── registry.py
│   └── ec01_*.py ... ec13_*.py
├── market_research/        # NEW — all MR category implementations
│   ├── __init__.py
│   ├── registry.py         # MR_CATEGORY_REGISTRY, phases
│   ├── base.py             # MRBaseCategory (extends BaseCategory)
│   └── mr01_market_definition.py ... mr10_barriers_ecosystem.py
├── orchestrator/
│   ├── runner.py            # Accept research_mode, select registry/plan
│   ├── phases.py            # Add get_mr_execution_plan()
│   └── progress.py
├── output/
│   ├── package_assembler.py # Mode-aware registry selection
│   ├── yaml_formatter.py
│   └── markdown_formatter.py # Mode-aware report header
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── InputForm.jsx       # Add mode selector
│   │   │   ├── ProgressPanel.jsx   # Add MR phase/category mappings
│   │   │   ├── CategoryCard.jsx    # Add MR category names
│   │   │   └── ...
│   │   └── hooks/
│   │       └── useResearchRun.js   # No changes needed
│   └── ...
├── market-research-inputs/          # Reference data (read-only)
│   ├── market-research-master-table.csv
│   └── market-research-master-table.md
└── run_web.py
```

---

## Category Mapping

The 130 inputs from the master table map to 10 research categories. Each category runs one GPT Researcher query that covers all inputs within that category.

| Category ID | Category Name | Input Count | Master Table IDs | Research Mode |
|---|---|---|---|---|
| MR-01 | Market Definition & Sizing | 19 | 1-18, 101 | deep |
| MR-02 | SAM / SOM / Reachability | 10 | 19-28 | deep |
| MR-03 | Segments & Concentration | 13 | 29-40, 122 | deep |
| MR-04 | Trends & Growth Quality | 10 | 41-50 | deep |
| MR-05 | Value Chain & Whitespace | 16 | 51-59, 116-121, 123 | deep |
| MR-06 | Competition & Channels | 10 | 60-64, 103-107 | deep |
| MR-07 | Buying Process, Budget & Pricing | 24 | 65-78, 102, 108-115, 124 | deep |
| MR-08 | Adoption & Expansion Dynamics | 6 | 79-84 | deep |
| MR-09 | Regulation & Platform Shifts | 11 | 85-90, 125-129 | deep |
| MR-10 | Barriers, Saturation & Ecosystem Power | 11 | 91-100, 130 | deep |

All MR categories use `deep` research mode with the `deep_landscape.json` GPTR config. This mode provides the broadest search coverage, which is appropriate for comprehensive market research.

---

## Phasing & Dependencies

### Phase 1: Foundation (parallel, no dependencies)

**Categories:** MR-01, MR-04, MR-06, MR-09

**Rationale:** These four categories can run independently. MR-01 (Market Definition) and MR-06 (Competition) produce foundational data needed by Phase 2 categories — market boundaries, competitor lists, and sizing context. MR-04 (Trends) and MR-09 (Regulation) are inherently independent.

### Phase 2: Structural (parallel, depends on Phase 1)

**Categories:** MR-02, MR-03, MR-05

**Rationale:** These categories benefit from Phase 1 outputs:
- MR-02 (SAM/SOM) uses market definition and sizing from MR-01 to calculate serviceable market
- MR-03 (Segments) uses market boundaries from MR-01 and competitor data from MR-06
- MR-05 (Value Chain) uses competitor landscape from MR-06 to map actors and control points

After Phase 1 completes, the orchestrator extracts key market definition terms and competitor names from MR-01 and MR-06 results and injects them into context for Phase 2 queries.

### Phase 3: Commercial (parallel, depends on Phase 2)

**Categories:** MR-07, MR-08, MR-10

**Rationale:** These categories depend on the structural understanding built in Phases 1-2:
- MR-07 (Buying Process) uses segment definitions from MR-03 and competition data from MR-06
- MR-08 (Adoption) uses segment maturity from MR-03 and competitor landscape from MR-06
- MR-10 (Barriers) uses value chain from MR-05, competition from MR-06, and segment data from MR-03

```
Phase 1 (Foundation)         Phase 2 (Structural)         Phase 3 (Commercial)
┌──────┐ ┌──────┐          ┌──────┐ ┌──────┐            ┌──────┐ ┌──────┐
│MR-01 │ │MR-04 │          │MR-02 │ │MR-03 │            │MR-07 │ │MR-08 │
│Market│ │Trends│    ──►   │SAM/  │ │Segmt │    ──►     │Buy   │ │Adopt │
│Defn  │ │      │          │SOM   │ │Conc  │            │Proc  │ │Dyn   │
└──────┘ └──────┘          └──────┘ └──────┘            └──────┘ └──────┘
┌──────┐ ┌──────┐          ┌──────┐                     ┌──────┐
│MR-06 │ │MR-09 │          │MR-05 │                     │MR-10 │
│Comp  │ │Reg   │          │Value │                     │Barr  │
│Chan  │ │Plat  │          │Chain │                     │Ecosys│
└──────┘ └──────┘          └──────┘                     └──────┘
```

---

## Backend Changes

### 1. `api/models.py` — Add `research_mode` field

Add the `research_mode` field to `ResearchRequest`:

```python
from typing import Literal

class ResearchRequest(BaseModel):
    document_text: str
    additional_context: str = ""
    core_question: str
    success_criteria: list[str]
    venture_name: str = ""
    categories_to_run: list[str] = []
    max_concurrent: int = Field(default=2, ge=1, le=6)
    research_mode: Literal["demand_validation", "market_research"] = "demand_validation"
```

This is the only model change. `categories_to_run` already accepts arbitrary IDs — it will accept `MR-01` through `MR-10` when mode is `market_research`.

### 2. `market_research/registry.py` — MR Category Registry (NEW FILE)

Create `innovera-research/market_research/registry.py`:

```python
"""
Registry of all market research categories with phase assignments and metadata.
"""
from enum import IntEnum
from dataclasses import dataclass, field


class MRPhase(IntEnum):
    """Execution phases for market research. Lower numbers run first."""
    FOUNDATION = 1
    STRUCTURAL = 2
    COMMERCIAL = 3


@dataclass
class MRCategoryMeta:
    """Metadata for a registered market research category."""
    category_id: str
    category_name: str
    phase: MRPhase
    research_mode: str  # all "deep" for MR
    depends_on: list[str]
    master_table_ids: list[int]


MR_CATEGORY_REGISTRY: dict[str, MRCategoryMeta] = {
    "MR-01": MRCategoryMeta(
        category_id="MR-01",
        category_name="Market Definition & Sizing",
        phase=MRPhase.FOUNDATION,
        research_mode="deep",
        depends_on=[],
        master_table_ids=list(range(1, 19)) + [101],
    ),
    "MR-02": MRCategoryMeta(
        category_id="MR-02",
        category_name="SAM / SOM / Reachability",
        phase=MRPhase.STRUCTURAL,
        research_mode="deep",
        depends_on=["MR-01", "MR-06"],
        master_table_ids=list(range(19, 29)),
    ),
    "MR-03": MRCategoryMeta(
        category_id="MR-03",
        category_name="Segments & Concentration",
        phase=MRPhase.STRUCTURAL,
        research_mode="deep",
        depends_on=["MR-01", "MR-06"],
        master_table_ids=list(range(29, 41)) + [122],
    ),
    "MR-04": MRCategoryMeta(
        category_id="MR-04",
        category_name="Trends & Growth Quality",
        phase=MRPhase.FOUNDATION,
        research_mode="deep",
        depends_on=[],
        master_table_ids=list(range(41, 51)),
    ),
    "MR-05": MRCategoryMeta(
        category_id="MR-05",
        category_name="Value Chain & Whitespace",
        phase=MRPhase.STRUCTURAL,
        research_mode="deep",
        depends_on=["MR-06"],
        master_table_ids=list(range(51, 60)) + list(range(116, 122)) + [123],
    ),
    "MR-06": MRCategoryMeta(
        category_id="MR-06",
        category_name="Competition & Channels",
        phase=MRPhase.FOUNDATION,
        research_mode="deep",
        depends_on=[],
        master_table_ids=list(range(60, 65)) + list(range(103, 108)),
    ),
    "MR-07": MRCategoryMeta(
        category_id="MR-07",
        category_name="Buying Process, Budget & Pricing",
        phase=MRPhase.COMMERCIAL,
        research_mode="deep",
        depends_on=["MR-03", "MR-06"],
        master_table_ids=list(range(65, 79)) + [102] + list(range(108, 116)) + [124],
    ),
    "MR-08": MRCategoryMeta(
        category_id="MR-08",
        category_name="Adoption & Expansion Dynamics",
        phase=MRPhase.COMMERCIAL,
        research_mode="deep",
        depends_on=["MR-03", "MR-06"],
        master_table_ids=list(range(79, 85)),
    ),
    "MR-09": MRCategoryMeta(
        category_id="MR-09",
        category_name="Regulation & Platform Shifts",
        phase=MRPhase.FOUNDATION,
        research_mode="deep",
        depends_on=[],
        master_table_ids=list(range(85, 91)) + list(range(125, 130)),
    ),
    "MR-10": MRCategoryMeta(
        category_id="MR-10",
        category_name="Barriers, Saturation & Ecosystem Power",
        phase=MRPhase.COMMERCIAL,
        research_mode="deep",
        depends_on=["MR-05", "MR-06", "MR-03"],
        master_table_ids=list(range(91, 101)) + [130],
    ),
}


def get_mr_categories_by_phase(phase: MRPhase) -> list[str]:
    """Return MR category IDs for a given phase."""
    return [cid for cid, meta in MR_CATEGORY_REGISTRY.items() if meta.phase == phase]
```

Also create `innovera-research/market_research/__init__.py` as an empty file.

### 3. `market_research/base.py` — MR Base Category (NEW FILE)

Create `innovera-research/market_research/base.py`. This extends the existing `BaseCategory` but adjusts it slightly for MR context:

```python
"""
Base class for all market research categories.
Extends the demand-validation BaseCategory with MR-specific helpers.
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from context_extraction.models import ContextSignals
from config.settings import GPTR_CONFIG_DIR


class MRBaseCategory(BaseCategory):
    """
    Base for market research categories.
    All MR categories use deep research mode.
    """

    def __init__(self, context: ContextSignals, venture_docs_dir: Path):
        super().__init__(context, venture_docs_dir)
        self.market_definition_terms: list[str] = []
        self.known_competitors: list[str] = []
        self.known_segments: list[str] = []

    def inject_phase1_results(
        self,
        market_terms: list[str] | None = None,
        competitors: list[str] | None = None,
        segments: list[str] | None = None,
    ):
        """Inject extracted data from Phase 1 results for Phase 2/3 queries."""
        if market_terms:
            self.market_definition_terms = market_terms
        if competitors:
            self.known_competitors = competitors
        if segments:
            self.known_segments = segments

    def get_report_type(self) -> str:
        return "deep"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "deep_landscape.json"

    def _market_context_block(self) -> str:
        """Standard context block used by all MR queries."""
        geo = self.context.geography
        industry = self.context.industry_vertical
        sub = self.context.sub_vertical or "General"
        solution = self.context.solution_category

        block = f"""**Industry:** {industry} / {sub}
**Solution Category:** {solution}
**Geography:** {geo}
**Business Model:** {self.context.business_model_type}
**Target Buyer:** {self.context.target_buyer_type}
**Problem Context:** {self.context.problem_summary}"""

        if self.market_definition_terms:
            block += f"\n**Market Terms:** {', '.join(self.market_definition_terms)}"
        if self.known_competitors:
            block += f"\n**Known Competitors:** {', '.join(self.known_competitors[:10])}"
        if self.known_segments:
            block += f"\n**Known Segments:** {', '.join(self.known_segments[:8])}"

        return block

    def parse_report(self, raw_report: str) -> dict:
        return {"raw_report_text": raw_report}
```

### 4. Ten MR Category Implementations (NEW FILES)

Create 10 files in `innovera-research/market_research/`. Each follows the same pattern as existing EC categories: implement `category_id`, `category_name`, and `build_query()`. The `parse_report()` method returns `{"raw_report_text": raw_report}` from the base class (same as existing EC categories).

Below are all 10 category implementations with their complete `build_query()` methods. Each query is constructed to cover every input from the master table for that category.

---

#### `market_research/mr01_market_definition.py`

```python
"""
MR-01: Market Definition & Sizing
Covers master table inputs 1-18, 101.
"""
from market_research.base import MRBaseCategory


class MR01MarketDefinition(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-01"

    @property
    def category_name(self) -> str:
        return "Market Definition & Sizing"

    def build_query(self) -> str:
        ctx = self._market_context_block()
        geo = self.context.geography
        solution = self.context.solution_category
        industry = self.context.industry_vertical
        sub = self.context.sub_vertical or ""

        verification_block = ""
        if self.context.market_size_claims:
            claims = "\n".join(f"  - {c}" for c in self.context.market_size_claims)
            verification_block = f"""
**Venture Claims to Verify:**
{claims}
"""

        return f"""Conduct comprehensive market definition and sizing research for this market:

{ctx}
{verification_block}

Search for: "{solution} market size {geo}", "{solution} market definition", "{industry} {sub} TAM", "{solution} NAICS code", "{solution} market growth forecast", "{solution} market methodology".

Research and report on ALL of the following. For every data point, cite the specific source and publication date.

**A. Market Boundary Definition**
1. **Canonical market definition**: The main category name used by analysts, regulators, and trade bodies. Search for NAICS codes, Gartner/IDC definitions, trade association classifications.
2. **Alternate labels and synonyms**: Adjacent labels, legacy names, and nearby category terms. Test whether different labels imply different market boundaries.
3. **Product-type inclusion rules**: Which product forms or solution types third-party sources explicitly include in their market totals. Reference methodology notes from major reports.
4. **Product-type exclusion rules**: Which adjacent offerings sources explicitly exclude, and why. Document the edges of the market.
5. **Geographic scope conventions**: How sources define region-level scope (global, North America, EU, APAC). Note any differences in regional definitions across sources.
6. **Customer-segment boundaries**: How sources split the market by enterprise size, industry vertical, buyer type, or operating model.
7. **Use-case boundaries**: How sources separate the market by application, workflow, or job-to-be-done.

**B. Market Sizing Data**
8. **Named TAM estimates**: Individual market-size figures from named third-party sources with year, scope, and source attached. Report ALL estimates found, not just one.
9. **TAM range**: Synthesize the low, midpoint, and high estimates from all sources found. Make uncertainty explicit.
10. **Historical market size series**: At least 3-5 years of historical data. Note data gaps.
11. **Projected market size series**: Forward estimates with forecast horizon. Include multiple projections if available.
12. **Historical CAGR by geography or segment**: Where available, break out growth rates by region or subsegment.
13. **Projected CAGR by geography or segment**: Forecast growth rates by region or subsegment. Identify where future demand concentrates.

**C. Sizing Methodology & Confidence**
14. **Sizing methodology per source**: Whether each source uses top-down, bottom-up, value-based, shipment-based, or spend-based methods. Compare rigor across sources.
15. **Bottom-up demand-unit proxies**: Public counts for buyers, users, seats, facilities, transactions, or assets that can anchor bottom-up sizing. Search for government censuses, industry directories, public databases.
16. **Unit price / spend / value-per-unit proxies**: Benchmarks for spend per account, per seat, per transaction that convert volume into dollar market size.
17. **Hard-data anchor points**: Official data from SEC filings, government statistics, regulator databases, or standards bodies that serve as high-confidence anchors.
18. **Source credibility metadata**: For each source, note recency, independence, transparency, sample quality, potential sponsor bias, and methodological caveats.
19. **Pricing trend / ASP trajectory**: Average selling price trends over time — is pricing rising, falling, or compressing by segment?

Prioritize data from the last 24 months. If only older data exists, note this explicitly. Distinguish between primary research, analyst estimates, and government statistics. Flag significant variance between sources."""

```

---

#### `market_research/mr02_sam_som.py`

```python
"""
MR-02: SAM / SOM / Reachability
Covers master table inputs 19-28.
"""
from market_research.base import MRBaseCategory


class MR02SamSom(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-02"

    @property
    def category_name(self) -> str:
        return "SAM / SOM / Reachability"

    def build_query(self) -> str:
        ctx = self._market_context_block()
        geo = self.context.geography
        solution = self.context.solution_category
        industry = self.context.industry_vertical

        return f"""Research the serviceable addressable market (SAM), serviceable obtainable market (SOM), and market reachability for:

{ctx}

Search for: "{solution} route to market", "{solution} channel partners", "{industry} licensing requirements", "{solution} adoption rate", "{industry} market penetration", "{solution} compliance requirements {geo}".

Research and report on ALL of the following. Cite specific sources for every data point.

**A. Route-to-Market & Channel Structure**
1. **Dominant route-to-market types**: The main commercial routes used in this market — direct sales, channel partners, marketplaces, OEM, resale, self-serve. Which routes dominate and why?
2. **Channel share and segment coverage**: How much of the market each route serves, and which customer segments each route reaches best. Quantify where possible.
3. **Marketplace or platform access requirements**: Public requirements for listing, integration, certification, or participation on key platforms and marketplaces in this category.

**B. Access & Compliance Gates**
4. **Jurisdiction-specific licensing or compliance requirements**: Publicly documented legal, certification, or compliance requirements that gate access to target geographies or segments in {geo}. These are the filters between theoretical demand and serviceable demand.
5. **Time and cost to satisfy access requirements**: Typical duration, fees, audits, or approval effort needed to meet these access requirements.
6. **Reachable ICP counts by subsegment**: Public counts of organizations or buyers matching the relevant firmographic and use-case profile. Search industry directories, public databases, trade associations.

**C. Adoption & Obtainability**
7. **Analogous adoption-ramp benchmarks**: How quickly similar products or categories reached meaningful adoption. Include time-to-X-customers benchmarks from comparable markets.
8. **Typical switching timelines**: How long it takes buyers to replace incumbent tools, manual processes, or vendors in this category. Include implementation timelines and procurement cycles.
9. **Public penetration and attach-rate benchmarks**: Comparable rates for adoption, seat penetration, attach, or conversion in adjacent categories. Search for "[category] market penetration rate" and "percentage of companies using [technology]".
10. **Evidence-backed versus speculative markers**: Which assumptions in public sizing are sourced versus inferred. Help separate robust inputs from guesswork.

For each finding, note whether it applies globally or is specific to {geo}. Distinguish between hard data and analyst inference."""

```

---

#### `market_research/mr03_segments.py`

```python
"""
MR-03: Segments & Concentration
Covers master table inputs 29-40, 122.
"""
from market_research.base import MRBaseCategory


class MR03Segments(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-03"

    @property
    def category_name(self) -> str:
        return "Segments & Concentration"

    def build_query(self) -> str:
        ctx = self._market_context_block()
        geo = self.context.geography
        solution = self.context.solution_category
        industry = self.context.industry_vertical

        return f"""Research market segmentation, concentration, and buyer dynamics for:

{ctx}

Search for: "{industry} market segmentation", "{solution} customer segments", "{industry} market share concentration", "{industry} buyer segments", "{solution} market by company size", "{industry} competitive intensity by segment", "{industry} M&A consolidation".

Research and report on ALL of the following. Cite specific sources for every data point.

**A. Segment Taxonomy**
1. **Segment taxonomy**: The usable segmentation scheme supported by public data — by industry vertical, company size, region, and use case. Document which segmentation frameworks public sources actually support with data.
2. **Addressable revenue by subsegment**: Public estimates of market spend or size for each major subsegment. This is needed to score segment size and focus the beachhead.
3. **Growth rate by subsegment**: Public growth rates for relevant verticals, buyer cohorts, regions, or use cases. Identify which pockets are growing fastest.
4. **Demand concentration by top segments**: Which segments account for the largest share of overall demand? Quantify the top-3 to top-5 segments by spend share.
5. **Primary customer segment descriptors**: Real-world attributes that make the leading segment identifiable and list-buildable — firmographic criteria, operational characteristics, buying signals.

**B. Buyer & User Roles**
6. **Buyer role titles by segment**: Common buyer titles or functions in each important segment. Who signs the check?
7. **User role titles by segment**: End-user or operator roles involved in the workflow. Who uses the product day-to-day?

**C. Competitive Intensity & Structure**
8. **Competitive intensity by subsegment**: How crowded each subsegment is and how strong incumbents appear. Search review sites, market maps, analyst landscapes.
9. **Fragmentation and consolidation indicators**: Vendor counts, share dispersion, HHI proxies, roll-up patterns, M&A consolidation signals. Is the market fragmenting or consolidating?
10. **Competitive layer structure**: Evidence for distinct layers — enterprise vs SMB, premium vs mass market, platform vs specialist.

**D. Concentration Risk**
11. **Buyer concentration indicators**: Whether demand is concentrated among a small number of large buyers, or broadly distributed.
12. **Whale-versus-long-tail demand pattern**: Does category spend appear dominated by large accounts or broadly distributed across many smaller buyers?
13. **Buyer power indicators**: Evidence that buyers have leverage via concentration, procurement sophistication, or volume-based negotiating power.

Structure the report with clear sections. For each segment claim, cite the source and note whether the data is directly reported or inferred."""

```

---

#### `market_research/mr04_trends.py`

```python
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

```

---

#### `market_research/mr05_value_chain.py`

```python
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

```

---

#### `market_research/mr06_competition.py`

```python
"""
MR-06: Competition & Channels
Covers master table inputs 60-64, 103-107.
"""
import re
from market_research.base import MRBaseCategory
from evidence_categories.base import CategoryResult


class MR06Competition(MRBaseCategory):

    @property
    def category_id(self) -> str:
        return "MR-06"

    @property
    def category_name(self) -> str:
        return "Competition & Channels"

    def build_query(self) -> str:
        ctx = self._market_context_block()
        geo = self.context.geography
        solution = self.context.solution_category
        industry = self.context.industry_vertical

        competitor_seed = ""
        if self.context.named_competitors:
            names = ", ".join(self.context.named_competitors)
            competitor_seed = f"\n**Known competitors to start with (search for more):** {names}"

        return f"""Conduct a comprehensive competitive landscape and distribution channel analysis for:

{ctx}
{competitor_seed}

Search for: "top companies in {industry}", "market leaders {industry}", "{solution} alternatives", "{solution} competitors comparison", "{solution} pricing", "{industry} distribution channels", "{industry} market share", "G2 reviews {solution}", "Capterra {solution}".

Research and report on ALL of the following. Cite specific sources for every data point.

**A. Competitor Identification**
1. **Direct competitor list**: Named direct competitors currently serving this market. For each, include: what they do, who they target, positioning, pricing model (if public), funding stage, estimated revenue or scale indicators.
2. **Substitute and workaround list**: Named substitute products, adjacent vendors, manual workflows, or outsourcing options buyers use instead. These are the real competitive alternatives.
3. **Competitor revenue or market-share estimates**: Public share figures or revenue estimates for relevant competitors. Note the basis for each estimate (filings, analyst reports, traffic analysis, etc.).
4. **Public inputs supporting share estimates**: Visible assumptions behind share estimates — customer counts, pricing, traffic, segment exposure.
5. **Distribution route mix and channel power**: The relative importance of direct, partner, marketplace, OEM, or distributor-led routes, and who holds leverage in each.

**B. Competitive Intelligence**
6. **Review-site sentiment and recurring complaints**: Common strengths, weaknesses, complaints, and delight points visible on G2, Capterra, app stores, Reddit, and forums. Search for actual reviews and synthesize patterns.
7. **Competitor geographic footprint**: Where major competitors are strongest or weakest by region. Note any geographic gaps.
8. **Competitor partnerships and ecosystem integrations**: Key technology, channel, OEM, reseller, data, and services partners attached to major competitors.
9. **Litigation, IP dispute, or antitrust history**: Material lawsuits, IP disputes, or regulatory enforcement involving major vendors.
10. **Competitor acquisition history**: Acquisitions made by leading vendors — what capabilities they bought and why. Include dates and deal sizes where public.

For each competitor, use a consistent format with the company name in bold. Be specific — name companies, cite sources, provide concrete details. If pricing is not public, say so."""

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
            "competitor_names_extracted": self._extract_competitor_names(raw_report),
        }

    def _extract_competitor_names(self, report: str) -> list[str]:
        """Extract competitor names from bold text patterns in the report."""
        names = []
        bold_pattern = re.findall(r'\*\*([A-Z][A-Za-z0-9\s&\.\-]+?)\*\*', report)
        skip_phrases = {
            "direct competitor", "substitute", "workaround", "competitor",
            "distribution", "channel", "review", "partnership", "litigation",
            "acquisition", "search for", "research and report", "note",
            "important", "summary", "conclusion", "sources", "known competitors",
            "industry", "geography", "solution", "business model", "target buyer",
            "problem context", "market terms",
        }
        for name in bold_pattern:
            name_clean = name.strip()
            if (
                len(name_clean) > 2
                and len(name_clean) < 50
                and name_clean.lower() not in skip_phrases
                and not any(skip in name_clean.lower() for skip in skip_phrases)
                and name_clean not in names
            ):
                names.append(name_clean)
        return names

    def get_competitor_list(self, result: CategoryResult) -> list[str]:
        """Public method for Phase 2/3 to get competitor list from MR-06 results."""
        if result and result.structured_findings:
            names = result.structured_findings.get("competitor_names_extracted", [])
            return list(set(names + self.context.named_competitors))
        return self.context.named_competitors
```

---

#### `market_research/mr07_buying_process.py`

```python
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

```

---

#### `market_research/mr08_adoption_dynamics.py`

```python
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

```

---

#### `market_research/mr09_regulation_platform.py`

```python
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

```

---

#### `market_research/mr10_barriers_ecosystem.py`

```python
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

```

### 5. `context_extraction/models.py` — Extend `ContextSignals` for Market Research

The current `ContextSignals` schema is venture-oriented but already contains many fields that can be reused. Extend it with a few market-research-specific fields rather than creating a separate model.

Add:

```python
class ContextSignals(BaseModel):
    # existing fields remain
    research_mode: str = "demand_validation"
    market_definition_terms: list[str] = Field(default_factory=list)
    adjacent_market_terms: list[str] = Field(default_factory=list)
    buyer_segments: list[str] = Field(default_factory=list)
    distribution_channels: list[str] = Field(default_factory=list)
    ecosystem_entities: list[str] = Field(default_factory=list)
```

Notes:
- `research_mode` should be persisted into the output package so downstream formatters and frontend views can branch cleanly.
- These added fields are useful for MR query composition, especially in Phase 2 and Phase 3.
- Keep all existing demand-validation fields intact for backward compatibility.

### 6. `context_extraction/prompts.py` — Add Market Research Extraction Prompt

Keep the current demand-validation prompt unchanged. Add a new system prompt and user prompt for market research mode.

```python
MARKET_RESEARCH_EXTRACTION_SYSTEM = """You are an expert market intelligence analyst preparing structured research signals for a market research pipeline. You will receive documents that describe a market, product category, industry problem, or venture. Your job is to extract the canonical market framing, search terms, segment language, regulatory language, and channel language needed to run 10 market research categories.

Output valid JSON matching the schema provided. Extract concrete, search-usable language from the source material. Do not invent facts not grounded in the documents.

Guidelines:
- venture_name: if the material is about a company, use the company name; if not, use the market/topic name.
- solution_category: the market or product category being researched.
- market_definition_terms: 5-15 phrases that credible sources would use for the category.
- adjacent_market_terms: nearby labels, alternate names, substitutes, or legacy category names.
- buyer_segments: named customer cohorts, verticals, buyer types, or firmographic slices.
- distribution_channels: named routes to market, such as direct sales, distributors, marketplaces, OEM, VARs, or self-serve.
- ecosystem_entities: named platforms, standards bodies, regulators, intermediaries, suppliers, or gatekeepers.
- named_competitors: include only if explicit or strongly implied by the documents.
- named_regulations: include laws, standards, or regulatory bodies explicitly referenced.

For category_priorities, assign all MR categories (MR-01 through MR-10) a priority using these rules:
- Always set MR-01, MR-04, MR-06, and MR-09 to critical.
- If regulation or compliance is central, MR-09 and MR-10 = critical.
- If the market appears fragmented or crowded, MR-06 and MR-10 = critical.
- If the brief emphasizes GTM or commercialization questions, MR-02 and MR-07 = critical.
- If whitespace, ecosystem structure, or control points are important, MR-05 and MR-10 = critical.
- Default remaining categories to high unless the docs make them clearly peripheral."""

MARKET_RESEARCH_EXTRACTION_USER = """Analyze the following documents and extract structured signals for a market research pipeline.

## Documents

{documents_text}

## Structured Metadata (if provided)

{metadata_text}

## Required Output

Return a single JSON object matching this schema exactly. Do not include any text outside the JSON object.

{schema_json}"""
```

### 7. `context_extraction/extractor.py` — Select Prompt by `research_mode`

The current extractor always uses `CONTEXT_EXTRACTION_SYSTEM` and `CONTEXT_EXTRACTION_USER`. Make it mode-aware.

Update the class signature and prompt selection:

```python
from .prompts import (
    CONTEXT_EXTRACTION_SYSTEM,
    CONTEXT_EXTRACTION_USER,
    MARKET_RESEARCH_EXTRACTION_SYSTEM,
    MARKET_RESEARCH_EXTRACTION_USER,
)

class ContextExtractor:
    def extract(
        self,
        venture_docs_dir: Path,
        metadata: dict | None = None,
        research_mode: str = "demand_validation",
    ) -> ContextSignals:
        documents_text = self._read_documents(venture_docs_dir)
        metadata_text = json.dumps(metadata, indent=2) if metadata else "No structured metadata provided."
        schema_json = json.dumps(ContextSignals.model_json_schema(), indent=2)

        if research_mode == "market_research":
            system_prompt = MARKET_RESEARCH_EXTRACTION_SYSTEM
            user_template = MARKET_RESEARCH_EXTRACTION_USER
        else:
            system_prompt = CONTEXT_EXTRACTION_SYSTEM
            user_template = CONTEXT_EXTRACTION_USER

        user_message = user_template.format(
            documents_text=documents_text,
            metadata_text=metadata_text,
            schema_json=schema_json,
        )

        response = self.client.chat.completions.create(
            model=CONTEXT_LLM_MODEL,
            max_tokens=CONTEXT_LLM_MAX_TOKENS,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        ...
```

Also set the result mode explicitly after validation:

```python
signals = ContextSignals.model_validate_json(response_text)
signals.research_mode = research_mode
return signals
```

### 8. `orchestrator/phases.py` — Add Market Research Execution Plan

Do not replace the existing `get_execution_plan()`. Add a parallel function for market research:

```python
from market_research.registry import MRPhase, MR_CATEGORY_REGISTRY, get_mr_categories_by_phase

def get_mr_execution_plan() -> list[dict]:
    plan = []
    for phase in sorted(MRPhase):
        category_ids = get_mr_categories_by_phase(phase)
        plan.append({
            "phase": phase.value,
            "phase_name": phase.name,
            "categories": category_ids,
            "parallel": True,
            "wait_for": list(set(
                dep
                for cid in category_ids
                for dep in MR_CATEGORY_REGISTRY[cid].depends_on
            )),
        })
    return plan
```

### 9. `orchestrator/runner.py` — Branch by `research_mode`

Update `ResearchRunner` so it can orchestrate either category family.

Required changes:

1. Add constructor arg:

```python
def __init__(
    self,
    context: ContextSignals,
    venture_docs_dir: Path,
    progress: Optional[ProgressTracker] = None,
    only_categories: Optional[list[str]] = None,
    research_mode: str = "demand_validation",
):
    ...
    self.research_mode = research_mode
```

2. Split category maps:

```python
from market_research.mr01_market_definition import MR01MarketDefinition
...
from market_research.mr10_barriers_ecosystem import MR10BarriersEcosystem

MR_CATEGORY_CLASSES = {
    "MR-01": MR01MarketDefinition,
    "MR-02": MR02SamSom,
    "MR-03": MR03Segments,
    "MR-04": MR04Trends,
    "MR-05": MR05ValueChain,
    "MR-06": MR06Competition,
    "MR-07": MR07BuyingProcess,
    "MR-08": MR08AdoptionDynamics,
    "MR-09": MR09RegulationPlatform,
    "MR-10": MR10BarriersEcosystem,
}
```

3. Choose plan and registry dynamically:

```python
if self.research_mode == "market_research":
    plan = get_mr_execution_plan()
    category_classes = MR_CATEGORY_CLASSES
    registry = MR_CATEGORY_REGISTRY
else:
    plan = get_execution_plan()
    category_classes = CATEGORY_CLASSES
    registry = CATEGORY_REGISTRY
```

4. Replace hardcoded EC logic with mode-aware extraction hooks:

```python
if self.research_mode == "demand_validation" and phase_info["phase"] == Phase.FOUNDATION:
    self._extract_competitor_list()

if self.research_mode == "market_research" and phase_info["phase"] == MRPhase.FOUNDATION:
    self._extract_market_research_context()
```

5. Add helper for MR context propagation:

```python
def _extract_market_research_context(self):
    mr01_result = self.results.get("MR-01")
    mr06_result = self.results.get("MR-06")

    market_terms = []
    if mr01_result and mr01_result.structured_findings:
        market_terms = mr01_result.structured_findings.get("market_terms_extracted", [])

    competitor_terms = []
    if mr06_result and mr06_result.structured_findings:
        competitor_terms = mr06_result.structured_findings.get("competitor_names_extracted", [])

    self.context.market_definition_terms = list(set(self.context.market_definition_terms + market_terms))
    self.context.named_competitors = list(set(self.context.named_competitors + competitor_terms))

    self.progress.log(
        f"Extracted {len(self.context.market_definition_terms)} market terms and "
        f"{len(self.context.named_competitors)} competitor names from Phase 1"
    )
```

6. In `_run_category`, use the correct category map and avoid hardcoded `EC-03`, `EC-04`, `EC-11` checks for MR mode.

### 10. `api/routes.py` — Pass `research_mode` Through the Pipeline

The route already builds a combined input document and launches `ContextExtractor`, `ResearchRunner`, and `PackageAssembler`. Make this path mode-aware without duplicating the route.

Changes:

1. Add `research_mode` to metadata:

```python
metadata = {
    "core_question": request.core_question,
    "success_criteria": request.success_criteria,
    "venture_name_override": request.venture_name or None,
    "research_mode": request.research_mode,
}
```

2. Pass mode to context extraction:

```python
context = extractor.extract(
    run_docs_dir,
    metadata,
    research_mode=request.research_mode,
)
```

3. Pass mode to runner:

```python
runner = ResearchRunner(
    context=context,
    venture_docs_dir=run_docs_dir,
    progress=progress,
    only_categories=only_categories,
    research_mode=request.research_mode,
)
```

4. Update progress log strings:

```python
mode_label = "Market Research" if request.research_mode == "market_research" else "Demand Validation"
progress.emit_log_detail(f"Starting {mode_label} run with max {max_conc} concurrent categories...", "info")
```

5. Persist the mode in `active_runs` and `run_meta.json`.

6. In `get_run_status()` and `retry_category()`, use the correct registry/category-class map for MR categories.

### 11. `api/progress_bridge.py` — Resolve MR Category Names

The current `_get_category_name()` only checks `CATEGORY_REGISTRY`. Make it check both registries.

```python
def _get_category_name(self, category_id: str) -> str:
    try:
        from evidence_categories.registry import CATEGORY_REGISTRY
        from market_research.registry import MR_CATEGORY_REGISTRY

        if category_id in CATEGORY_REGISTRY:
            return CATEGORY_REGISTRY[category_id].category_name
        if category_id in MR_CATEGORY_REGISTRY:
            return MR_CATEGORY_REGISTRY[category_id].category_name
        return category_id
    except ImportError:
        return category_id
```

## Output Changes

### 12. `output/package_assembler.py` — Mode-Aware Consumption Map and Metadata

The current assembler always uses `get_consumption_map()` from the EC registry. Add a market-research consumption map and branch by mode.

In `market_research/registry.py`, add:

```python
def get_mr_consumption_map() -> dict[str, list[dict]]:
    consumption = {}
    for cid, meta in MR_CATEGORY_REGISTRY.items():
        for section_id, role in meta.section_consumption.items():
            consumption.setdefault(section_id, []).append({
                "category_id": cid,
                "category_name": meta.category_name,
                "role": role,
            })
    return consumption
```

Then update `PackageAssembler.__init__`:

```python
from market_research.registry import get_mr_consumption_map, MR_CATEGORY_REGISTRY

if context.research_mode == "market_research":
    self.consumption_map = get_mr_consumption_map()
    self.registry = MR_CATEGORY_REGISTRY
else:
    self.consumption_map = get_consumption_map()
    self.registry = CATEGORY_REGISTRY
```

Also add mode metadata:

```python
"metadata": {
    "research_mode": self.context.research_mode,
    ...
}
```

### 13. `output/markdown_formatter.py` — Mode-Aware Report Framing

The current formatter assumes an evidence package. Keep the structure but branch the title and summary framing.

Example adjustment:

```python
title = (
    f"# Innovera Market Research Report: {context.venture_name}"
    if context.research_mode == "market_research"
    else f"# Innovera Evidence Package: {context.venture_name}"
)
sections.append(title)
```

For market research mode:
- Keep `Executive Summary`
- Rename `Evidence by Category` to `Market Research by Category`
- Keep `Context Signals`
- Keep `Gap Inventory`

Do not invent a totally different report format. The point is compatibility with the existing output viewer and download flow.

## Frontend Changes

### 14. `frontend/src/components/InputForm.jsx` — Add Research Mode Selector

The current form has one fixed category list. Add a top-level selector and swap labels/category lists based on mode.

Add:

```javascript
const DEMAND_VALIDATION_PHASES = { ...existing CATEGORY_PHASES... };

const MARKET_RESEARCH_PHASES = {
  'Phase 1: Foundation': [
    { id: 'MR-01', name: 'Market Definition & Sizing' },
    { id: 'MR-04', name: 'Trends & Growth Quality' },
    { id: 'MR-06', name: 'Competition & Channels' },
    { id: 'MR-09', name: 'Regulation & Platform Shifts' },
  ],
  'Phase 2: Structural': [
    { id: 'MR-02', name: 'SAM / SOM / Reachability' },
    { id: 'MR-03', name: 'Segments & Concentration' },
    { id: 'MR-05', name: 'Value Chain & Whitespace' },
  ],
  'Phase 3: Commercial': [
    { id: 'MR-07', name: 'Buying Process, Budget & Pricing' },
    { id: 'MR-08', name: 'Adoption & Expansion Dynamics' },
    { id: 'MR-10', name: 'Barriers, Saturation & Ecosystem Power' },
  ],
};
```

Add state:

```javascript
const [researchMode, setResearchMode] = useState('demand_validation');
const categoryPhases =
  researchMode === 'market_research'
    ? MARKET_RESEARCH_PHASES
    : DEMAND_VALIDATION_PHASES;
const allCategoryIds = Object.values(categoryPhases).flat().map((c) => c.id);
```

Reset selected categories when the mode changes:

```javascript
useEffect(() => {
  setSelectedCategories(new Set(allCategoryIds));
}, [researchMode]);
```

Render a radio group near the top:

```jsx
<section className="space-y-3">
  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
    Research Mode
  </label>
  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
    <label className="border rounded-lg p-4 cursor-pointer ...">
      <input
        type="radio"
        name="research_mode"
        checked={researchMode === 'demand_validation'}
        onChange={() => setResearchMode('demand_validation')}
      />
      <div>
        <div className="font-medium">Demand Validation</div>
        <div className="text-sm text-slate-500">Test a specific venture or thesis.</div>
      </div>
    </label>
    <label className="border rounded-lg p-4 cursor-pointer ...">
      <input
        type="radio"
        name="research_mode"
        checked={researchMode === 'market_research'}
        onChange={() => setResearchMode('market_research')}
      />
      <div>
        <div className="font-medium">Market Research</div>
        <div className="text-sm text-slate-500">Map a market, structure, economics, and GTM dynamics.</div>
      </div>
    </label>
  </div>
</section>
```

Update copy dynamically:
- `Document Content` helper text should mention either venture documents or market/topic briefing.
- `Strategic Question` can stay, but for market research the placeholder should be more like: `e.g., What does the U.S. remote patient monitoring market look like structurally, commercially, and competitively?`
- `Success Criteria` remains useful and should not be removed.

Include `research_mode` in the submit payload:

```javascript
await onSubmit({
  research_mode: researchMode,
  document_text: documentText,
  ...
});
```

### 15. `frontend/src/components/ProgressPanel.jsx` — Add MR Phase Mappings

Replace the fixed phase constants with per-mode maps.

```javascript
const CATEGORY_PHASES_BY_MODE = {
  demand_validation: {
    FOUNDATION: ['EC-01', 'EC-02', 'EC-05', 'EC-06', 'EC-10'],
    COMPETITOR_DEPENDENT: ['EC-03', 'EC-04', 'EC-11'],
    SYNTHESIS: ['EC-07', 'EC-08', 'EC-09', 'EC-12', 'EC-13'],
  },
  market_research: {
    FOUNDATION: ['MR-01', 'MR-04', 'MR-06', 'MR-09'],
    STRUCTURAL: ['MR-02', 'MR-03', 'MR-05'],
    COMMERCIAL: ['MR-07', 'MR-08', 'MR-10'],
  },
};

const PHASE_LABELS_BY_MODE = {
  demand_validation: {
    FOUNDATION: 'Phase 1: Foundation',
    COMPETITOR_DEPENDENT: 'Phase 2: Competitor-Dependent',
    SYNTHESIS: 'Phase 3: Synthesis',
  },
  market_research: {
    FOUNDATION: 'Phase 1: Foundation',
    STRUCTURAL: 'Phase 2: Structural',
    COMMERCIAL: 'Phase 3: Commercial',
  },
};
```

The frontend can derive mode from the category IDs present in `run.categories` or from `run.contextInfo` if you include `research_mode` in the `context_ready` event.

### 16. `frontend/src/components/CategoryCard.jsx` — Add MR Category Names

Extend the `CATEGORY_NAMES` mapping:

```javascript
const CATEGORY_NAMES = {
  ...existingEcNames,
  'MR-01': 'Market Definition & Sizing',
  'MR-02': 'SAM / SOM / Reachability',
  'MR-03': 'Segments & Concentration',
  'MR-04': 'Trends & Growth Quality',
  'MR-05': 'Value Chain & Whitespace',
  'MR-06': 'Competition & Channels',
  'MR-07': 'Buying Process, Budget & Pricing',
  'MR-08': 'Adoption & Expansion Dynamics',
  'MR-09': 'Regulation & Platform Shifts',
  'MR-10': 'Barriers, Saturation & Ecosystem Power',
};
```

No other card behavior needs to change.

### 17. `frontend/src/App.jsx` and `useResearchRun.js`

No structural changes are required in `App.jsx`. It simply passes form data to `run.startRun(formData)`.

`useResearchRun.js` can remain mostly unchanged. The only recommended enhancement is to make phase-name display mode-aware if you want prettier log messages:

```javascript
const PHASE_NAMES = {
  FOUNDATION: 'Phase 1: Foundation',
  COMPETITOR_DEPENDENT: 'Phase 2: Competitor-Dependent',
  SYNTHESIS: 'Phase 3: Synthesis',
  STRUCTURAL: 'Phase 2: Structural',
  COMMERCIAL: 'Phase 3: Commercial',
};
```

## Build Order

### Step 1: Backend contract changes
1. Add `research_mode` to `ResearchRequest` in `api/models.py`.
2. Extend `ContextSignals` with MR helper fields and `research_mode`.
3. Add market-research prompts to `context_extraction/prompts.py`.
4. Make `ContextExtractor.extract()` mode-aware.
5. Test: start-up still imports cleanly; no breakage to the current demand-validation route path.

### Step 2: Market research category framework
1. Create `market_research/registry.py`.
2. Create `market_research/base.py`.
3. Create `mr01` through `mr10` implementation files.
4. Add `market_research/__init__.py`.
5. Test: import each MR category class in a Python shell or a small smoke test.

### Step 3: Orchestration
1. Add `get_mr_execution_plan()` to `orchestrator/phases.py`.
2. Make `ResearchRunner` mode-aware.
3. Add MR Phase 1 extraction hook to propagate market terms and competitor names.
4. Make retry logic aware of MR categories.
5. Test: run a mocked MR request through the orchestrator and verify phase ordering.

### Step 4: API route plumbing
1. Pass `research_mode` from `/api/research/start` into extractor and runner.
2. Persist `research_mode` into `active_runs` and `run_meta.json`.
3. Update status/name lookup to work for MR categories.
4. Test: `POST /api/research/start` with `research_mode="market_research"` should create a run and stream phase/category events.

### Step 5: Output packaging
1. Add MR consumption map support in the assembler.
2. Make markdown formatter mode-aware.
3. Ensure raw reports save as `MR-XX_<slug>.md`.
4. Test: completed MR run produces YAML, Markdown, and per-category raw reports.

### Step 6: Frontend mode support
1. Add the mode selector to `InputForm.jsx`.
2. Add MR category lists to `InputForm.jsx`.
3. Update `ProgressPanel.jsx` and `CategoryCard.jsx` with MR mappings.
4. Optionally add `STRUCTURAL` and `COMMERCIAL` labels to `useResearchRun.js`.
5. Test: form switches between category families correctly, and the submitted payload includes `research_mode`.

### Step 7: End-to-end validation
1. Run one demand-validation request and verify nothing regressed.
2. Run one market-research request and verify:
   - the run starts successfully
   - MR phases display correctly
   - MR categories stream progress
   - output files are generated
   - historical run metadata includes `research_mode`

## Success Criteria

- The user can choose between `demand_validation` and `market_research` from the existing input form.
- Demand Validation behavior remains unchanged when the default mode is used.
- Market Research runs 10 new MR categories mapped from the master input table.
- The MR pipeline uses the same API route, WebSocket progress system, output packaging, and frontend shell.
- Market Research queries reflect the 130-input master table with one GPT Researcher run per top-level category.
- MR phases execute in the new 3-phase sequence: Foundation → Structural → Commercial.
- MR Phase 2 and Phase 3 categories can consume extracted market terms and competitor names from earlier phases.
- Outputs are saved in the existing `output_packages/{run_id}/` structure with YAML, Markdown, and raw category reports.
- The history system and output endpoints continue to work for both modes.

## Notes and Constraints

- Do not rewrite or remove the existing `evidence_categories/` pipeline.
- Do not introduce a second API route just for market research; use `research_mode` branching.
- Do not create a separate frontend app or separate run-history path.
- Prefer additive changes and shared abstractions over copy-pasting the demand-validation pipeline.
- Keep the input experience aligned across both modes: same form shell, same core fields, different category family and explanatory copy.
- All new category implementations should stay in `market_research/`, not `evidence_categories/`, to keep the two pipelines clearly separated.

## Testing Notes

Use a simple market-oriented input document for the first smoke test, for example:

```md
# Market Research Brief

We want to understand the U.S. remote patient monitoring market.

Focus areas:
- market size and definition
- segmentation by buyer and care setting
- competitive landscape
- regulation and reimbursement
- buying process in health systems
- market-entry barriers
```

Suggested request body:

```json
{
  "research_mode": "market_research",
  "document_text": "We want to understand the U.S. remote patient monitoring market...",
  "additional_context": "Focus on provider-side demand and reimbursement-backed adoption.",
  "core_question": "What does the U.S. remote patient monitoring market look like structurally, commercially, and competitively?",
  "success_criteria": [
    "Market definition is defensible",
    "Top segments and channels are identified",
    "Key barriers and regulatory constraints are mapped"
  ],
  "venture_name": "U.S. Remote Patient Monitoring Market",
  "categories_to_run": [],
  "max_concurrent": 2
}
```

This spec is complete enough for Claude to implement the new pipeline end-to-end without changing the current demand-validation behavior.