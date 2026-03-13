"""
Markdown output formatter for the human-readable evidence report.
"""
from context_extraction.models import ContextSignals
from evidence_categories.base import CategoryResult
from evidence_categories.registry import CATEGORY_REGISTRY
from market_research.registry import MR_CATEGORY_REGISTRY


def format_markdown_report(
    package: dict,
    context: ContextSignals,
    results: dict[str, CategoryResult],
    competitive_table=None,
) -> str:
    """Format the evidence package as a human-readable Markdown report."""
    meta = package["research_package"]["metadata"]
    gap_summary = package["research_package"]["gap_summary"]

    is_market_research = context.research_mode == "market_research"

    sections = []

    # Header
    if is_market_research:
        sections.append(f"# Innovera Market Research Report: {context.venture_name}")
    else:
        sections.append(f"# Innovera Evidence Package: {context.venture_name}")
    sections.append("")
    sections.append(f"**Generated:** {meta['generated_at']}")
    sections.append(f"**Industry:** {context.industry_vertical} / {context.sub_vertical or 'General'}")
    sections.append(f"**Geography:** {context.geography}")
    sections.append(f"**Stage:** {context.stage}")
    sections.append("")

    # Executive Summary
    sections.append("## Executive Summary")
    sections.append("")
    sections.append(f"- **Categories executed:** {meta['categories_executed']}")
    sections.append(f"- **Succeeded:** {meta['categories_succeeded']}")
    sections.append(f"- **Failed:** {meta['categories_failed']}")
    sections.append(f"- **Total sources consulted:** {meta['total_sources_consulted']}")
    sections.append(f"- **Total execution time:** {meta['total_execution_seconds']}s")
    sections.append("")

    if gap_summary["critical_gaps"]:
        sections.append("### Critical Gaps")
        sections.append("")
        for gap in gap_summary["critical_gaps"]:
            sections.append(f"- **{gap['category_id']}** ({gap['category_name']}): {gap['gap']}")
        sections.append("")

    # Context Signals Summary
    sections.append("## Context Signals")
    sections.append("")
    sections.append(f"**Problem:** {context.problem_summary}")
    sections.append("")
    sections.append(f"**Solution:** {context.solution_summary}")
    sections.append("")
    sections.append(f"**Target Customer:** {context.target_customer_summary}")
    sections.append("")
    sections.append(f"**Problem Keywords:** {', '.join(context.problem_keywords)}")
    sections.append("")
    sections.append(f"**Named Competitors:** {', '.join(context.named_competitors) if context.named_competitors else 'None identified'}")
    sections.append("")

    # Competitive Landscape (if table available)
    if competitive_table:
        sections.append("---")
        sections.append("")
        sections.append("## Competitive Landscape")
        sections.append("")

        md = competitive_table.metadata if hasattr(competitive_table, 'metadata') else None
        if md and md.table_summary:
            sections.append(md.table_summary)
            sections.append("")

        # Render the table as a markdown table
        if competitive_table.attributes and competitive_table.competitors:
            # Build header
            all_entries = []
            if competitive_table.venture_entry:
                all_entries.append(competitive_table.venture_entry)
            all_entries.extend(competitive_table.competitors[:15])  # Cap for readability

            header_names = ["Attribute"] + [e.name for e in all_entries]
            sections.append("| " + " | ".join(header_names) + " |")
            sections.append("| " + " | ".join(["---"] * len(header_names)) + " |")

            for attr in competitive_table.attributes:
                row = [f"**{attr.name}**"]
                for entry in all_entries:
                    cell = entry.attributes.get(attr.attribute_id)
                    if cell and cell.value is not None:
                        val = str(cell.value)
                        if len(val) > 60:
                            val = val[:57] + "..."
                        row.append(val)
                    else:
                        row.append("—")
                sections.append("| " + " | ".join(row) + " |")
            sections.append("")

        # Strengths / Weaknesses
        if md and md.venture_strengths:
            sections.append("### Venture Strengths")
            for s in md.venture_strengths:
                sections.append(f"- {s}")
            sections.append("")

        if md and md.venture_weaknesses:
            sections.append("### Venture Weaknesses")
            for w in md.venture_weaknesses:
                sections.append(f"- {w}")
            sections.append("")

        if md and md.dangerous_competitors:
            sections.append("### Most Dangerous Competitors")
            for d in md.dangerous_competitors:
                sections.append(f"- {d}")
            sections.append("")

    # Evidence/Research Categories
    sections.append("---")
    sections.append("")
    if is_market_research:
        sections.append("## Market Research by Category")
    else:
        sections.append("## Evidence by Category")
    sections.append("")

    registry = MR_CATEGORY_REGISTRY if is_market_research else CATEGORY_REGISTRY

    for cid in sorted(results.keys()):
        result = results[cid]
        meta_entry = registry.get(cid)

        status_icon = "+" if result.status == "success" else "x" if result.status == "failed" else "~"
        sections.append(f"### {cid}: {result.category_name} [{status_icon}]")
        sections.append("")
        sections.append(f"**Status:** {result.status} | **Time:** {result.execution_time_seconds:.1f}s | **Sources:** {len(result.sources)}")
        sections.append("")

        if result.error:
            sections.append(f"**Error:** {result.error}")
            sections.append("")

        if result.raw_report:
            # Include the full raw report (no truncation)
            sections.append(result.raw_report)
            sections.append("")

        if result.gaps:
            sections.append("**Gaps:**")
            for gap in result.gaps:
                sections.append(f"- {gap}")
            sections.append("")

        if result.sources:
            sections.append("**Sources:**")
            for src in result.sources[:10]:
                sections.append(f"- {src.get('url', 'N/A')}")
            if len(result.sources) > 10:
                sections.append(f"- ... and {len(result.sources) - 10} more")
            sections.append("")

        sections.append("---")
        sections.append("")

    # Gap Inventory
    sections.append("## Gap Inventory")
    sections.append("")

    if gap_summary["critical_gaps"]:
        sections.append("### Critical")
        for gap in gap_summary["critical_gaps"]:
            sections.append(f"- [{gap['category_id']}] {gap['gap']}")
        sections.append("")

    if gap_summary["moderate_gaps"]:
        sections.append("### Moderate")
        for gap in gap_summary["moderate_gaps"]:
            sections.append(f"- [{gap['category_id']}] {gap['gap']}")
        sections.append("")

    return "\n".join(sections)
