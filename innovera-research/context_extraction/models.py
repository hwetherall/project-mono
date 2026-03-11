"""
Data models for extracted context signals.
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class PriorityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CategoryPriority(BaseModel):
    """Dynamic priority for a single evidence category based on venture context."""
    category_id: str
    priority: PriorityLevel
    rationale: str = Field(description="Why this priority was assigned")


class ContextSignals(BaseModel):
    """
    Structured signals extracted from venture documents.
    These drive query generation across all 13 evidence categories.
    """
    # --- Core Identifiers ---
    venture_name: str
    industry_vertical: str
    sub_vertical: Optional[str] = None
    geography: str
    stage: str = Field(description="e.g., 'Pre-revenue', 'Seed', 'Series A', 'Growth'")
    business_model_type: str = Field(description="e.g., 'B2B SaaS', 'Marketplace', 'Hardware + Software'")
    target_buyer_type: str = Field(description="e.g., 'Enterprise', 'SMB', 'Government', 'Consumer'")
    solution_category: str = Field(description="What product category this falls into")
    parent_company: Optional[str] = None

    # --- Extracted Research Signals ---
    problem_keywords: list[str] = Field(description="Core nouns/verbs from the problem statement")
    industry_terms: list[str] = Field(description="Domain-specific jargon")
    named_competitors: list[str] = Field(default_factory=list, description="Competitors explicitly mentioned")
    named_regulations: list[str] = Field(default_factory=list, description="Regulations, standards, or mandates cited")
    pain_drivers: list[str] = Field(description="Stated causes of customer pain: cost, risk, compliance, speed, etc.")
    customer_roles: list[str] = Field(description="Specific roles mentioned: CTO, ops manager, etc.")
    technology_stack: list[str] = Field(default_factory=list, description="Technologies mentioned: IoT, AI, cloud, etc.")
    workaround_mentions: list[str] = Field(default_factory=list, description="Current solutions or workarounds described")
    geographic_qualifiers: list[str] = Field(description="Country/region-specific context")
    urgency_signals: list[str] = Field(default_factory=list, description="Deadlines, mandates, or timing pressure mentioned")
    market_size_claims: list[str] = Field(default_factory=list, description="Any TAM/SAM figures cited by the venture")
    analogies_mentioned: list[str] = Field(default_factory=list, description="'Like X for Y' or comparable market references")

    # --- Problem Summary (for GPT Researcher prompts) ---
    problem_summary: str = Field(description="2-3 sentence summary of the core problem, written for a research agent")
    solution_summary: str = Field(description="2-3 sentence summary of what the venture does")
    target_customer_summary: str = Field(description="1-2 sentence description of the target customer")

    # --- Dynamic Category Priorities ---
    category_priorities: list[CategoryPriority] = Field(
        description="Priority assignments for each of the 13 evidence categories based on venture context"
    )
