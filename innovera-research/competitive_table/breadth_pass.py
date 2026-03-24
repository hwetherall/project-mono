"""
Breadth Pass: Lightweight first pass to get basic facts for ALL competitors.

Uses direct Tavily search (no GPTResearcher overhead) + a small LLM extraction
call per competitor. Runs all competitors in parallel with rate-limit semaphore.

Cost: ~$0.05-0.10 per competitor (1 Tavily basic search + 1 small LLM call).
"""
import asyncio
import json
import logging
from typing import Optional

import httpx
from openai import OpenAI

from competitive_table.models import (
    CompetitiveAttribute, CompetitorEntry, CellValue,
)
from competitive_table.prompts import (
    BREADTH_EXTRACTION_SYSTEM, BREADTH_EXTRACTION_USER,
)
from config.settings import (
    TAVILY_API_KEY,
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, CONTEXT_LLM_MODEL,
)

logger = logging.getLogger(__name__)

TAVILY_SEARCH_URL = "https://api.tavily.com/search"

# Basic attributes that the breadth pass targets — these are cheap to find
# and provide a baseline for every competitor even if deep research fails.
BASIC_ATTR_IDS = {
    "description", "year_founded", "hq_location", "revenue_estimate",
    "employee_count", "ownership_structure", "primary_product_category",
    "business_model_type",
}

# Concurrency: Tavily handles high concurrency well
BREADTH_SEMAPHORE_LIMIT = 10


async def breadth_pass(
    competitors: list[CompetitorEntry],
    attributes: list[CompetitiveAttribute],
    progress_callback=None,
) -> list[CompetitorEntry]:
    """
    For each competitor, run 1 Tavily basic search for basic facts,
    then extract basic attributes via a single cheap LLM call.
    All competitors run in parallel (with semaphore for rate limiting).
    """
    # Filter attributes to only the basic ones that exist in the schema
    basic_attrs = [a for a in attributes if a.attribute_id in BASIC_ATTR_IDS]
    if not basic_attrs:
        # Fallback: take the first 8 required/important attributes
        basic_attrs = [
            a for a in attributes if a.priority in ("required", "important")
        ][:8]

    if not basic_attrs:
        logger.warning("No basic attributes found for breadth pass, skipping")
        return list(competitors)

    semaphore = asyncio.Semaphore(BREADTH_SEMAPHORE_LIMIT)
    total = len(competitors)
    done = 0

    async def research_one(comp: CompetitorEntry) -> CompetitorEntry:
        nonlocal done
        async with semaphore:
            try:
                result = await _breadth_research_single(comp, basic_attrs)
            except Exception as exc:
                logger.warning("Breadth pass failed for %s: %s", comp.name, exc)
                result = comp
            done += 1
            if progress_callback:
                progress_callback("breadth_pass", done, total)
            return result

    async with httpx.AsyncClient() as http_client:
        # Store the http client for use by _tavily_search_basic
        _breadth_research_single._http_client = http_client
        results = await asyncio.gather(
            *[research_one(c) for c in competitors],
            return_exceptions=True,
        )

    # Replace exceptions with original entries
    final = []
    for i, result in enumerate(results):
        if isinstance(result, CompetitorEntry):
            final.append(result)
        else:
            logger.warning("Breadth pass exception for %s: %s", competitors[i].name, result)
            final.append(competitors[i])
    return final


async def _breadth_research_single(
    comp: CompetitorEntry,
    basic_attrs: list[CompetitiveAttribute],
) -> CompetitorEntry:
    """Run Tavily search + LLM extraction for one competitor's basic facts."""
    http_client = getattr(_breadth_research_single, "_http_client", None)
    if http_client is None:
        http_client = httpx.AsyncClient()

    # 1. Tavily basic search
    query = f"{comp.name} company overview founded headquarters revenue employees"
    results = await _tavily_search_basic(query, http_client)

    if not results:
        logger.info("Breadth pass: no Tavily results for %s", comp.name)
        return comp

    # 2. Concatenate top results (cap at 8K chars)
    search_content = _build_search_content(results, max_chars=8000)

    # 3. LLM extraction for basic attributes
    extracted = await _extract_basic_attrs(comp.name, search_content, basic_attrs)

    if not extracted:
        return comp

    # 4. Build updated CompetitorEntry with basic attrs populated
    from datetime import datetime, timezone
    new_attrs = dict(comp.attributes)  # Preserve any existing attrs
    for attr_id, cell_data in extracted.items():
        if attr_id not in new_attrs or (
            attr_id in new_attrs and new_attrs[attr_id].value is None
        ):
            if isinstance(cell_data, dict):
                new_attrs[attr_id] = CellValue(**cell_data)
            else:
                new_attrs[attr_id] = CellValue(value=str(cell_data))

    # Collect source URLs from search results
    source_urls = [r.get("url", "") for r in results if r.get("url")]

    return CompetitorEntry(
        competitor_id=comp.competitor_id,
        name=comp.name,
        tier=comp.tier,
        description=comp.description,
        competitor_type=comp.competitor_type,
        attributes=new_attrs,
        sources=list(set(comp.sources + source_urls)),
        confidence=comp.confidence,
        last_researched=datetime.now(timezone.utc).isoformat(),
    )


async def _tavily_search_basic(
    query: str,
    client: httpx.AsyncClient,
) -> list[dict]:
    """Execute a single Tavily basic search (no domain restriction)."""
    payload = {
        "query": query,
        "search_depth": "basic",
        "max_results": 5,
        "include_raw_content": False,
        "include_answer": False,
        "api_key": TAVILY_API_KEY,
    }

    try:
        response = await client.post(TAVILY_SEARCH_URL, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as exc:
        logger.warning("Tavily basic search failed for '%s': %s", query[:80], exc)
        return []


def _build_search_content(results: list[dict], max_chars: int = 8000) -> str:
    """Concatenate search result content, capped at max_chars."""
    parts = []
    total = 0
    for r in results:
        title = r.get("title", "")
        url = r.get("url", "")
        content = r.get("content", "")
        snippet = f"### {title}\nURL: {url}\n{content}\n\n"
        if total + len(snippet) > max_chars:
            remaining = max_chars - total
            if remaining > 100:
                parts.append(snippet[:remaining])
            break
        parts.append(snippet)
        total += len(snippet)
    return "".join(parts)


async def _extract_basic_attrs(
    competitor_name: str,
    search_content: str,
    attributes: list[CompetitiveAttribute],
) -> dict:
    """Use LLM to extract basic attributes from search content."""
    attrs_schema = "\n".join(
        f"- {a.attribute_id}: {a.name} — {a.description}" for a in attributes
    )

    user_message = BREADTH_EXTRACTION_USER.format(
        competitor_name=competitor_name,
        search_content=search_content,
        attributes_schema=attrs_schema,
    )

    try:
        client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)
        response = client.chat.completions.create(
            model=CONTEXT_LLM_MODEL,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": BREADTH_EXTRACTION_SYSTEM},
                {"role": "user", "content": user_message},
            ],
        )

        response_text = response.choices[0].message.content
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0]

        return json.loads(response_text)
    except json.JSONDecodeError:
        logger.warning("Breadth extraction JSON parse failed for %s", competitor_name)
        return {}
    except Exception as exc:
        logger.warning("Breadth extraction failed for %s: %s", competitor_name, exc)
        return {}
