"""
Steps 3–4: Populate the competitive table with researched data.
Tier 1 = one deep research call per competitor.
Tier 2 = batched 3–5 per call.
Tier 3 = single summary call.
Step 4 = Venture column from brief (no web research).

Includes retry logic: if a research call returns an empty or near-empty
report, the competitor is retried up to MAX_RETRIES times before giving up.
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
import re as _re

from competitive_table.prompts import (
    TIER1_POPULATION_QUERY, TIER2_POPULATION_QUERY, TIER3_POPULATION_QUERY,
    POPULATION_EXTRACTION_SYSTEM, POPULATION_EXTRACTION_USER,
    VENTURE_POPULATION_SYSTEM, VENTURE_POPULATION_USER,
)
from competitive_table.breadth_pass import breadth_pass
from competitive_table.result_merger import merge_competitor_results
from context_extraction.models import ContextSignals
from config.settings import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL,
    CONTEXT_LLM_MODEL, CONTEXT_LLM_MAX_TOKENS,
    MAX_CONCURRENT_CATEGORIES, CATEGORY_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)

# Retry settings
MAX_RETRIES = 2
MIN_REPORT_LENGTH = 200  # characters — anything shorter is considered empty
MIN_FILLED_ATTRS = 3     # require at least this many non-null attributes


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


# Suffixes stripped during fuzzy name normalization
_CORP_SUFFIXES = _re.compile(
    r"\s*\b(inc\.?|ltd\.?|llc|corp\.?|corporation|company|co\.?|plc|gmbh|s\.?a\.?|ag|n\.?v\.?)\s*$",
    _re.IGNORECASE,
)


def _normalize_name(name: str) -> str:
    """Normalize a company name for fuzzy matching."""
    # Strip parentheticals: "TE Connectivity (Medical)" → "TE Connectivity"
    name = _re.sub(r"\s*\(.*?\)\s*", " ", name)
    # Strip corporate suffixes
    name = _CORP_SUFFIXES.sub("", name)
    # Lowercase, collapse whitespace
    return " ".join(name.lower().split())


def _fuzzy_match_name(target: str, candidates: dict[str, dict]) -> dict | None:
    """Try to match target name against candidate keys with fuzzy fallback.

    Returns the matched value dict, or None.
    """
    # 1. Exact match
    if target in candidates:
        return candidates[target]

    # 2. Case-insensitive match
    target_lower = target.lower()
    for key, val in candidates.items():
        if key.lower() == target_lower:
            return val

    # 3. Normalized match (strip suffixes, parentheticals)
    target_norm = _normalize_name(target)
    for key, val in candidates.items():
        if _normalize_name(key) == target_norm:
            return val

    # 4. Substring containment (either direction)
    for key, val in candidates.items():
        key_norm = _normalize_name(key)
        if target_norm in key_norm or key_norm in target_norm:
            return val

    # 5. First-word match (e.g., "Abbott Labs" ↔ "Abbott Laboratories")
    target_first = target_norm.split()[0] if target_norm else ""
    if len(target_first) >= 4:
        for key, val in candidates.items():
            key_first = _normalize_name(key).split()[0] if _normalize_name(key) else ""
            if target_first == key_first:
                return val

    return None


async def populate_table(
    competitors: list[CompetitorEntry],
    attributes: list[CompetitiveAttribute],
    context: ContextSignals,
    config_path: str,
    progress_callback=None,
    run_id: str | None = None,
) -> list[CompetitorEntry]:
    """Populate attribute values using a two-pass strategy:
    Pass 1 (breadth): lightweight Tavily search for basic facts on ALL competitors.
    Pass 2 (depth): existing tiered deep research for specialized attributes.
    Results are merged with depth taking precedence.
    """
    # --- Pass 1: Breadth (basic facts for ALL competitors) ---
    logger.info("Starting breadth pass for %d competitors", len(competitors))
    try:
        breadth_results = await breadth_pass(competitors, attributes, progress_callback)
    except Exception as exc:
        logger.warning("Breadth pass failed (non-blocking): %s", exc)
        breadth_results = list(competitors)

    # --- Pass 2: Depth (tiered deep research) ---
    logger.info("Starting depth pass for %d competitors", len(competitors))
    depth_results = await _depth_pass(
        competitors, attributes, context, config_path, progress_callback,
    )

    # --- Merge: depth wins, breadth fills gaps ---
    return merge_competitor_results(breadth_results, depth_results)


async def _depth_pass(
    competitors: list[CompetitorEntry],
    attributes: list[CompetitiveAttribute],
    context: ContextSignals,
    config_path: str,
    progress_callback=None,
) -> list[CompetitorEntry]:
    """Original tiered research logic (T1 individual, T2 batched, T3 summary)."""
    tier1 = [c for c in competitors if c.tier == 1]
    tier2 = [c for c in competitors if c.tier == 2]
    tier3 = [c for c in competitors if c.tier == 3]

    populated = []
    total = len(competitors)
    done = 0

    # --- Tier 1: One call per competitor (with retry) ---
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_CATEGORIES)

    async def research_tier1(comp: CompetitorEntry) -> CompetitorEntry:
        nonlocal done
        async with semaphore:
            last_result = comp
            for attempt in range(1, MAX_RETRIES + 2):  # 1 initial + MAX_RETRIES retries
                try:
                    result = await _research_single_competitor(comp, attributes, context, config_path)
                    filled = _count_filled(result)
                    if filled >= MIN_FILLED_ATTRS:
                        done += 1
                        if progress_callback:
                            progress_callback("population", done, total)
                        return result
                    # Not enough data — retry
                    last_result = result
                    if attempt <= MAX_RETRIES:
                        logger.info(
                            "Tier 1 research for %s returned only %d attrs (attempt %d/%d), retrying...",
                            comp.name, filled, attempt, MAX_RETRIES + 1,
                        )
                    else:
                        logger.warning(
                            "Tier 1 research for %s still sparse after %d attempts (%d attrs filled)",
                            comp.name, attempt, filled,
                        )
                except asyncio.TimeoutError:
                    logger.warning("Tier 1 research timed out for %s (attempt %d)", comp.name, attempt)
                except Exception as e:
                    logger.warning("Tier 1 research failed for %s (attempt %d): %s", comp.name, attempt, e)

            done += 1
            if progress_callback:
                progress_callback("population", done, total)
            return last_result

    if tier1:
        tier1_tasks = [
            asyncio.wait_for(research_tier1(c), timeout=CATEGORY_TIMEOUT_SECONDS * (MAX_RETRIES + 1))
            for c in tier1
        ]
        tier1_results = await asyncio.gather(*tier1_tasks, return_exceptions=True)
        for i, result in enumerate(tier1_results):
            populated.append(result if isinstance(result, CompetitorEntry) else tier1[i])

    # --- Tier 2: Batched 3-5 per call (PARALLEL batches with semaphore) ---
    batch_size = 4
    if tier2:
        t2_batches = [
            tier2[i:i + batch_size] for i in range(0, len(tier2), batch_size)
        ]

        async def research_t2_batch(batch: list[CompetitorEntry]) -> list[CompetitorEntry]:
            nonlocal done
            async with semaphore:
                best_results = list(batch)
                for attempt in range(1, MAX_RETRIES + 2):
                    try:
                        batch_results = await asyncio.wait_for(
                            _research_batch(batch, attributes, context, config_path, tier=2),
                            timeout=CATEGORY_TIMEOUT_SECONDS,
                        )
                        avg_filled = sum(_count_filled(r) for r in batch_results) / max(len(batch_results), 1)
                        best_results = batch_results
                        if avg_filled >= MIN_FILLED_ATTRS:
                            break
                        if attempt <= MAX_RETRIES:
                            names = ", ".join(c.name for c in batch)
                            logger.info("Tier 2 batch [%s] avg %.1f attrs (attempt %d), retrying...", names, avg_filled, attempt)
                        else:
                            logger.warning("Tier 2 batch still sparse after %d attempts (avg %.1f attrs)", attempt, avg_filled)
                    except Exception as e:
                        logger.warning("Tier 2 batch failed (attempt %d): %s", attempt, e)

                done += len(batch)
                if progress_callback:
                    progress_callback("population", done, total)
                return best_results

        t2_tasks = [research_t2_batch(batch) for batch in t2_batches]
        t2_results = await asyncio.gather(*t2_tasks, return_exceptions=True)
        for i, result in enumerate(t2_results):
            if isinstance(result, list):
                populated.extend(result)
            else:
                logger.warning("Tier 2 batch %d failed: %s", i, result)
                populated.extend(t2_batches[i])

    # --- Tier 3: Single summary call (with retry) ---
    if tier3:
        best_results = list(tier3)
        for attempt in range(1, MAX_RETRIES + 2):
            try:
                tier3_results = await asyncio.wait_for(
                    _research_batch(tier3, attributes, context, config_path, tier=3),
                    timeout=CATEGORY_TIMEOUT_SECONDS,
                )
                avg_filled = sum(_count_filled(r) for r in tier3_results) / max(len(tier3_results), 1)
                best_results = tier3_results
                if avg_filled >= MIN_FILLED_ATTRS or attempt > MAX_RETRIES:
                    break
                logger.info("Tier 3 avg %.1f attrs (attempt %d), retrying...", avg_filled, attempt)
            except Exception as e:
                logger.warning("Tier 3 research failed (attempt %d): %s", attempt, e)

        populated.extend(best_results)
        done += len(tier3)
        if progress_callback:
            progress_callback("population", done, total)

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

    # Validate report content
    if not raw_report or len(raw_report.strip()) < MIN_REPORT_LENGTH:
        logger.warning(
            "GPTResearcher returned empty/short report for %s (%d chars)",
            comp.name, len(raw_report.strip()) if raw_report else 0,
        )
        # Return entry with empty attributes so retry logic can detect it
        return CompetitorEntry(
            competitor_id=comp.competitor_id,
            name=comp.name,
            tier=comp.tier,
            description=comp.description,
            competitor_type=comp.competitor_type,
            attributes={},
            sources=comp.sources,
            confidence=0.0,
            last_researched=datetime.now(timezone.utc).isoformat(),
        )

    # Extract sources
    try:
        sources = list(researcher.get_source_urls()) if hasattr(researcher, 'get_source_urls') else []
    except Exception:
        sources = []

    # LLM extraction of structured data
    extracted = await _extract_attributes_from_report(
        raw_report, [comp.name], attributes
    )

    comp_data = _fuzzy_match_name(comp.name, extracted) or {}
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

    # Validate report content
    if not raw_report or len(raw_report.strip()) < MIN_REPORT_LENGTH:
        names = ", ".join(c.name for c in batch)
        logger.warning(
            "GPTResearcher returned empty/short report for batch [%s] (%d chars)",
            names, len(raw_report.strip()) if raw_report else 0,
        )
        # Return original entries so retry logic can detect sparse results
        return list(batch)

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
        comp_data = _fuzzy_match_name(comp.name, extracted) or {}
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

    CHUNK_SIZE = 50000
    OVERLAP = 2000

    # If the report fits in one chunk, extract directly
    if len(raw_report) <= CHUNK_SIZE:
        return _extract_single_chunk(client, competitor_names, attributes, raw_report)

    # Chunked extraction for very long reports
    logger.info("Report length %d chars — splitting into overlapping chunks", len(raw_report))
    merged: dict[str, dict] = {}
    offset = 0
    while offset < len(raw_report):
        chunk = raw_report[offset : offset + CHUNK_SIZE]
        chunk_result = _extract_single_chunk(client, competitor_names, attributes, chunk)

        # Merge: keep higher-confidence values
        for comp_name, attrs in chunk_result.items():
            if comp_name not in merged:
                merged[comp_name] = {}
            for attr_id, cell in attrs.items():
                existing = merged[comp_name].get(attr_id)
                if existing is None:
                    merged[comp_name][attr_id] = cell
                elif isinstance(cell, dict) and cell.get("value") is not None:
                    if existing.get("value") is None:
                        merged[comp_name][attr_id] = cell

        offset += CHUNK_SIZE - OVERLAP

    return merged


def _extract_single_chunk(
    client,
    competitor_names: list[str],
    attributes: list[CompetitiveAttribute],
    report_chunk: str,
) -> dict[str, dict]:
    """Extract attributes from a single report chunk."""
    user_message = POPULATION_EXTRACTION_USER.format(
        competitor_names=", ".join(competitor_names),
        attributes_schema=_format_attributes_schema(attributes),
        raw_report=report_chunk,
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
        # Try to salvage partial JSON
        logger.warning("Failed to parse attribute extraction response, attempting salvage")
        start = response_text.find("{")
        end = response_text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(response_text[start : end + 1])
            except json.JSONDecodeError:
                pass
        logger.warning("JSON salvage failed — returning empty extraction")
        return {}


def _count_filled(entry: CompetitorEntry) -> int:
    """Count attributes with non-null values."""
    return sum(
        1 for v in entry.attributes.values()
        if v and v.value is not None
    )


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
