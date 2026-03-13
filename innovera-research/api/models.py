"""
Pydantic request/response models for the API.
"""
from typing import Literal
from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    """Input from the frontend. All fields are text - no file uploads."""

    document_text: str = Field(
        description="The venture document content as markdown/plain text."
    )

    additional_context: str = Field(
        default="",
        description="Any supplementary context the user wants to provide."
    )

    core_question: str = Field(
        description="The strategic question this research aims to answer."
    )

    success_criteria: list[str] = Field(
        description="List of measurable success criteria."
    )

    # --- Optional configuration ---
    venture_name: str = Field(
        default="",
        description="Override venture name. If empty, extracted from documents."
    )
    categories_to_run: list[str] = Field(
        default_factory=list,
        description="Subset of category IDs to run. Empty = run all."
    )
    max_concurrent: int = Field(
        default=2,
        ge=1, le=6,
        description="Max parallel categories per phase."
    )
    research_mode: Literal["demand_validation", "market_research", "competitive_table"] = Field(
        default="demand_validation",
        description="Which research pipeline to run."
    )
    prebuilt_competitive_table: dict | None = Field(
        default=None,
        description="Pre-built competitive_table.json content. When provided, the CT Phase 0 build is skipped."
    )


CHAIN_MODES = ["competitive_table", "market_research", "demand_validation"]

MODE_LABELS = {
    "competitive_table": "Competitive Table",
    "market_research": "Market Research",
    "demand_validation": "Demand Validation",
}


class ChainRequest(BaseModel):
    """Run all three research chapters sequentially."""

    document_text: str = Field(
        description="The venture document content as markdown/plain text."
    )
    additional_context: str = Field(
        default="",
        description="Any supplementary context the user wants to provide."
    )
    core_question: str = Field(
        description="The strategic question this research aims to answer."
    )
    success_criteria: list[str] = Field(
        description="List of measurable success criteria."
    )
    venture_name: str = Field(
        default="",
        description="Override venture name. If empty, extracted from documents."
    )
    max_concurrent: int = Field(
        default=2,
        ge=1, le=6,
        description="Max parallel categories per phase."
    )
    prebuilt_competitive_table: dict | None = Field(
        default=None,
        description="Pre-built competitive_table.json content. When provided, the CT step is skipped."
    )


class ChainStepInfo(BaseModel):
    step_index: int
    mode: str
    mode_label: str
    run_id: str | None = None
    status: str = "pending"


class ChainResponse(BaseModel):
    chain_id: str
    status: str
    message: str
    steps: list[ChainStepInfo]


class ResearchResponse(BaseModel):
    run_id: str
    status: str
    message: str


class CategoryStatus(BaseModel):
    category_id: str
    category_name: str
    status: str  # "pending" | "running" | "success" | "failed" | "skipped"
    elapsed_seconds: float = 0
    error: str | None = None
    gap_count: int = 0
    source_count: int = 0
    checkpoint_stage: str | None = None
    can_resume: bool = False
    resume_reason: str | None = None
    last_persisted_at: str | None = None


class RunStatus(BaseModel):
    run_id: str
    status: str  # "running" | "completed" | "failed"
    phase: str
    categories: dict[str, CategoryStatus]
    elapsed_seconds: float
    output_files: list[str]
    error: str | None = None
    competitive_table_status: str | None = None  # pending | building | complete | failed
    competitive_table_progress: str | None = None  # e.g. "5/18 competitors populated"
