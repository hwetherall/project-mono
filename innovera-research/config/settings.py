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
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- Context Extraction Config (via OpenRouter) ---
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
CONTEXT_LLM_MODEL = os.getenv("CONTEXT_LLM_MODEL", "anthropic/claude-sonnet-4.6")
CONTEXT_LLM_MAX_TOKENS = 8192

# --- GPT Researcher LLM Config ---
GPTR_SMART_LLM = os.getenv("GPTR_SMART_LLM", "openai:gpt-5")
GPTR_STRATEGIC_LLM = os.getenv("GPTR_STRATEGIC_LLM", "openai:gpt-5.4")
GPTR_FAST_LLM = os.getenv("GPTR_FAST_LLM", "openai:gpt-5-mini")

# --- Execution Config ---
MAX_CONCURRENT_CATEGORIES = 3              # Bumped from 2 to 3 after splitting MR-01/MR-06 into smaller tasks
CATEGORY_TIMEOUT_SECONDS = int(os.getenv("CATEGORY_TIMEOUT_SECONDS") or "2700")  # Default to 45 minutes for deep research categories
TOTAL_TIMEOUT_SECONDS = 5400               # 90 min max for entire run
RATE_LIMIT_MAX_RETRIES = 5                 # Retry attempts on 429 errors
RATE_LIMIT_BASE_DELAY = 10                 # Base delay in seconds (exponential backoff)

# --- Output Config ---
INCLUDE_RAW_REPORTS = True
