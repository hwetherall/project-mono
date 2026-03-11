# Innovera Web Research Pre-Step: Claude Code Build Spec v2

## Overview

Build a Python-based research orchestration tool that gathers web evidence across 13 evidence categories before the Analyst-Associate-Partner pipeline runs. The tool uses:

- **Claude API** (via Anthropic SDK) for the initial context extraction from venture documents
- **GPT Researcher** (pip package) for all web research — using **deep research mode** for landscape categories and **custom report mode** for targeted lookup categories
- **Tavily** as GPT Researcher's search backend (configured within GPT Researcher, not called directly)

The operator provides venture documents and metadata. The tool produces a structured evidence package (YAML + Markdown) that feeds into the Innovera analyst frameworks.

---

## 1. Prerequisites & Dependencies

### 1.1 Python Environment

```
Python >= 3.11
```

### 1.2 API Keys Required

```env
# .env file
OPENAI_API_KEY=sk-...              # For GPT Researcher's LLM calls
TAVILY_API_KEY=tvly-...            # For GPT Researcher's web search backend
ANTHROPIC_API_KEY=sk-ant-...       # For context extraction via Claude
```

### 1.3 Python Dependencies

```txt
# requirements.txt
gpt-researcher>=0.9.0
anthropic>=0.40.0
pyyaml>=6.0
python-dotenv>=1.0
asyncio
aiofiles>=24.0
rich>=13.0                         # Progress display in terminal
```

### 1.4 Install GPT Researcher

```bash
pip install gpt-researcher
```

GPT Researcher pulls in its own dependencies including Tavily integration. No separate Tavily SDK install needed.

---

## 2. Project Structure

```
innovera-research/
├── .env                               # API keys (gitignored)
├── .env.example                       # Template for API keys
├── README.md                          # Setup and usage instructions
├── requirements.txt                   # Python dependencies
├── run_research.py                    # CLI entry point
│
├── config/
│   ├── __init__.py
│   ├── settings.py                    # Global settings, model config, defaults
│   └── gptr_configs/                  # Per-category GPT Researcher config files
│       ├── deep_landscape.json        # Config for deep research categories
│       ├── targeted_lookup.json       # Config for targeted lookup categories
│       └── hybrid_mission.json        # Config for hybrid categories
│
├── context_extraction/
│   ├── __init__.py
│   ├── extractor.py                   # Reads venture inputs → calls Claude → returns signals
│   ├── prompts.py                     # Claude system/user prompts for extraction
│   └── models.py                      # Pydantic models for extracted signals
│
├── evidence_categories/
│   ├── __init__.py
│   ├── base.py                        # BaseCategory abstract class
│   ├── registry.py                    # Category registry + phase/priority metadata
│   ├── ec01_market_sizing.py
│   ├── ec02_competitor_landscape.py
│   ├── ec03_investment_signals.py
│   ├── ec04_alt_failures_reviews.py
│   ├── ec05_problem_prevalence.py
│   ├── ec06_regulatory_compliance.py
│   ├── ec07_enabling_tech.py
│   ├── ec08_urgency_forcing.py
│   ├── ec09_analyst_coverage.py
│   ├── ec10_voice_of_market.py
│   ├── ec11_search_hiring_trends.py
│   ├── ec12_budget_procurement.py
│   └── ec13_proxy_markets.py
│
├── orchestrator/
│   ├── __init__.py
│   ├── runner.py                      # Phase sequencing + parallel execution
│   ├── phases.py                      # Phase definitions and dependency graph
│   └── progress.py                    # Rich terminal progress display
│
├── output/
│   ├── __init__.py
│   ├── package_assembler.py           # Combines category outputs → final package
│   ├── yaml_formatter.py              # Machine-readable YAML output
│   └── markdown_formatter.py          # Human-readable Markdown report
│
├── venture_docs/                      # Default location for venture input documents
│   └── .gitkeep
│
└── output_packages/                   # Generated evidence packages land here
    └── .gitkeep
```

---

## 3. Configuration

### 3.1 Global Settings (`config/settings.py`)

```python
"""
Global settings for the Innovera research pre-step.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
PROJECT_ROOT = Path(__file__).parent.parent
VENTURE_DOCS_DIR = PROJECT_ROOT / "venture_docs"
OUTPUT_DIR = PROJECT_ROOT / "output_packages"
GPTR_CONFIG_DIR = PROJECT_ROOT / "config" / "gptr_configs"

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# --- Claude Config (Context Extraction) ---
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # For context extraction
CLAUDE_MAX_TOKENS = 8192

# --- GPT Researcher LLM Config ---
# These are set as env vars that GPT Researcher reads
# User should set preferred model (o3, gpt-5.4, etc.)
GPTR_SMART_LLM = os.getenv("GPTR_SMART_LLM", "openai:o3")
GPTR_STRATEGIC_LLM = os.getenv("GPTR_STRATEGIC_LLM", "openai:o3")
GPTR_FAST_LLM = os.getenv("GPTR_FAST_LLM", "openai:gpt-4o-mini")

# --- Execution Config ---
MAX_CONCURRENT_CATEGORIES = 4          # How many categories run in parallel within a phase
CATEGORY_TIMEOUT_SECONDS = 600         # 10 min timeout per category
TOTAL_TIMEOUT_SECONDS = 3600           # 1 hour max for entire run

# --- Output Config ---
INCLUDE_RAW_REPORTS = True             # Include GPT Researcher's raw reports in output
```

### 3.2 GPT Researcher Config Files

Three config files for different mission types. These are passed via `config_path` to GPT Researcher.

**`config/gptr_configs/deep_landscape.json`** — For categories needing recursive deep exploration:

```json
{
  "RETRIEVER": "tavily",
  "EMBEDDING": "openai:text-embedding-3-small",
  "SIMILARITY_THRESHOLD": 0.42,
  "FAST_LLM": "openai:gpt-4o-mini",
  "SMART_LLM": "openai:o3",
  "STRATEGIC_LLM": "openai:o3",
  "CURATE_SOURCES": true,
  "FAST_TOKEN_LIMIT": 2000,
  "SMART_TOKEN_LIMIT": 4000,
  "STRATEGIC_TOKEN_LIMIT": 4000,
  "BROWSE_CHUNK_MAX_LENGTH": 8192,
  "TEMPERATURE": 0.3,
  "TOTAL_WORDS": 3000,
  "MAX_SEARCH_RESULTS_PER_QUERY": 8,
  "DEEP_RESEARCH_BREADTH": 4,
  "DEEP_RESEARCH_DEPTH": 2,
  "DEEP_RESEARCH_CONCURRENCY": 4,
  "REPORT_FORMAT": "APA",
  "REPORT_SOURCE": "web",
  "LANGUAGE": "english",
  "REASONING_EFFORT": "high"
}
```

**`config/gptr_configs/targeted_lookup.json`** — For categories needing specific data points:

```json
{
  "RETRIEVER": "tavily",
  "EMBEDDING": "openai:text-embedding-3-small",
  "SIMILARITY_THRESHOLD": 0.42,
  "FAST_LLM": "openai:gpt-4o-mini",
  "SMART_LLM": "openai:o3",
  "STRATEGIC_LLM": "openai:o3",
  "CURATE_SOURCES": false,
  "FAST_TOKEN_LIMIT": 2000,
  "SMART_TOKEN_LIMIT": 4000,
  "STRATEGIC_TOKEN_LIMIT": 4000,
  "BROWSE_CHUNK_MAX_LENGTH": 8192,
  "TEMPERATURE": 0.2,
  "TOTAL_WORDS": 2000,
  "MAX_SEARCH_RESULTS_PER_QUERY": 5,
  "MAX_ITERATIONS": 3,
  "REPORT_FORMAT": "APA",
  "REPORT_SOURCE": "web",
  "LANGUAGE": "english"
}
```

**`config/gptr_configs/hybrid_mission.json`** — For categories that combine venture docs + web research:

```json
{
  "RETRIEVER": "tavily",
  "EMBEDDING": "openai:text-embedding-3-small",
  "SIMILARITY_THRESHOLD": 0.42,
  "FAST_LLM": "openai:gpt-4o-mini",
  "SMART_LLM": "openai:o3",
  "STRATEGIC_LLM": "openai:o3",
  "CURATE_SOURCES": true,
  "FAST_TOKEN_LIMIT": 2000,
  "SMART_TOKEN_LIMIT": 4000,
  "STRATEGIC_TOKEN_LIMIT": 4000,
  "BROWSE_CHUNK_MAX_LENGTH": 8192,
  "TEMPERATURE": 0.3,
  "TOTAL_WORDS": 2500,
  "MAX_SEARCH_RESULTS_PER_QUERY": 6,
  "DEEP_RESEARCH_BREADTH": 3,
  "DEEP_RESEARCH_DEPTH": 2,
  "DEEP_RESEARCH_CONCURRENCY": 3,
  "REPORT_FORMAT": "APA",
  "REPORT_SOURCE": "hybrid",
  "LANGUAGE": "english",
  "REASONING_EFFORT": "high"
}
```

**Important:** The `SMART_LLM` and `STRATEGIC_LLM` values in these configs should reference the user's preferred model. If the user wants to use `gpt-5.4` or `o3`, update these values. GPT Researcher accepts the format `"openai:model-name"`.

---

## 4. Context Extraction Layer

### 4.1 Purpose

Reads the venture brief, client documents, and any structured metadata to produce a set of **research signals** that shape every downstream GPT Researcher query. This step uses the Claude API because the extraction requires high reasoning quality — it's reading unstructured documents and producing structured analytical output.

### 4.2 Pydantic Models (`context_extraction/models.py`)

```python
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
```

### 4.3 Extraction Prompt (`context_extraction/prompts.py`)

```python
"""
Prompts for Claude-based context extraction.
"""

CONTEXT_EXTRACTION_SYSTEM = """You are an expert venture analyst preparing research signals for a web research system. You will receive venture documents (briefs, pitch decks, strategy docs, etc.) and must extract structured signals that will drive targeted web research across 13 evidence categories.

Your output must be valid JSON matching the schema provided. Be specific and concrete — vague signals produce vague research. Extract what's actually stated in the documents; do not infer or speculate beyond what the text supports.

For each field:
- problem_keywords: Extract 5-15 core nouns and noun phrases that describe the problem. These become search query terms. Be specific: "water pipe corrosion detection" not "infrastructure problems."
- industry_terms: Domain jargon that would appear in industry publications. E.g., "SCADA systems," "non-revenue water," "asset lifecycle management."
- named_competitors: Only include competitors explicitly named in the documents. Do not infer competitors.
- pain_drivers: The stated reasons the problem hurts. E.g., "unplanned maintenance costs," "regulatory non-compliance risk," "safety incidents."
- customer_roles: Specific job titles or functions mentioned. E.g., "utility operations manager," "CFO," "maintenance supervisor."
- problem_summary: Write this as a research briefing — clear enough that a researcher with no domain knowledge could understand what to look for.
- solution_summary: What the venture builds/does, stated neutrally (not marketing language).

For category_priorities, assign each of the 13 categories (EC-01 through EC-13) a priority based on these rules:
- Regulated industry → EC-06 (Regulatory) = critical
- Pre-revenue / concept stage → EC-05 (Prevalence) = critical, EC-03 (Investment) = high
- Crowded market (3+ named competitors) → EC-02 (Competitors) = critical, EC-04 (Reviews) = critical
- Novel category (no competitors named) → EC-13 (Proxy Markets) = high, EC-07 (Enabling Tech) = high
- Government / public sector buyer → EC-12 (Budget/Procurement) = critical, EC-06 (Regulatory) = critical
- Consumer or SMB target → EC-10 (Voice of Market) = critical, EC-11 (Search Trends) = high
- Explicit timing pressure mentioned → EC-08 (Urgency) = critical
- Default priorities if no special conditions: EC-01=critical, EC-02=critical, EC-05=critical, EC-03=high, EC-04=high, EC-08=high, EC-09=high, EC-10=high, EC-06=medium, EC-07=medium, EC-11=medium, EC-12=medium, EC-13=medium
"""

CONTEXT_EXTRACTION_USER = """Analyze the following venture documents and extract structured research signals.

## Documents

{documents_text}

## Structured Metadata (if provided)

{metadata_text}

## Required Output

Return a single JSON object matching this schema exactly. Do not include any text outside the JSON object.

{schema_json}
"""
```

### 4.4 Extractor (`context_extraction/extractor.py`)

```python
"""
Context extraction using Claude API.
Reads venture documents and produces structured research signals.
"""
import json
from pathlib import Path
from anthropic import Anthropic
from .prompts import CONTEXT_EXTRACTION_SYSTEM, CONTEXT_EXTRACTION_USER
from .models import ContextSignals
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS

class ContextExtractor:
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)

    def extract(
        self,
        venture_docs_dir: Path,
        metadata: dict | None = None
    ) -> ContextSignals:
        """
        Read all documents in venture_docs_dir, call Claude,
        return structured ContextSignals.
        """
        # 1. Read all document files
        documents_text = self._read_documents(venture_docs_dir)

        # 2. Format metadata
        metadata_text = json.dumps(metadata, indent=2) if metadata else "No structured metadata provided."

        # 3. Get schema for Claude
        schema_json = json.dumps(ContextSignals.model_json_schema(), indent=2)

        # 4. Call Claude
        user_message = CONTEXT_EXTRACTION_USER.format(
            documents_text=documents_text,
            metadata_text=metadata_text,
            schema_json=schema_json
        )

        response = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            system=CONTEXT_EXTRACTION_SYSTEM,
            messages=[{"role": "user", "content": user_message}]
        )

        # 5. Parse response
        response_text = response.content[0].text

        # Strip markdown code fences if present
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0]

        signals = ContextSignals.model_validate_json(response_text)
        return signals

    def _read_documents(self, docs_dir: Path) -> str:
        """Read all supported files from the documents directory."""
        supported_extensions = {".md", ".txt", ".pdf", ".docx", ".csv"}
        documents = []

        for file_path in sorted(docs_dir.iterdir()):
            if file_path.suffix.lower() in supported_extensions:
                # For now, read text-based files directly
                # PDF/DOCX extraction can be added via pypdf/python-docx
                if file_path.suffix.lower() in {".md", ".txt", ".csv"}:
                    content = file_path.read_text(encoding="utf-8")
                    documents.append(f"--- FILE: {file_path.name} ---\n{content}\n")
                else:
                    # Placeholder for binary file extraction
                    # TODO: Add PDF extraction (pypdf2) and DOCX extraction (python-docx)
                    documents.append(f"--- FILE: {file_path.name} (binary — extraction not yet implemented) ---\n")

        if not documents:
            raise FileNotFoundError(f"No supported documents found in {docs_dir}")

        return "\n".join(documents)
```

---

## 5. Evidence Category Architecture

### 5.1 Base Category Class (`evidence_categories/base.py`)

Every evidence category inherits from this. The base class handles GPT Researcher instantiation, execution, and output collection.

```python
"""
Base class for all evidence categories.
"""
import asyncio
import json
import yaml
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from gpt_researcher import GPTResearcher
from context_extraction.models import ContextSignals, PriorityLevel

@dataclass
class CategoryResult:
    """Output from a single evidence category execution."""
    category_id: str
    category_name: str
    status: str  # "success" | "partial" | "failed"
    raw_report: str  # Full GPT Researcher report text
    structured_findings: dict  # Parsed structured data (category-specific)
    sources: list[dict]  # URLs and metadata from research
    gaps: list[str]  # Identified evidence gaps
    execution_time_seconds: float
    error: Optional[str] = None

class BaseCategory(ABC):
    """
    Abstract base class for evidence categories.

    Each category must implement:
    - build_query(): Constructs the GPT Researcher query from context signals
    - get_report_type(): Returns "deep" or "custom_report"
    - get_config_path(): Returns path to the appropriate GPTR config
    - parse_report(): Extracts structured findings from GPT Researcher's raw report
    """

    def __init__(self, context: ContextSignals, venture_docs_dir: Path):
        self.context = context
        self.venture_docs_dir = venture_docs_dir

    @property
    @abstractmethod
    def category_id(self) -> str:
        """E.g., 'EC-01'"""
        pass

    @property
    @abstractmethod
    def category_name(self) -> str:
        """E.g., 'Market Sizing & Growth'"""
        pass

    @abstractmethod
    def build_query(self) -> str:
        """
        Build the research query/prompt from context signals.
        This is the most important method — it determines what GPT Researcher looks for.
        """
        pass

    @abstractmethod
    def get_report_type(self) -> str:
        """Return 'deep' for landscape categories or 'custom_report' for targeted lookups."""
        pass

    @abstractmethod
    def get_config_path(self) -> Path:
        """Return path to the appropriate GPT Researcher config file."""
        pass

    @abstractmethod
    def parse_report(self, raw_report: str) -> dict:
        """
        Parse GPT Researcher's raw markdown report into structured findings.
        Each category defines its own output structure.
        """
        pass

    def get_priority(self) -> PriorityLevel:
        """Look up this category's priority from the context signals."""
        for cp in self.context.category_priorities:
            if cp.category_id == self.category_id:
                return cp.priority
        return PriorityLevel.MEDIUM  # Default if not found

    async def execute(self) -> CategoryResult:
        """
        Run the GPT Researcher mission for this category.
        This is the main execution method called by the orchestrator.
        """
        import time
        start_time = time.time()

        try:
            query = self.build_query()
            report_type = self.get_report_type()
            config_path = str(self.get_config_path())

            # Set up GPT Researcher
            # If hybrid mode, set DOC_PATH env var for venture docs
            researcher_kwargs = {
                "query": query,
                "report_type": report_type,
                "config_path": config_path,
            }

            # For hybrid categories, pass local docs
            if self.get_report_type() == "deep" and self._use_hybrid():
                import os
                os.environ["DOC_PATH"] = str(self.venture_docs_dir)
                researcher_kwargs["report_source"] = "hybrid"

            researcher = GPTResearcher(**researcher_kwargs)

            # Conduct research
            await researcher.conduct_research()

            # Generate report
            raw_report = await researcher.write_report()

            # Extract sources
            sources = self._extract_sources(researcher)

            # Parse into structured findings
            structured = self.parse_report(raw_report)

            # Identify gaps
            gaps = self._identify_gaps(structured)

            elapsed = time.time() - start_time

            return CategoryResult(
                category_id=self.category_id,
                category_name=self.category_name,
                status="success",
                raw_report=raw_report,
                structured_findings=structured,
                sources=[{"url": s} for s in sources],
                gaps=gaps,
                execution_time_seconds=elapsed,
            )

        except Exception as e:
            elapsed = time.time() - start_time
            return CategoryResult(
                category_id=self.category_id,
                category_name=self.category_name,
                status="failed",
                raw_report="",
                structured_findings={},
                sources=[],
                gaps=[f"Category execution failed: {str(e)}"],
                execution_time_seconds=elapsed,
                error=str(e),
            )

    def _use_hybrid(self) -> bool:
        """Override in subclasses that should use hybrid (web + local docs) mode."""
        return False

    def _extract_sources(self, researcher: GPTResearcher) -> list[str]:
        """Extract source URLs from the researcher's results."""
        try:
            return list(researcher.get_source_urls()) if hasattr(researcher, 'get_source_urls') else []
        except Exception:
            return []

    def _identify_gaps(self, structured: dict) -> list[str]:
        """
        Default gap identification. Subclasses can override for category-specific logic.
        Looks for empty fields, "not found" markers, and low-confidence items.
        """
        gaps = []
        if not structured:
            gaps.append(f"No structured findings could be extracted for {self.category_name}")
            return gaps

        # Walk the structured dict looking for gap markers
        for key, value in structured.items():
            if value is None or value == "" or value == []:
                gaps.append(f"No data found for: {key}")
            elif isinstance(value, str) and any(marker in value.lower() for marker in
                ["not found", "no data", "unavailable", "insufficient", "could not find"]):
                gaps.append(f"Gap in {key}: {value[:100]}")

        return gaps
```

### 5.2 Category Registry (`evidence_categories/registry.py`)

```python
"""
Registry of all evidence categories with phase assignments and metadata.
"""
from enum import IntEnum
from dataclasses import dataclass

class Phase(IntEnum):
    """Execution phases. Lower numbers run first."""
    FOUNDATION = 1      # No dependencies on other categories
    COMPETITOR_DEPENDENT = 2  # Needs competitor list from EC-02
    SYNTHESIS = 3        # Synthesis-heavy, no category dependencies

@dataclass
class CategoryMeta:
    """Metadata for a registered category."""
    category_id: str
    category_name: str
    phase: Phase
    research_mode: str  # "deep" | "custom_report"
    depends_on: list[str]  # Category IDs this depends on (for data, not just phase)
    section_consumption: dict[str, str]  # {section_id: "primary" | "supporting"}

# --- CATEGORY REGISTRY ---
# This is the single source of truth for all 13 categories

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
    Build the section → category consumption map.
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
```

### 5.3 Example Category Implementation: EC-02 Competitor Landscape

This is the most complex category (deep research, produces outputs consumed by Phase 2 categories). All other categories follow the same pattern but are simpler.

```python
"""
EC-02: Competitor Landscape & Positioning

Deep research category that maps direct competitors, adjacent solutions,
and DIY alternatives. Produces a competitor list consumed by Phase 2 categories.
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from context_extraction.models import ContextSignals
from config.settings import GPTR_CONFIG_DIR

class EC02CompetitorLandscape(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-02"

    @property
    def category_name(self) -> str:
        return "Competitor Landscape & Positioning"

    def get_report_type(self) -> str:
        return "deep"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "deep_landscape.json"

    def build_query(self) -> str:
        """
        Build the deep research query. This is a detailed prompt that
        tells GPT Researcher what to look for and how to structure findings.
        """
        # Build competitor seed list
        competitor_seed = ""
        if self.context.named_competitors:
            names = ", ".join(self.context.named_competitors)
            competitor_seed = f"\n\nKnown competitors to start with (search for more): {names}"

        # Build workaround context
        workaround_context = ""
        if self.context.workaround_mentions:
            workarounds = ", ".join(self.context.workaround_mentions)
            workaround_context = f"\n\nKnown workarounds customers use today: {workarounds}"

        query = f"""Conduct a comprehensive competitive landscape analysis for the following venture:

**Venture:** {self.context.venture_name}
**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Geography:** {self.context.geography}
**Solution category:** {self.context.solution_category}
**Problem being solved:** {self.context.problem_summary}
**Target customer:** {self.context.target_customer_summary}
{competitor_seed}
{workaround_context}

Research and report on:

1. **Direct Competitors**: Companies offering products/services that directly address the same problem for the same target customer. For each, include: what they do, who they target, their positioning/messaging, pricing model (if public), known strengths, known weaknesses, and funding stage.

2. **Adjacent Solutions**: Products that partially address the problem or serve an adjacent market that could expand into this space. Include the same details as above.

3. **DIY Alternatives**: Manual processes, spreadsheets, internal tools, outsourced services, or consultancies that customers currently use to address this problem without a dedicated product.

4. **Do-Nothing Analysis**: What happens when organizations don't adopt any solution? How prevalent is inaction, and what does it cost?

5. **Landscape Summary**: Total competitors found, market maturity assessment (early/growing/mature/consolidating), dominant approach in the market, the gap no current player adequately addresses, and fragmentation level.

Structure the report with clear sections for each of the above. For each competitor, use a consistent format. Be specific — name companies, cite sources, provide concrete details rather than generalities. If pricing information is not public, say so explicitly rather than guessing.

Focus on {self.context.geography} but include global players that compete in this market."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        """
        Parse GPT Researcher's markdown report into structured findings.

        NOTE: GPT Researcher returns markdown prose. This parser extracts
        key entities and structures them. For V1, this can be a best-effort
        extraction — the raw report is always preserved alongside.

        For a more robust approach, consider a follow-up LLM call that
        takes the raw report and extracts structured JSON.
        """
        # V1 approach: store the raw report sections and extract competitor names
        # A more sophisticated version would use an LLM call to structure this
        structured = {
            "raw_report_text": raw_report,
            "competitor_names_extracted": self._extract_competitor_names(raw_report),
            "landscape_maturity": self._extract_field(raw_report, "maturity"),
        }
        return structured

    def _extract_competitor_names(self, report: str) -> list[str]:
        """
        Best-effort extraction of competitor names from the report.
        These are passed to Phase 2 categories (EC-03, EC-04, EC-11).

        V1: Simple heuristic — look for bold names in competitor sections.
        V2: Use a fast LLM call to extract names reliably.
        """
        # Placeholder — implement extraction logic
        # This is an important integration point: Phase 2 categories
        # read this list to construct their own queries
        names = []
        # TODO: Parse report markdown for competitor names
        # Consider a lightweight Claude/GPT call:
        #   "Extract all company/product names mentioned as competitors
        #    in this report. Return as a JSON array of strings."
        return names

    def _extract_field(self, report: str, field_name: str) -> str:
        """Extract a specific field value from the report. Placeholder for V1."""
        return "see raw report"

    def get_competitor_list(self, result) -> list[str]:
        """
        Public method for Phase 2 categories to get the competitor list.
        Called by the orchestrator after EC-02 completes.
        """
        if result and result.structured_findings:
            names = result.structured_findings.get("competitor_names_extracted", [])
            # Merge with context-provided names
            all_names = list(set(names + self.context.named_competitors))
            return all_names
        return self.context.named_competitors
```

### 5.4 Example Category: EC-01 Market Sizing (Targeted Lookup)

Shows the simpler `custom_report` pattern:

```python
"""
EC-01: Market Sizing & Growth

Targeted lookup category for market size, growth rates, and structure data.
"""
from pathlib import Path
from evidence_categories.base import BaseCategory
from config.settings import GPTR_CONFIG_DIR

class EC01MarketSizing(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-01"

    @property
    def category_name(self) -> str:
        return "Market Sizing & Growth"

    def get_report_type(self) -> str:
        return "custom_report"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "targeted_lookup.json"

    def build_query(self) -> str:
        # Build verification queries for any venture-claimed market sizes
        verification_block = ""
        if self.context.market_size_claims:
            claims = "\n".join(f"  - {c}" for c in self.context.market_size_claims)
            verification_block = f"""
6. **Venture Claims Verification**: The venture has made these market size claims. Verify, challenge, or contextualize each:
{claims}
"""

        query = f"""Research and report on market sizing data for the following:

**Solution category:** {self.context.solution_category}
**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Geography:** {self.context.geography}
**Problem:** {self.context.problem_summary}

Find and report:

1. **Total Addressable Market (TAM)**: The total global or regional market size for {self.context.solution_category}. Include the dollar value, the year of the estimate, and the source. If multiple estimates exist, report all and note the range.

2. **Market Growth Rate**: CAGR or annual growth rate forecasts. Include the forecast period and source.

3. **Serviceable Addressable Market (SAM)**: The subset relevant to {self.context.industry_vertical} in {self.context.geography}. If this specific segment isn't broken out in reports, note the closest available segmentation.

4. **Market Structure**: Is this market fragmented or consolidated? Emerging or mature? Who are the largest players by revenue or market share?

5. **Industry Revenue/Volume Data**: Any statistics on the size of the {self.context.industry_vertical} industry in {self.context.geography} that contextualizes the opportunity (e.g., total infrastructure spending, number of target organizations, etc.).
{verification_block}
For every data point, cite the specific source and publication date. Distinguish between: primary research (from market research firms), analyst estimates, and government statistics. Flag any significant variance between sources.

Prioritize data from the last 24 months. If only older data exists, note this explicitly."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        return {
            "raw_report_text": raw_report,
            # V1: structured extraction via follow-up LLM call (see Section 7.2)
        }
```

### 5.5 Remaining Category Implementations

Each of the 11 remaining categories (EC-03 through EC-13) follows the same pattern:

1. Inherit from `BaseCategory`
2. Set `category_id` and `category_name`
3. Choose `report_type`: `"deep"` for landscape categories, `"custom_report"` for targeted lookups
4. Choose `config_path`: `deep_landscape.json` or `targeted_lookup.json`
5. Implement `build_query()` using context signals to construct a venture-specific research prompt
6. Implement `parse_report()` (V1: store raw report; V2: LLM-based structured extraction)

**Category → Report Type Mapping:**

| Category | Report Type | Config | Rationale |
|----------|------------|--------|-----------|
| EC-01 Market Sizing | `custom_report` | targeted_lookup | Specific data points: numbers, sources, dates |
| EC-02 Competitor Landscape | `deep` | deep_landscape | Multi-entity exploration, pattern recognition |
| EC-03 Investment Signals | `custom_report` | targeted_lookup | Specific funding rounds, M&A events |
| EC-04 Alt Failures & Reviews | `deep` | deep_landscape | Cross-platform synthesis, pattern recognition |
| EC-05 Problem Prevalence | `deep` | deep_landscape | Cross-study synthesis, cost modeling |
| EC-06 Regulatory & Compliance | `deep` | deep_landscape | Multi-source regulatory environment mapping |
| EC-07 Enabling Tech Trends | `deep` | deep_landscape | Technology trajectory synthesis |
| EC-08 Urgency & Forcing | `deep` | deep_landscape | Multi-factor urgency synthesis |
| EC-09 Analyst Coverage | `deep` | deep_landscape | Cross-analyst narrative synthesis |
| EC-10 Voice of Market | `deep` | deep_landscape | Community sentiment pattern recognition |
| EC-11 Search & Hiring Trends | `custom_report` | targeted_lookup | Specific data points: volumes, counts |
| EC-12 Budget & Procurement | `deep` | deep_landscape | Process/requirements synthesis |
| EC-13 Proxy Markets | `deep` | deep_landscape | Historical trajectory narrative synthesis |

**Build instruction for Claude Code:** For each remaining category, create the file following the EC-01 and EC-02 patterns. The `build_query()` method is the critical piece — use the query generation logic from the evidence category specifications in `web-research-pre-step-spec.md` (the companion document) to construct each category's prompt. Each prompt should incorporate the relevant `ContextSignals` fields to make the research venture-specific.

---

## 6. Orchestrator

### 6.1 Phase Definitions (`orchestrator/phases.py`)

```python
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
            "wait_for": [
                dep
                for cid in category_ids
                for dep in CATEGORY_REGISTRY[cid].depends_on
            ],
        })
    return plan
```

### 6.2 Runner (`orchestrator/runner.py`)

```python
"""
Main orchestration runner.
Executes evidence categories in phased order with parallel execution within phases.
"""
import asyncio
import time
from pathlib import Path
from typing import Optional

from context_extraction.models import ContextSignals
from evidence_categories.base import CategoryResult
from evidence_categories.registry import (
    Phase, CATEGORY_REGISTRY, get_categories_by_phase
)
from orchestrator.phases import get_execution_plan
from orchestrator.progress import ProgressTracker
from config.settings import MAX_CONCURRENT_CATEGORIES, CATEGORY_TIMEOUT_SECONDS

# Import all category classes
from evidence_categories.ec01_market_sizing import EC01MarketSizing
from evidence_categories.ec02_competitor_landscape import EC02CompetitorLandscape
# ... import all 13 category classes

# Map category IDs to their implementation classes
CATEGORY_CLASSES = {
    "EC-01": EC01MarketSizing,
    "EC-02": EC02CompetitorLandscape,
    # "EC-03": EC03InvestmentSignals,
    # "EC-04": EC04AltFailuresReviews,
    # "EC-05": EC05ProblemPrevalence,
    # "EC-06": EC06RegulatoryCompliance,
    # "EC-07": EC07EnablingTech,
    # "EC-08": EC08UrgencyForcing,
    # "EC-09": EC09AnalystCoverage,
    # "EC-10": EC10VoiceOfMarket,
    # "EC-11": EC11SearchHiringTrends,
    # "EC-12": EC12BudgetProcurement,
    # "EC-13": EC13ProxyMarkets,
}


class ResearchRunner:
    """Orchestrates the phased execution of all evidence categories."""

    def __init__(
        self,
        context: ContextSignals,
        venture_docs_dir: Path,
        progress: Optional[ProgressTracker] = None,
    ):
        self.context = context
        self.venture_docs_dir = venture_docs_dir
        self.progress = progress or ProgressTracker()
        self.results: dict[str, CategoryResult] = {}
        self.competitor_list: list[str] = []

    async def run_all(self) -> dict[str, CategoryResult]:
        """Execute all phases in order."""
        plan = get_execution_plan()
        total_start = time.time()

        for phase_info in plan:
            phase_name = phase_info["phase_name"]
            category_ids = phase_info["categories"]

            self.progress.start_phase(phase_name, category_ids)

            # Filter to only categories that have implementations
            runnable = [cid for cid in category_ids if cid in CATEGORY_CLASSES]

            if not runnable:
                self.progress.log(f"Phase {phase_name}: no implemented categories, skipping")
                continue

            # Skip low-priority categories if desired
            runnable = self._filter_by_priority(runnable)

            # Run categories in parallel with concurrency limit
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_CATEGORIES)

            async def run_with_semaphore(cid: str):
                async with semaphore:
                    return await self._run_category(cid)

            phase_results = await asyncio.gather(
                *[run_with_semaphore(cid) for cid in runnable],
                return_exceptions=True,
            )

            # Store results
            for cid, result in zip(runnable, phase_results):
                if isinstance(result, Exception):
                    self.results[cid] = CategoryResult(
                        category_id=cid,
                        category_name=CATEGORY_REGISTRY[cid].category_name,
                        status="failed",
                        raw_report="",
                        structured_findings={},
                        sources=[],
                        gaps=[f"Unhandled exception: {str(result)}"],
                        execution_time_seconds=0,
                        error=str(result),
                    )
                else:
                    self.results[cid] = result

            # After Phase 1, extract competitor list from EC-02 for Phase 2
            if phase_info["phase"] == Phase.FOUNDATION:
                self._extract_competitor_list()

            self.progress.end_phase(phase_name)

        total_elapsed = time.time() - total_start
        self.progress.complete(total_elapsed)

        return self.results

    async def _run_category(self, category_id: str) -> CategoryResult:
        """Run a single category with timeout."""
        self.progress.start_category(category_id)

        category_class = CATEGORY_CLASSES[category_id]
        category = category_class(
            context=self.context,
            venture_docs_dir=self.venture_docs_dir,
        )

        # If this is a Phase 2 category, inject competitor list into context
        if category_id in ["EC-03", "EC-04", "EC-11"] and self.competitor_list:
            # Add discovered competitors to the context signals
            # so the category's build_query() can reference them
            all_competitors = list(set(
                self.context.named_competitors + self.competitor_list
            ))
            self.context.named_competitors = all_competitors

        try:
            result = await asyncio.wait_for(
                category.execute(),
                timeout=CATEGORY_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            result = CategoryResult(
                category_id=category_id,
                category_name=CATEGORY_REGISTRY[category_id].category_name,
                status="failed",
                raw_report="",
                structured_findings={},
                sources=[],
                gaps=[f"Category timed out after {CATEGORY_TIMEOUT_SECONDS}s"],
                execution_time_seconds=CATEGORY_TIMEOUT_SECONDS,
                error="Timeout",
            )

        self.progress.end_category(category_id, result.status)
        return result

    def _extract_competitor_list(self):
        """After Phase 1, pull the competitor list from EC-02's results."""
        ec02_result = self.results.get("EC-02")
        if ec02_result and ec02_result.status == "success":
            ec02_class = CATEGORY_CLASSES["EC-02"]
            ec02_instance = ec02_class(
                context=self.context,
                venture_docs_dir=self.venture_docs_dir,
            )
            self.competitor_list = ec02_instance.get_competitor_list(ec02_result)
            self.progress.log(
                f"Extracted {len(self.competitor_list)} competitors from EC-02: "
                f"{', '.join(self.competitor_list[:5])}{'...' if len(self.competitor_list) > 5 else ''}"
            )

    def _filter_by_priority(self, category_ids: list[str]) -> list[str]:
        """
        Optionally filter out low-priority categories.
        For V1, run everything. Can add filtering logic later.
        """
        return category_ids
```

### 6.3 Progress Tracker (`orchestrator/progress.py`)

```python
"""
Terminal progress display using Rich.
"""
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

class ProgressTracker:
    """Displays real-time research progress in the terminal."""

    def __init__(self):
        self.console = Console()
        self.current_phase = ""
        self.category_statuses: dict[str, str] = {}

    def start_phase(self, phase_name: str, category_ids: list[str]):
        self.current_phase = phase_name
        for cid in category_ids:
            self.category_statuses[cid] = "pending"
        self.console.print(f"\n[bold blue]═══ Phase: {phase_name} ═══[/bold blue]")
        self.console.print(f"  Categories: {', '.join(category_ids)}")

    def start_category(self, category_id: str):
        self.category_statuses[category_id] = "running"
        self.console.print(f"  [yellow]▶ Starting {category_id}[/yellow]")

    def end_category(self, category_id: str, status: str):
        self.category_statuses[category_id] = status
        icon = "✓" if status == "success" else "✗" if status == "failed" else "~"
        color = "green" if status == "success" else "red" if status == "failed" else "yellow"
        self.console.print(f"  [{color}]{icon} {category_id}: {status}[/{color}]")

    def end_phase(self, phase_name: str):
        self.console.print(f"[bold blue]═══ Phase {phase_name} complete ═══[/bold blue]")

    def log(self, message: str):
        self.console.print(f"  [dim]{message}[/dim]")

    def complete(self, total_seconds: float):
        mins = int(total_seconds // 60)
        secs = int(total_seconds % 60)
        self.console.print(f"\n[bold green]✓ Research complete in {mins}m {secs}s[/bold green]")

        # Summary table
        table = Table(title="Category Results")
        table.add_column("Category", style="cyan")
        table.add_column("Status")
        for cid, status in sorted(self.category_statuses.items()):
            color = "green" if status == "success" else "red" if status == "failed" else "yellow"
            table.add_row(cid, f"[{color}]{status}[/{color}]")
        self.console.print(table)
```

---

## 7. Output Assembly

### 7.1 Package Assembler (`output/package_assembler.py`)

```python
"""
Assembles all category results into the final evidence package.
"""
import yaml
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from context_extraction.models import ContextSignals
from evidence_categories.base import CategoryResult
from evidence_categories.registry import get_consumption_map, CATEGORY_REGISTRY
from output.yaml_formatter import format_yaml_package
from output.markdown_formatter import format_markdown_report


class PackageAssembler:
    """Combines all category outputs into the final evidence package."""

    def __init__(
        self,
        context: ContextSignals,
        results: dict[str, CategoryResult],
        output_dir: Path,
    ):
        self.context = context
        self.results = results
        self.output_dir = output_dir
        self.consumption_map = get_consumption_map()

    def assemble(self) -> tuple[Path, Path]:
        """
        Produce both output formats. Returns (yaml_path, markdown_path).
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        venture_slug = self.context.venture_name.lower().replace(" ", "-")

        # Build the package data structure
        package = self._build_package(timestamp)

        # YAML output
        yaml_filename = f"{venture_slug}_evidence_{timestamp}.yaml"
        yaml_path = self.output_dir / yaml_filename
        yaml_content = format_yaml_package(package)
        yaml_path.write_text(yaml_content, encoding="utf-8")

        # Markdown output
        md_filename = f"{venture_slug}_evidence_{timestamp}.md"
        md_path = self.output_dir / md_filename
        md_content = format_markdown_report(package, self.context, self.results)
        md_path.write_text(md_content, encoding="utf-8")

        # Also save raw reports individually for debugging
        raw_dir = self.output_dir / "raw_reports"
        raw_dir.mkdir(exist_ok=True)
        for cid, result in self.results.items():
            if result.raw_report:
                raw_path = raw_dir / f"{cid}_{venture_slug}.md"
                raw_path.write_text(result.raw_report, encoding="utf-8")

        return yaml_path, md_path

    def _build_package(self, timestamp: str) -> dict:
        """Build the complete package data structure."""

        # Aggregate stats
        total_sources = sum(len(r.sources) for r in self.results.values())
        successful = sum(1 for r in self.results.values() if r.status == "success")
        failed = sum(1 for r in self.results.values() if r.status == "failed")
        total_time = sum(r.execution_time_seconds for r in self.results.values())

        # Collect all gaps by severity
        critical_gaps = []
        moderate_gaps = []
        for cid, result in self.results.items():
            meta = CATEGORY_REGISTRY.get(cid)
            priority = "high" if meta and any(
                v == "primary" for v in meta.section_consumption.values()
            ) else "moderate"

            for gap in result.gaps:
                gap_entry = {
                    "category_id": cid,
                    "category_name": result.category_name,
                    "gap": gap,
                }
                if result.status == "failed" or priority == "high":
                    critical_gaps.append(gap_entry)
                else:
                    moderate_gaps.append(gap_entry)

        return {
            "research_package": {
                "metadata": {
                    "venture_name": self.context.venture_name,
                    "generated_at": timestamp,
                    "categories_executed": len(self.results),
                    "categories_succeeded": successful,
                    "categories_failed": failed,
                    "total_sources_consulted": total_sources,
                    "total_execution_seconds": round(total_time, 1),
                },
                "context_signals": self.context.model_dump(),
                "evidence": {
                    cid: {
                        "category_name": result.category_name,
                        "status": result.status,
                        "findings": result.structured_findings,
                        "sources": result.sources,
                        "gaps": result.gaps,
                        "execution_seconds": round(result.execution_time_seconds, 1),
                    }
                    for cid, result in sorted(self.results.items())
                },
                "consumption_map": self.consumption_map,
                "gap_summary": {
                    "critical_gaps": critical_gaps,
                    "moderate_gaps": moderate_gaps,
                },
            }
        }
```

### 7.2 Structured Extraction (V2 Enhancement)

The V1 `parse_report()` methods store raw report text. For V2, add a post-processing step that uses a fast LLM call to extract structured data from each raw report:

```python
# NOT part of V1 build — document as future enhancement

async def extract_structured_findings(raw_report: str, category_id: str, schema: dict) -> dict:
    """
    Post-process a GPT Researcher report into structured findings.
    Uses a fast model (gpt-4o-mini) to extract specific data points
    from the narrative report into the category's schema.
    """
    from openai import AsyncOpenAI
    client = AsyncOpenAI()

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "system",
            "content": f"Extract structured data from this research report. Return valid JSON matching the provided schema. If a field cannot be filled from the report, set it to null."
        }, {
            "role": "user",
            "content": f"Schema:\n{json.dumps(schema)}\n\nReport:\n{raw_report}"
        }],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
```

---

## 8. CLI Entry Point (`run_research.py`)

```python
"""
CLI entry point for the Innovera research pre-step.

Usage:
  python run_research.py --docs ./venture_docs/
  python run_research.py --docs ./venture_docs/ --metadata ./metadata.yaml
  python run_research.py --docs ./venture_docs/ --output ./custom_output/
"""
import asyncio
import argparse
import yaml
from pathlib import Path
from rich.console import Console

from config.settings import VENTURE_DOCS_DIR, OUTPUT_DIR
from context_extraction.extractor import ContextExtractor
from orchestrator.runner import ResearchRunner
from orchestrator.progress import ProgressTracker
from output.package_assembler import PackageAssembler

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Innovera Web Research Pre-Step")
    parser.add_argument(
        "--docs", type=str, default=str(VENTURE_DOCS_DIR),
        help="Path to directory containing venture documents"
    )
    parser.add_argument(
        "--metadata", type=str, default=None,
        help="Path to YAML file with structured metadata (optional)"
    )
    parser.add_argument(
        "--output", type=str, default=str(OUTPUT_DIR),
        help="Path to output directory for evidence packages"
    )
    args = parser.parse_args()

    docs_dir = Path(args.docs)
    output_dir = Path(args.output)

    if not docs_dir.exists():
        console.print(f"[red]Error: Documents directory not found: {docs_dir}[/red]")
        return

    # Load metadata if provided
    metadata = None
    if args.metadata:
        metadata_path = Path(args.metadata)
        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = yaml.safe_load(f)
        else:
            console.print(f"[yellow]Warning: Metadata file not found: {metadata_path}[/yellow]")

    # --- Step 1: Context Extraction ---
    console.print("\n[bold]Step 1: Extracting context from venture documents...[/bold]")
    extractor = ContextExtractor()
    context = extractor.extract(docs_dir, metadata)
    console.print(f"[green]✓ Context extracted for: {context.venture_name}[/green]")
    console.print(f"  Industry: {context.industry_vertical}")
    console.print(f"  Problem keywords: {', '.join(context.problem_keywords[:5])}...")
    console.print(f"  Named competitors: {', '.join(context.named_competitors) or 'None'}")

    # --- Step 2: Research Execution ---
    console.print("\n[bold]Step 2: Executing research across 13 evidence categories...[/bold]")
    progress = ProgressTracker()
    runner = ResearchRunner(context, docs_dir, progress)
    results = asyncio.run(runner.run_all())

    # --- Step 3: Package Assembly ---
    console.print("\n[bold]Step 3: Assembling evidence package...[/bold]")
    assembler = PackageAssembler(context, results, output_dir)
    yaml_path, md_path = assembler.assemble()

    console.print(f"\n[bold green]✓ Evidence package generated:[/bold green]")
    console.print(f"  YAML: {yaml_path}")
    console.print(f"  Markdown: {md_path}")
    console.print(f"  Raw reports: {output_dir / 'raw_reports'}/")


if __name__ == "__main__":
    main()
```

---

## 9. Build Order for Claude Code

Execute in this order. Each step should be a discrete commit.

### Step 1: Project Scaffolding
- Create the directory structure from Section 2
- Create `requirements.txt`, `.env.example`, `README.md`
- Create `config/settings.py` with all settings
- Create all three GPT Researcher config JSON files
- Create all `__init__.py` files

### Step 2: Context Extraction
- Create `context_extraction/models.py` (Pydantic models)
- Create `context_extraction/prompts.py` (Claude prompts)
- Create `context_extraction/extractor.py`
- **Test:** Run extractor against the NLM venture brief to verify Claude returns valid ContextSignals

### Step 3: Base Category Architecture
- Create `evidence_categories/base.py` (BaseCategory class + CategoryResult)
- Create `evidence_categories/registry.py` (full registry with all 13 categories)
- **Test:** Verify registry functions return correct phase assignments and consumption maps

### Step 4: Implement All 13 Categories
Build each category file. The critical part is `build_query()` — each must construct a venture-specific prompt using ContextSignals. Use the query generation logic from the companion document `web-research-pre-step-spec.md`.

**Build in this order (matching execution phases):**

Phase 1 (Foundation):
1. `ec02_competitor_landscape.py` — Most complex; produces competitor list for Phase 2
2. `ec05_problem_prevalence.py` — Deep research; cost/prevalence synthesis
3. `ec01_market_sizing.py` — Targeted lookup; specific data points
4. `ec06_regulatory_compliance.py` — Deep research; conditional priority
5. `ec10_voice_of_market.py` — Deep research; community sentiment

Phase 2 (Competitor-Dependent):
6. `ec03_investment_signals.py` — Targeted lookup; uses competitor list
7. `ec04_alt_failures_reviews.py` — Deep research; uses competitor list
8. `ec11_search_hiring_trends.py` — Targeted lookup; uses competitor list

Phase 3 (Synthesis):
9. `ec07_enabling_tech.py` — Deep research
10. `ec08_urgency_forcing.py` — Deep research
11. `ec09_analyst_coverage.py` — Deep research
12. `ec12_budget_procurement.py` — Deep research
13. `ec13_proxy_markets.py` — Deep research

**Test after each:** Instantiate the category with mock ContextSignals, call `build_query()`, and verify the prompt is well-formed and venture-specific.

### Step 5: Orchestrator
- Create `orchestrator/phases.py`
- Create `orchestrator/progress.py`
- Create `orchestrator/runner.py`
- **Test:** Run with 1-2 categories to verify phase sequencing and parallel execution work

### Step 6: Output Assembly
- Create `output/yaml_formatter.py`
- Create `output/markdown_formatter.py`
- Create `output/package_assembler.py`
- **Test:** Feed mock results into assembler and verify output structure

### Step 7: CLI Entry Point
- Create `run_research.py`
- **Test:** Full end-to-end run against NLM venture documents

### Step 8: Integration Testing
- Full run against NLM venture
- Verify all 13 categories execute
- Verify output YAML structure matches the spec
- Verify Markdown report is readable and useful
- Check that Phase 2 categories correctly receive competitor list from EC-02
- Time the full execution and note cost

---

## 10. Key Implementation Notes

### 10.1 GPT Researcher Environment Variables

GPT Researcher reads some settings from environment variables, not just config files. Ensure the `.env` file or runtime environment has:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
RETRIEVER=tavily
```

The per-category config files (Section 3.2) override most settings, but API keys must be in the environment.

### 10.2 Model Configuration

The user wants to use `o3` or `gpt-5.4` as the primary reasoning model. In GPT Researcher's config:
- `SMART_LLM`: Set to `"openai:o3"` or `"openai:gpt-5.4"` (the model doing report synthesis)
- `STRATEGIC_LLM`: Set to the same (the model doing research planning)
- `FAST_LLM`: Keep as `"openai:gpt-4o-mini"` (used for summaries — doesn't need a frontier model)

These values live in the three JSON config files. The user should update them when switching models.

### 10.3 Competitor List Handoff (Phase 1 → Phase 2)

This is the most important integration point. After EC-02 completes in Phase 1:

1. The runner calls `ec02_instance.get_competitor_list(result)` to extract competitor names
2. These names are added to `context.named_competitors`
3. When Phase 2 categories (EC-03, EC-04, EC-11) build their queries, they reference `self.context.named_competitors` which now includes both the originally provided names AND the discovered names

The `get_competitor_list()` method on EC-02 needs to reliably extract company names from GPT Researcher's markdown output. For V1, implement a lightweight extraction (regex for bolded names, or a fast LLM call). This is a known fragile point — if extraction fails, Phase 2 categories fall back to only the context-provided competitor names, which is acceptable but suboptimal.

### 10.4 Error Resilience

The system must be resilient to individual category failures:
- A failed category should not block other categories in the same phase
- A failed Phase 1 category should not prevent Phase 2 from running (except for EC-02 failure, which degrades Phase 2 quality but doesn't block it)
- All failures are logged with error details and appear in the gap summary
- The final output package is always produced, even with failed categories — gaps are clearly marked

### 10.5 Cost Estimation

Based on GPT Researcher docs, deep research costs ~$0.40 per mission with o3-mini. With o3 or gpt-5.4:
- 10 deep research categories × ~$1-2 each = $10-20
- 3 targeted lookup categories × ~$0.50 each = $1.50
- 1 Claude API call for context extraction = ~$0.10
- **Estimated total: $12-22 per venture**

Actual costs will vary based on model pricing and research depth settings. The config files can be tuned to reduce cost (lower breadth/depth) or increase thoroughness (higher breadth/depth).

### 10.6 Connecting to the Innovera Pipeline

The output evidence package (YAML) is designed to be consumed by the existing `websearch-import` partial in each framework snip. The connection is:

1. The YAML file goes into the project's `research/` directory
2. The `websearch-import` partial is updated to:
   a. Load the YAML evidence package
   b. Read the `consumption_map` to identify which categories are relevant to the current section
   c. Inject the relevant category findings (both structured and raw report text) into the framework's context
3. Each framework still has the ability to run its own supplementary searches via the existing per-framework search system

This pipeline integration is a separate task from the research tool build. The tool produces the package; the pipeline integration consumes it.

---

## 11. Companion Documents

This build spec should be used alongside:

1. **`web-research-pre-step-spec.md`** — The evidence category specifications document. Contains detailed descriptions of what each category looks for, expected source types, output structures, and the full section consumption map. Claude Code should reference this when implementing each category's `build_query()` method.

2. **GPT Researcher documentation** — https://docs.gptr.dev/docs/gpt-researcher/gptr/deep_research for deep research configuration, and https://docs.gptr.dev/docs/gpt-researcher/gptr/config for all config options.

---

## 12. Success Criteria

The build is complete when:

- [ ] `python run_research.py --docs ./venture_docs/` executes end-to-end without errors
- [ ] All 13 categories execute (some may have gaps — that's expected)
- [ ] Phase sequencing works correctly (Phase 2 waits for Phase 1; Phase 3 waits for Phase 2)
- [ ] EC-02 competitor list is passed to Phase 2 categories
- [ ] Output YAML contains all 13 category results with findings, sources, and gaps
- [ ] Output Markdown is readable and organized by evidence category
- [ ] Raw GPT Researcher reports are saved individually for debugging
- [ ] Failed categories don't crash the pipeline
- [ ] Total execution completes within 30 minutes for a typical venture
- [ ] Context extraction produces sensible signals from the NLM venture brief
