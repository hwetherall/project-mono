"""
Main orchestration for the Consultant Primer phase.

Builds search queries from ContextSignals, calls Tavily API directly with
include_domains, deduplicates results, runs LLM extraction, and returns
ConsultantContext.
"""
import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Optional

import httpx

from consultant_primer.models import ConsultantSource, ConsultantContext
from consultant_primer.domains import (
    get_domains_for_context, firm_name_from_url, tier_from_url,
    TIER1_DOMAINS, TIER2_DOMAINS, TIER3_DOMAINS,
)
from consultant_primer.prompts import (
    CONSULTANT_EXTRACTION_SYSTEM, CONSULTANT_EXTRACTION_USER,
)
from context_extraction.models import ContextSignals
from config.settings import (
    TAVILY_API_KEY,
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, CONTEXT_LLM_MODEL,
    CONSULTANT_PRIMER_MAX_SOURCES,
    CONSULTANT_PRIMER_TIMEOUT,
    CONSULTANT_PRIMER_MAX_CONTENT_CHARS,
)

logger = logging.getLogger(__name__)

TAVILY_SEARCH_URL = "https://api.tavily.com/search"
MAX_CONTENT_PER_SOURCE = 15000  # Truncate per-source content for LLM extraction


def _build_search_queries(context: ContextSignals) -> list[dict]:
    """Build 3-5 targeted Tavily search queries from context signals.

    Returns list of dicts with 'query' and 'domains' keys.
    """
    industry = context.industry_vertical
    geo = context.geography
    year = datetime.now().year

    tier12 = TIER1_DOMAINS + TIER2_DOMAINS
    tier123 = tier12 + TIER3_DOMAINS

    queries = []

    # 1. Industry overview
    queries.append({
        "query": f"{industry} market overview report {geo}",
        "domains": tier12,
    })

    # 2. Market sizing
    queries.append({
        "query": f"{industry} market size TAM {geo} {year}",
        "domains": tier123,
    })

    # 3. Trends / outlook
    queries.append({
        "query": f"{industry} trends outlook forecast {geo}",
        "domains": tier12,
    })

    # 4. Problem-specific
    problem_kw = " ".join(context.problem_keywords[:5])
    solution = context.solution_category
    if problem_kw or solution:
        queries.append({
            "query": f"{problem_kw} {solution} analysis",
            "domains": tier12,
        })

    # 5. Competitive dynamics (if named competitors exist)
    if context.named_competitors:
        comp_str = " ".join(context.named_competitors[:3])
        queries.append({
            "query": f"{industry} competitive landscape {comp_str}",
            "domains": tier123,
        })

    return queries


async def _tavily_search(
    query: str,
    include_domains: list[str],
    client: httpx.AsyncClient,
) -> list[dict]:
    """Execute a single Tavily search with include_domains restriction."""
    payload = {
        "query": query,
        "search_depth": "advanced",
        "include_domains": include_domains,
        "max_results": 10,
        "include_raw_content": True,
        "include_answer": False,
        "api_key": TAVILY_API_KEY,
    }

    try:
        response = await client.post(TAVILY_SEARCH_URL, json=payload, timeout=60.0)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as exc:
        logger.warning("Tavily search failed for query '%s': %s", query[:80], exc)
        return []


def _deduplicate_results(all_results: list[dict]) -> list[dict]:
    """Deduplicate by URL, keeping the version with the longest raw_content."""
    by_url: dict[str, dict] = {}
    for result in all_results:
        url = result.get("url", "")
        if not url:
            continue
        existing = by_url.get(url)
        if existing is None:
            by_url[url] = result
        else:
            # Keep the version with richer content
            new_len = len(result.get("raw_content") or result.get("content") or "")
            old_len = len(existing.get("raw_content") or existing.get("content") or "")
            if new_len > old_len:
                by_url[url] = result
    return list(by_url.values())


async def _extract_from_source(
    result: dict,
    context: ContextSignals,
) -> Optional[ConsultantSource]:
    """Run LLM extraction on a single Tavily result to produce a ConsultantSource."""
    url = result.get("url", "")
    title = result.get("title", "Untitled")
    content = result.get("raw_content") or result.get("content") or ""

    if not content or len(content) < 100:
        return None

    # Truncate content for LLM token limits
    if len(content) > MAX_CONTENT_PER_SOURCE:
        content = content[:MAX_CONTENT_PER_SOURCE]

    firm = firm_name_from_url(url)
    tier = tier_from_url(url)

    try:
        from openai import OpenAI
        client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)

        user_message = CONSULTANT_EXTRACTION_USER.format(
            industry_vertical=context.industry_vertical,
            problem_summary=context.problem_summary,
            geography=context.geography,
            source_title=title,
            source_url=url,
            firm_name=firm,
            content=content,
        )

        response = client.chat.completions.create(
            model=CONTEXT_LLM_MODEL,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": CONSULTANT_EXTRACTION_SYSTEM},
                {"role": "user", "content": user_message},
            ],
        )

        response_text = response.choices[0].message.content
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0]

        extracted = json.loads(response_text)

        return ConsultantSource(
            url=url,
            title=title,
            firm_name=firm,
            tier=tier,
            publication_date=extracted.get("publication_date"),
            raw_content_length=len(content),
            key_facts=extracted.get("key_facts", []),
            market_data_points=extracted.get("market_data_points", []),
            trend_signals=extracted.get("trend_signals", []),
            competitive_mentions=extracted.get("competitive_mentions", []),
            regulatory_mentions=extracted.get("regulatory_mentions", []),
            relevance_score=float(extracted.get("relevance_score", 0.0)),
        )

    except Exception as exc:
        logger.warning("LLM extraction failed for %s: %s", url, exc)
        # Return a minimal source with no extracted findings
        return ConsultantSource(
            url=url,
            title=title,
            firm_name=firm,
            tier=tier,
            raw_content_length=len(content),
        )


async def run_consultant_primer(
    context: ContextSignals,
    progress=None,
) -> ConsultantContext:
    """Main entry point: search consultant domains, extract insights, return ConsultantContext.

    Args:
        context: Extracted venture context signals.
        progress: Optional ProgressTracker / WebSocketProgressBridge for status events.

    Returns:
        ConsultantContext with extracted sources and findings.
    """
    start_time = time.time()

    # Emit: starting
    if progress and hasattr(progress, 'emit_log_detail'):
        progress.emit_log_detail("Searching consultant databases...", "info")
    elif progress:
        progress.log("Searching consultant databases...")

    # Build queries
    search_queries = _build_search_queries(context)
    query_strings = [q["query"] for q in search_queries]

    # Execute all Tavily searches in parallel
    all_results: list[dict] = []
    async with httpx.AsyncClient() as client:
        tasks = [
            _tavily_search(q["query"], q["domains"], client)
            for q in search_queries
        ]
        try:
            search_results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=CONSULTANT_PRIMER_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.warning("Consultant primer search phase timed out after %ds", CONSULTANT_PRIMER_TIMEOUT)
            search_results = []

        for batch in search_results:
            if isinstance(batch, list):
                all_results.extend(batch)

    # Deduplicate
    unique_results = _deduplicate_results(all_results)

    # Emit: search complete
    firm_set = set()
    for r in unique_results:
        firm_set.add(firm_name_from_url(r.get("url", "")))
    firm_set.discard("Unknown")

    if progress and hasattr(progress, 'emit_log_detail'):
        progress.emit_log_detail(
            f"Found {len(unique_results)} consultant sources from {len(firm_set)} firms",
            "info",
        )
    elif progress:
        progress.log(f"Found {len(unique_results)} consultant sources from {len(firm_set)} firms")

    if not unique_results:
        industry = context.industry_vertical
        if progress and hasattr(progress, 'emit_log_detail'):
            progress.emit_log_detail(
                f"No consultant-grade sources found for {industry}. "
                "Research will proceed with web sources only.",
                "warning",
            )
        elif progress:
            progress.log(
                f"No consultant-grade sources found for {industry}. "
                "Research will proceed with web sources only."
            )
        elapsed = time.time() - start_time
        return ConsultantContext(
            search_queries_used=query_strings,
            execution_time_seconds=elapsed,
        )

    # Cap the number of sources to extract
    results_to_extract = unique_results[:CONSULTANT_PRIMER_MAX_SOURCES]

    # Emit: extracting
    if progress and hasattr(progress, 'emit_log_detail'):
        progress.emit_log_detail("Extracting insights from consultant reports...", "info")
    elif progress:
        progress.log("Extracting insights from consultant reports...")

    # Run LLM extraction (sequential to avoid rate limits on the context LLM)
    sources: list[ConsultantSource] = []
    for result in results_to_extract:
        try:
            source = await asyncio.wait_for(
                _extract_from_source(result, context),
                timeout=60,  # 60s per source extraction
            )
            if source:
                sources.append(source)
        except asyncio.TimeoutError:
            logger.warning("Extraction timed out for %s", result.get("url", "unknown"))
        except Exception as exc:
            logger.warning("Extraction error for %s: %s", result.get("url", "unknown"), exc)

    # Sort by tier (lower tier = higher authority), then by relevance
    sources.sort(key=lambda s: (s.tier, -s.relevance_score))

    # Enforce max content chars by trimming sources if needed
    total_chars = 0
    trimmed_sources = []
    for s in sources:
        source_chars = sum(
            len(f) for f in s.key_facts + s.market_data_points +
            s.trend_signals + s.competitive_mentions + s.regulatory_mentions
        )
        if total_chars + source_chars <= CONSULTANT_PRIMER_MAX_CONTENT_CHARS:
            trimmed_sources.append(s)
            total_chars += source_chars
        else:
            break
    sources = trimmed_sources

    # Build context
    elapsed = time.time() - start_time
    consultant_context = ConsultantContext(
        sources=sources,
        total_sources_found=len(unique_results),
        total_sources_extracted=len(sources),
        tier1_count=sum(1 for s in sources if s.tier == 1),
        tier2_count=sum(1 for s in sources if s.tier == 2),
        tier3_count=sum(1 for s in sources if s.tier == 3),
        search_queries_used=query_strings,
        execution_time_seconds=elapsed,
    )

    # Emit: complete
    firms_found = sorted(set(s.firm_name for s in sources))
    if progress and hasattr(progress, 'emit_log_detail'):
        progress.emit_log_detail(
            f"Consultant primer complete: {len(sources)} sources from {', '.join(firms_found) or 'none'}",
            "success",
        )
    elif progress:
        progress.log(
            f"Consultant primer complete: {len(sources)} sources from {', '.join(firms_found) or 'none'}"
        )

    return consultant_context
