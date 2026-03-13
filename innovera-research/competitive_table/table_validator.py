"""
Step 5: Validate the completed table and generate narrative summary.
"""
import json
import logging

from openai import OpenAI

from competitive_table.models import CompetitiveTable, TableMetadata
from competitive_table.prompts import VALIDATION_SYSTEM, VALIDATION_USER
from config.settings import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL,
    CONTEXT_LLM_MODEL, CONTEXT_LLM_MAX_TOKENS,
)

logger = logging.getLogger(__name__)


def compute_coverage(table: CompetitiveTable) -> float:
    """Calculate the percentage of non-null cells in the table."""
    if not table.attributes or not table.competitors:
        return 0.0

    total_cells = len(table.attributes) * len(table.competitors)
    if total_cells == 0:
        return 0.0

    filled = 0
    for comp in table.competitors:
        for attr in table.attributes:
            cell = comp.attributes.get(attr.attribute_id)
            if cell and cell.value is not None:
                filled += 1

    return round((filled / total_cells) * 100, 1)


def compute_metadata(table: CompetitiveTable, research_time: float) -> TableMetadata:
    """Compute table statistics."""
    total_sources = set()
    for comp in table.competitors:
        total_sources.update(comp.sources)
    if table.venture_entry:
        total_sources.update(table.venture_entry.sources)

    return TableMetadata(
        competitor_count=len(table.competitors),
        attribute_count=len(table.attributes),
        tier1_count=sum(1 for c in table.competitors if c.tier == 1),
        tier2_count=sum(1 for c in table.competitors if c.tier == 2),
        tier3_count=sum(1 for c in table.competitors if c.tier == 3),
        coverage_percent=compute_coverage(table),
        total_sources=len(total_sources),
        research_time_seconds=research_time,
    )


async def validate_and_summarize(table: CompetitiveTable) -> TableMetadata:
    """Call LLM to validate the table and generate narrative summary."""
    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)

    # Build a condensed table JSON for the LLM
    table_summary = _condense_table_for_prompt(table)

    user_message = VALIDATION_USER.format(
        venture_name=table.venture_name,
        industry=table.industry,
        competitor_count=len(table.competitors),
        attribute_count=len(table.attributes),
        coverage_percent=table.metadata.coverage_percent,
        table_json=json.dumps(table_summary, indent=2, default=str)[:12000],
    )

    response = client.chat.completions.create(
        model=CONTEXT_LLM_MODEL,
        max_tokens=CONTEXT_LLM_MAX_TOKENS,
        messages=[
            {"role": "system", "content": VALIDATION_SYSTEM},
            {"role": "user", "content": user_message},
        ],
    )

    response_text = response.choices[0].message.content
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0]

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        logger.warning("Failed to parse validation response")
        result = {}

    # Update metadata with LLM results
    table.metadata.table_summary = result.get("table_summary", "")
    table.metadata.venture_strengths = result.get("venture_strengths", [])
    table.metadata.venture_weaknesses = result.get("venture_weaknesses", [])
    table.metadata.dangerous_competitors = result.get("dangerous_competitors", [])
    table.metadata.rationale = table.metadata.rationale or result.get("rationale", "")

    logger.info(
        "Table validated: %d competitors, %d attributes, %.1f%% coverage",
        table.metadata.competitor_count,
        table.metadata.attribute_count,
        table.metadata.coverage_percent,
    )

    return table.metadata


def _condense_table_for_prompt(table: CompetitiveTable) -> dict:
    """Build a compact representation of the table for the LLM prompt."""
    rows = {}
    for comp in table.competitors:
        row = {"tier": comp.tier, "type": comp.competitor_type}
        for attr in table.attributes:
            cell = comp.attributes.get(attr.attribute_id)
            if cell and cell.value is not None:
                row[attr.attribute_id] = cell.value
            else:
                row[attr.attribute_id] = None
        rows[comp.name] = row

    # Include venture
    if table.venture_entry:
        row = {"tier": 0, "type": "venture"}
        for attr in table.attributes:
            cell = table.venture_entry.attributes.get(attr.attribute_id)
            if cell and cell.value is not None:
                row[attr.attribute_id] = cell.value
            else:
                row[attr.attribute_id] = None
        rows[table.venture_entry.name] = row

    return {
        "attributes": [{"id": a.attribute_id, "name": a.name, "group": a.group} for a in table.attributes],
        "data": rows,
    }
