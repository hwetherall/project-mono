"""
Phase definitions and dependency management for research execution.
"""
from evidence_categories.registry import Phase, CATEGORY_REGISTRY, get_categories_by_phase


def get_execution_plan() -> list[dict]:
    """
    Return the ordered execution plan.

    Phase 1 (Foundation): EC-01, EC-02, EC-05, EC-06, EC-10
      - All run in parallel, no dependencies
      - EC-02 produces competitor list needed by Phase 2

    Phase 2 (Competitor-Dependent): EC-03, EC-04, EC-11
      - All run in parallel after Phase 1 completes
      - Each receives competitor list from EC-02

    Phase 3 (Synthesis): EC-07, EC-08, EC-09, EC-12, EC-13
      - All run in parallel after Phase 2 completes
      - No inter-category dependencies
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
