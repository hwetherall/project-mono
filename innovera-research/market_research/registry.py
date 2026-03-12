"""
Registry of all market research categories with phase assignments and metadata.
"""
from enum import IntEnum
from dataclasses import dataclass, field


class MRPhase(IntEnum):
    """Execution phases for market research. Lower numbers run first."""
    FOUNDATION = 1
    STRUCTURAL = 2
    COMMERCIAL = 3


@dataclass
class MRCategoryMeta:
    """Metadata for a registered market research category."""
    category_id: str
    category_name: str
    phase: MRPhase
    research_mode: str  # all "deep" for MR
    depends_on: list[str]
    master_table_ids: list[int]
    section_consumption: dict[str, str] = field(default_factory=dict)


MR_CATEGORY_REGISTRY: dict[str, MRCategoryMeta] = {
    "MR-01a": MRCategoryMeta(
        category_id="MR-01a",
        category_name="Market Definition & Boundaries",
        phase=MRPhase.FOUNDATION,
        research_mode="deep",
        depends_on=[],
        master_table_ids=list(range(1, 8)),
    ),
    "MR-01b": MRCategoryMeta(
        category_id="MR-01b",
        category_name="Market Sizing & Methodology",
        phase=MRPhase.FOUNDATION,
        research_mode="deep",
        depends_on=[],
        master_table_ids=list(range(8, 19)) + [101],
    ),
    "MR-02": MRCategoryMeta(
        category_id="MR-02",
        category_name="SAM / SOM / Reachability",
        phase=MRPhase.STRUCTURAL,
        research_mode="deep",
        depends_on=["MR-01a", "MR-01b", "MR-06a", "MR-06b"],
        master_table_ids=list(range(19, 29)),
    ),
    "MR-03": MRCategoryMeta(
        category_id="MR-03",
        category_name="Segments & Concentration",
        phase=MRPhase.STRUCTURAL,
        research_mode="deep",
        depends_on=["MR-01a", "MR-01b", "MR-06a", "MR-06b"],
        master_table_ids=list(range(29, 41)) + [122],
    ),
    "MR-04": MRCategoryMeta(
        category_id="MR-04",
        category_name="Trends & Growth Quality",
        phase=MRPhase.FOUNDATION,
        research_mode="deep",
        depends_on=[],
        master_table_ids=list(range(41, 51)),
    ),
    "MR-05": MRCategoryMeta(
        category_id="MR-05",
        category_name="Value Chain & Whitespace",
        phase=MRPhase.STRUCTURAL,
        research_mode="deep",
        depends_on=["MR-06a", "MR-06b"],
        master_table_ids=list(range(51, 60)) + list(range(116, 122)) + [123],
    ),
    "MR-06a": MRCategoryMeta(
        category_id="MR-06a",
        category_name="Competitor Identification",
        phase=MRPhase.FOUNDATION,
        research_mode="deep",
        depends_on=[],
        master_table_ids=list(range(60, 65)),
    ),
    "MR-06b": MRCategoryMeta(
        category_id="MR-06b",
        category_name="Competitive Intelligence",
        phase=MRPhase.FOUNDATION,
        research_mode="deep",
        depends_on=[],
        master_table_ids=list(range(103, 108)),
    ),
    "MR-07": MRCategoryMeta(
        category_id="MR-07",
        category_name="Buying Process, Budget & Pricing",
        phase=MRPhase.COMMERCIAL,
        research_mode="deep",
        depends_on=["MR-03", "MR-06a", "MR-06b"],
        master_table_ids=list(range(65, 79)) + [102] + list(range(108, 116)) + [124],
    ),
    "MR-08": MRCategoryMeta(
        category_id="MR-08",
        category_name="Adoption & Expansion Dynamics",
        phase=MRPhase.COMMERCIAL,
        research_mode="deep",
        depends_on=["MR-03", "MR-06a", "MR-06b"],
        master_table_ids=list(range(79, 85)),
    ),
    "MR-09": MRCategoryMeta(
        category_id="MR-09",
        category_name="Regulation & Platform Shifts",
        phase=MRPhase.FOUNDATION,
        research_mode="deep",
        depends_on=[],
        master_table_ids=list(range(85, 91)) + list(range(125, 130)),
    ),
    "MR-10": MRCategoryMeta(
        category_id="MR-10",
        category_name="Barriers, Saturation & Ecosystem Power",
        phase=MRPhase.COMMERCIAL,
        research_mode="deep",
        depends_on=["MR-05", "MR-06a", "MR-06b", "MR-03"],
        master_table_ids=list(range(91, 101)) + [130],
    ),
}


def get_mr_categories_by_phase(phase: MRPhase) -> list[str]:
    """Return MR category IDs for a given phase."""
    return [cid for cid, meta in MR_CATEGORY_REGISTRY.items() if meta.phase == phase]


def get_mr_consumption_map() -> dict[str, list[dict]]:
    """Build section -> category consumption map for MR categories."""
    consumption: dict[str, list[dict]] = {}
    for cid, meta in MR_CATEGORY_REGISTRY.items():
        for section_id, role in meta.section_consumption.items():
            consumption.setdefault(section_id, []).append({
                "category_id": cid,
                "category_name": meta.category_name,
                "role": role,
            })
    return consumption
