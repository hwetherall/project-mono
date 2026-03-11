"""
Registry of all evidence categories with phase assignments and metadata.
"""
from enum import IntEnum
from dataclasses import dataclass, field


class Phase(IntEnum):
    """Execution phases. Lower numbers run first."""
    FOUNDATION = 1
    COMPETITOR_DEPENDENT = 2
    SYNTHESIS = 3


@dataclass
class CategoryMeta:
    """Metadata for a registered category."""
    category_id: str
    category_name: str
    phase: Phase
    research_mode: str  # "deep" | "custom_report"
    depends_on: list[str]
    section_consumption: dict[str, str]


CATEGORY_REGISTRY: dict[str, CategoryMeta] = {
    "EC-01": CategoryMeta(
        category_id="EC-01",
        category_name="Market Sizing & Growth",
        phase=Phase.FOUNDATION,
        research_mode="custom_report",
        depends_on=[],
        section_consumption={
            "S1-B": "primary", "S2-B": "supporting", "S2-C": "supporting",
            "S3-B": "supporting", "S4-B": "primary", "S4-C": "primary",
        }
    ),
    "EC-02": CategoryMeta(
        category_id="EC-02",
        category_name="Competitor Landscape & Positioning",
        phase=Phase.FOUNDATION,
        research_mode="deep",
        depends_on=[],
        section_consumption={
            "S1-A": "supporting", "S2-C": "supporting", "S3-A": "primary",
            "S3-B": "supporting", "S4-B": "supporting", "S4-C": "supporting",
        }
    ),
    "EC-03": CategoryMeta(
        category_id="EC-03",
        category_name="Investment & Financial Signals",
        phase=Phase.COMPETITOR_DEPENDENT,
        research_mode="custom_report",
        depends_on=["EC-02"],
        section_consumption={
            "S2-B": "primary", "S2-C": "primary", "S3-A": "supporting",
            "S3-B": "supporting", "S4-C": "supporting",
        }
    ),
    "EC-04": CategoryMeta(
        category_id="EC-04",
        category_name="Alternative Solution Failures & Reviews",
        phase=Phase.COMPETITOR_DEPENDENT,
        research_mode="deep",
        depends_on=["EC-02"],
        section_consumption={
            "S1-A": "supporting", "S2-C": "supporting", "S3-A": "primary",
            "S3-C": "supporting", "S4-B": "supporting",
        }
    ),
    "EC-05": CategoryMeta(
        category_id="EC-05",
        category_name="Problem Prevalence & Cost Data",
        phase=Phase.FOUNDATION,
        research_mode="deep",
        depends_on=[],
        section_consumption={
            "S1-A": "primary", "S1-B": "primary", "S2-B": "primary",
            "S2-C": "supporting", "S2-D": "primary",
        }
    ),
    "EC-06": CategoryMeta(
        category_id="EC-06",
        category_name="Regulatory & Compliance Environment",
        phase=Phase.FOUNDATION,
        research_mode="deep",
        depends_on=[],
        section_consumption={
            "S2-B": "supporting", "S2-C": "supporting", "S3-B": "primary",
            "S4-A": "primary", "S4-B": "supporting",
        }
    ),
    "EC-07": CategoryMeta(
        category_id="EC-07",
        category_name="Enabling Technology Trends",
        phase=Phase.SYNTHESIS,
        research_mode="deep",
        depends_on=[],
        section_consumption={
            "S1-A": "supporting", "S3-B": "primary", "S2-D": "supporting",
        }
    ),
    "EC-08": CategoryMeta(
        category_id="EC-08",
        category_name="Urgency Drivers & Forcing Functions",
        phase=Phase.SYNTHESIS,
        research_mode="deep",
        depends_on=[],
        section_consumption={
            "S2-B": "supporting", "S3-B": "primary", "S4-B": "primary",
            "S2-D": "primary",
        }
    ),
    "EC-09": CategoryMeta(
        category_id="EC-09",
        category_name="Industry Analyst & Expert Coverage",
        phase=Phase.SYNTHESIS,
        research_mode="deep",
        depends_on=[],
        section_consumption={
            "S2-C": "primary", "S2-B": "supporting", "S2-D": "supporting",
            "S3-B": "supporting",
        }
    ),
    "EC-10": CategoryMeta(
        category_id="EC-10",
        category_name="Voice of Market (Pain Language & Community)",
        phase=Phase.FOUNDATION,
        research_mode="deep",
        depends_on=[],
        section_consumption={
            "S1-A": "supporting", "S2-A": "supporting", "S2-C": "supporting",
            "S3-C": "supporting", "S4-B": "supporting",
        }
    ),
    "EC-11": CategoryMeta(
        category_id="EC-11",
        category_name="Search & Hiring Trends",
        phase=Phase.COMPETITOR_DEPENDENT,
        research_mode="custom_report",
        depends_on=["EC-02"],
        section_consumption={
            "S2-B": "supporting", "S2-C": "supporting", "S3-B": "supporting",
            "S4-B": "supporting",
        }
    ),
    "EC-12": CategoryMeta(
        category_id="EC-12",
        category_name="Budget & Procurement Context",
        phase=Phase.SYNTHESIS,
        research_mode="deep",
        depends_on=[],
        section_consumption={
            "S3-B": "supporting", "S4-A": "primary", "S4-C": "supporting",
        }
    ),
    "EC-13": CategoryMeta(
        category_id="EC-13",
        category_name="Proxy Market Trajectories",
        phase=Phase.SYNTHESIS,
        research_mode="deep",
        depends_on=[],
        section_consumption={
            "S2-B": "supporting", "S2-C": "supporting", "S2-D": "supporting",
            "S3-B": "supporting",
        }
    ),
}


def get_categories_by_phase(phase: Phase) -> list[str]:
    """Return category IDs for a given phase."""
    return [cid for cid, meta in CATEGORY_REGISTRY.items() if meta.phase == phase]


def get_consumption_map() -> dict[str, list[dict]]:
    """
    Build the section -> category consumption map.
    Returns: {"S1-A": [{"category_id": "EC-05", "role": "primary"}, ...], ...}
    """
    consumption: dict[str, list[dict]] = {}
    for cid, meta in CATEGORY_REGISTRY.items():
        for section_id, role in meta.section_consumption.items():
            if section_id not in consumption:
                consumption[section_id] = []
            consumption[section_id].append({
                "category_id": cid,
                "category_name": meta.category_name,
                "role": role,
            })
    return consumption
