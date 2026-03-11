# Web Research Pre-Step: Evidence Gathering Specification

## Purpose

This document defines the comprehensive, pre-analyst web research step for the Demand Validation chapter. This step runs **before** the Analyst-Associate-Partner flow, producing a structured evidence package that all 120+ framework executions can draw from. Individual frameworks may still run their own targeted searches, but this pre-step ensures every analyst starts with a rich, venture-specific evidence base rather than relying entirely on per-framework search.

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                     INPUTS                          │
│  Venture Brief + Client Docs + Structured Metadata  │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│            CONTEXT EXTRACTION LAYER                 │
│  Reads inputs → produces structured research        │
│  signals that drive query generation                │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│          RESEARCH EXECUTION ENGINE                  │
│  13 evidence categories, each with its own          │
│  search strategy and query generation logic         │
│                                                     │
│  ┌──────────┐  ┌──────────────────┐                │
│  │  Tavily   │  │  GPT Researcher  │                │
│  │ (lookups) │  │  (deep dives)    │                │
│  └──────────┘  └──────────────────┘                │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│           STRUCTURED EVIDENCE PACKAGE               │
│  Organized by evidence category                     │
│  + Section consumption map as metadata              │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│         ANALYST FRAMEWORKS (Level 0)                │
│  Each receives full evidence package                │
│  + may run supplementary targeted searches          │
└─────────────────────────────────────────────────────┘
```

---

## Part 1: Context Extraction Layer

Before any web search runs, the system reads the venture brief, client documents, and structured metadata to produce a set of **research signals**. These signals shape which evidence categories are prioritized, what queries are generated, and how results are filtered.

### 1.1 Required Structured Metadata

These fields are provided by the client or extracted from intake:

| Field | Description | Example |
|-------|-------------|---------|
| `venture_name` | Name of the venture or initiative | "AquaSense" |
| `industry_vertical` | Primary industry or sector | "Water infrastructure / Utilities" |
| `sub_vertical` | Specific niche within the industry | "Municipal water system maintenance" |
| `geography` | Primary geographic focus | "Japan, with expansion to Southeast Asia" |
| `stage` | Venture maturity | "Pre-revenue / Concept" |
| `business_model_type` | Revenue model category | "B2B SaaS + hardware sensor" |
| `target_buyer_type` | Enterprise, SMB, consumer, government | "Municipal government / Public utility" |
| `solution_category` | What category the product falls into | "Predictive maintenance / IoT monitoring" |
| `parent_company` | Corporate parent (if corporate venture) | "Nippon Light Metal" |

### 1.2 Extracted Research Signals

The context extraction prompt reads all inputs and produces these signals, which are then passed to every evidence category's query generator:

| Signal | How It's Extracted | What It Drives |
|--------|--------------------|----------------|
| `problem_keywords` | Core nouns/verbs from the problem statement | Query terms across all categories |
| `industry_terms` | Domain-specific jargon from venture brief | Search refinement, source filtering |
| `named_competitors` | Any competitors explicitly mentioned | Competitor category query seeding |
| `named_regulations` | Any regulations, standards, or mandates cited | Regulatory category prioritization |
| `pain_drivers` | Stated causes of customer pain (cost, risk, compliance, speed, etc.) | Category weighting and query focus |
| `customer_roles` | Specific roles mentioned (CTO, ops manager, etc.) | Voice-of-market targeting, procurement context |
| `technology_stack` | Technologies mentioned (IoT, AI, cloud, etc.) | Enabling tech category queries |
| `workaround_mentions` | Current solutions or workarounds described | Alternative/review category queries |
| `geographic_qualifiers` | Country/region-specific context | All queries get geo-qualification where relevant |
| `urgency_signals` | Any mentioned deadlines, mandates, or timing pressure | Urgency/forcing function category prioritization |
| `market_size_claims` | Any TAM/SAM figures cited by the venture | Market sizing category — verify/challenge these |
| `analogies_mentioned` | "Like X for Y" or comparable market references | Proxy market category seeding |

### 1.3 Category Priority Weighting

Not all 13 categories deserve equal depth for every venture. The context extraction layer also produces a **priority weight** (Critical / High / Medium / Low) for each category based on the venture's characteristics:

| Condition | Categories Upgraded | Categories Downgraded |
|-----------|--------------------|-----------------------|
| Regulated industry (healthcare, finance, utilities) | Regulatory & Compliance → Critical | — |
| Pre-revenue / concept stage | Problem Prevalence → Critical; Competitor Investment → High | Budget & Procurement → Low |
| Crowded market (3+ named competitors) | Competitor Landscape → Critical; Reviews & Failures → Critical | — |
| Novel category (no competitors named) | Proxy Markets → High; Enabling Tech → High | Competitor categories → Medium |
| Government / public sector buyer | Budget & Procurement → Critical; Regulatory → Critical | — |
| Consumer or SMB target | Voice of Market → Critical; Search Trends → High | Procurement → Low |
| Explicit timing pressure mentioned | Urgency & Forcing Functions → Critical | — |

---

## Part 2: Evidence Categories

### Category Index

| ID | Category Name | Default Priority | Search Strategy |
|----|--------------|-----------------|-----------------|
| EC-01 | Market Sizing & Growth | Critical | Tavily (lookup) |
| EC-02 | Competitor Landscape & Positioning | Critical | GPT Researcher (landscape) |
| EC-03 | Investment & Financial Signals | High | Tavily (lookup) |
| EC-04 | Alternative Solution Failures & Reviews | High | GPT Researcher (landscape) |
| EC-05 | Problem Prevalence & Cost Data | Critical | Hybrid |
| EC-06 | Regulatory & Compliance Environment | Conditional | GPT Researcher (landscape) |
| EC-07 | Enabling Technology Trends | Medium | GPT Researcher (landscape) |
| EC-08 | Urgency Drivers & Forcing Functions | High | Hybrid |
| EC-09 | Industry Analyst & Expert Coverage | High | GPT Researcher (landscape) |
| EC-10 | Voice of Market (Pain Language & Community) | High | GPT Researcher (landscape) |
| EC-11 | Search & Hiring Trends | Medium | Tavily (lookup) |
| EC-12 | Budget & Procurement Context | Conditional | Hybrid |
| EC-13 | Proxy Market Trajectories | Medium | GPT Researcher (landscape) |

**Search Strategy Definitions:**
- **Tavily (lookup):** Fast, structured queries targeting specific data points. Best for factual lookups, numbers, named entities. Typically 3–8 targeted queries per category.
- **GPT Researcher (landscape):** Multi-page synthesis requiring reading across sources, identifying patterns, and producing analytical summaries. Best for competitive mapping, trend synthesis, community sentiment. Typically 1–3 research missions per category.
- **Hybrid:** Some queries are lookup (specific data points), others require landscape synthesis. Split execution across both tools.

---

### EC-01: Market Sizing & Growth

**What we're looking for:** Total addressable market, serviceable addressable market, and serviceable obtainable market estimates for the venture's category. Market growth rates. Market structure (fragmented vs. consolidated, emerging vs. mature). Industry revenue and volume data.

**Why it matters:** Feeds S1-B (scalability assessment), S2-B (prevalence context), S4-B (targeting), S4-C (scalability verdict). Also provides the denominator for any penetration rate analysis.

**Search strategy:** Tavily (lookup). Market sizing data lives in specific, findable reports and databases. We need numbers, not narrative.

**Query generation logic:**
```
Base queries (always run):
  - "{solution_category} market size {geography}"
  - "{solution_category} market growth rate forecast"
  - "{industry_vertical} {sub_vertical} market size"
  - "{industry_vertical} technology spending"

Conditional queries:
  IF market_size_claims exist:
    - Verify: "{specific_claim} market size source"
  IF geography is non-US:
    - Add region-specific: "{solution_category} market {geography} growth"
  IF business_model_type includes "hardware":
    - Add: "{hardware_category} installed base {geography}"
```

**Expected source types:** Market research firms (Statista, Grand View Research, MarketsandMarkets, IBISWorld), analyst estimates, industry association publications, government statistical agencies.

**Quality signals:** Prefer sources published within 24 months. Flag estimates with wide variance across sources. Note methodological differences (top-down vs. bottom-up sizing).

**Output structure:**
```yaml
category: EC-01
title: "Market Sizing & Growth"
findings:
  - finding_id: "EC01-001"
    claim: "Global predictive maintenance market valued at $X.XB in 2024"
    value: "X.X"
    unit: "USD billions"
    source: "Source name"
    source_url: "https://..."
    source_date: "2024-XX-XX"
    confidence: "high | medium | low"
    notes: "Specific to industrial IoT; water infrastructure subset not broken out"
  - finding_id: "EC01-002"
    claim: "Market CAGR of XX.X% from 2024-2030"
    # ... etc
gaps:
  - "No market sizing data found specific to {sub_vertical}. Closest proxy is {proxy_category}."
  - "Growth estimates range from X% to Y% depending on source — significant variance."
venture_claims_check:
  - claim: "The venture brief states TAM of $XB"
    verification: "Partially supported — closest independent estimate is $YB for broader category"
```

**Section consumption:**

| Section | How it's used |
|---------|---------------|
| S1-B | Market size as scalability ceiling input |
| S2-B | Prevalence denominator — how big is the market the problem exists in |
| S2-C | Independent market narrative corroboration |
| S3-B | Market maturity assessment (emerging vs. mature affects timing) |
| S4-B | Addressable segment sizing for targeting |
| S4-C | Market-level scalability constraint or enabler |

---

### EC-02: Competitor Landscape & Positioning

**What we're looking for:** Comprehensive map of direct competitors, adjacent solutions, and DIY alternatives. For each: what they do, how they position, who they target, their pricing model (if public), key differentiators, and known weaknesses. Also: the "do nothing" option — what happens when customers don't adopt any solution.

**Why it matters:** This is the single most consumed evidence category. Feeds S1-A (why hasn't this been solved), S2-C (corroboration), S3-A (alternatives landscape — primary consumer), S3-B (timing/adoption), S4-B (targeting differentiation), S4-C (scalability in competitive context).

**Search strategy:** GPT Researcher (landscape). Competitive mapping requires reading across company websites, review platforms, press coverage, and analyst commentary. A few Tavily lookups won't capture the structure.

**Query generation logic:**
```
Phase 1 — Discovery (identify the players):
  - "{solution_category} companies {geography}"
  - "{problem_keywords} software vendors"
  - "{problem_keywords} solutions comparison"
  - "alternatives to {workaround_mentions}"

Phase 2 — Deep dive (research each identified player):
  For each competitor found in Phase 1:
    - "{competitor_name} product features pricing"
    - "{competitor_name} target market customers"
    - "{competitor_name} reviews problems"

Conditional queries:
  IF named_competitors provided:
    - Start Phase 2 with these; also search for competitors THEY compete with
  IF solution_category is novel:
    - Broaden: "{problem_keywords} how companies solve"
    - Add: "{problem_keywords} consulting firms services"
    - Add: "{problem_keywords} manual process workaround"
```

**Expected source types:** Competitor websites, G2/Capterra/TrustRadius, Crunchbase, analyst comparison reports, product review blogs, LinkedIn company pages, industry conference exhibitor lists.

**Quality signals:** Prefer primary sources (competitor's own site) for feature/positioning claims. Prefer independent sources (reviews, analysts) for effectiveness claims. Flag competitors that appear in only one source. Note date of most recent product update.

**Output structure:**
```yaml
category: EC-02
title: "Competitor Landscape & Positioning"
competitors:
  - competitor_id: "EC02-C01"
    name: "CompetitorName"
    type: "direct | adjacent | DIY_alternative | do_nothing"
    description: "One-paragraph description of what they do"
    target_market: "Who they sell to"
    positioning: "How they describe themselves"
    pricing_model: "SaaS / per-seat / usage-based / unknown"
    pricing_range: "$X-$Y per month or 'not public'"
    key_strengths: ["strength 1", "strength 2"]
    known_weaknesses: ["weakness 1", "weakness 2"]
    funding_stage: "Series B / Public / Bootstrapped / Unknown"
    sources: ["url1", "url2"]
  # ... repeat for each competitor

do_nothing_analysis:
  description: "What happens when organizations don't adopt any solution"
  prevalence: "How common is the do-nothing approach"
  consequences: "What the cost of inaction looks like"
  sources: ["url1"]

landscape_summary:
  total_competitors_found: N
  market_maturity: "early | growing | mature | consolidating"
  dominant_approach: "What most competitors do similarly"
  gap_in_landscape: "What no current player adequately addresses"
  fragmentation_level: "high | medium | low"

gaps:
  - "Limited pricing transparency — only X of Y competitors publish pricing"
  - "No independent analyst comparison found for this specific sub-category"
```

**Section consumption:**

| Section | How it's used |
|---------|---------------|
| S1-A | Structural reasons existing players haven't solved the problem |
| S2-C | Competitive activity as market corroboration signal |
| S3-A | Primary consumer — full alternatives landscape and failure analysis |
| S3-B | Competitive maturity informs timing assessment |
| S4-B | Competitive white space informs targeting |
| S4-C | Competitive density as scalability factor |

---

### EC-03: Investment & Financial Signals

**What we're looking for:** Venture capital investment in the space (funding rounds, amounts, investors, timing). M&A activity. IPOs or public company moves into the category. Public company earnings commentary referencing the problem or solution space. Corporate venture activity.

**Why it matters:** Investment activity is one of the strongest independent signals that sophisticated actors believe in the market. Also identifies potential acquirers and competitive threats from well-funded entrants.

**Search strategy:** Tavily (lookup). Funding data, M&A announcements, and earnings calls are structured, specific, and well-indexed.

**Query generation logic:**
```
Base queries:
  - "{solution_category} funding rounds {current_year}"
  - "{solution_category} venture capital investment"
  - "{solution_category} acquisitions mergers"
  - "{industry_vertical} technology investment trends"

For each named competitor:
  - "{competitor_name} funding raised investors"
  - "{competitor_name} acquisition"

Conditional:
  IF parent_company exists:
    - "{parent_company} venture investments {industry_vertical}"
    - "{parent_company} competitors innovation"
  IF public companies operate in space:
    - "{public_company} earnings {problem_keywords}"
```

**Expected source types:** Crunchbase, PitchBook, TechCrunch, press releases, SEC filings (for public companies), Bloomberg/Reuters, CB Insights.

**Output structure:**
```yaml
category: EC-03
title: "Investment & Financial Signals"
funding_activity:
  - company: "CompanyName"
    round: "Series B"
    amount: "$45M"
    date: "2024-06-15"
    lead_investor: "InvestorName"
    source: "url"
  # ... repeat

ma_activity:
  - acquirer: "AcquirerName"
    target: "TargetName"
    amount: "$XXM or undisclosed"
    date: "2024-XX-XX"
    strategic_rationale: "Brief note on why"
    source: "url"

aggregate_signals:
  total_funding_in_space: "$XXM across N companies in last 24 months"
  funding_trend: "accelerating | stable | decelerating"
  largest_round: "$XXM to CompanyName (Series X)"
  investor_quality_signal: "Tier 1 VCs active | Mostly seed-stage | Corporate strategic only"
  public_company_interest: "Yes/No — details"

gaps:
  - "Funding data may be incomplete for non-US companies"
```

**Section consumption:**

| Section | How it's used |
|---------|---------------|
| S2-B | Investment as market-level traction indicator |
| S2-C | Independent corroboration of market thesis |
| S3-A | Well-funded competitors as landscape context |
| S3-B | Investment timing informs "why now" assessment |
| S4-C | Capital intensity of competitive landscape affects scalability |

---

### EC-04: Alternative Solution Failures & Reviews

**What we're looking for:** Third-party reviews of existing solutions in the category. Recurring complaints, unmet needs, and feature gaps. Workaround evidence — what customers build internally, the spreadsheets, the manual processes, the extra hires. "Shadow spend" on consulting or services to patch solution gaps.

**Why it matters:** This is the evidence that the problem is real at the practitioner level — not just a market thesis but an experienced daily pain. The language in reviews and complaints is also critical raw material for the Voice of Market category (EC-10), but here we focus on the *substance* of failures, not the *language* of pain.

**Search strategy:** GPT Researcher (landscape). Reviews are qualitative, dispersed, and require pattern recognition across multiple platforms. Workaround evidence is even harder — it's buried in forums, job postings, and consultant directories.

**Query generation logic:**
```
For each identified competitor (from EC-02):
  - "{competitor_name} reviews complaints"
  - "{competitor_name} limitations problems"
  - "{competitor_name} vs alternatives"

For workaround evidence:
  - "{problem_keywords} workaround manual process"
  - "{problem_keywords} Excel spreadsheet tracking"
  - "{problem_keywords} internal tool built"
  - "{industry_vertical} {problem_keywords} consulting services"

Conditional:
  IF workaround_mentions provided:
    - "{specific_workaround} limitations problems"
  IF customer_roles provided:
    - "{customer_role} {problem_keywords} frustration"
```

**Expected source types:** G2, Capterra, TrustRadius, Reddit (r/[industry]), industry-specific forums, Stack Overflow (for technical products), Glassdoor (job postings indicating workaround staffing), consultant/services firm listings.

**Output structure:**
```yaml
category: EC-04
title: "Alternative Solution Failures & Reviews"
reviews_by_competitor:
  - competitor: "CompetitorName"
    review_platform: "G2"
    average_rating: "3.8/5"
    review_count: 245
    top_complaints:
      - theme: "Integration complexity"
        frequency: "Mentioned in ~30% of negative reviews"
        representative_language: "Paraphrased summary of complaint pattern"
      - theme: "Limited customization"
        frequency: "Mentioned in ~25%"
        representative_language: "..."
    top_praise:
      - theme: "Core functionality"
        representative_language: "..."
    source: "url"

workaround_evidence:
  - workaround_type: "Manual spreadsheet tracking"
    description: "How customers currently patch the gap"
    prevalence_signal: "Found in X forum threads, Y job postings"
    cost_signal: "Requires dedicated FTE or X hours/week"
    sources: ["url1", "url2"]

failure_pattern_synthesis:
  dominant_failure_modes: ["mode 1", "mode 2", "mode 3"]
  underserved_need: "The thing no current solution adequately addresses"
  workaround_prevalence: "high | moderate | low | unknown"

gaps:
  - "Limited review data for {competitor} — fewer than 20 reviews found"
  - "Workaround evidence is anecdotal; no quantified workaround-spend data found"
```

**Section consumption:**

| Section | How it's used |
|---------|---------------|
| S1-A | Evidence for why the problem persists (incumbent failure) |
| S2-C | Review patterns as independent problem corroboration |
| S3-A | Primary consumer — current alternatives and how they fail |
| S3-C | Workaround baseline as success criteria context |
| S4-B | Review complaints inform targeting (who's most underserved) |

---

### EC-05: Problem Prevalence & Cost Data

**What we're looking for:** Statistical evidence of how widespread the problem is. Quantified cost-of-problem figures: per-incident cost, annual cost per organization, industry-wide cost. Frequency data: how often the failure mode occurs. Government statistics, academic studies, benchmarking reports, and industry surveys that put numbers on the pain.

**Why it matters:** This is the quantitative backbone of the demand thesis. Without prevalence and cost data, the analysis is purely qualitative. This category feeds S2-B directly and provides the "quantified consequence" for S1-A.

**Search strategy:** Hybrid. Some data points are specific lookups (government statistics, published benchmarks). But synthesizing across studies to build a cost-of-problem picture requires reading and cross-referencing — that's a GPT Researcher mission.

**Query generation logic:**
```
Tavily lookups:
  - "{problem_keywords} statistics {geography}"
  - "{problem_keywords} cost per incident"
  - "{problem_keywords} annual cost industry"
  - "{problem_keywords} frequency rate"
  - "{industry_vertical} failure rate statistics"
  - "{problem_keywords} benchmark study report"

GPT Researcher deep dive:
  - "Synthesize available data on the cost and prevalence of {problem_keywords}
     in {industry_vertical}. Include: per-incident costs, annual aggregate
     costs, frequency of occurrence, affected population size, and trend
     direction. Note data quality and recency for each source."

Conditional:
  IF pain_drivers include "compliance" or "regulatory":
    - "{industry_vertical} compliance failure cost penalty"
    - "{named_regulations} non-compliance cost statistics"
  IF pain_drivers include "safety" or "risk":
    - "{problem_keywords} incident rate accident statistics"
    - "{problem_keywords} liability claims cost"
  IF geography is specific:
    - Add geo-qualifier to all statistical queries
```

**Expected source types:** Government agencies (BLS, Census, OSHA, EPA, sector-specific regulators), academic papers (Google Scholar), industry benchmarking studies, consulting firm reports (McKinsey, Deloitte, BCG), insurance/actuarial data, trade association publications.

**Output structure:**
```yaml
category: EC-05
title: "Problem Prevalence & Cost Data"
prevalence_data:
  - metric: "Percentage of {target} affected"
    value: "XX%"
    population: "N organizations/individuals"
    source: "Source name"
    source_date: "YYYY"
    methodology: "Survey of N=X / Census data / Estimate"
    confidence: "high | medium | low"

cost_data:
  - metric: "Cost per incident"
    value: "$X,XXX"
    context: "Per event for a typical {customer_type}"
    source: "Source name"
    source_date: "YYYY"
    confidence: "high | medium | low"
  - metric: "Annual cost per organization"
    value: "$X.XM"
    context: "For a mid-size {industry} company"
    # ...
  - metric: "Industry-wide annual cost"
    value: "$X.XB"
    context: "{geography}, all segments"
    # ...

frequency_data:
  - metric: "Occurrence frequency"
    value: "X times per [unit]"
    context: "Per {customer_type} per {time_period}"
    source: "..."

trend_direction:
  assessment: "worsening | stable | improving"
  evidence: "Brief explanation with data"

cost_of_problem_synthesis:
  per_customer_annual: "$X — based on frequency × cost-per-incident"
  show_math: "X incidents/year × $Y/incident = $Z"
  confidence_in_math: "Explain what's estimated vs. sourced"

gaps:
  - "No per-incident cost data found; estimate derived from {proxy}"
  - "Prevalence data is for {broader_category}, not specific to {sub_vertical}"
```

**Section consumption:**

| Section | How it's used |
|---------|---------------|
| S1-A | Quantified consequence in problem definition |
| S1-B | Pain intensity quantification across segments |
| S2-B | Primary consumer — prevalence, frequency, and cost analysis |
| S2-C | Independent quantitative corroboration |
| S2-D | Evidence weight for demand verdict |

---

### EC-06: Regulatory & Compliance Environment

**What we're looking for:** Current regulations, standards, and mandates affecting the problem or solution space. Pending or proposed regulatory changes. Enforcement actions, fines, and compliance costs. Compliance requirements that affect buying decisions (security certifications, data residency, audit requirements). Regulatory bodies and their current priorities.

**Why it matters:** Regulation can be either an urgency driver (mandates create forcing functions) or an adoption barrier (compliance requirements slow procurement). This category serves both functions.

**Default priority:** Conditional — Critical for regulated industries, Low for unregulated consumer/tech markets. The context extraction layer determines priority.

**Search strategy:** GPT Researcher (landscape). Regulatory environments are complex, multi-layered, and require reading primary sources (government publications) with interpretive context (legal analysis, industry guidance).

**Query generation logic:**
```
Base queries:
  - "{industry_vertical} regulations compliance requirements"
  - "{industry_vertical} regulatory changes {current_year}"
  - "{problem_keywords} regulatory requirements"

Conditional (high priority):
  IF named_regulations exist:
    - "{regulation_name} requirements timeline enforcement"
    - "{regulation_name} compliance cost"
    - "{regulation_name} penalties non-compliance"
  IF target_buyer_type is "government":
    - "{geography} government procurement regulations {solution_category}"
    - "{geography} public sector technology requirements"
  IF pain_drivers include "compliance":
    - "{industry_vertical} compliance audit requirements frequency"
    - "{industry_vertical} compliance technology mandates"
  IF solution_category involves data:
    - "{geography} data privacy regulations {industry_vertical}"
    - "data residency requirements {geography}"
```

**Expected source types:** Government websites, regulatory body publications, legal databases (LexisNexis, WestLaw — via summaries), law firm client alerts, compliance consulting firms, trade association regulatory guides.

**Output structure:**
```yaml
category: EC-06
title: "Regulatory & Compliance Environment"
current_regulations:
  - regulation_name: "Name"
    jurisdiction: "Country/region"
    relevance: "How it relates to the venture's problem/solution"
    key_requirements: ["req 1", "req 2"]
    enforcement: "Active | Pending | Lax"
    compliance_cost: "$X per org or 'not quantified'"
    source: "url"

pending_changes:
  - change_description: "What's changing"
    expected_timeline: "When"
    impact_on_venture: "How this affects the problem or solution"
    source: "url"

compliance_as_buying_friction:
  - requirement_type: "Security certification | Data residency | Audit trail"
    description: "What buyers need to see"
    typical_timeline: "How long this adds to procurement"
    source: "url"

regulatory_urgency_signal:
  assessment: "Regulation is creating urgency | neutral | creating friction"
  explanation: "Brief synthesis"

gaps:
  - "Regulatory landscape outside {primary_geography} not researched"
```

**Section consumption:**

| Section | How it's used |
|---------|---------------|
| S2-B | Regulatory cost as prevalence/urgency data |
| S2-C | Regulatory attention as corroboration signal |
| S3-B | Regulation as timing driver or barrier |
| S4-A | Compliance requirements as purchase constraints |
| S4-B | Regulatory pressure as urgency driver for targeting |

---

### EC-07: Enabling Technology Trends

**What we're looking for:** Technology shifts, platform changes, infrastructure developments, and cost curve movements that make the venture's solution feasible or economically viable now when it wasn't before. This is the "why now is this technically possible" evidence, distinct from urgency ("why now is this needed").

**Why it matters:** Answers the technical dimension of "why now" — a key component of S3-B's timing assessment. Also provides context for S1-A's root cause analysis (was the problem previously unsolvable due to technical constraints?).

**Search strategy:** GPT Researcher (landscape). Technology trend analysis requires synthesizing across vendor announcements, cost benchmarks, platform roadmaps, and industry commentary.

**Query generation logic:**
```
Base queries:
  - "{technology_stack} cost trends {current_year}"
  - "{technology_stack} adoption rate enterprise"
  - "{solution_category} technology enablers"
  - "{technology_stack} maturity enterprise readiness"

Conditional:
  IF technology_stack includes "IoT":
    - "IoT sensor cost reduction trends"
    - "IoT connectivity infrastructure {geography}"
  IF technology_stack includes "AI" or "ML":
    - "AI {industry_vertical} adoption readiness"
    - "foundation model cost per token trends"
  IF technology_stack includes "cloud":
    - "cloud adoption {industry_vertical} {geography}"
    - "edge computing {industry_vertical}"
```

**Expected source types:** Gartner Hype Cycles, technology vendor reports, cost benchmark studies, platform documentation, infrastructure provider announcements, academic/technical publications, developer community analyses.

**Output structure:**
```yaml
category: EC-07
title: "Enabling Technology Trends"
enabling_shifts:
  - trend_name: "Name of technology shift"
    description: "What changed and when"
    relevance_to_venture: "How this enables the solution"
    maturity: "emerging | maturing | mature"
    evidence: "Specific data points"
    source: "url"

cost_curves:
  - technology: "Specific technology"
    cost_trajectory: "Cost per unit has dropped X% over Y years"
    current_cost: "$X per unit"
    projected_cost: "$Y per unit by YYYY"
    source: "url"

infrastructure_readiness:
  assessment: "Ready | Mostly ready | Significant gaps"
  key_dependencies: ["dep 1", "dep 2"]
  geographic_variation: "Any regional differences in readiness"

gaps:
  - "Cost curve data for {specific_tech} is based on global figures; {geography}-specific costs may differ"
```

**Section consumption:**

| Section | How it's used |
|---------|---------------|
| S1-A | Technical root cause — was this previously infeasible? |
| S3-B | Primary consumer for "why now technically possible" |
| S2-D | Technology readiness as timing verdict input |

---

### EC-08: Urgency Drivers & Forcing Functions

**What we're looking for:** External events, deadlines, and pressure that create near-term decision urgency for the target customer. Regulatory deadlines. Technology sunsets or platform migrations. Budget cycles and fiscal year windows. Contract renewal timing. Industry events or competitive pressures that force action. Trend data showing the problem is getting worse.

**Why it matters:** Urgency evidence distinguishes "nice to have" from "must act now." This is critical for S3-B (timing), S4-B (targeting — urgency defines best-fit segments), and S2-D (demand verdict).

**Search strategy:** Hybrid. Some forcing functions are specific, dated events (Tavily lookup). But urgency trend synthesis requires reading across sources (GPT Researcher).

**Query generation logic:**
```
Tavily lookups:
  - "{industry_vertical} regulatory deadline {current_year} {next_year}"
  - "{industry_vertical} technology migration deadline"
  - "{industry_vertical} budget cycle fiscal year"
  - "{problem_keywords} getting worse trend"

GPT Researcher:
  - "What external forces are creating urgency for {industry_vertical}
     organizations to address {problem_keywords}? Include regulatory
     deadlines, technology shifts, competitive pressures, and cost trends."

Conditional:
  IF urgency_signals exist in venture brief:
    - Verify each: "{specific_urgency_signal} timeline details"
  IF named_regulations exist:
    - "{regulation_name} compliance deadline enforcement date"
  IF industry_vertical has cyclical patterns:
    - "{industry_vertical} procurement cycle timing"
    - "{industry_vertical} budget planning timeline"
```

**Expected source types:** Regulatory announcements, vendor deprecation notices, industry calendars, budget/fiscal year guides, trend reports, news coverage of industry shifts.

**Output structure:**
```yaml
category: EC-08
title: "Urgency Drivers & Forcing Functions"
forcing_functions:
  - driver_name: "Name of forcing function"
    type: "regulatory_deadline | technology_sunset | cost_escalation | competitive_pressure | budget_cycle"
    description: "What's happening and why it creates urgency"
    timeline: "When the pressure peaks"
    affected_segments: "Which customer segments feel this most"
    strength: "hard_deadline | strong_pressure | moderate | weak"
    source: "url"

trend_urgency:
  - trend: "Problem is [intensifying/stabilizing]"
    evidence: "Data showing trajectory"
    implication: "What this means for buyer urgency"

trigger_events:
  - trigger: "Observable event that causes buying action"
    description: "What happens and why it triggers search"
    predictability: "predictable | somewhat_predictable | unpredictable"
    frequency: "How often this trigger occurs"

urgency_synthesis:
  overall_urgency: "high | moderate | low"
  strongest_driver: "Which forcing function is most powerful"
  urgency_timeline: "When urgency peaks"
  segment_variation: "Which segments feel urgency most"

gaps:
  - "Budget cycle timing for {target_buyer_type} not confirmed"
```

**Section consumption:**

| Section | How it's used |
|---------|---------------|
| S2-B | Urgency as prevalence/frequency amplifier |
| S3-B | Primary consumer — timing and adoption analysis |
| S4-B | Urgency-driven segment prioritization, trigger events |
| S2-D | Urgency evidence in demand verdict |

---

### EC-09: Industry Analyst & Expert Coverage

**What we're looking for:** Analyst reports (Gartner, Forrester, IDC, McKinsey, etc.) covering the problem domain or solution category. Trade publication coverage. Conference keynote themes and session topics. Expert commentary and thought leadership. Industry priority rankings.

**Why it matters:** Analyst coverage is a credibility signal and an independent perspective check. If major analysts are writing about this problem, it corroborates the demand thesis. If they're not, that's either a warning sign or an opportunity indicator (too early for analysts to cover).

**Search strategy:** GPT Researcher (landscape). Analyst coverage requires reading across multiple sources and synthesizing the overall market narrative.

**Query generation logic:**
```
Base queries:
  - "Gartner {solution_category} {current_year}"
  - "Forrester {solution_category} {current_year}"
  - "{solution_category} analyst report {current_year}"
  - "{problem_keywords} industry report"
  - "{industry_vertical} {problem_keywords} conference {current_year}"
  - "{solution_category} market trends expert analysis"

Conditional:
  IF solution_category maps to a Gartner Magic Quadrant:
    - "Gartner Magic Quadrant {category} {current_year}"
  IF industry has specific trade publications:
    - "{trade_publication} {problem_keywords} coverage"
```

**Expected source types:** Gartner, Forrester, IDC, McKinsey Global Institute, BCG, Deloitte, industry-specific analysts, trade publications, conference proceedings, expert blogs.

**Output structure:**
```yaml
category: EC-09
title: "Industry Analyst & Expert Coverage"
analyst_coverage:
  - analyst_firm: "Gartner"
    report_title: "Title (paraphrased)"
    date: "YYYY-MM"
    key_findings: "Paraphrased summary of relevant findings"
    relevance: "How this relates to the venture"
    source: "url"

market_narrative:
  analyst_consensus: "What analysts broadly agree on about this space"
  dissenting_views: "Where analysts disagree"
  category_maturity_per_analysts: "How analysts classify this market"

priority_ranking:
  - source: "Gartner Top 10 Strategic Technology Trends"
    year: YYYY
    ranking_or_inclusion: "Included / Not included"
    relevance: "How directly relevant"

conference_coverage:
  - conference: "Conference Name"
    year: YYYY
    relevant_sessions: N
    theme_relevance: "How central was this problem to the event"

coverage_assessment:
  volume: "heavy | moderate | light | absent"
  trend: "increasing | stable | decreasing"
  implication: "What the coverage level tells us about market maturity"

gaps:
  - "No Gartner or Forrester coverage found specific to {sub_vertical}"
  - "Analyst coverage may be biased toward {geography} markets"
```

**Section consumption:**

| Section | How it's used |
|---------|---------------|
| S2-C | Primary consumer — third-party corroboration |
| S2-B | Analyst data points feeding prevalence analysis |
| S2-D | Analyst consensus as verdict input |
| S3-B | Analyst timing assessments |

---

### EC-10: Voice of Market (Pain Language & Community)

**What we're looking for:** How practitioners actually talk about the problem in their own words. Recurring language patterns from forums, review platforms, social media, community discussions, and public complaints. The vocabulary gap (or alignment) between how the venture frames the problem and how the market experiences it.

**Why it matters:** This is the ground-truth check on problem framing. If the venture says "predictive asset lifecycle management" but practitioners say "we can't tell when pipes are going to break," that gap is critical information for S1-A (problem definition), S2-A (language alignment), and S4-B (messaging-market fit).

**Search strategy:** GPT Researcher (landscape). Pain language is qualitative, dispersed, and requires pattern recognition across community sources.

**Query generation logic:**
```
Base queries:
  - "{problem_keywords} Reddit {industry_vertical}"
  - "{problem_keywords} forum discussion"
  - "{industry_vertical} {problem_keywords} frustration complaints"
  - "{customer_roles} challenges {problem_keywords}"
  - "{problem_keywords} LinkedIn discussion"

Conditional:
  IF industry has specific forums:
    - Search those forums directly
  IF customer_roles are technical:
    - "Stack Overflow {problem_keywords}"
    - "{technical_community} {problem_keywords}"
  IF geography is non-English-speaking:
    - Note gap: community language analysis limited to English sources
```

**Expected source types:** Reddit, LinkedIn, Twitter/X, Hacker News, Stack Overflow, industry-specific forums, Quora, conference Q&A recordings, podcast transcripts.

**Output structure:**
```yaml
category: EC-10
title: "Voice of Market"
pain_language_patterns:
  - theme: "Infrastructure aging"
    frequency: "Appears in X of Y sources"
    representative_phrases:
      - "Paraphrased common expression 1"
      - "Paraphrased common expression 2"
    sentiment_intensity: "high | moderate | mild"
    context: "Where and when this language appears"
    sources: ["url1", "url2"]

vocabulary_analysis:
  venture_framing: "How the venture describes the problem"
  market_framing: "How practitioners describe the problem"
  alignment: "strong | moderate | weak | misaligned"
  implications: "What this means for positioning and sales"

community_activity:
  discussion_volume: "high | moderate | low | absent"
  trend: "growing | stable | declining"
  most_active_communities: ["community 1", "community 2"]

escalation_signals:
  - signal: "Problem mentioned in executive/leadership context"
    evidence: "Where and how"
    source: "url"

gaps:
  - "Community discussion analysis limited to English-language sources"
  - "Low forum activity may reflect early market stage rather than low pain"
```

**Section consumption:**

| Section | How it's used |
|---------|---------------|
| S1-A | Problem definition grounding in market language |
| S2-A | Language alignment evidence |
| S2-C | Community activity as corroboration |
| S3-C | Practitioner success criteria language |
| S4-B | Pain language informs targeting and messaging |

---

### EC-11: Search & Hiring Trends

**What we're looking for:** Google Trends data for problem-related and solution-related search terms. Keyword search volumes. Job posting trends related to the problem area (indicating internal investment in solving the problem). Hiring patterns among competitors.

**Why it matters:** Search trends are a revealed-preference indicator — people search for things they actually care about. Job posting trends show organizational investment: if companies are hiring people to manually solve this problem, that's both a prevalence signal and a workaround-spend indicator.

**Search strategy:** Tavily (lookup). Trend data and job posting counts are specific, quantifiable data points.

**Query generation logic:**
```
Base queries:
  - "{problem_keywords} Google Trends interest"
  - "{solution_category} search volume growth"
  - "{problem_keywords} job postings {geography}"
  - "{problem_keywords} hiring trends {industry_vertical}"

For competitor hiring:
  - "{competitor_name} hiring growth headcount"
  - "{competitor_name} job openings"

Conditional:
  IF solution_category is a new term:
    - Compare search volume of new term vs. established equivalent
  IF geography is specific:
    - Google Trends with geo filter
```

**Expected source types:** Google Trends, SEMrush/Ahrefs, Indeed/LinkedIn Jobs, Glassdoor, Lightcast/Emsi, SimilarWeb (for competitor traffic), BuiltWith (for technology adoption).

**Output structure:**
```yaml
category: EC-11
title: "Search & Hiring Trends"
search_trends:
  - term: "Search term"
    trend_direction: "growing | stable | declining"
    growth_rate: "X% over Y months"
    current_volume: "Monthly search volume or relative index"
    source: "Google Trends / SEMrush"
    geographic_note: "Global / US / specific region"

job_posting_trends:
  - role_category: "Role related to the problem"
    posting_volume: "N postings"
    trend: "growing | stable | declining"
    employers: "Types of organizations posting"
    implication: "What this indicates about internal investment"
    source: "Indeed / LinkedIn"

competitor_hiring:
  - competitor: "CompetitorName"
    headcount_trend: "growing | stable"
    key_roles_hiring: ["role 1", "role 2"]
    source: "LinkedIn / Glassdoor"

gaps:
  - "Google Trends data may not capture B2B-specific search behavior well"
  - "Job posting data skewed toward {geography}"
```

**Section consumption:**

| Section | How it's used |
|---------|---------------|
| S2-B | Search volume as prevalence indicator |
| S2-C | Trend data as corroboration signal |
| S3-B | Search trend trajectory as timing signal |
| S4-B | Job posting geography/industry as targeting data |

---

### EC-12: Budget & Procurement Context

**What we're looking for:** Enterprise IT/technology budget data and spending surveys. Budget ownership norms for the target category (OpEx vs. CapEx, which department owns the budget). Typical procurement processes, timelines, and requirements. Security/compliance certification requirements (SOC 2, ISO 27001, FedRAMP, etc.). Implementation timeline benchmarks.

**Why it matters:** Even validated demand fails if the buying process is impenetrable. This category provides the structural context for S4-A (buying mechanics) and informs S3-B (adoption friction).

**Default priority:** Conditional — Critical for government/enterprise, Low for SMB/consumer. Context extraction layer determines priority.

**Search strategy:** Hybrid. Budget survey data is Tavily-lookup-friendly. Procurement process norms require landscape synthesis.

**Query generation logic:**
```
Tavily lookups:
  - "{industry_vertical} IT technology budget {current_year}"
  - "{industry_vertical} technology spending forecast"
  - "{solution_category} typical deal size pricing"
  - "{target_buyer_type} procurement process timeline"

GPT Researcher:
  - "What does the typical procurement process look like for {solution_category}
     in {industry_vertical}? Include: approval steps, required certifications,
     typical timelines, common deal-killers, and budget ownership."

Conditional:
  IF target_buyer_type is "government":
    - "{geography} government procurement requirements technology"
    - "{geography} public tender process requirements"
    - "FedRAMP / GovCloud requirements" (if US)
  IF business_model_type includes "SaaS":
    - "enterprise SaaS procurement requirements {industry_vertical}"
    - "SOC 2 ISO 27001 requirement {industry_vertical}"
  IF solution involves data:
    - "data security requirements {industry_vertical} {geography}"
```

**Expected source types:** Gartner IT spending reports, Flexera State of IT, Deloitte tech spending surveys, procurement guides, industry-specific buying process documentation, security framework documentation.

**Output structure:**
```yaml
category: EC-12
title: "Budget & Procurement Context"
budget_data:
  - metric: "Average IT/tech budget as % of revenue"
    value: "X%"
    segment: "{industry_vertical}, {company_size}"
    source: "Gartner / Flexera"
    year: YYYY

budget_ownership:
  likely_budget_line: "IT / Operations / Compliance / Other"
  budget_type: "OpEx | CapEx | Mixed"
  evidence: "How this was determined"

procurement_process:
  typical_steps: ["step 1", "step 2", "step 3"]
  typical_timeline: "X weeks/months from first meeting to signed contract"
  required_certifications: ["SOC 2", "ISO 27001", etc.]
  common_deal_killers: ["killer 1", "killer 2"]
  variability_drivers: "What makes procurement faster or slower"

implementation_benchmarks:
  typical_time_to_live: "X weeks from contract to first use"
  typical_time_to_value: "X months from first use to measurable ROI"
  source: "url"

gaps:
  - "Procurement process norms for {sub_vertical} specifically not found"
  - "Implementation timeline benchmarks are for {adjacent_category}, not exact match"
```

**Section consumption:**

| Section | How it's used |
|---------|---------------|
| S3-B | Procurement friction as adoption barrier |
| S4-A | Primary consumer — buying mechanics, budget, constraints |
| S4-C | GTM repeatability assessment |

---

### EC-13: Proxy Market Trajectories

**What we're looking for:** Adoption history and inflection points in analogous markets. "Like X for Y" comparisons that the venture (or the market) uses. Comparable technology adoption curves. Markets that solved a structurally similar problem in a different vertical or geography.

**Why it matters:** When direct evidence is thin (pre-revenue, novel category), proxy markets provide the strongest available signal for market timing and adoption trajectory. Critical for S2-D (demand verdict) and S3-B (timing).

**Search strategy:** GPT Researcher (landscape). Proxy market analysis requires identifying appropriate analogues and then researching their trajectories — this is inherently synthetic.

**Query generation logic:**
```
IF analogies_mentioned exist:
  - "{analogy} market adoption history trajectory"
  - "{analogy} market inflection point"
  - "{analogy} early market growth"

Base queries:
  - "{solution_category} comparable markets adoption"
  - "{problem_keywords} solved in other industries"
  - "{technology_stack} adoption curve {similar_vertical}"

GPT Researcher mission:
  - "Identify 2-3 analogous markets or comparable adoption trajectories
     for {solution_category} in {industry_vertical}. For each analogue:
     describe the problem similarity, adoption timeline, inflection points,
     and what lessons apply to the target market."
```

**Expected source types:** Market history reports, company origin stories, funding/growth archives, academic case studies, trade publication retrospectives.

**Output structure:**
```yaml
category: EC-13
title: "Proxy Market Trajectories"
analogues:
  - analogue_name: "Name of analogous market/product"
    similarity_basis: "Why this is a valid comparison"
    adoption_timeline:
      - phase: "Early adoption"
        period: "YYYY-YYYY"
        characteristics: "What the early market looked like"
      - phase: "Inflection point"
        period: "YYYY"
        trigger: "What caused acceleration"
      - phase: "Mainstream"
        period: "YYYY-YYYY"
        scale: "How big it got"
    lessons_for_venture: "What this trajectory suggests for the target market"
    limitations_of_analogy: "Where the comparison breaks down"
    sources: ["url1", "url2"]

trajectory_synthesis:
  implied_timing: "Where the target market sits on the adoption curve"
  confidence: "high | moderate | low"
  key_caveat: "The most important way the target differs from the analogue"

gaps:
  - "Proxy market data is inherently approximate — structural differences noted"
```

**Section consumption:**

| Section | How it's used |
|---------|---------------|
| S2-B | Proxy prevalence data |
| S2-C | Proxy market as corroboration |
| S2-D | Proxy trajectory informs demand verdict |
| S3-B | Adoption timing inference from analogues |

---

## Part 3: Section Consumption Map

This matrix shows which evidence categories are consumed by which sections, and whether the category is a **primary input** (P) or **supporting context** (S) for that section.

| Evidence Category | S1-A | S1-B | S2-A | S2-B | S2-C | S2-D | S3-A | S3-B | S3-C | S4-A | S4-B | S4-C |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EC-01: Market Sizing | — | P | — | S | S | — | — | S | — | — | P | P |
| EC-02: Competitor Landscape | S | — | — | — | S | — | P | S | — | — | S | S |
| EC-03: Investment Signals | — | — | — | P | P | — | S | S | — | — | — | S |
| EC-04: Alt Failures & Reviews | S | — | — | — | S | — | P | — | S | — | S | — |
| EC-05: Problem Prevalence | P | P | — | P | S | P | — | — | — | — | — | — |
| EC-06: Regulatory & Compliance | — | — | — | S | S | — | — | P | — | P | S | — |
| EC-07: Enabling Tech Trends | S | — | — | — | — | — | — | P | — | — | — | — |
| EC-08: Urgency & Forcing | — | — | — | S | — | P | — | P | — | — | P | — |
| EC-09: Analyst Coverage | — | — | — | S | P | S | — | S | — | — | — | — |
| EC-10: Voice of Market | S | — | S | — | S | — | — | — | S | — | S | — |
| EC-11: Search & Hiring | — | — | — | S | S | — | — | S | — | — | S | — |
| EC-12: Budget & Procurement | — | — | — | — | — | — | — | S | — | P | — | S |
| EC-13: Proxy Markets | — | — | — | S | S | S | — | S | — | — | — | — |

**Reading the map:**
- **P (Primary):** This is a core input — the section cannot be written well without this evidence
- **S (Supporting):** This provides useful context but isn't the central evidence for the section
- **—:** Not consumed by this section

---

## Part 4: Execution Sequencing

Some categories have dependencies — EC-02 (Competitor Landscape) identifies competitors that EC-03, EC-04, and EC-11 then research individually. The recommended execution order:

### Phase 0: Context Extraction (must complete first)
- Read venture brief + client docs + metadata
- Produce all research signals (Section 1.2)
- Set category priority weights (Section 1.3)

### Phase 1: Foundation (can run in parallel)
- EC-01: Market Sizing
- EC-02: Competitor Landscape (discovery phase)
- EC-05: Problem Prevalence
- EC-06: Regulatory & Compliance
- EC-10: Voice of Market

### Phase 2: Dependent on Phase 1 (can run in parallel with each other)
- EC-03: Investment Signals (needs competitor list from EC-02)
- EC-04: Alt Failures & Reviews (needs competitor list from EC-02)
- EC-11: Search & Hiring Trends (needs competitor list from EC-02 for hiring data)

### Phase 3: Synthesis-Heavy (can run in parallel)
- EC-07: Enabling Technology Trends
- EC-08: Urgency Drivers & Forcing Functions
- EC-09: Analyst Coverage
- EC-12: Budget & Procurement Context
- EC-13: Proxy Market Trajectories

Total estimated execution: 3 phases, with parallelism within each phase.

---

## Part 5: Non-Web-Searchable Input Guidance

The following internal/customer data categories are **not gathered by this research step** but should be used to **guide** the research when present in the venture brief or client documents:

| Internal Signal | How It Guides Research |
|-----------------|----------------------|
| Customer interview transcripts | Extract pain language → refine EC-10 queries; extract competitor mentions → seed EC-02; extract workaround descriptions → refine EC-04 |
| Named customer segments | All queries get segment-specific refinement |
| Pilot/beta data | If metrics exist, search for benchmark comparisons (EC-05) |
| Sales pipeline data | Named prospects → industry/size context for market sizing (EC-01) |
| Pricing conversations | Price points → refine EC-12 budget context queries |
| LOIs or contracts | Named buyer types → refine EC-12 procurement research |
| Problem framing iterations | Prior framings → test both old and new language in EC-10 |
| Customer workflow descriptions | Workflow tools mentioned → search those tools in EC-04 |

The context extraction layer (Part 1) is responsible for surfacing these signals from the input documents and routing them to the appropriate evidence categories.

---

## Part 6: Output Package Format

The final output of the research pre-step is delivered to analysts as a structured evidence package. Two formats are produced:

### 6.1 Machine-Readable (YAML)

```yaml
research_package:
  metadata:
    venture_name: "VentureName"
    generated_at: "ISO-8601 timestamp"
    input_documents: ["doc1.pdf", "doc2.md"]
    execution_time_seconds: NNN
    categories_executed: 13
    total_sources_consulted: NNN
    total_findings: NNN

  context_signals:
    # All signals from Section 1.2
    problem_keywords: ["kw1", "kw2"]
    industry_terms: ["term1", "term2"]
    # ... etc

  evidence:
    EC-01:
      # Full output structure as defined above
    EC-02:
      # ...
    # ... through EC-13

  consumption_map:
    S1-A: ["EC-01", "EC-02", "EC-05", "EC-07", "EC-10"]
    S1-B: ["EC-01", "EC-05"]
    # ... etc

  gap_summary:
    critical_gaps:
      - category: "EC-05"
        gap: "No per-incident cost data found for {sub_vertical}"
        implication: "S2-B prevalence analysis will rely on proxy data"
        recommended_action: "Framework-level targeted search or manual research"
    moderate_gaps:
      - # ...
```

### 6.2 Human-Readable (Markdown Report)

A formatted markdown document with:
1. Executive summary of what was found and what's missing
2. Each evidence category as a section with findings, sources, and gaps
3. Cross-category synthesis: key themes, contradictions, and surprising findings
4. Gap inventory with severity and recommended mitigation

---

## Appendix A: Inventory Reconciliation Notes

This spec was built from three source inventories with the following reconciliation decisions:

| Source | Role in Reconciliation |
|--------|----------------------|
| `input-data-requirements-Claude.md` Category C | **Primary backbone.** 22 web-searchable items provided the foundational taxonomy. All 22 are represented in the 13 evidence categories. |
| `framework_inputs-gemini.md` | **Granularity supplement.** Gemini's more detailed breakdown of competitor intelligence (funding vs. growth vs. features) shaped the EC-02/EC-03 split. Its "Enablers vs Drivers" distinction became the EC-07/EC-08 split. Items identified as analytical outputs (Evidence Weighting, Corroboration Summary, Bear Case Arguments) were excluded — these are associate/partner tasks, not raw research. |
| `demand-validation-input-inventory.md` | **Completeness cross-check.** Seven items from this inventory that were underrepresented in the other two were explicitly added: Problem Persistence Evidence → EC-02/EC-04; Compensating Behaviors → EC-04; Trigger Events → EC-08; Wedge Market Size → EC-01; Source Credibility Metadata → all categories (as quality signal guidance); Problem Repeatability Evidence → EC-05; GTM Repeatability Evidence → EC-12. |

### Items Excluded from This Spec (Not Web-Searchable)

These items from the inventories require internal/customer data and are handled by the venture brief input path, not by web research:

- Venture Brief / Problem Statement / Value Proposition (Company/Internal)
- Customer Interview Transcripts / Survey Results (Customer Evidence)
- LOIs / Pre-orders / Deposits (Customer Evidence)
- Pilot / Beta Program Data (Customer Evidence)
- Product Usage Analytics (Company/Internal)
- CRM / Sales Pipeline Data (Company/Internal)
- All "Validation Activity" items (Customer Evidence)
- Customer Intent and Switching Evidence (Customer Evidence)
- Problem-Language Alignment Evidence (Customer Evidence — though EC-10 provides the *market side* of this comparison)
- Negative Signal Data (Customer Evidence)
- Design Partner Relationships (Company/Internal)

These are used as *context signals* when present (per Part 5), not as research targets.
