# Innovera Research — Runtime Recovery Patch Brief

## Purpose

This brief is a narrowly scoped recovery task for Claude Code after the broader runtime and checkpoint changes introduced two regressions:

1. Market research categories now fail at construction time.
2. The Tavily compatibility patch still does not apply.

Do not treat this as a broad refactor. Fix these regressions first, then run a narrow retest.

## Immediate Objective

Restore the ability to run `MR-01b` and `MR-06a` successfully enough to verify:

- category construction works
- Tavily patch applies
- Tavily requests no longer fail immediately due to the outdated payload

Only after that should broader checkpoint/resume validation continue.

---

## Regression 1: Market Research Constructor Mismatch

### Problem

`ResearchRunner` now constructs categories with `run_id` and `research_mode`, but `MRBaseCategory.__init__()` still uses the old signature.

### Evidence

`innovera-research/orchestrator/runner.py`:

```python
category = category_class(
    context=self.context,
    venture_docs_dir=self.venture_docs_dir,
    run_id=self.run_id,
    research_mode=self.research_mode,
)
```

`innovera-research/market_research/base.py` still has:

```python
def __init__(self, context: ContextSignals, venture_docs_dir: Path):
    super().__init__(context, venture_docs_dir)
```

This causes:

- `MRBaseCategory.__init__() got an unexpected keyword argument 'run_id'`

### Required Fix

Update `innovera-research/market_research/base.py` so `MRBaseCategory.__init__()` accepts and forwards:

- `run_id`
- `research_mode`

It must remain compatible with the new `BaseCategory.__init__()` signature.

### Constraint

Do not work around this by removing `run_id` and `research_mode` from `ResearchRunner`. Those are needed for checkpointing.

---

## Regression 2: Tavily Compatibility Patch Not Applied

### Problem

The compat patch exists, but it still logs:

```text
Could not import TavilySearch from gpt_researcher — Tavily compatibility patch not applied
```

### Root Cause

The import paths in `innovera-research/integrations/tavily_compat.py` are wrong for the installed GPT Researcher version.

The installed package exposes `TavilySearch` at:

- `gpt_researcher.retrievers.tavily.tavily_search`

### Required Fix

In `innovera-research/integrations/tavily_compat.py`:

1. Import `TavilySearch` from the correct module path.
2. Keep the patch idempotent.
3. Keep safe diagnostics, but do not block patching if `.env` is hidden from the agent.

### Constraint

Do not edit Python `site-packages`.

---

## Regression 3: Wrong Tavily Request Interception

### Problem

The current compat layer only rewrites `requests.post(..., json=...)`, but the installed Tavily retriever uses:

```python
requests.post(self.base_url, data=json.dumps(data), headers=self.headers, timeout=100)
```

So the existing interception never strips unsupported fields from the real request body.

### Required Fix

Use one of these approaches:

#### Preferred

Patch `TavilySearch._search()` directly so the outgoing payload is rebuilt locally without unsupported fields.

#### Acceptable Alternative

Intercept `requests.post()` when the URL is Tavily, parse `kwargs["data"]` if it is JSON, strip unsupported fields, and then re-serialize it.

### Fields To Strip

At minimum strip:

- `days`

Also evaluate whether `use_cache` should be removed if current Tavily Search does not accept it.

### Supported Payload Shape

Keep the payload to fields that Tavily currently supports and this app actually uses:

```python
{
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
```

If empty domain lists are present, omitting them is acceptable.

### Logging

If Tavily still returns non-200:

- log status code
- log response text
- log topic and max results
- never log the full API key

---

## Required Retest Scope

Do not retest the whole product first.

Run a narrow validation with:

- `MR-01b`
- `MR-06a`

Confirm all of the following:

1. No `unexpected keyword argument 'run_id'`
2. No `Could not import TavilySearch...`
3. No immediate Tavily `400`
4. Categories actually enter research
5. Activity/progress logs move past initialization

Only after that passes should broader checkpoint/resume testing continue.

---

## Files To Modify

- `innovera-research/market_research/base.py`
- `innovera-research/integrations/tavily_compat.py`

Potentially:

- `innovera-research/evidence_categories/base.py`

Only if needed to ensure the Tavily patch is applied at the correct time.

---

## Success Criteria

- [ ] `MRBaseCategory` accepts the new constructor arguments required by checkpointing.
- [ ] The Tavily compatibility patch actually imports and applies.
- [ ] The outgoing Tavily request no longer includes unsupported fields such as `days`.
- [ ] A narrow run for `MR-01b` and `MR-06a` gets past startup and category construction.
- [ ] The narrow run no longer fails immediately with the previous constructor error or the previous Tavily patch import failure.
