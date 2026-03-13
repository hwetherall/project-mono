"""
Step 2: Competitor discovery via GPT Researcher deep research.
"""
import json
import logging
import re
from datetime import datetime, timezone

from gpt_researcher import GPTResearcher

from competitive_table.models import CompetitorEntry, CompetitiveTableSchema, CellValue
from competitive_table.prompts import COMPETITOR_DISCOVERY_QUERY, POPULATION_EXTRACTION_SYSTEM, POPULATION_EXTRACTION_USER
from context_extraction.models import ContextSignals
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, CONTEXT_LLM_MODEL, CONTEXT_LLM_MAX_TOKENS

logger = logging.getLogger(__name__)


def _slugify(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


async def discover_competitors(
    context: ContextSignals,
    schema: CompetitiveTableSchema,
    config_path: str,
) -> list[CompetitorEntry]:
    """Run GPT Researcher to discover competitors, then parse into structured entries."""

    named_block = ""
    if context.named_competitors:
        names = ", ".join(context.named_competitors)
        named_block = f"\n**Known competitors (must be included):** {names}"

    query = COMPETITOR_DISCOVERY_QUERY.format(
        venture_name=context.venture_name,
        industry=context.industry_vertical,
        sub_vertical=context.sub_vertical or "General",
        geography=context.geography,
        solution_category=context.solution_category,
        problem_summary=context.problem_summary,
        solution_summary=context.solution_summary,
        named_competitors_block=named_block,
        target_min=schema.target_competitor_min,
        target_max=schema.target_competitor_max,
    )

    researcher = GPTResearcher(
        query=query,
        report_type="deep",
        config_path=config_path,
    )
    await researcher.conduct_research()
    raw_report = await researcher.write_report()

    # Extract sources
    sources = []
    try:
        sources = list(researcher.get_source_urls()) if hasattr(researcher, 'get_source_urls') else []
    except Exception:
        pass

    # Parse competitors from the raw report using LLM
    competitors = await _parse_competitors_from_report(raw_report, context, schema, sources)

    # Ensure seeded competitors are included
    found_names = {c.name.lower() for c in competitors}
    for seeded in schema.seeded_competitors:
        if seeded.lower() not in found_names:
            competitors.append(CompetitorEntry(
                competitor_id=_slugify(seeded),
                name=seeded,
                tier=2,
                description=f"Named in venture brief. Details to be researched.",
                competitor_type="direct",
                sources=sources[:3],
                last_researched=datetime.now(timezone.utc).isoformat(),
            ))

    logger.info("Discovered %d competitors", len(competitors))
    return competitors


async def _parse_competitors_from_report(
    raw_report: str,
    context: ContextSignals,
    schema: CompetitiveTableSchema,
    sources: list[str],
) -> list[CompetitorEntry]:
    """Use LLM to extract structured competitor entries from the discovery report."""
    from openai import OpenAI

    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)

    extraction_prompt = f"""Extract competitor entries from the following research report.

For each competitor found, return a JSON array of objects with:
- "name": company name
- "tier": 1, 2, or 3
- "description": one-paragraph summary
- "competitor_type": "direct" | "substitute" | "adjacent" | "emerging" | "incumbent"

Report:
{raw_report[:12000]}

Return ONLY a JSON array. No markdown, no explanation."""

    response = client.chat.completions.create(
        model=CONTEXT_LLM_MODEL,
        max_tokens=CONTEXT_LLM_MAX_TOKENS,
        messages=[
            {"role": "system", "content": "You extract structured data from research reports. Return ONLY valid JSON."},
            {"role": "user", "content": extraction_prompt},
        ],
    )

    response_text = response.choices[0].message.content
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0]

    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError:
        logger.warning("Failed to parse competitor extraction response, falling back to regex")
        return _regex_fallback(raw_report, sources)

    entries = []
    now = datetime.now(timezone.utc).isoformat()
    for item in parsed:
        if not isinstance(item, dict) or "name" not in item:
            continue
        entries.append(CompetitorEntry(
            competitor_id=_slugify(item["name"]),
            name=item["name"],
            tier=item.get("tier", 2),
            description=item.get("description", ""),
            competitor_type=item.get("competitor_type", "direct"),
            sources=sources[:5],
            last_researched=now,
        ))

    return entries


def _regex_fallback(raw_report: str, sources: list[str]) -> list[CompetitorEntry]:
    """Fallback: extract competitor names from bold patterns."""
    names = []
    bold_pattern = re.findall(r'\*\*([A-Z][A-Za-z0-9\s&\.\-]+?)\*\*', raw_report)
    skip_phrases = {
        "direct competitor", "substitute", "competitor", "search for",
        "industry", "geography", "solution", "summary", "conclusion",
        "source", "report", "analysis", "market",
    }
    now = datetime.now(timezone.utc).isoformat()
    seen = set()
    for name in bold_pattern:
        name_clean = name.strip()
        if (
            3 < len(name_clean) < 50
            and name_clean.lower() not in skip_phrases
            and not any(skip in name_clean.lower() for skip in skip_phrases)
            and name_clean.lower() not in seen
        ):
            seen.add(name_clean.lower())
            names.append(name_clean)

    return [
        CompetitorEntry(
            competitor_id=_slugify(n),
            name=n,
            tier=2,
            description="Extracted from report (details pending).",
            competitor_type="direct",
            sources=sources[:3],
            last_researched=now,
        )
        for n in names[:25]
    ]
