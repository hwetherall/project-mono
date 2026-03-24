"""
Merge breadth-pass results with depth-pass results.

Depth-pass values take precedence (higher confidence from deep research).
Breadth-pass fills gaps where depth returned null.
"""
import logging
from competitive_table.models import CompetitorEntry, CellValue

logger = logging.getLogger(__name__)


def merge_competitor_results(
    breadth_results: list[CompetitorEntry],
    depth_results: list[CompetitorEntry],
) -> list[CompetitorEntry]:
    """
    For each competitor, merge attributes from both passes.
    Depth-pass values take precedence (higher confidence).
    Breadth-pass fills gaps.
    """
    # Index depth results by competitor_id
    depth_by_id: dict[str, CompetitorEntry] = {
        c.competitor_id: c for c in depth_results
    }

    merged = []
    for breadth_entry in breadth_results:
        depth_entry = depth_by_id.pop(breadth_entry.competitor_id, None)

        if depth_entry is None:
            # Only breadth data exists
            merged.append(breadth_entry)
            continue

        # Merge attributes: depth wins, breadth fills gaps
        merged_attrs: dict[str, CellValue] = {}

        # Start with breadth attrs as base
        for attr_id, cell in breadth_entry.attributes.items():
            merged_attrs[attr_id] = cell

        # Overlay depth attrs (overwrite when depth has a non-null value)
        for attr_id, cell in depth_entry.attributes.items():
            if cell and cell.value is not None:
                merged_attrs[attr_id] = cell
            elif attr_id not in merged_attrs:
                merged_attrs[attr_id] = cell

        # Merge sources
        combined_sources = list(set(breadth_entry.sources + depth_entry.sources))

        # Use the higher confidence score
        confidence = max(breadth_entry.confidence, depth_entry.confidence)

        merged.append(CompetitorEntry(
            competitor_id=depth_entry.competitor_id,
            name=depth_entry.name,
            tier=depth_entry.tier,
            description=depth_entry.description or breadth_entry.description,
            competitor_type=depth_entry.competitor_type,
            attributes=merged_attrs,
            sources=combined_sources,
            confidence=confidence,
            last_researched=depth_entry.last_researched or breadth_entry.last_researched,
        ))

    # Add any depth-only competitors (shouldn't happen, but be safe)
    for remaining in depth_by_id.values():
        merged.append(remaining)

    breadth_total = sum(
        sum(1 for v in c.attributes.values() if v and v.value is not None)
        for c in breadth_results
    )
    depth_total = sum(
        sum(1 for v in c.attributes.values() if v and v.value is not None)
        for c in depth_results
    )
    merged_total = sum(
        sum(1 for v in c.attributes.values() if v and v.value is not None)
        for c in merged
    )
    logger.info(
        "Merge results: breadth=%d cells, depth=%d cells, merged=%d cells",
        breadth_total, depth_total, merged_total,
    )

    return merged
