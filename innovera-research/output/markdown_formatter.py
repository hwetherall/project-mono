"""
Markdown output formatter for the human-readable evidence report.
"""
from context_extraction.models import ContextSignals
from evidence_categories.base import CategoryResult
from evidence_categories.registry import CATEGORY_REGISTRY


def format_markdown_report(
    package: dict,
    context: ContextSignals,
    results: dict[str, CategoryResult],
) -> str:
    """Format the evidence package as a human-readable Markdown report."""
    meta = package["research_package"]["metadata"]
    gap_summary = package["research_package"]["gap_summary"]

    sections = []

    # Header
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

    # Evidence Categories
    sections.append("---")
    sections.append("")
    sections.append("## Evidence by Category")
    sections.append("")

    for cid in sorted(results.keys()):
        result = results[cid]
        meta_entry = CATEGORY_REGISTRY.get(cid)

        status_icon = "+" if result.status == "success" else "x" if result.status == "failed" else "~"
        sections.append(f"### {cid}: {result.category_name} [{status_icon}]")
        sections.append("")
        sections.append(f"**Status:** {result.status} | **Time:** {result.execution_time_seconds:.1f}s | **Sources:** {len(result.sources)}")
        sections.append("")

        if result.error:
            sections.append(f"**Error:** {result.error}")
            sections.append("")

        if result.raw_report:
            # Include the raw report (truncated if very long)
            report_text = result.raw_report
            if len(report_text) > 5000:
                report_text = report_text[:5000] + "\n\n... [truncated — see raw report file for full text]"
            sections.append(report_text)
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
