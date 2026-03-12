"""
Phase definitions and dependency management for research execution.
"""
from evidence_categories.registry import Phase, CATEGORY_REGISTRY, get_categories_by_phase
from market_research.registry import MRPhase, MR_CATEGORY_REGISTRY, get_mr_categories_by_phase


def get_execution_plan() -> list[dict]:
    """
    Return the ordered execution plan for demand validation.

    Phase 1 (Foundation): EC-01, EC-02, EC-05, EC-06, EC-10
    Phase 2 (Competitor-Dependent): EC-03, EC-04, EC-11
    Phase 3 (Synthesis): EC-07, EC-08, EC-09, EC-12, EC-13
    """
    plan = []
    for phase in sorted(Phase):
        category_ids = get_categories_by_phase(phase)
        plan.append({
            "phase": phase.value,
            "phase_name": phase.name,
            "categories": category_ids,
            "parallel": True,
            "wait_for": list(set(
                dep
                for cid in category_ids
                for dep in CATEGORY_REGISTRY[cid].depends_on
            )),
        })
    return plan


def get_mr_execution_plan() -> list[dict]:
    """
    Return the ordered execution plan for market research.

    Phase 1 (Foundation): MR-01, MR-04, MR-06, MR-09
    Phase 2 (Structural): MR-02, MR-03, MR-05
    Phase 3 (Commercial): MR-07, MR-08, MR-10
    """
    plan = []
    for phase in sorted(MRPhase):
        category_ids = get_mr_categories_by_phase(phase)
        plan.append({
            "phase": phase.value,
            "phase_name": phase.name,
            "categories": category_ids,
            "parallel": True,
            "wait_for": list(set(
                dep
                for cid in category_ids
                for dep in MR_CATEGORY_REGISTRY[cid].depends_on
            )),
        })
    return plan
