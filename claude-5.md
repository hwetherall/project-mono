# Innovera Research — Consultant Lens (Consultant Primer Phase)

## Purpose

This brief adds a **Consultant Primer** phase that runs once, early in the pipeline, to discover and deeply read consulting firm reports relevant to the venture's industry. The extracted insights become a shared knowledge base injected into every subsequent research category, dramatically improving source quality and research efficiency.

The core principle: **read 3–7 tier-1 consulting reports in depth once, then use that context everywhere** — rather than grinding through hundreds of random web sources per category.

## Current Problem

### No Source Quality Bias

Today, every evidence category builds a query and hands it to GPT Researcher, which uses Tavily to search the open web. The search treats all sources equally — a random blog post ranks alongside a McKinsey industry report if the keywords match. There is no mechanism to prefer high-authority consulting sources.

### Redundant Source Discovery

Each category runs its own independent web search. If McKinsey published a report on the venture's industry, it might be discovered by EC-01 (market sizing) but missed by EC-05 (problem prevalence) or MR-04 (trends), even though the same report contains valuable data for all of them. There is no shared source pool.

### Missing Consultant Coverage Signal

There is currently no way to know whether the research found any consulting-firm-grade analysis at all. A run could complete with 200 web sources, none of which are from reputable consultancies, and the user would have no signal that this gap exists.

## Product Goal

Build a **Consultant Primer** phase that:

1. Searches a curated list of consulting firm domains for reports relevant to the venture's industry, problem, and geography.
2. Fetches and deeply reads the full content of discovered consultant pages.
3. Extracts structured key findings (market sizes, trends, competitive dynamics, etc.) from each report.
4. Stores the extracted context as a shared `ConsultantContext` artifact available to all subsequent phases.
5. Injects this consultant knowledge into every category's GPT Researcher run as pre-loaded context so the LLM can cite and build upon it.
6. Flags which categories received consultant coverage and which did not — surfacing this as a quality signal in the output.

## Design

### Phase Position in Pipeline

```
User Input
    │
    ▼
Context Extraction  (existing — unchanged)
    │
    ▼
┌──────────────────────────────────────┐
│  NEW: Consultant Primer Phase        │  ← runs here, before everything else
│  Search consultant domains → fetch   │
│  → extract → store ConsultantContext  │
└──────────────────────────────────────┘
    │
    ▼
Competitive Table   (existing Phase 0 — unchanged, but receives consultant context)
    │
    ▼
Category Phases     (existing Phases 1–3 — each receives consultant context)
    │
    ▼
Package Assembly    (existing — extended with consultant coverage summary)
```

The Consultant Primer runs **after** context extraction (it needs `ContextSignals` to know what to search for) and **before** the competitive table and all category phases (they all consume its output).

### Consultant Domain Tiers

Organize consultant domains into tiers for search prioritization:

**Tier 1 — Global Strategy Firms (highest authority):**
- `mckinsey.com`
- `bcg.com`, `bcgperspectives.com`
- `bain.com`

**Tier 2 — Big Four + Major Consultancies:**
- `pwc.com`
- `ey.com`
- `deloitte.com`
- `kpmg.com`
- `accenture.com`
- `oliverwyman.com`
- `rolandberger.com`
- `strategyand.pwc.com`
- `lek.com`

**Tier 3 — Industry Research & Analyst Firms:**
- `gartner.com`
- `forrester.com`
- `idc.com`
- `woodmac.com` (Wood Mackenzie)
- `ihsmarkit.com`, `spglobal.com`
- `frost.com` (Frost & Sullivan)
- `mordorintelligence.com`
- `grandviewresearch.com`
- `marketsandmarkets.com`
- `verifiedmarketresearch.com`

**Tier 4 — Sector-Specific (optional, context-dependent):**
- Energy: `woodmac.com`, `lazard.com`, `bnef.com` (Bloomberg NEF)
- Healthcare: `evaluate.com`, `iqvia.com`
- Tech: `cb-insights.com`, `pitchbook.com`, `crunchbase.com`

The system should search Tier 1 and Tier 2 domains always. Tier 3 domains should be included when the topic warrants analyst coverage. Tier 4 should be selected based on `ContextSignals.industry_vertical`.

### Search Strategy

The primer should construct **3–5 targeted Tavily searches** using `include_domains` to restrict results to consultant sites:

1. **Industry overview query**: `"{industry_vertical} market overview report {geography}"` restricted to all Tier 1+2 domains.
2. **Market sizing query**: `"{industry_vertical} market size TAM {geography} {current_year}"` restricted to all Tier 1+2+3 domains.
3. **Trends/outlook query**: `"{industry_vertical} trends outlook forecast {geography}"` restricted to all Tier 1+2 domains.
4. **Problem-specific query**: `"{problem_keywords} {solution_category} analysis"` restricted to all Tier 1+2 domains.
5. **Competitive dynamics query** (if named_competitors exist): `"{industry_vertical} competitive landscape {named_competitors[:3]}"` restricted to all Tier 1+2+3 domains.

Each search should request `max_results=10` and `include_raw_content=true` from Tavily to get full page text where available.

Use `search_depth="advanced"` for richer results.

### Content Extraction

For each result returned by Tavily:

1. Use the `raw_content` field if Tavily provides it (it often does for `include_raw_content=true`).
2. If `raw_content` is absent, use the `content` snippet as-is.
3. Pass the full text through an LLM extraction step that produces structured findings:
   - **Source metadata**: title, URL, publication date, firm name.
   - **Key facts**: A list of discrete, citable facts extracted from the report (e.g., "The US energy storage market was valued at $X.XB in 2024").
   - **Market data points**: Any TAM/SAM/CAGR/market-size numbers with the year and scope.
   - **Trend signals**: Named trends or forecasts.
   - **Competitive mentions**: Any competitor names or competitive dynamics described.
   - **Regulatory/policy mentions**: Named regulations, mandates, or policy drivers.

This extraction should use the same `CONTEXT_LLM_MODEL` (Claude Sonnet) via OpenRouter, consistent with how `extract_structured_findings` works elsewhere.

### Data Model

Create `consultant_primer/models.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional

class ConsultantSource(BaseModel):
    """A single page/report from a consulting firm."""
    url: str
    title: str
    firm_name: str
    tier: int = Field(description="1=MBB, 2=Big4+, 3=Analyst, 4=Sector-specific")
    publication_date: Optional[str] = None
    raw_content_length: int = 0
    key_facts: list[str] = Field(default_factory=list)
    market_data_points: list[str] = Field(default_factory=list)
    trend_signals: list[str] = Field(default_factory=list)
    competitive_mentions: list[str] = Field(default_factory=list)
    regulatory_mentions: list[str] = Field(default_factory=list)
    relevance_score: float = Field(default=0.0, description="0-1 LLM-assessed relevance to the venture")

class ConsultantContext(BaseModel):
    """Aggregated consultant knowledge for a research run."""
    sources: list[ConsultantSource] = Field(default_factory=list)
    total_sources_found: int = 0
    total_sources_extracted: int = 0
    tier1_count: int = 0
    tier2_count: int = 0
    tier3_count: int = 0
    search_queries_used: list[str] = Field(default_factory=list)
    execution_time_seconds: float = 0.0

    @property
    def has_consultant_coverage(self) -> bool:
        return len(self.sources) > 0

    @property
    def coverage_summary(self) -> str:
        if not self.sources:
            return "No consultant sources found"
        firms = sorted(set(s.firm_name for s in self.sources))
        return f"{len(self.sources)} sources from {', '.join(firms)}"

    def get_context_text(self, max_chars: int = 50000) -> str:
        """Build a single text block of consultant findings for injection into GPT Researcher."""
        parts = ["## Consultant & Analyst Report Findings\n"]
        parts.append("The following facts and insights were extracted from consulting firm and industry analyst reports. "
                      "Use these as high-authority reference points. Cite the source when referencing these findings.\n")
        
        char_count = sum(len(p) for p in parts)
        for source in sorted(self.sources, key=lambda s: s.tier):
            source_header = f"\n### {source.firm_name} — {source.title}\n"
            source_header += f"Source: {source.url}\n"
            
            findings = []
            for fact in source.key_facts:
                findings.append(f"- {fact}")
            for dp in source.market_data_points:
                findings.append(f"- [Market Data] {dp}")
            for trend in source.trend_signals:
                findings.append(f"- [Trend] {trend}")
            for comp in source.competitive_mentions:
                findings.append(f"- [Competitive] {comp}")
            for reg in source.regulatory_mentions:
                findings.append(f"- [Regulatory] {reg}")
            
            block = source_header + "\n".join(findings) + "\n"
            if char_count + len(block) > max_chars:
                break
            parts.append(block)
            char_count += len(block)
        
        return "\n".join(parts)
```

### Injection into Categories

The key integration point is `BaseCategory._execute_once()` in `evidence_categories/base.py`. Currently it creates a `GPTResearcher` and calls `conduct_research()` + `write_report()`.

**Modification**: Add `consultant_context: Optional[ConsultantContext]` to `BaseCategory.__init__()`. When present, prepend the consultant context text to the query or inject it as pre-loaded context.

GPT Researcher supports a `context` parameter in its constructor — a list of strings that it treats as pre-gathered research context. The consultant findings should be injected here:

```python
# In BaseCategory._execute_once(), before creating the researcher:
researcher_kwargs = {
    "query": query,
    "report_type": report_type,
    "config_path": config_path,
}

# Inject consultant context if available
if self.consultant_context and self.consultant_context.has_consultant_coverage:
    consultant_text = self.consultant_context.get_context_text(max_chars=40000)
    researcher_kwargs["context"] = [consultant_text]

researcher = GPTResearcher(**researcher_kwargs)
```

When GPT Researcher receives pre-loaded `context`, it incorporates that text into its research alongside whatever it finds from its own web searches. This means the consultant findings are available to the LLM during report writing without replacing the broad web search.

### Runner Integration

In `orchestrator/runner.py`, the `ResearchRunner` needs:

1. A new `consultant_context: Optional[ConsultantContext]` field.
2. A new method or phase call that runs the primer before `_build_competitive_table()`.
3. The consultant context passed to each category instance during `_run_category()`.

```python
# In ResearchRunner.run_all(), insert before competitive table:
async def run_all(self) -> dict[str, CategoryResult]:
    # ... existing plan selection ...

    # NEW: Run Consultant Primer
    await self._run_consultant_primer()

    # Phase 0: Build Competitive Table (existing)
    await self._build_competitive_table()

    # ... existing phase loop ...
```

In `_run_category()`, pass the consultant context to the category:

```python
category = category_class(
    context=self.context,
    venture_docs_dir=self.venture_docs_dir,
    run_id=self.run_id,
    research_mode=self.research_mode,
    consultant_context=self.consultant_context,  # NEW
)
```

### Consultant Coverage Flagging

Each `CategoryResult` should gain an optional field:

```python
consultant_sources_used: int = 0  # How many consultant sources were in the pre-loaded context
```

The output formatters should include a consultant coverage summary:

- In the markdown report, add a section after "Context Signals":
  ```
  ## Consultant & Analyst Coverage
  
  **Sources found:** 7 (McKinsey: 2, BCG: 1, Deloitte: 2, Wood Mackenzie: 2)
  **Tier 1 (MBB):** 3 sources
  **Tier 2 (Big Four+):** 2 sources
  **Tier 3 (Analyst):** 2 sources
  
  Key findings pre-loaded into all categories from these sources.
  Categories with NO consultant-sourced data: EC-10 (Voice of Market), EC-11 (Hiring Trends)
  ```

- In the YAML package, add a `consultant_coverage` key under `research_package`.

### Checkpoint Support

Save a checkpoint after the consultant primer completes:

- Checkpoint ID: `CONSULTANT-PRIMER`
- Stage: `"completed"`
- Payload: The full `ConsultantContext` serialized as JSON.

On resume, if the consultant primer checkpoint exists and is valid, skip the primer and load context from checkpoint.

### Progress Tracking

Emit progress events during the primer:

1. `"Searching consultant databases..."` — when starting Tavily searches
2. `"Found N consultant sources from M firms"` — after searches complete
3. `"Extracting insights from consultant reports..."` — during LLM extraction
4. `"Consultant primer complete: N sources from [firm list]"` — on completion

If zero sources found, emit a warning:
`"No consultant-grade sources found for {industry_vertical}. Research will proceed with web sources only."`

## File Changes Summary

### New Files

| File | Purpose |
|------|---------|
| `consultant_primer/__init__.py` | Package init |
| `consultant_primer/models.py` | `ConsultantSource`, `ConsultantContext` data models |
| `consultant_primer/domains.py` | Tiered domain lists and sector-specific domain selection |
| `consultant_primer/primer.py` | Main orchestration: search → fetch → extract → build ConsultantContext |
| `consultant_primer/prompts.py` | LLM prompt templates for consultant report extraction |

### Modified Files

| File | Change |
|------|--------|
| `orchestrator/runner.py` | Add `_run_consultant_primer()` method; call it before `_build_competitive_table()`; pass `consultant_context` to categories |
| `evidence_categories/base.py` | Add `consultant_context` parameter to `BaseCategory.__init__()`; inject into GPTResearcher via `context` kwarg |
| `market_research/base.py` | Same as above — `MRBaseCategory` also needs `consultant_context` support |
| `config/settings.py` | Add `CONSULTANT_PRIMER_ENABLED`, `CONSULTANT_PRIMER_MAX_SOURCES`, `CONSULTANT_PRIMER_TIMEOUT` |
| `output/markdown_formatter.py` | Add "Consultant & Analyst Coverage" section |
| `output/yaml_formatter.py` | Add `consultant_coverage` to YAML output |
| `output/package_assembler.py` | Accept and pass `consultant_context` to formatters |
| `context_extraction/models.py` | No change needed — consultant context is a separate artifact, not part of ContextSignals |
| `api/routes.py` | No structural changes needed — the primer runs inside `ResearchRunner.run_all()` |

### New Config

Add to `config/settings.py`:

```python
# --- Consultant Primer Config ---
CONSULTANT_PRIMER_ENABLED = os.getenv("CONSULTANT_PRIMER_ENABLED", "true").lower() == "true"
CONSULTANT_PRIMER_MAX_SOURCES = int(os.getenv("CONSULTANT_PRIMER_MAX_SOURCES", "20"))
CONSULTANT_PRIMER_TIMEOUT = int(os.getenv("CONSULTANT_PRIMER_TIMEOUT", "300"))  # 5 minutes
CONSULTANT_PRIMER_MAX_CONTENT_CHARS = int(os.getenv("CONSULTANT_PRIMER_MAX_CONTENT_CHARS", "50000"))
```

## Implementation Notes

### Tavily Direct Calls

The consultant primer should call the Tavily API **directly** rather than going through GPT Researcher. GPT Researcher adds overhead (sub-query generation, embedding-based curation) that isn't needed here — we know exactly which domains to search and what queries to run.

Use `requests` or `httpx` to call `https://api.tavily.com/search` with the `include_domains` field. The Tavily API key is already available in `config.settings.TAVILY_API_KEY`.

Example Tavily request body:
```json
{
    "query": "energy storage market size TAM United States 2025",
    "search_depth": "advanced",
    "include_domains": ["mckinsey.com", "bcg.com", "bain.com", "deloitte.com", "pwc.com", "ey.com", "kpmg.com"],
    "max_results": 10,
    "include_raw_content": true,
    "include_answer": false,
    "api_key": "<TAVILY_API_KEY>"
}
```

### Deduplication

Multiple search queries may return the same URL. Deduplicate by URL before extraction. If the same report appears in multiple searches, keep the version with the richest content (longest `raw_content`).

### Content Length Management

Consultant reports can be very long. The `get_context_text()` method has a `max_chars` cap (default 50,000) to prevent overwhelming GPT Researcher's context window. Sources are ordered by tier (Tier 1 first) so the highest-authority content gets priority if truncation occurs.

The LLM extraction step should also cap input at ~15,000 characters per source to stay within token limits. If a source's raw content exceeds this, truncate from the end (consultant reports front-load key findings).

### Graceful Degradation

If the consultant primer fails entirely (API errors, timeout, zero results), the pipeline should continue exactly as it does today — web-only research. The primer is an enhancement, not a gate.

If `CONSULTANT_PRIMER_ENABLED` is `false`, skip the phase entirely.

### Do NOT Edit site-packages

Per project rules, do not modify any files under Python `site-packages`. All GPT Researcher behavior modifications must happen via monkey-patching (as already done in `tavily_compat.py` and `base.py`) or via GPT Researcher's config/constructor parameters.

## Build Order

1. **Models first** (`consultant_primer/models.py`) — define `ConsultantSource` and `ConsultantContext`.
2. **Domains** (`consultant_primer/domains.py`) — define tiered domain lists and sector selection logic.
3. **Prompts** (`consultant_primer/prompts.py`) — write the LLM extraction prompt for parsing consultant report content.
4. **Primer logic** (`consultant_primer/primer.py`) — implement `run_consultant_primer(context: ContextSignals) -> ConsultantContext`.
5. **Runner integration** (`orchestrator/runner.py`) — add `_run_consultant_primer()` and wire it into `run_all()`.
6. **Base category integration** (`evidence_categories/base.py`, `market_research/base.py`) — accept `consultant_context` and inject into GPTResearcher.
7. **Output integration** (`output/markdown_formatter.py`, `output/yaml_formatter.py`, `output/package_assembler.py`) — add consultant coverage reporting.
8. **Settings** (`config/settings.py`) — add new config constants.
9. **Test** — run a research pipeline and verify consultant sources appear in category reports.

## Success Criteria

1. Running a research pipeline on any venture brief produces a `ConsultantContext` with at least 1 consultant source for common industries (energy, tech, healthcare, manufacturing).
2. Category raw reports cite consultant findings when relevant context was injected.
3. The markdown evidence report includes a "Consultant & Analyst Coverage" section showing which firms contributed and which categories lacked consultant data.
4. The pipeline gracefully degrades to web-only research if zero consultant sources are found.
5. Resume/checkpoint works: a crashed run can reload consultant context from checkpoint without re-running the primer.
6. Total primer execution time is under 5 minutes (typically 1–3 minutes for the Tavily searches + LLM extraction).
