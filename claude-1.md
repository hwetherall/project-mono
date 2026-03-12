# Innovera Research — Runtime Hotfix Spec

## Purpose

This brief covers the current blocking runtime issues only. Treat it as higher priority than broader product polish.

## Current Situation

The app starts, accepts a research request, and begins orchestration, but the run fails during GPT Researcher's Tavily-backed search stage. The backend terminal also shows useful deep-research progress lines that never reach the frontend Activity Stream.

## Non-Negotiable Assumptions

- A real local `.env` file exists even if the coding agent cannot read it.
- The hidden `.env` file already contains a valid `TAVILY_API_KEY`.
- Do not spend implementation time "fixing" a missing Tavily key unless runtime evidence proves the key is absent.
- Do not modify Python `site-packages`.
- Do not rewrite the overall research pipeline architecture.
- Prefer a local compatibility patch inside the repo.

## Hotfix Goals

1. Restore Tavily search so market research and evidence-category runs can complete.
2. Preserve the assumption that `.env` already contains the Tavily key.
3. Mirror backend terminal output into the frontend Activity Stream while keeping normal terminal behavior intact.

---

## Hotfix 1: Tavily Compatibility Patch

### Problem

Installed `gpt-researcher` posts an outdated Tavily request payload. The retriever implementation in site-packages sends a `days` field to `https://api.tavily.com/search`. Current Tavily docs no longer document `days` on the Search endpoint.

Observed failure:

- `400 Client Error: Bad Request for url: https://api.tavily.com/search`

This is a Tavily payload-compatibility problem, not a frontend problem.

### Root Cause

The installed Tavily retriever builds a request body like:

```json
{
  "query": "...",
  "search_depth": "basic",
  "topic": "general",
  "days": 2,
  "max_results": 10,
  "api_key": "tvly-..."
}
```

The risky field is `days`. Current Tavily Search should use supported date controls only:

- `time_range`
- `start_date`
- `end_date`

If no date filter is needed, omit date filtering entirely.

### Required Implementation Strategy

Implement a local compatibility patch in the repo. Do not edit anything under Python `site-packages`.

Preferred approach:

1. Create a small compatibility module in the repo.
2. Monkey-patch GPT Researcher's Tavily request builder at startup.
3. Strip unsupported fields from the outgoing payload.
4. Preserve the rest of GPT Researcher's behavior and response shape.
5. Improve error logging so Tavily's actual response body becomes visible in diagnostics.

### Suggested Module

- `innovera-research/integrations/tavily_compat.py`

Responsibilities:

1. Import GPT Researcher's Tavily retriever from the installed package.
2. Save the original low-level request method if useful for traceability.
3. Replace the Tavily request construction path with a compatible version.
4. Strip `days` from the payload.
5. Only include supported Tavily fields.
6. Preserve timeout behavior.
7. On non-200 responses, log the response text before raising.

### Supported Tavily Payload

Use a request payload limited to fields Tavily currently supports and this app actually needs:

```python
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
```

Notes:

- Do not send `days`.
- Do not invent new Tavily fields unless official docs support them.
- If future work needs time filtering, use `time_range`, `start_date`, or `end_date`.
- If `include_domains` or `exclude_domains` is empty, it is acceptable to omit them.

### Where To Apply The Patch

Apply the patch once, early in app startup, before any category constructs a `GPTResearcher` instance.

Good hook points:

- `innovera-research/api/app.py`
- `innovera-research/evidence_categories/base.py`

Preferred approach:

- Keep all GPT Researcher monkey patches together in `evidence_categories/base.py` or a dedicated `integrations/` patch module imported from there.

### Required Logging Improvements

When Tavily returns a non-200 response:

- include the HTTP status code
- include the raw response text if available
- include the query topic and max results
- never print the full API key

Expected example:

```text
Tavily search failed: status=400 topic=general max_results=8 body={"detail":{"error":"Invalid request ..."}}
```

### Constraints

- No direct edits to installed package files.
- No vendoring the whole GPT Researcher retriever stack into the repo.
- No fallback to a different retriever unless Tavily still fails after the payload fix.
- Do not treat missing `.env` visibility as proof the key does not exist.

### Verification Checklist

1. Start `python run_web.py`.
2. Launch a research run that previously failed immediately.
3. Confirm the terminal no longer shows an immediate Tavily `400`.
4. Confirm at least one category proceeds into source collection and report writing.
5. If Tavily still errors, confirm the improved logs now show Tavily's response body.

---

## Hotfix 2: Environment-Key Handling Guidance

### Problem

Agents working in this repo may not be able to read the real `.env` file. That can lead to false diagnoses claiming the Tavily key is missing when the runtime environment is actually configured.

### Required Guidance

Future work in this repo should assume:

- `.env` exists locally
- `config/settings.py` is intended to load it via `load_dotenv()`
- `TAVILY_API_KEY` should be treated as present unless runtime evidence proves otherwise

### Safe Diagnostics

If runtime diagnostics are added, keep them safe:

- log whether `TAVILY_API_KEY` is present
- log only a redacted prefix if absolutely necessary
- never log the full key

Safe example:

```text
Tavily key detected: yes
```

Optional richer example:

```text
Tavily key detected: yes (prefix=tvly-)
```

### Do Not Do

- Do not print the full env file.
- Do not fail startup only because the agent could not inspect `.env`.
- Do not overwrite real env values from placeholder entries in `.env.example`.

---

## Hotfix 3: Mirror Terminal Output Into Activity Stream

### Problem

Important research progress appears only in the backend terminal, for example:

- `DEEP RESEARCH: Starting with breadth=4, depth=2, concurrency=4`
- `Generating 4 search queries...`
- source-fetch errors and other GPT Researcher print output

The frontend Activity Stream only shows curated websocket events and misses the most "alive" part of the run.

### Goal

Stream meaningful backend terminal output into the frontend Activity Stream in near real time while keeping normal terminal behavior intact.

### Design Principle

Treat terminal mirroring as an additive telemetry layer:

- the terminal should still print normally
- the Activity Stream should receive mirrored lines
- existing structured websocket events should remain
- terminal mirroring should supplement, not replace, higher-level events

### Required Backend Design

Create a tee-style stdout/stderr capture utility for the research run.

Recommended new module:

- `innovera-research/api/terminal_stream.py`

Responsibilities:

1. Wrap `sys.stdout` and optionally `sys.stderr` with a line-buffering tee.
2. Forward every line to the original stream.
3. Emit selected lines to `WebSocketProgressBridge`.
4. Normalize partial writes into newline-delimited messages.
5. Filter obvious non-pipeline noise when appropriate.

### Emission Model

Add a new websocket event type for mirrored terminal lines:

```json
{
  "type": "terminal_line",
  "level": "info",
  "message": "Generating 4 search queries..."
}
```

Potential levels:

- `info`
- `warning`
- `error`
- `debug`

### Suggested Filtering

Mirror research-related lines such as:

- lines containing `DEEP RESEARCH`
- lines containing `Generating`
- lines containing `rate-limit`
- lines containing `Error:`
- lines containing category IDs like `EC-` or `MR-`
- lines emitted by GPT Researcher during search, scrape, or report generation

Suppress or de-prioritize:

- uvicorn startup lines
- HTTP access logs
- websocket connection boilerplate

Filtering should be conservative. When unsure, prefer showing the line.

### Where To Capture

Only capture around the actual research pipeline execution, not for the full lifetime of the process.

Recommended scope:

- wrap `runner.run_all()`
- optionally wrap context extraction and package assembly if they print useful logs

Because the app enforces a single active research run, a temporary process-wide stdout tee is acceptable here.

### Backend Integration

In `innovera-research/api/routes.py` inside `run_pipeline()`:

1. Initialize the stdout/stderr tee with access to `progress`.
2. Enter the tee context before context extraction and/or before `runner.run_all()`.
3. Exit the tee context when the run completes or fails.
4. Ensure teardown always happens in `finally`.

### Progress Bridge Additions

In `innovera-research/api/progress_bridge.py`, add:

- `emit_terminal_line(message: str, level: str = "info")`

That should enqueue an event like:

```python
{
    "type": "terminal_line",
    "level": level,
    "message": message,
}
```

Keep `emit_log_detail()` too:

- `log_detail` = curated lifecycle milestones
- `terminal_line` = mirrored live backend output

### Frontend Hook Changes

Update `innovera-research/frontend/src/hooks/useResearchRun.js` so the Activity Stream accepts:

- `log_detail`
- `log`
- `terminal_line`
- existing synthesized lifecycle events

Suggested handling:

```javascript
case 'terminal_line':
  setActivityLog((prev) => [
    ...prev,
    {
      timestamp: Date.now(),
      level: event.level || 'info',
      message: event.message,
      source: 'terminal',
    },
  ]);
  break;
```

### Activity Stream Rendering

In `ActivityStream.jsx`:

- visually distinguish mirrored terminal lines from higher-level lifecycle events
- keep terminal-like styling
- use monospace rendering for mirrored lines
- preserve auto-scroll and pause behavior
- cap retained entries to avoid unbounded growth

Suggested distinction:

- lifecycle events use icons like `●`, `→`, `✓`, `⚠`
- mirrored terminal lines use a subtle prefix like `…`

### Deduplication

Some messages may exist both as a structured event and as a mirrored terminal line.

To avoid noisy duplication:

- prefer keeping structured events
- if a terminal line exactly matches a recent structured message, skip it
- do not aggressively dedupe similar-but-not-identical lines

### Error Handling

The terminal tee must never break the run if websocket clients disconnect.

Requirements:

- if emitting to the websocket bridge fails, still write to the original terminal
- swallow tee-emission failures after logging them locally
- never let telemetry failure stop research execution

### Verification Checklist

1. Start a run from the UI.
2. Confirm the terminal still shows deep research lines.
3. Confirm the Activity Stream now shows mirrored lines such as query generation and Tavily/search progress.
4. Confirm HTTP access-log noise does not dominate the stream.
5. Confirm structured milestone events still appear.
6. Confirm the stream still works when no browser websocket is connected.

---

## Hotfix Build Order

1. Implement Tavily compatibility patch.
2. Add safe Tavily diagnostic logging.
3. Verify a run gets past Tavily source fetching.
4. Implement stdout/stderr tee and `terminal_line` websocket events.
5. Update `useResearchRun.js` and `ActivityStream.jsx` to consume mirrored lines.
6. Run an end-to-end research session and confirm the web Activity Stream now feels like the backend terminal.

## Files Most Likely To Change

### Backend

- `innovera-research/evidence_categories/base.py`
- `innovera-research/api/routes.py`
- `innovera-research/api/progress_bridge.py`
- `innovera-research/api/terminal_stream.py` (new)
- `innovera-research/integrations/tavily_compat.py` (new, recommended)

### Frontend

- `innovera-research/frontend/src/hooks/useResearchRun.js`
- `innovera-research/frontend/src/components/ActivityStream.jsx`
- `innovera-research/frontend/src/components/ProgressPanel.jsx`

## Success Criteria

- [ ] Research runs no longer fail immediately with Tavily `400 Bad Request` caused by the outdated payload.
- [ ] The implementation does not edit Python `site-packages`.
- [ ] The codebase assumes the real `.env` exists and does not misdiagnose Tavily auth purely because the file is hidden from the agent.
- [ ] The backend terminal still shows the same live research output as before.
- [ ] The frontend Activity Stream now includes mirrored terminal and deep-research lines in real time.
- [ ] Structured websocket lifecycle events still work and remain readable.
