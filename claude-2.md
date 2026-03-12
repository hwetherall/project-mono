# Innovera Research — Checkpoint Resume Spec

## Purpose

This brief defines a generic checkpoint-and-resume system for long-running categories. It should support both research modes and enable a truthful `Continue` action after timeouts or interruptions.

## Overview

Long-running categories such as `MR-01b` and `MR-06a` can time out after 30 minutes even when expensive research work has already completed and the system is partway through report generation or finalization.

The goal is to let the user click `Continue` and resume from saved progress instead of:

- rerunning the entire pipeline
- silently losing partial work
- depending purely on fragile in-memory state

This should be implemented generically for all categories and both research modes, not as a one-off fix for market research.

## Current Problem

### Timeout Behavior Today

Category timeout is enforced in `innovera-research/orchestrator/runner.py` by wrapping the entire `category.execute()` coroutine in `asyncio.wait_for(...)` using `CATEGORY_TIMEOUT_SECONDS`, which defaults to 1800 seconds.

When timeout occurs, the runner creates a brand-new failed `CategoryResult` with:

- `status="failed"`
- empty `raw_report`
- empty `structured_findings`
- empty `sources`
- a timeout gap message
- `error="Timeout"`

That means partial state is effectively discarded.

### Why The Current Retry Is Not Enough

The app already has:

- `POST /api/research/{run_id}/retry/{category_id}`

But that reruns the category from scratch. It does not resume from partial work and depends on `active_runs` memory being intact.

### Why In-Memory-Only Resume Is Not Good Enough

An in-memory-only solution is too fragile:

- it breaks on server restart
- it breaks if `active_runs` is cleared
- it does not help when the browser reconnects later
- current orchestration does not preserve a resumable partial category object after timeout

The recommended solution is a disk-backed checkpoint system that still uses memory as an optimization when available.

## Product Goal

Add a `Continue` action for timed-out or interrupted categories that:

- resumes from the last durable checkpoint if one exists
- falls back to retry only if no usable checkpoint exists
- preserves completed category work
- rebuilds the final package after successful resume
- works for both active runs and interrupted runs that survive a server restart

## Recommended Architecture

Implement a generic per-category checkpoint model.

The user-facing control should be called `Continue`, but the backend behavior should be:

- `resume from checkpoint if available`
- otherwise `retry from scratch`

## Execution Model

Refactor category execution into resumable stages in `innovera-research/evidence_categories/base.py`.

Recommended stages:

- `research_started`
- `research_completed`
- `report_started`
- `report_completed`
- `parsed`
- `finalized`

Each time a category crosses one of these boundaries, write a checkpoint to disk.

## Checkpoint Storage

Store checkpoints under the run output directory:

- `innovera-research/output_packages/<run_id>/checkpoints/<category_id>.json`

This keeps checkpoint state close to run artifacts and makes interrupted-run recovery practical.

## Checkpoint Schema

Each checkpoint should contain enough data to determine whether resume is possible and where to resume from.

Suggested fields:

- `run_id`
- `category_id`
- `category_name`
- `research_mode`
- `stage`
- `status`
- `query`
- `config_path`
- `report_type`
- `started_at`
- `updated_at`
- `elapsed_seconds`
- `error`
- `timeout_seconds`
- `can_resume`
- `resume_reason`
- `source_urls`
- `research_context`
- `raw_report`
- `structured_findings`

Notes:

- `research_context` should store normalized post-`conduct_research()` context if available.
- `raw_report` should be stored once `write_report()` completes.
- `structured_findings` should be stored after parsing completes.
- `source_urls` should be preserved even if final package assembly has not happened.

## Required Backend Changes

### 1. Add Checkpoint Persistence Helpers

Add a repo-owned checkpoint module, for example:

- `innovera-research/orchestrator/checkpoints.py`

It should provide helpers for:

- saving a checkpoint
- loading a checkpoint
- deleting or superseding stale checkpoints
- deriving whether a checkpoint is resumable
- converting checkpoint data back into a partial or final `CategoryResult`

### 2. Refactor Category Execution To Save Stages

Update `innovera-research/evidence_categories/base.py` so category execution checkpoints at each major milestone.

Desired flow:

1. Build query and execution metadata.
2. Save `research_started`.
3. Run `conduct_research()`.
4. Save `research_completed` with normalized research context and source URLs.
5. Save `report_started`.
6. Run `write_report()`.
7. Save `report_completed` with raw report.
8. Parse report.
9. Save `parsed` with structured findings.
10. Build final `CategoryResult`.
11. Save `finalized`.

If timeout or error occurs:

- preserve the last successful checkpoint
- write an updated error state
- do not collapse the category into a totally empty synthetic failure if resumable work exists

### 3. Update Timeout Handling

Current timeout logic in `innovera-research/orchestrator/runner.py` should become checkpoint-aware.

Instead of always replacing the category result with a blank failure:

- inspect whether a checkpoint exists
- if the category had already completed research or report writing, expose the category as resumable
- return a failed or interrupted result that includes resumable metadata

This can still appear as a failed result in the UI, but it must not hide the fact that continuation is possible.

### 4. Add Resume Endpoint

Add a new endpoint in `innovera-research/api/routes.py`:

- `POST /api/research/{run_id}/resume/{category_id}`

Behavior:

- load run context and checkpoint
- determine the latest valid stage
- if stage is `research_completed`, skip new web research and continue with report writing, parsing, and finalization
- if stage is `report_completed`, skip directly to parsing and finalization
- if stage is `parsed`, skip directly to finalization and package rebuild if possible
- if no valid checkpoint exists, return a clear error or optionally fall back to retry

After successful resume:

- update `run["results"][category_id]`
- rebuild outputs with `PackageAssembler`
- refresh stored YAML and Markdown file pointers
- emit progress and Activity Stream events that explain what was resumed

### 5. Reuse Existing Retry/Reassembly Logic

The current retry path in `innovera-research/api/routes.py` already:

- executes one category
- updates `run["results"]`
- reruns `PackageAssembler(...).assemble()`

Do not duplicate that logic.

Refactor shared behavior into an internal helper that both endpoints can use:

- `retry` = hard rerun from scratch
- `resume` = checkpoint-aware continuation

### 6. Surface Resumable State In APIs

Update API responses in `innovera-research/api/models.py` and `innovera-research/api/routes.py` so category status data includes:

- `checkpoint_stage`
- `can_resume`
- `resume_reason`
- `last_persisted_at`

This should be included anywhere the frontend needs to decide between:

- show `Continue`
- show `Retry`
- show neither

Good candidates:

- `/api/research/{run_id}/status`
- `/api/research/{run_id}/full`

## Frontend Changes

### 1. `useResearchRun.js`

Update `innovera-research/frontend/src/hooks/useResearchRun.js` to:

- read `can_resume` and related metadata from status responses
- expose a `resumeCategory(categoryId)` action
- keep `retryCategory(categoryId)` for non-resumable failures

### 2. `ProgressPanel.jsx`

Update `innovera-research/frontend/src/components/ProgressPanel.jsx` so category cards/actions display:

- `Continue` when `can_resume === true`
- `Retry` when category failed but no checkpoint-backed continuation is available

The UI should be explicit. Do not label a full rerun as `Continue`.

### 3. Activity Stream

The Activity Stream should narrate resume behavior clearly. Add messages like:

- `MR-01b timed out after 1800s — checkpoint saved at research_completed`
- `Resuming MR-01b from research checkpoint`
- `Skipping web research; continuing report generation`
- `Rebuilding evidence package after resume`

This is important because the user needs confidence that prior work was reused.

## GPT Researcher Reuse Risk

This is the biggest technical unknown.

The ideal version is:

- `conduct_research()` completes
- its output/context is serialized to checkpoint
- `write_report()` can later be invoked from that serialized context without rerunning search

However, that depends on what GPT Researcher actually requires internally after `conduct_research()`.

### Required Investigation

Before finalizing implementation details, inspect the installed GPT Researcher package and determine:

1. what state exists immediately after `conduct_research()`
2. whether `write_report()` depends only on normalized context or on hidden internal fields
3. whether that state can be reconstructed from checkpoint data

### If True Resume Is Possible

Implement full continuation from:

- `research_completed`
- `report_completed`
- `parsed`

### If True Resume Is Not Possible

Keep the same checkpoint architecture, but gracefully downgrade:

- completed categories remain preserved
- interrupted category can be resumed only from later stages if enough state exists
- otherwise the system performs a targeted rerun of only that failed category
- the rest of the run remains intact

This still provides major UX value because the user avoids rerunning the whole pipeline.

## Packaging Behavior

Final package assembly currently happens after full run completion in:

- `innovera-research/output/package_assembler.py`

That should remain the canonical finalization step.

After a successful resume:

- regenerate the YAML package
- regenerate the Markdown report
- write any newly available raw report files

Do not require a full rerun of all categories just to regenerate the final report.

## Persistence Rules

### What Must Persist Before Final Assembly

The current architecture mostly persists only final outputs. That is insufficient for resume.

Persist these earlier:

- per-category checkpoint JSON
- raw report text as soon as it exists
- source URLs as soon as they exist
- resumable error metadata on timeout

### What Should Still Stay In Memory

Keep using `active_runs` for fast updates during active sessions:

- context
- current category results
- websocket progress bridge

But memory should be treated as an optimization, not the source of truth for resume.

## UX Expectations

The user flow should feel like this:

1. A long category times out.
2. The UI indicates that progress was saved.
3. The category card shows `Continue`.
4. Clicking `Continue` resumes from the latest checkpoint.
5. The Activity Stream explains which steps were skipped and which were resumed.
6. On success, the final evidence package is rebuilt and becomes available immediately.

## Constraints

- Design this as a generic mechanism for all categories and both research modes.
- Do not make it a special case only for `MR-01b` and `MR-06a`.
- Do not require the whole run to restart.
- Do not depend exclusively on in-memory state.
- Do not silently call a full retry when the UI says `Continue`.
- Keep the existing retry endpoint for true reruns.

## Suggested File Targets

### Backend

- `innovera-research/evidence_categories/base.py`
- `innovera-research/orchestrator/runner.py`
- `innovera-research/orchestrator/checkpoints.py` (new)
- `innovera-research/api/routes.py`
- `innovera-research/api/models.py`
- `innovera-research/api/progress_bridge.py`

### Frontend

- `innovera-research/frontend/src/hooks/useResearchRun.js`
- `innovera-research/frontend/src/components/ProgressPanel.jsx`
- `innovera-research/frontend/src/components/ActivityStream.jsx`

## Build Order

### Step 1: Investigate GPT Researcher Resume Feasibility

Inspect the installed GPT Researcher package and verify what state can be serialized after `conduct_research()` and reused later by `write_report()`.

### Step 2: Add Checkpoint Schema And Persistence

Create checkpoint helpers and wire stage-based persistence into category execution.

### Step 3: Make Timeout Handling Checkpoint-Aware

Preserve resumable state on timeout rather than always collapsing to an empty failed result.

### Step 4: Add Resume Endpoint

Implement checkpoint-aware resume in parallel with the existing retry flow.

### Step 5: Expose Resume Metadata To Frontend

Return checkpoint stage and resumable flags from status and full-run APIs.

### Step 6: Add Continue Button

Show `Continue` only when checkpoint-backed resume is actually possible. Otherwise keep `Retry`.

### Step 7: Validate End-To-End

Test:

- timeout during research
- timeout after research but before finalization
- resume within same server session
- resume after server restart
- package rebuild after successful resume

## Success Criteria

- [ ] A timed-out category can advertise resumable progress instead of appearing as a total loss.
- [ ] The UI shows a truthful `Continue` action when checkpoint-backed resume exists.
- [ ] Resuming does not rerun completed categories.
- [ ] Final YAML and Markdown outputs are rebuilt after successful resume.
- [ ] Resume works after server restart when checkpoint files are present.
- [ ] If true continuation is impossible for a given stage, the system degrades cleanly to targeted retry while preserving all other completed work.
