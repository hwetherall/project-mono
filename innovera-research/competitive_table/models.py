"""
Pydantic data models for the Competitive Table.
"""
from pydantic import BaseModel, Field
from typing import Optional


class CellValue(BaseModel):
    """A single cell in the competitive matrix."""
    value: Optional[str | float | list[str] | bool] = None
    confidence: str = Field(default="unknown", description="high | medium | low | unknown")
    source_url: Optional[str] = None
    notes: str = ""


class CompetitiveAttribute(BaseModel):
    """Definition of a single attribute (Y axis row)."""
    attribute_id: str
    name: str
    description: str = ""
    group: str = Field(description="Logical grouping: profile, commercial, strategic, technical")
    data_type: str = Field(default="text", description="text | numeric | rating | list | boolean")
    priority: str = Field(default="important", description="required | important | optional")


class CompetitorEntry(BaseModel):
    """A single competitor column in the table."""
    competitor_id: str
    name: str
    tier: int = Field(default=2, ge=1, le=3)
    description: str = ""
    competitor_type: str = Field(
        default="direct",
        description="direct | substitute | adjacent | emerging | incumbent",
    )
    attributes: dict[str, CellValue] = Field(default_factory=dict)
    sources: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    last_researched: str = ""


class AttributeGroup(BaseModel):
    """Logical grouping of attributes for rendering."""
    group_id: str
    name: str
    attribute_ids: list[str] = Field(default_factory=list)


class TableMetadata(BaseModel):
    """Statistics and summary for the table."""
    competitor_count: int = 0
    attribute_count: int = 0
    tier1_count: int = 0
    tier2_count: int = 0
    tier3_count: int = 0
    coverage_percent: float = 0.0
    total_sources: int = 0
    research_time_seconds: float = 0.0
    rationale: str = ""
    table_summary: str = ""
    venture_strengths: list[str] = Field(default_factory=list)
    venture_weaknesses: list[str] = Field(default_factory=list)
    dangerous_competitors: list[str] = Field(default_factory=list)


class CompetitiveTableSchema(BaseModel):
    """Output of Step 1 — the schema before population."""
    attributes: list[CompetitiveAttribute] = Field(default_factory=list)
    attribute_groups: list[AttributeGroup] = Field(default_factory=list)
    target_competitor_min: int = 8
    target_competitor_max: int = 25
    seeded_competitors: list[str] = Field(default_factory=list)
    must_include_companies: list[str] = Field(
        default_factory=list,
        description="User-specified companies that MUST appear in the table.",
    )
    custom_parameters: list[str] = Field(
        default_factory=list,
        description="User-specified custom attributes that MUST appear in the table.",
    )
    rationale: str = ""


class CompetitiveTable(BaseModel):
    """The full competitive table artifact."""
    table_id: str
    venture_name: str
    industry: str
    geography: str
    generated_at: str = ""
    attributes: list[CompetitiveAttribute] = Field(default_factory=list)
    competitors: list[CompetitorEntry] = Field(default_factory=list)
    venture_entry: Optional[CompetitorEntry] = None
    attribute_groups: list[AttributeGroup] = Field(default_factory=list)
    metadata: TableMetadata = Field(default_factory=TableMetadata)
