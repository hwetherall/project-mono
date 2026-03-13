"""
All prompts used in the Competitive Table construction pipeline.
"""

# ---------------------------------------------------------------------------
# Step 1: Schema Generation
# ---------------------------------------------------------------------------

SCHEMA_GENERATION_SYSTEM = """You are a competitive-intelligence analyst designing a structured competitor matrix for a specific venture.

Your job is to define:
1. The set of competitive attributes (rows) that matter most for this specific industry and venture.
2. A target competitor count range with justification.
3. Logical groupings for the attributes.

Return ONLY valid JSON matching the schema provided. No markdown, no explanation outside the JSON."""

SCHEMA_GENERATION_USER = """Design a competitive matrix schema for the following venture:

**Venture:** {venture_name}
**Industry:** {industry} / {sub_vertical}
**Geography:** {geography}
**Stage:** {stage}
**Business Model:** {business_model}
**Solution Category:** {solution_category}
**Target Buyer:** {target_buyer}
**Problem Summary:** {problem_summary}
**Solution Summary:** {solution_summary}
**Named Competitors (from brief):** {named_competitors}

Consider the competitive dynamics of this specific market. For example:
- A component manufacturer competing for OEM contracts needs attributes like certification status, manufacturing scale, and key OEM relationships — not consumer features.
- A B2B SaaS startup needs attributes like pricing model, ACV range, integrations, and GTM motion.
- A consumer brand needs attributes like brand recognition, retail distribution, and pricing tiers.

### Examples of attribute sets for different industries

**SaaS Startup:**
Groups: Company Profile, Product & Technology, Commercial, Strategic Positioning
Attributes: year_founded, hq_location, employee_count, funding_raised, primary_use_case, key_integrations, pricing_model, acv_range, target_icp, gtm_motion, nps_score, market_positioning, competitive_moat

**Medical Device Manufacturer:**
Groups: Company Profile, Manufacturing & Technical, Regulatory & Quality, Market Position
Attributes: year_founded, hq_location, revenue_estimate, technology_type, manufacturing_capability, production_scale, iso_certifications, fda_clearances, target_applications, key_oem_relationships, patent_count, geographic_presence

**Consumer Goods:**
Groups: Company Profile, Product, Distribution, Brand & Market
Attributes: year_founded, hq_location, revenue_estimate, product_range, price_points, retail_presence, online_channels, brand_recognition, customer_demographics, sustainability_certifications

### Instructions
1. Determine a target competitor count range (min and max). Justify based on market concentration.
2. Select 15–30 attributes organized into 3–6 logical groups.
3. Classify each attribute by data_type (text, numeric, rating, list, boolean) and priority (required, important, optional).
4. Near-universal attributes to consider including: name, description, year_founded, hq_location, revenue_estimate, employee_count.
5. Include industry-specific attributes that reflect THIS venture's competitive dynamics.

Return JSON matching this schema:
{schema_json}"""


# ---------------------------------------------------------------------------
# Step 2: Competitor Discovery
# ---------------------------------------------------------------------------

COMPETITOR_DISCOVERY_QUERY = """Conduct a comprehensive competitor discovery for the following venture and market:

**Venture:** {venture_name}
**Industry:** {industry} / {sub_vertical}
**Geography:** {geography}
**Solution Category:** {solution_category}
**Problem Summary:** {problem_summary}
**Solution Summary:** {solution_summary}
{named_competitors_block}

Search for: "top companies in {industry}", "market leaders {industry}", "{solution_category} alternatives", "{solution_category} competitors", "{solution_category} market share", "emerging players {industry}".

### Target
Identify {target_min}–{target_max} competitors across these types:
- **Direct competitors**: Companies offering the same or very similar solution.
- **Substitutes**: Alternative approaches or workarounds that serve the same need.
- **Adjacent players**: Companies in neighboring markets that could enter this space.
- **Emerging entrants**: Startups or new entrants gaining traction.
- **Legacy incumbents**: Established players with entrenched market positions.

### Output Format
For EACH competitor discovered, provide:
1. **Name**: Full company name
2. **Type**: direct | substitute | adjacent | emerging | incumbent
3. **Tier recommendation**: 1 (top 3–5 direct competitors), 2 (next 5–10 relevant), or 3 (remaining)
4. **Description**: One-paragraph summary of what they do, who they serve, and why they are relevant.

Be thorough. Include companies explicitly named in the brief and discover additional ones through research. Prioritize specificity — name real companies with real details."""


# ---------------------------------------------------------------------------
# Step 3: Table Population (per-competitor for Tier 1)
# ---------------------------------------------------------------------------

TIER1_POPULATION_QUERY = """Research the following competitor in detail and provide specific data for each attribute listed below.

**Competitor:** {competitor_name}
**Industry Context:** {industry} / {sub_vertical}
**Venture Context:** {venture_name} — {solution_category}

### Attributes to Research
{attributes_list}

### Instructions
- For each attribute, provide a specific, sourced data point.
- If the data is not publicly available, note that explicitly rather than guessing.
- Include source URLs where possible.
- Be specific: exact numbers, named products, specific dates — not vague descriptions.
- Format your response as a structured list with each attribute on its own line."""


TIER2_POPULATION_QUERY = """Research the following competitors and provide comparative data across the key attributes listed below.

**Competitors:** {competitor_names}
**Industry Context:** {industry} / {sub_vertical}
**Venture Context:** {venture_name} — {solution_category}

### Attributes to Research
{attributes_list}

### Instructions
- For each competitor, provide data for each attribute where available.
- Prioritize required and important attributes.
- Include source URLs where possible.
- Be specific and cite sources.
- Format as a comparison table or structured list by competitor."""


TIER3_POPULATION_QUERY = """Provide a brief competitive profile for each of the following companies. Focus on the most critical attributes only.

**Competitors:** {competitor_names}
**Industry Context:** {industry} / {sub_vertical}

### Required Attributes Only
{attributes_list}

### Instructions
- Brief, factual entries for each competitor.
- Focus on publicly available information.
- One paragraph per competitor with key data points."""


# ---------------------------------------------------------------------------
# Step 3b: Structured extraction from research reports
# ---------------------------------------------------------------------------

POPULATION_EXTRACTION_SYSTEM = """You are a data extraction assistant. Given a research report about one or more competitors, extract structured attribute values for each competitor.

Return ONLY valid JSON. No markdown, no explanation outside the JSON."""

POPULATION_EXTRACTION_USER = """Extract structured competitive data from the following research report.

### Competitors to extract data for:
{competitor_names}

### Attributes to extract (attribute_id: description):
{attributes_schema}

### Research Report:
{raw_report}

### Output Format
Return a JSON object where each key is a competitor name and each value is an object mapping attribute_id to:
{{
  "value": <extracted value or null>,
  "confidence": "high" | "medium" | "low" | "unknown",
  "source_url": <URL if found in report, else null>,
  "notes": "<any caveats>"
}}

If a value cannot be extracted from the report, set value to null and confidence to "unknown".
Do NOT hallucinate values — only extract what is explicitly stated in the report."""


# ---------------------------------------------------------------------------
# Step 4: Venture Column Population
# ---------------------------------------------------------------------------

VENTURE_POPULATION_SYSTEM = """You are a data mapping assistant. Given a venture brief and a set of competitive attributes, map information from the brief to each attribute.

Return ONLY valid JSON. No markdown, no explanation outside the JSON."""

VENTURE_POPULATION_USER = """Map information from the following venture brief to each competitive attribute.

### Venture Brief:
{venture_brief}

### Context Signals:
- Venture: {venture_name}
- Industry: {industry}
- Geography: {geography}
- Solution: {solution_category}
- Stage: {stage}
- Business Model: {business_model}
- Problem: {problem_summary}
- Solution: {solution_summary}
- Technology Stack: {technology_stack}

### Attributes to populate (attribute_id: description):
{attributes_schema}

### Output Format
Return a JSON object mapping each attribute_id to:
{{
  "value": <value from the brief or null>,
  "confidence": "high" | "medium" | "low" | "unknown",
  "notes": "<explanation or 'Not mentioned in brief'>"
}}

Only extract what is explicitly stated or strongly implied by the brief. For attributes not covered, set value to null with a note explaining the gap."""


# ---------------------------------------------------------------------------
# Step 5: Table Validation & Summary
# ---------------------------------------------------------------------------

VALIDATION_SYSTEM = """You are a competitive analysis expert reviewing a completed competitive matrix. Provide a narrative summary and strategic assessment.

Return ONLY valid JSON. No markdown, no explanation outside the JSON."""

VALIDATION_USER = """Review the following competitive table and provide a strategic assessment.

### Venture: {venture_name}
### Industry: {industry}
### Competitor Count: {competitor_count}
### Attribute Count: {attribute_count}
### Coverage: {coverage_percent:.1f}%

### Competitive Table Data:
{table_json}

### Provide:
1. **table_summary**: A 3–5 paragraph narrative summary of the competitive landscape. What are the key dynamics? Who dominates? Where are the gaps?
2. **venture_strengths**: Top 3 strengths of the venture relative to the competition (list of strings).
3. **venture_weaknesses**: Top 3 weaknesses or gaps (list of strings).
4. **dangerous_competitors**: The 2–3 most dangerous competitors and a one-sentence explanation for each (list of strings like "CompanyX — reason").
5. **data_flags**: Any suspicious or inconsistent data points that should be verified (list of strings). Return empty list if none.

Return JSON:
{{
  "table_summary": "...",
  "venture_strengths": ["...", "...", "..."],
  "venture_weaknesses": ["...", "...", "..."],
  "dangerous_competitors": ["...", "...", "..."],
  "data_flags": ["..."]
}}"""


# ---------------------------------------------------------------------------
# Universal Parse Depth: Structured Extraction
# ---------------------------------------------------------------------------

STRUCTURED_EXTRACTION_SYSTEM = """You are a structured data extraction assistant. Given a research report and an extraction schema, extract specific data points from the report.

Return ONLY valid JSON matching the requested fields. No markdown, no explanation outside the JSON."""

STRUCTURED_EXTRACTION_USER = """Extract structured findings from the following research report.

### Category: {category_id} — {category_name}
### Extraction Schema:
{extraction_schema}

### Raw Report:
{raw_report}

### Instructions:
- Extract each field listed in the schema.
- For each field, provide the extracted value and a confidence level (high/medium/low/unknown).
- If a field cannot be extracted, set it to null.
- Do NOT hallucinate — only extract what is explicitly stated.
- Include source references where they appear in the report.

Return a JSON object with keys matching the schema field names."""
