# Innovera Research — Competitive Table Feature Spec

## Purpose

This brief defines the **Competitive Table**: a shared, structured competitor matrix that serves as the single source of truth for all competitive data across both Market Research (MR) and the future Competitor Analysis (CA) chapter. The table has a dynamic competitor axis and a dynamic attribute axis, both determined at runtime based on venture context.

This module should be implemented before any CA category work. It also modifies the MR pipeline to consume the table rather than discovering competitors independently.

## Current Problem

### Fragmented Competitor Data

Today, competitor identification happens in multiple places:

- `MR-06a` (Competitor Identification) runs deep research to discover competitors and extract names from bold-text patterns.
- `MR-06b` (Competitive Intelligence) researches sentiment, partnerships, litigation, and acquisitions for those competitors.
- `EC-02` (Competitor Landscape) does its own competitor discovery for the demand-validation pipeline.
- Context extraction pulls `named_competitors` from the venture brief.

Each of these discovers competitors independently. There is no canonical competitor roster. The competitor list produced by MR-06a is extracted via regex from unstructured markdown and injected into later phases, but the data is lossy and unstructured.

### No Structured Competitive Data

Current `parse_report()` implementations across most categories return only `{"raw_report_text": raw_report}`. Competitor names are extracted via regex heuristics. There is no structured representation of competitive attributes, pricing, positioning, market share, or other variables. This makes cross-competitor comparison impossible at the data layer.

### Static Analytical Framework

The current competitive queries use a fixed set of questions regardless of the venture. A medical device substrate manufacturer faces a fundamentally different competitive landscape than a B2B SaaS startup. The questions asked, the attributes analyzed, and even the number of relevant competitors should vary based on context.

## Product Goal

Build a **Competitive Table** that:

1. Identifies the right set of competitors for this specific venture and market (dynamic X axis).
2. Determines the most relevant competitive attributes for this specific industry and context (dynamic Y axis).
3. Populates the table with researched data for each competitor across each attribute.
4. Includes the venture itself as a column for direct comparison.
5. Persists as a first-class run artifact alongside YAML and Markdown outputs.
6. Is consumed by both MR categories and future CA categories as structured input.
7. Renders in the frontend as an interactive competitive matrix.

## Design Principles

### Dynamic Cardinality

The number of competitors must be determined at runtime. Examples:

- **Airplane manufacturing**: 3–5 competitors (Boeing, Airbus, Bombardier, Embraer, COMAC).
- **B2B SaaS CRM**: 15–25 competitors across tiers (Salesforce, HubSpot, Pipedrive, etc.).
- **Medical device substrates**: 10–20 competitors across OEMs, CDMOs, and component suppliers.
- **Craft beer**: Potentially 30+ regional and national competitors, but analysis should focus on the 15–20 most strategically relevant.

The system should target a range, not a fixed number. A reasonable default range is **8–25 competitors**, but the LLM should justify the actual count based on market structure.

### Dynamic Attribute Selection

The attributes (Y axis) must also be determined at runtime. Examples:

For a **SaaS startup**, relevant attributes might include:
- Pricing model, ACV range, target ICP, GTM motion, funding raised, employee count, key integrations, NPS/G2 rating, churn rate, primary use case, competitive positioning.

For a **medical device substrate manufacturer** like LGIT, relevant attributes might include:
- Technology type, manufacturing capability, regulatory certifications, target applications, production scale, key OEM relationships, patent portfolio, geographic presence, revenue estimate, entry strategy.

The LLM should select 15–30 attributes organized into logical groups. Some attributes are near-universal (name, description, year founded, HQ location, revenue estimate, employee count). Others are industry-specific and must be inferred from the venture context.

### Venture as a Column

The venture itself occupies a column in the table. Its data is populated primarily from the venture brief and context signals, not from web research. This enables direct side-by-side comparison: "How does our substrate capability compare to Linxens? To Cirtec?"

### Tiered Research Depth

Not all competitors deserve equal research investment. The table should support tiered depth:

- **Tier 1 (Deep)**: Top 3–5 direct competitors. Full deep research per competitor.
- **Tier 2 (Standard)**: Next 5–10 relevant competitors. Batched research (3–5 per query).
- **Tier 3 (Light)**: Remaining competitors. Profiled from existing research context or a single summary query.

This manages cost and time while ensuring the most important competitors get adequate coverage.

## Data Model

### Core Schema

Define the competitive table data model in a new module:

- `innovera-research/competitive_table/models.py`

Required Pydantic models:

```python
class CompetitiveAttribute:
    attribute_id: str          # e.g., "pricing_model", "gtm_motion"
    name: str                  # Human-readable name
    description: str           # What this attribute measures
    group: str                 # Logical grouping: "profile", "commercial", "strategic", "technical"
    data_type: str             # "text", "numeric", "rating", "list", "boolean"
    priority: str              # "required", "important", "optional"

class CompetitorEntry:
    competitor_id: str         # Slugified unique ID
    name: str                  # Display name
    tier: int                  # 1, 2, or 3
    description: str           # One-paragraph summary
    competitor_type: str       # "direct", "substitute", "adjacent", "emerging", "incumbent"
    attributes: dict[str, CellValue]  # attribute_id -> value
    sources: list[str]         # URLs supporting this competitor's data
    confidence: float          # 0.0–1.0 overall data confidence
    last_researched: str       # ISO timestamp

class CellValue:
    value: str | float | list[str] | bool | None
    confidence: str            # "high", "medium", "low", "unknown"
    source_url: str | None     # Primary source for this specific cell
    notes: str                 # Caveats, qualifications

class CompetitiveTable:
    table_id: str              # Usually matches run_id
    venture_name: str
    industry: str
    geography: str
    generated_at: str
    attributes: list[CompetitiveAttribute]   # The Y axis
    competitors: list[CompetitorEntry]        # The X axis (excluding venture)
    venture_entry: CompetitorEntry            # The venture's own column
    attribute_groups: list[AttributeGroup]    # Logical groupings for rendering
    metadata: TableMetadata

class AttributeGroup:
    group_id: str
    name: str                  # e.g., "Company Profile", "Commercial", "Strategic Positioning"
    attribute_ids: list[str]

class TableMetadata:
    competitor_count: int
    attribute_count: int
    tier1_count: int
    tier2_count: int
    tier3_count: int
    coverage_percent: float    # % of cells that have non-null values
    total_sources: int
    research_time_seconds: float
    rationale: str             # LLM's explanation for competitor/attribute selection
```

## Construction Pipeline

The Competitive Table is built in a multi-step pipeline that runs as a new phase in the orchestrator, BEFORE existing MR or CA category phases.

### Step 1: Schema Generation (LLM call, no web research)

**Input**: `ContextSignals` (venture brief, industry, problem summary, named competitors, solution category)

**Process**: Call the context extraction LLM (via OpenRouter) with a specialized prompt that asks it to:

1. Determine how many competitors to target and why (considering market structure, concentration, fragmentation).
2. Select 15–30 competitive attributes organized into logical groups, tailored to this specific industry and venture context.
3. Classify each attribute by data type, priority, and group.
4. Identify any competitors already named in the venture brief and assign them a tier.

**Output**: A `CompetitiveTableSchema` containing the attribute list, attribute groups, target competitor count range, and any pre-seeded competitors.

**Module**: `innovera-research/competitive_table/schema_generator.py`

**Implementation Notes**:
- Use the same OpenRouter client and model as context extraction (`CONTEXT_LLM_MODEL`).
- The prompt should include the full `ContextSignals` and examples of good attribute selections for different industries.
- The prompt should explicitly instruct the LLM to consider the venture's specific competitive dynamics (e.g., "This is a component manufacturer entering a new market, not an end-product company — competitive attributes should reflect supply chain positioning, certification status, and manufacturing capability, not consumer-facing features").
- Return structured JSON matching the schema.

### Step 2: Competitor Discovery (GPT Researcher deep research)

**Input**: `ContextSignals` + `CompetitiveTableSchema` (attribute list, target count)

**Process**: Run a single GPT Researcher deep research mission to discover and profile competitors. The query should:

1. Search for competitors in this specific market and geography.
2. Identify direct competitors, substitutes, adjacent players, emerging entrants, and legacy incumbents.
3. For each competitor found, provide: name, type, one-paragraph description, and tier recommendation.
4. Target the count range specified by the schema.
5. Include competitors already named in the venture brief.

**Output**: A list of `CompetitorEntry` objects with names, types, tiers, descriptions, and sources — but attribute values not yet populated.

**Module**: `innovera-research/competitive_table/competitor_discovery.py`

**Implementation Notes**:
- This is a single deep research call using `GPTResearcher`, similar to how MR-06a works today.
- The query should be carefully constructed to target the right competitor types for this industry.
- Apply the Tavily compatibility patch (already in place via `evidence_categories/base.py`).
- Save a checkpoint after discovery completes (reuse the existing checkpoint infrastructure from `orchestrator/checkpoints.py`).

### Step 3: Table Population (GPT Researcher batched research)

**Input**: Competitor list + attribute schema

**Process**: Research and populate attribute values for each competitor. Use tiered batching:

- **Tier 1**: One deep research call per competitor. The query should target all attributes for that specific competitor.
- **Tier 2**: Batch 3–5 competitors per research call. The query should cover key attributes for the batch.
- **Tier 3**: One summary research call for all tier-3 competitors, focusing on the most critical attributes only.

After each research call completes, parse the results into structured `CellValue` entries for each attribute. This is where **parse depth** matters — the system must extract specific data points, not just raw text.

**Output**: Fully populated `CompetitorEntry` objects with attribute values, confidence scores, and source URLs per cell.

**Module**: `innovera-research/competitive_table/table_populator.py`

**Implementation Notes**:
- Each research call uses `GPTResearcher` in deep mode.
- Parsing structured data from GPT Researcher reports requires a post-processing LLM call. After each raw report is generated, call the context extraction LLM to extract structured attribute values from the report text. This is the "parse depth increase" — using an LLM to parse reports into structured data rather than relying on regex.
- Checkpoint after each competitor or batch completes.
- Respect `MAX_CONCURRENT_CATEGORIES` for parallel execution of tier-1 competitor research.
- The venture's own column is populated from the venture brief and `ContextSignals`, not from web research. Use an LLM call to map venture brief content to the attribute schema.

### Step 4: Venture Column Population (LLM call, no web research)

**Input**: Venture brief text + `ContextSignals` + attribute schema

**Process**: Call the LLM to populate the venture's own column by mapping information from the venture brief to each attribute. For attributes not covered by the brief, mark the cell as `"unknown"` with a note explaining the gap.

**Output**: A populated `CompetitorEntry` for the venture.

**Module**: Can live in `table_populator.py` as a separate method.

### Step 5: Table Validation and Summary (LLM call)

**Input**: The fully populated `CompetitiveTable`

**Process**: Call the LLM to:

1. Verify completeness and flag suspicious data.
2. Calculate coverage statistics.
3. Generate a narrative summary of the competitive landscape based on the table data.
4. Identify the venture's top 3 strengths and top 3 weaknesses relative to the competition.
5. Flag the most dangerous competitors and explain why.

**Output**: Updated `TableMetadata` with coverage stats and a `table_summary` narrative.

**Module**: `innovera-research/competitive_table/table_validator.py`

## Universal Parse Depth Increase

### Problem

Most `parse_report()` implementations currently return only `{"raw_report_text": raw_report}`. This makes downstream consumption and cross-category analysis impossible at the structured data layer.

### Solution

Add an LLM-based structured extraction step that runs after every category's `write_report()` completes. This is a universal enhancement that applies to all existing categories (EC, MR) and future CA categories.

### Implementation

Add a new method to `BaseCategory` in `innovera-research/evidence_categories/base.py`:

```python
async def extract_structured_findings(self, raw_report: str) -> dict:
    """Use LLM to extract structured findings from the raw report."""
```

This method should:

1. Call the context extraction LLM (via OpenRouter) with a prompt that includes the raw report and asks for structured extraction.
2. The prompt should be category-aware — each category defines what structured fields to extract.
3. Return a structured dict that replaces or enriches the current `parse_report()` output.

Each category should define an `extraction_schema` property that specifies what structured fields the LLM should extract. For example:

- MR-01a might extract: `market_terms`, `tam_estimate`, `growth_rate`, `key_sources`.
- MR-06a might extract: `competitors` (list of objects with name, type, positioning, pricing).
- MR-07 might extract: `sales_cycle_days`, `dmu_size`, `pricing_models`, `churn_rate`.

The extraction schema is defined per-category but the extraction mechanism is universal.

### Where This Fits in Execution

In `_execute_once()` in `base.py`, after `write_report()` and before `parse_report()`:

1. Call `extract_structured_findings(raw_report)` to get LLM-parsed structured data.
2. Merge the LLM-extracted findings with any regex-based `parse_report()` results.
3. Store the enriched structured findings in the checkpoint and final result.

### Backward Compatibility

- Keep existing `parse_report()` methods as-is. They continue to work.
- The LLM extraction is additive — it enriches, not replaces.
- If the LLM extraction fails (timeout, API error), fall back to the existing `parse_report()` result.
- The extraction LLM call should be fast (not deep research, just parsing) — use `CONTEXT_LLM_MODEL` with a tight token budget.

## Integration With Existing Pipeline

### Orchestrator Changes

Update `innovera-research/orchestrator/runner.py` to support a new pre-phase step:

1. After context extraction and before category execution, check if the research mode requires a Competitive Table.
2. If yes, run the table construction pipeline (Steps 1–5 above).
3. Store the completed table on the `ResearchRunner` instance.
4. Inject table data into categories that need it (MR-06a, MR-06b, and future CA categories).

The table construction should be treated as a **Phase 0** that runs before `FOUNDATION`. It should:

- Emit progress events to the Activity Stream.
- Save checkpoints at each step.
- Respect timeout limits.
- Be resumable from checkpoints.

### MR Category Changes

Once the Competitive Table exists:

- **MR-06a** (Competitor Identification): Should receive the table's competitor list as input. Its query should validate and enrich the table data rather than discovering competitors from scratch. If the table already exists, MR-06a's role shifts from "discovery" to "validation and enrichment."
- **MR-06b** (Competitive Intelligence): Should receive the table's competitor list and focus its research on intelligence gaps not covered by the table (sentiment, litigation, acquisitions).
- **Other MR categories** that reference competitors (MR-02, MR-03, MR-05, MR-07, MR-08, MR-10): Should pull competitor names from the table instead of from `context.named_competitors`. This ensures consistency.

### Context Signals Enrichment

After the Competitive Table is built, update `ContextSignals` with:

- `named_competitors`: Full list from the table.
- Any new market terms discovered during competitor research.

This ensures downstream categories benefit from the table even if they don't directly consume it.

### How To Inject Table Data Into Categories

Add a new method to `MRBaseCategory` in `innovera-research/market_research/base.py`:

```python
def inject_competitive_table(self, table: CompetitiveTable):
    """Make the competitive table available to this category's query builder."""
    self.competitive_table = table
```

Categories that want to reference the table can then access `self.competitive_table` in their `build_query()` method to include competitor names, attribute summaries, or specific data points in their research prompts.

## Storage and Persistence

### File Format

Store the Competitive Table as JSON in the run output directory:

- `innovera-research/output_packages/<run_id>/competitive_table.json`

The JSON should be a serialized `CompetitiveTable` model.

### Checkpoint Integration

Save intermediate checkpoints during table construction:

- `innovera-research/output_packages/<run_id>/checkpoints/CT-schema.json` (after Step 1)
- `innovera-research/output_packages/<run_id>/checkpoints/CT-discovery.json` (after Step 2)
- `innovera-research/output_packages/<run_id>/checkpoints/CT-populate-<batch>.json` (after each population batch)
- `innovera-research/output_packages/<run_id>/checkpoints/CT-complete.json` (after Step 5)

Use the existing checkpoint infrastructure from `orchestrator/checkpoints.py`. The `category_id` for table checkpoints should use the `CT-` prefix.

### Output Package Integration

Update `innovera-research/output/package_assembler.py` to include the Competitive Table in the final output:

- Add a `competitive_table` section to the YAML package.
- Add a rendered Competitive Table section to the Markdown report.
- Store the raw JSON alongside YAML and Markdown outputs.

## API Changes

### New Endpoint

Add to `innovera-research/api/routes.py`:

```
GET /api/research/{run_id}/competitive-table
```

Returns the full `CompetitiveTable` as JSON. This endpoint should:

- Check in-memory active runs first.
- Fall back to disk (`competitive_table.json`).
- Return 404 if no table exists for this run.

### Status Endpoint Enhancement

Update `GET /api/research/{run_id}/status` to include:

- `competitive_table_status`: `"pending"` | `"building"` | `"complete"` | `"failed"` | `null`
- `competitive_table_progress`: Number of competitors populated vs total.

### Structured Output Enhancement

Update `GET /api/research/{run_id}/output/structured` to include:

- `competitive_table`: The full table data for frontend rendering.

## Frontend Rendering

### Competitive Table Component

Create `innovera-research/frontend/src/components/CompetitiveTable.jsx`.

This component should render the table as an interactive matrix:

- **Columns**: Competitors (including the venture, highlighted).
- **Rows**: Attributes, grouped by `AttributeGroup`.
- **Cells**: Show the value with confidence coloring (high=green, medium=yellow, low=red, unknown=gray).
- **Sorting**: Allow sorting by any attribute.
- **Filtering**: Allow filtering by competitor type, tier, or attribute group.
- **Sticky headers**: Competitor names should stick when scrolling vertically. Attribute names should stick when scrolling horizontally.
- **Hover**: Show cell notes, source URL, and confidence on hover.
- **Venture highlight**: The venture's column should be visually distinct (e.g., pinned left with a highlight color).

### Integration Into Report

The Competitive Table should appear as a dedicated section in the report output viewer:

- In the sidebar table of contents, add a "Competitive Landscape" entry.
- The table section should appear before individual MR category sections.
- Include the LLM-generated narrative summary above the table.
- Include the venture's strengths/weaknesses analysis below the table.

### Progress Panel Integration

During table construction, the Activity Stream should show:

- "Generating competitive framework for [industry]..."
- "Discovering competitors in [market]..."
- "Found [N] competitors across [tiers]..."
- "Researching [competitor name] (Tier 1, 1/5)..."
- "Populating competitive data for [batch]..."
- "Competitive table complete: [N] competitors, [M] attributes, [P]% coverage"

## Directory Structure

```
innovera-research/
├── competitive_table/
│   ├── __init__.py
│   ├── models.py              # Pydantic data models
│   ├── schema_generator.py    # Step 1: LLM-based schema generation
│   ├── competitor_discovery.py # Step 2: GPT Researcher competitor discovery
│   ├── table_populator.py     # Steps 3-4: Batched population + venture column
│   ├── table_validator.py     # Step 5: Validation and summary
│   └── prompts.py             # All prompts for table construction
```

## Prompts

### Schema Generation Prompt

The schema generation prompt must:

1. Receive the full `ContextSignals` as context.
2. Explain that the output will drive a competitive matrix.
3. Ask the LLM to consider: What makes competition meaningful in this specific market? What attributes would an analyst building a competitor comparison use?
4. Request a target competitor count range with justification.
5. Request 15–30 attributes organized into groups.
6. Include 2–3 worked examples showing different attribute sets for different industries (SaaS, hardware manufacturing, consumer goods) so the LLM understands the expected variety.
7. Return structured JSON.

### Competitor Discovery Prompt

The discovery query for GPT Researcher must:

1. Include the venture context (industry, geography, solution category, problem summary).
2. Include any known competitors from the venture brief.
3. Include the target competitor count range from the schema.
4. Request structured output: for each competitor, provide name, type, tier recommendation, and a one-paragraph description.
5. Explicitly search for: direct competitors, substitutes, adjacent players, emerging entrants, and legacy incumbents.
6. Include specific search terms derived from the context (e.g., "top companies in [industry]", "[solution] competitors", "[solution] alternatives").

### Population Prompt

For each Tier 1 competitor research call:

1. Focus the query on a single named competitor.
2. Include the full attribute list.
3. Ask for specific, sourced data points for each attribute.
4. Request the output as a structured list of attribute values with sources.

For Tier 2 batched calls:

1. Name 3–5 competitors per batch.
2. Include the most important attributes (required + important priority).
3. Ask for comparative data across the batch.

For Tier 3 summary calls:

1. Name all remaining competitors.
2. Focus on required attributes only.
3. Accept briefer, less-sourced responses.

### Structured Extraction Prompt (Universal Parse Depth)

For the universal parse depth increase, the extraction prompt must:

1. Receive the raw report text.
2. Receive the category's extraction schema (list of fields to extract with types).
3. Extract specific data points, metrics, named entities, and structured findings.
4. Return structured JSON matching the schema.
5. For each extracted field, include a confidence level and source reference if available.
6. If a field cannot be extracted from the report, return null rather than hallucinating.

## Progress Events

Add new websocket event types for table construction:

```json
{"type": "competitive_table_status", "status": "building", "step": "schema_generation"}
{"type": "competitive_table_status", "status": "building", "step": "competitor_discovery", "found": 18}
{"type": "competitive_table_status", "status": "building", "step": "population", "completed": 5, "total": 18}
{"type": "competitive_table_status", "status": "complete", "competitors": 18, "attributes": 22, "coverage": 0.87}
```

Update `innovera-research/api/progress_bridge.py` to support these events.

Update `innovera-research/frontend/src/hooks/useResearchRun.js` to handle these events and expose table construction status to the UI.

## Constraints

- Do not modify Python `site-packages`.
- The table construction must respect `CATEGORY_TIMEOUT_SECONDS` per research call.
- The table construction must be checkpoint-resumable using the existing checkpoint system.
- The table must work for both `market_research` and `demand_validation` modes (and the future `competitor_analysis` mode).
- LLM calls for schema generation, venture column population, and structured extraction should use `CONTEXT_LLM_MODEL` via OpenRouter (not GPT Researcher).
- Web research calls (competitor discovery and table population) should use `GPTResearcher` with the existing deep research configuration.
- The feature must degrade gracefully if table construction fails — existing MR categories should still function without the table using their current discovery logic.
- Do not break the existing MR or EC pipelines. Table injection should be additive.

## Build Order

### Step 1: Data Models

Create `innovera-research/competitive_table/models.py` with all Pydantic models. Validate that the schema supports the full range of competitive data needed.

### Step 2: Schema Generator

Implement `schema_generator.py`. Test with the LGIT venture brief to verify it produces a sensible attribute set and competitor count range for a medical device substrate manufacturer.

### Step 3: Competitor Discovery

Implement `competitor_discovery.py`. Wire it to use `GPTResearcher` with checkpointing. Test that it discovers a reasonable competitor set.

### Step 4: Table Populator

Implement `table_populator.py` with tiered batching. This is the most expensive step — ensure checkpointing works per-batch. Implement the venture column population.

### Step 5: Table Validator

Implement `table_validator.py`. Verify coverage stats and narrative generation.

### Step 6: Orchestrator Integration

Wire the table construction into `runner.py` as a Phase 0 step. Inject the table into MR categories. Ensure progress events flow to the frontend.

### Step 7: Universal Parse Depth

Add the LLM-based `extract_structured_findings()` to `BaseCategory`. Define extraction schemas for at least MR-01a, MR-01b, MR-06a, MR-06b, and MR-07 to start. Verify that structured extraction works without breaking existing functionality.

### Step 8: API and Storage

Add the competitive table API endpoint. Update the package assembler. Update the structured output endpoint.

### Step 9: Frontend Rendering

Build `CompetitiveTable.jsx`. Integrate into the report viewer. Add progress events to the Activity Stream.

### Step 10: End-to-End Validation

Run a full pipeline with the LGIT venture brief. Verify:
- Schema generation produces sensible attributes for medical device substrates.
- Competitor discovery finds the right competitors (Linxens, Cirtec, Flex, Jabil, etc.).
- Table population fills in meaningful data.
- MR categories receive and use the table data.
- The frontend renders the table correctly.
- Checkpointing and resume work for table construction.

## Files Most Likely To Change

### New Files

- `innovera-research/competitive_table/__init__.py`
- `innovera-research/competitive_table/models.py`
- `innovera-research/competitive_table/schema_generator.py`
- `innovera-research/competitive_table/competitor_discovery.py`
- `innovera-research/competitive_table/table_populator.py`
- `innovera-research/competitive_table/table_validator.py`
- `innovera-research/competitive_table/prompts.py`
- `innovera-research/frontend/src/components/CompetitiveTable.jsx`

### Modified Files

- `innovera-research/evidence_categories/base.py` (universal parse depth)
- `innovera-research/market_research/base.py` (table injection)
- `innovera-research/market_research/mr06a_competitor_identification.py` (consume table)
- `innovera-research/market_research/mr06b_competitive_intelligence.py` (consume table)
- `innovera-research/orchestrator/runner.py` (Phase 0 table construction)
- `innovera-research/orchestrator/phases.py` (table phase)
- `innovera-research/api/routes.py` (new endpoint)
- `innovera-research/api/progress_bridge.py` (table progress events)
- `innovera-research/api/models.py` (table status model)
- `innovera-research/output/package_assembler.py` (table in output)
- `innovera-research/output/markdown_formatter.py` (table rendering)
- `innovera-research/frontend/src/hooks/useResearchRun.js` (table events)
- `innovera-research/frontend/src/components/ProgressPanel.jsx` (table progress)
- `innovera-research/frontend/src/components/OutputViewer.jsx` (table section)

## Success Criteria

- [ ] The Competitive Table is dynamically generated based on venture context, not a static template.
- [ ] The competitor count varies by market (e.g., 5 for concentrated markets, 20+ for fragmented ones).
- [ ] The attribute set varies by industry and venture context.
- [ ] The venture appears as a highlighted column in the table for direct comparison.
- [ ] Tiered research depth ensures the most important competitors get the deepest coverage.
- [ ] MR categories consume the same competitor set as the table, eliminating divergence.
- [ ] The table persists as a JSON artifact in the run output directory.
- [ ] The table is accessible via API endpoint.
- [ ] The frontend renders the table as an interactive, sortable, filterable matrix.
- [ ] Table construction is checkpoint-resumable.
- [ ] The universal parse depth increase extracts structured findings from all category reports.
- [ ] Existing MR and EC pipelines continue to function if table construction fails.
- [ ] End-to-end test with the LGIT venture brief produces a credible competitive matrix.
