"""
Tavily compatibility patch for GPT Researcher.

Monkey-patches the Tavily retriever's _search method to strip unsupported
fields (e.g. `days`, `use_cache`) from the outgoing payload. This avoids
400 Bad Request errors caused by the installed gpt-researcher sending an
outdated request body to https://api.tavily.com/search.

Apply once at startup by calling `apply_tavily_patch()`.
"""
import json
import logging
import os

logger = logging.getLogger(__name__)

_PATCH_APPLIED = False

# Fields that the current Tavily Search API actually supports.
_SUPPORTED_FIELDS = {
    "query",
    "search_depth",
    "topic",
    "include_answer",
    "include_raw_content",
    "max_results",
    "include_domains",
    "exclude_domains",
    "include_images",
    "api_key",
    # Supported date controls (not used by default, but safe to keep if present)
    "time_range",
    "start_date",
    "end_date",
}


def _strip_unsupported_fields(data: dict) -> dict:
    """Remove fields not supported by the current Tavily API."""
    stripped = {}
    removed = []
    for key, value in data.items():
        if key in _SUPPORTED_FIELDS:
            # Omit empty domain lists
            if key in ("include_domains", "exclude_domains") and not value:
                continue
            stripped[key] = value
        else:
            removed.append(key)
    if removed:
        logger.debug("Stripped unsupported Tavily fields: %s", removed)
    return stripped


def apply_tavily_patch():
    """Monkey-patch the Tavily retriever used by GPT Researcher."""
    global _PATCH_APPLIED
    if _PATCH_APPLIED:
        return

    # Safe diagnostic: log whether the Tavily key is present
    tavily_key = os.environ.get("TAVILY_API_KEY", "")
    if tavily_key:
        logger.info("Tavily key detected: yes (prefix=%s)", tavily_key[:5] + "...")
    else:
        logger.warning("Tavily key detected: no — searches will likely fail")

    # Import TavilySearch from the correct module path
    TavilySearch = None
    import_paths = [
        "gpt_researcher.retrievers.tavily.tavily_search",
        "gpt_researcher.retrievers.tavily.tavily",
        "gpt_researcher.retrievers.tavily_search.tavily_search",
    ]
    for modpath in import_paths:
        try:
            import importlib
            mod = importlib.import_module(modpath)
            TavilySearch = getattr(mod, "TavilySearch", None)
            if TavilySearch is not None:
                logger.info("Found TavilySearch at %s", modpath)
                break
        except ImportError:
            continue

    if TavilySearch is None:
        logger.warning(
            "Could not import TavilySearch from gpt_researcher — "
            "Tavily compatibility patch not applied"
        )
        _PATCH_APPLIED = True
        return

    # Patch _search directly — this is where the payload is built and sent.
    _original_search = TavilySearch._search

    def _patched_search(self, query, search_depth="basic", topic="general",
                        days=2, max_results=10, include_domains=None,
                        exclude_domains=None, include_answer=False,
                        include_raw_content=False, include_images=False,
                        use_cache=True, **extra_kwargs):
        """Replacement _search that strips unsupported fields before sending."""
        import requests as _requests

        data = {
            "query": query,
            "search_depth": search_depth,
            "topic": topic,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "max_results": max_results,
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "include_images": include_images,
            "api_key": self.api_key,
        }

        # Strip unsupported fields (days, use_cache, and anything unexpected)
        data = _strip_unsupported_fields(data)

        logger.debug(
            "Tavily request: topic=%s max_results=%s",
            topic, max_results,
        )

        response = _requests.post(
            self.base_url, data=json.dumps(data), headers=self.headers, timeout=100
        )

        if response.status_code == 200:
            return response.json()
        else:
            # Log error details without exposing the API key
            logger.error(
                "Tavily search failed: status=%d topic=%s max_results=%s response=%s",
                response.status_code,
                topic,
                max_results,
                response.text[:500],
            )
            response.raise_for_status()

    TavilySearch._search = _patched_search

    _PATCH_APPLIED = True
    logger.info("Tavily compatibility patch applied — unsupported fields will be stripped")
