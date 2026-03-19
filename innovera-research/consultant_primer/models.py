"""
Data models for the Consultant Primer phase.
"""
from pydantic import BaseModel, Field
from typing import Optional


class ConsultantSource(BaseModel):
    """A single page/report from a consulting firm."""
    url: str
    title: str
    firm_name: str
    tier: int = Field(description="1=MBB, 2=Big4+, 3=Analyst, 4=Sector-specific")
    publication_date: Optional[str] = None
    raw_content_length: int = 0
    key_facts: list[str] = Field(default_factory=list)
    market_data_points: list[str] = Field(default_factory=list)
    trend_signals: list[str] = Field(default_factory=list)
    competitive_mentions: list[str] = Field(default_factory=list)
    regulatory_mentions: list[str] = Field(default_factory=list)
    relevance_score: float = Field(default=0.0, description="0-1 LLM-assessed relevance to the venture")


class ConsultantContext(BaseModel):
    """Aggregated consultant knowledge for a research run."""
    sources: list[ConsultantSource] = Field(default_factory=list)
    total_sources_found: int = 0
    total_sources_extracted: int = 0
    tier1_count: int = 0
    tier2_count: int = 0
    tier3_count: int = 0
    search_queries_used: list[str] = Field(default_factory=list)
    execution_time_seconds: float = 0.0

    @property
    def has_consultant_coverage(self) -> bool:
        return len(self.sources) > 0

    @property
    def coverage_summary(self) -> str:
        if not self.sources:
            return "No consultant sources found"
        firms = sorted(set(s.firm_name for s in self.sources))
        return f"{len(self.sources)} sources from {', '.join(firms)}"

    def get_context_text(self, max_chars: int = 50000) -> str:
        """Build a single text block of consultant findings for injection into GPT Researcher."""
        parts = ["## Consultant & Analyst Report Findings\n"]
        parts.append(
            "The following facts and insights were extracted from consulting firm and industry analyst reports. "
            "Use these as high-authority reference points. Cite the source when referencing these findings.\n"
        )

        char_count = sum(len(p) for p in parts)
        for source in sorted(self.sources, key=lambda s: s.tier):
            source_header = f"\n### {source.firm_name} — {source.title}\n"
            source_header += f"Source: {source.url}\n"

            findings = []
            for fact in source.key_facts:
                findings.append(f"- {fact}")
            for dp in source.market_data_points:
                findings.append(f"- [Market Data] {dp}")
            for trend in source.trend_signals:
                findings.append(f"- [Trend] {trend}")
            for comp in source.competitive_mentions:
                findings.append(f"- [Competitive] {comp}")
            for reg in source.regulatory_mentions:
                findings.append(f"- [Regulatory] {reg}")

            block = source_header + "\n".join(findings) + "\n"
            if char_count + len(block) > max_chars:
                break
            parts.append(block)
            char_count += len(block)

        return "\n".join(parts)
