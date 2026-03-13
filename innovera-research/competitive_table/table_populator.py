"""
Steps 3–4: Populate the competitive table with researched data.
Tier 1 = one deep research call per competitor.
Tier 2 = batched 3–5 per call.
Tier 3 = single summary call.
Step 4 = Venture column from brief (no web research).
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from gpt_researcher import GPTResearcher
from openai import OpenAI

from competitive_table.models import (
    CompetitiveAttribute, CompetitorEntry, CellValue, CompetitiveTable,
)
from competitive_table.prompts import (
    TIER1_POPULATION_QUERY, TIER2_POPULATION_QUERY, TIER3_POPULATION_QUERY,
    POPULATION_EXTRACTION_SYSTEM, POPULATION_EXTRACTION_USER,
    VENTURE_POPULATION_SYSTEM, VENTURE_POPULATION_USER,
)
from context_extraction.models import ContextSignals
from config.settings import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL,
    CONTEXT_LLM_MODEL, CONTEXT_LLM_MAX_TOKENS,
    MAX_CONCURRENT_CATEGORIES, CATEGORY_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)


def _format_attributes_list(attributes: list[CompetitiveAttribute], priority_filter: str | None = None) -> str:
    """Format attributes as a numbered list for prompts."""
    lines = []
    for i, attr in enumerate(attributes, 1):
        if priority_filter and attr.priority != priority_filter and priority_filter != "all":
            continue
        lines.append(f"{i}. **{attr.name}** ({attr.attribute_id}): {attr.description} [type: {attr.data_type}]")
    return "\n".join(lines)


def _format_attributes_schema(attributes: list[CompetitiveAttribute]) -> str:
    """Format attributes as id: description for extraction prompts."""
    return "\n".join(f"- {a.attribute_id}: {a.name} — {a.description}" for a in attributes)


async def populate_table(
    competitors: list[CompetitorEntry],
    attributes: list[CompetitiveAttribute],
    context: ContextSignals,
    config_path: str,
    progress_callback=None,
    run_id: str | None = None,
) -> list[CompetitorEntry]:
    """Populate attribute values for all competitors using tiered research."""
    tier1 = [c for c in competitors if c.tier == 1]
    tier2 = [c for c in competitors if c.tier == 2]
    tier3 = [c for c in competitors if c.tier == 3]

    populated = []
    total = len(competitors)
    done = 0

    # --- Tier 1: One call per competitor ---
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_CATEGORIES)

    async def research_tier1(comp: CompetitorEntry) -> CompetitorEntry:
        nonlocal done
        async with semaphore:
            try:
                result = await _research_single_competitor(comp, attributes, context, config_path)
                done += 1
                if progress_callback:
                    progress_callback("population", done, total)
                return result
            except asyncio.TimeoutError:
                logger.warning("Tier 1 research timed out for %s", comp.name)
                done += 1
                return comp
            except Exception as e:
                logger.warning("Tier 1 research failed for %s: %s", comp.name, e)
                done += 1
                return comp

    if tier1:
        tier1_tasks = [
            asyncio.wait_for(research_tier1(c), timeout=CATEGORY_TIMEOUT_SECONDS)
            for c in tier1
        ]
        tier1_results = await asyncio.gather(*tier1_tasks, return_exceptions=True)
        for i, result in enumerate(tier1_results):
            populated.append(result if isinstance(result, CompetitorEntry) else tier1[i])

    # --- Tier 2: Batched 3-5 per call ---
    batch_size = 4
    for batch_start in range(0, len(tier2), batch_size):
        batch = tier2[batch_start:batch_start + batch_size]
        try:
            batch_results = await asyncio.wait_for(
                _research_batch(batch, attributes, context, config_path, tier=2),
                timeout=CATEGORY_TIMEOUT_SECONDS,
            )
            populated.extend(batch_results)
            done += len(batch)
            if progress_callback:
                progress_callback("population", done, total)
        except Exception as e:
            logger.warning("Tier 2 batch failed: %s", e)
            populated.extend(batch)
            done += len(batch)

    # --- Tier 3: Single summary call ---
    if tier3:
        try:
            tier3_results = await asyncio.wait_for(
                _research_batch(tier3, attributes, context, config_path, tier=3),
                timeout=CATEGORY_TIMEOUT_SECONDS,
            )
            populated.extend(tier3_results)
            done += len(tier3)
            if progress_callback:
                progress_callback("population", done, total)
        except Exception as e:
            logger.warning("Tier 3 research failed: %s", e)
            populated.extend(tier3)

    return populated


async def _research_single_competitor(
    comp: CompetitorEntry,
    attributes: list[CompetitiveAttribute],
    context: ContextSignals,
    config_path: str,
) -> CompetitorEntry:
    """Tier 1: Deep research for a single competitor."""
    query = TIER1_POPULATION_QUERY.format(
        competitor_name=comp.name,
        industry=context.industry_vertical,
        sub_vertical=context.sub_vertical or "General",
        venture_name=context.venture_name,
        solution_category=context.solution_category,
        attributes_list=_format_attributes_list(attributes, "all"),
    )

    researcher = GPTResearcher(query=query, report_type="deep", config_path=config_path)
    await researcher.conduct_research()
    raw_report = await researcher.write_report()

    # Extract sources
    try:
        sources = list(researcher.get_source_urls()) if hasattr(researcher, 'get_source_urls') else []
    except Exception:
        sources = []

    # LLM extraction of structured data
    extracted = await _extract_attributes_from_report(
        raw_report, [comp.name], attributes
    )

    comp_data = extracted.get(comp.name, {})
    now = datetime.now(timezone.utc).isoformat()

    return CompetitorEntry(
        competitor_id=comp.competitor_id,
        name=comp.name,
        tier=comp.tier,
        description=comp.description,
        competitor_type=comp.competitor_type,
        attributes={
            attr_id: CellValue(**cell_data) if isinstance(cell_data, dict) else CellValue(value=str(cell_data))
            for attr_id, cell_data in comp_data.items()
        },
        sources=list(set(comp.sources + sources)),
        confidence=_calculate_confidence(comp_data, attributes),
        last_researched=now,
    )


async def _research_batch(
    batch: list[CompetitorEntry],
    attributes: list[CompetitiveAttribute],
    context: ContextSignals,
    config_path: str,
    tier: int = 2,
) -> list[CompetitorEntry]:
    """Tier 2/3: Batched research for multiple competitors."""
    names = ", ".join(c.name for c in batch)
    priority_filter = "all" if tier == 2 else "required"

    if tier == 2:
        query = TIER2_POPULATION_QUERY.format(
            competitor_names=names,
            industry=context.industry_vertical,
            sub_vertical=context.sub_vertical or "General",
            venture_name=context.venture_name,
            solution_category=context.solution_category,
            attributes_list=_format_attributes_list(
                [a for a in attributes if a.priority in ("required", "important")], "all"
            ),
        )
    else:
        query = TIER3_POPULATION_QUERY.format(
            competitor_names=names,
            industry=context.industry_vertical,
            sub_vertical=context.sub_vertical or "General",
            attributes_list=_format_attributes_list(
                [a for a in attributes if a.priority == "required"], "all"
            ),
        )

    researcher = GPTResearcher(query=query, report_type="deep", config_path=config_path)
    await researcher.conduct_research()
    raw_report = await researcher.write_report()

    try:
        sources = list(researcher.get_source_urls()) if hasattr(researcher, 'get_source_urls') else []
    except Exception:
        sources = []

    extracted = await _extract_attributes_from_report(
        raw_report, [c.name for c in batch], attributes
    )

    now = datetime.now(timezone.utc).isoformat()
    results = []
    for comp in batch:
        comp_data = extracted.get(comp.name, {})
        results.append(CompetitorEntry(
            competitor_id=comp.competitor_id,
            name=comp.name,
            tier=comp.tier,
            description=comp.description,
            competitor_type=comp.competitor_type,
            attributes={
                attr_id: CellValue(**cell_data) if isinstance(cell_data, dict) else CellValue(value=str(cell_data))
                for attr_id, cell_data in comp_data.items()
            },
            sources=list(set(comp.sources + sources)),
            confidence=_calculate_confidence(comp_data, attributes),
            last_researched=now,
        ))

    return results


async def _extract_attributes_from_report(
    raw_report: str,
    competitor_names: list[str],
    attributes: list[CompetitiveAttribute],
) -> dict[str, dict]:
    """Use LLM to extract structured attribute values from a research report."""
    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)

    user_message = POPULATION_EXTRACTION_USER.format(
        competitor_names=", ".join(competitor_names),
        attributes_schema=_format_attributes_schema(attributes),
        raw_report=raw_report[:15000],
    )

    response = client.chat.completions.create(
        model=CONTEXT_LLM_MODEL,
        max_tokens=CONTEXT_LLM_MAX_TOKENS,
        messages=[
            {"role": "system", "content": POPULATION_EXTRACTION_SYSTEM},
            {"role": "user", "content": user_message},
        ],
    )

    response_text = response.choices[0].message.content
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0]

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        logger.warning("Failed to parse attribute extraction response")
        return {}


def _calculate_confidence(comp_data: dict, attributes: list[CompetitiveAttribute]) -> float:
    """Calculate overall confidence as ratio of non-null required/important attributes."""
    important_attrs = [a for a in attributes if a.priority in ("required", "important")]
    if not important_attrs:
        return 0.0
    filled = sum(
        1 for a in important_attrs
        if a.attribute_id in comp_data
        and comp_data[a.attribute_id] is not None
        and (isinstance(comp_data[a.attribute_id], dict) and comp_data[a.attribute_id].get("value") is not None
             or not isinstance(comp_data[a.attribute_id], dict))
    )
    return round(filled / len(important_attrs), 2)


async def populate_venture_column(
    context: ContextSignals,
    attributes: list[CompetitiveAttribute],
    venture_brief_text: str,
) -> CompetitorEntry:
    """Step 4: Populate the venture's own column from the brief (no web research)."""
    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)

    user_message = VENTURE_POPULATION_USER.format(
        venture_brief=venture_brief_text[:8000],
        venture_name=context.venture_name,
        industry=context.industry_vertical,
        geography=context.geography,
        solution_category=context.solution_category,
        stage=context.stage,
        business_model=context.business_model_type,
        problem_summary=context.problem_summary,
        solution_summary=context.solution_summary,
        technology_stack=", ".join(context.technology_stack) if context.technology_stack else "Not specified",
        attributes_schema=_format_attributes_schema(attributes),
    )

    response = client.chat.completions.create(
        model=CONTEXT_LLM_MODEL,
        max_tokens=CONTEXT_LLM_MAX_TOKENS,
        messages=[
            {"role": "system", "content": VENTURE_POPULATION_SYSTEM},
            {"role": "user", "content": user_message},
        ],
    )

    response_text = response.choices[0].message.content
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0]

    try:
        venture_data = json.loads(response_text)
    except json.JSONDecodeError:
        logger.warning("Failed to parse venture column extraction")
        venture_data = {}

    import re
    venture_id = re.sub(r'[^a-z0-9]+', '-', context.venture_name.lower()).strip('-')

    return CompetitorEntry(
        competitor_id=venture_id,
        name=context.venture_name,
        tier=1,
        description=context.solution_summary,
        competitor_type="venture",
        attributes={
            attr_id: CellValue(**cell_data) if isinstance(cell_data, dict) else CellValue(value=str(cell_data))
            for attr_id, cell_data in venture_data.items()
        },
        sources=[],
        confidence=_calculate_confidence(venture_data, attributes),
        last_researched=datetime.now(timezone.utc).isoformat(),
    )
