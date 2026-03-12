# Innovera Research — Product Build Spec

## Overview

This brief covers the broader v2 product work for the Innovera Research web app.

The backend pipeline already exists. The goal is to evolve the frontend and supporting APIs so the app feels like a polished research product rather than a prototype.

Do not rewrite the existing pipeline or backend logic. Prefer refactoring in place with targeted backend additions.

## Current Architecture

```text
innovera-research/
├── api/
│   ├── app.py
│   ├── routes.py
│   ├── models.py
│   ├── websocket.py
│   └── progress_bridge.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── components/
│   │   ├── hooks/
│   │   └── index.css
├── output/
│   └── markdown_formatter.py
└── run_web.py
```

## Improvement 1: Report UI Overhaul

### Problem

The current `OutputViewer` renders raw markdown with minimal hierarchy. Reports feel like a wall of text. The current summary tab is too generic and does not help users reason about the result.

### Goal

Replace the tabbed markdown dump with a rich, document-like report layout.

### Desired Report Structure

- sticky left sidebar with table of contents
- main document area with verdict, summary, evidence sections, gaps, and sources
- category cards instead of flat markdown
- document typography rather than app-like prose blocks

### Verdict Dashboard

At the top of the report, show a visual scorecard for all categories:

- category name and ID
- status indicator
- confidence bar based on source count and gaps
- one-line key finding extracted from the report

Clicking a card should scroll to the corresponding section.

### Category Sections

Each evidence category should render as a rich card with:

- category header
- execution time
- key metrics bar if metrics can be parsed
- full rendered markdown content, not truncated
- collapsible raw report section
- gap callouts
- clickable sources
- previous and next navigation

### Source Quality Panel

Add a report-level source panel that:

- groups sources across categories
- deduplicates by URL
- shows domain, title when possible, and cited-by categories
- sorts by citation count

### Backend Support

Modify `innovera-research/output/markdown_formatter.py` to remove raw report truncation.

Add `GET /api/research/{run_id}/output/structured` to return a JSON view optimized for frontend rendering:

- metadata
- context signals
- per-category report content
- sources
- gaps
- gap inventory

### Typography

- use a serif font for report body text
- use monospace for IDs, metrics, and dense data
- increase line height
- add subtle left-border status cues

## Improvement 2: Live Process Stream

### Problem

The current progress log feels hidden and too raw.

### Goal

Show a prominent live Activity Stream that feels like watching a build log or terminal.

### Requirements

- dark terminal-like styling
- auto-scroll with pause control
- colored status glyphs
- readable timestamps
- human-friendly messages

### Backend Support

Add richer `log_detail` events from `routes.py` and `progress_bridge.py` around:

- context extraction start and completion
- phase starts
- category starts and completions
- rate limits
- parsing
- package assembly

### Frontend Support

Update `useResearchRun.js` and `ProgressPanel.jsx` so the Activity Stream sits alongside the category grid and shows live run narration.

## Improvement 3: Run History

### Problem

There is no real frontend history UI even though run metadata is persisted to disk.

### Goal

Add a history view so users can revisit past runs.

### Requirements

- history list view
- run cards with venture name, date, duration, category success count, sources, and status
- click to open historical output
- delete run with confirmation

### Backend Support

In `innovera-research/api/routes.py`:

- enhance `GET /api/runs`
- add `GET /api/research/{run_id}/full`
- ensure output endpoints work for historical runs via disk fallback
- add `DELETE /api/research/{run_id}`

### Frontend Support

- add lightweight routing in `App.jsx`
- add navigation links in `Layout.jsx`
- create `RunHistory.jsx`

## Improvement 4: Source Citations And Quality

### Problem

Sources are shown as bare URL lists with little signal.

### Goal

Make citations legible and useful.

### Requirements

- render inline numbered citation references
- render a category-level citation list
- add a deduplicated report-level source table
- group by domain and show cited-by categories

Implementation can be client-side using markdown post-processing.

## Improvement 5: Dark Mode

### Problem

The app is light-only even though runs are long and often monitored for extended periods.

### Goal

Add full dark mode with persistence.

### Requirements

- `ThemeProvider` in `hooks/useTheme.js`
- `dark:` classes across views
- persistent theme setting in localStorage
- theme toggle in `Layout.jsx`
- dark-compatible Activity Stream

## Improvement 6: Search Within Results

### Problem

Large evidence reports are hard to navigate.

### Goal

Add client-side search across rendered report sections.

### Requirements

- search input at top of report
- match counts per category
- click to scroll to result
- match highlighting
- debounce input

Native browser search can still work, but the custom report search should be category-aware.

## Improvement 7: PDF Export

### Problem

Stakeholders often need PDF output, not only web rendering or markdown.

### Goal

Use a print-optimized stylesheet and `window.print()` for v2.

### Requirements

- add print stylesheet in `index.css`
- hide UI chrome in print
- force clean typography and full-width content
- add page breaks between categories
- show URLs after links in print
- add `Export PDF` button

Server-side PDF generation is optional later, not required for v2.

## Improvement 8: Executive Verdict Dashboard

### Problem

The current summary is too generic and does not directly answer the user's strategic question.

### Goal

Put a verdict-oriented summary at the top of the results.

### Requirements

- show the user's core question
- show category success and failure counts
- show critical and moderate gaps
- show total sources and total duration
- evaluate success criteria heuristically
- show a compact category confidence grid

The first version can infer success-criteria support client-side from the report content. A future version can add an LLM evaluation pass.

## Recommended File Changes

### Backend

- `innovera-research/api/routes.py`
- `innovera-research/api/models.py`
- `innovera-research/api/progress_bridge.py`
- `innovera-research/output/markdown_formatter.py`

### Frontend Modified

- `innovera-research/frontend/src/App.jsx`
- `innovera-research/frontend/src/components/Layout.jsx`
- `innovera-research/frontend/src/components/ProgressPanel.jsx`
- `innovera-research/frontend/src/components/OutputViewer.jsx`
- `innovera-research/frontend/src/components/CategoryCard.jsx`
- `innovera-research/frontend/src/components/InputForm.jsx`
- `innovera-research/frontend/src/hooks/useResearchRun.js`
- `innovera-research/frontend/src/index.css`

### Frontend New

- `innovera-research/frontend/src/components/ActivityStream.jsx`
- `innovera-research/frontend/src/components/RunHistory.jsx`
- `innovera-research/frontend/src/components/VerdictDashboard.jsx`
- `innovera-research/frontend/src/components/SourcePanel.jsx`
- `innovera-research/frontend/src/components/ReportSearch.jsx`
- `innovera-research/frontend/src/components/ReportSidebar.jsx`
- `innovera-research/frontend/src/hooks/useTheme.js`

## Build Order

### Step 1: Backend Foundations

1. Add `GET /api/research/{run_id}/full`
2. Add `GET /api/research/{run_id}/output/structured`
3. Fix output endpoints to work for historical runs
4. Add `DELETE /api/research/{run_id}`
5. Enhance `GET /api/runs`
6. Add richer log events
7. Remove markdown truncation

### Step 2: Theme And Navigation

1. Add theme provider
2. Update header navigation
3. Add dark mode styles
4. Add print styles

### Step 3: Run History

1. Add routing for history and historical run detail
2. Create `RunHistory.jsx`
3. Wire history view to backend run metadata
4. Add delete flow

### Step 4: Activity Stream

1. Build `ActivityStream.jsx`
2. Update `useResearchRun.js`
3. Restructure `ProgressPanel.jsx`
4. Add pause and auto-scroll behavior

### Step 5: Report Overhaul

1. Fetch structured output
2. Build sidebar table of contents
3. Build enhanced category sections
4. Build verdict dashboard
5. Build source quality panel
6. Replace the old tabbed viewer

### Step 6: Search And Citations

1. Add search bar
2. Add match highlighting
3. Add citation transformation
4. Add aggregated source panel

### Step 7: Polish And Export

1. Add PDF export button
2. Improve responsive behavior
3. Add loading and error states
4. Build frontend and test end to end

## Implementation Notes

### Dependencies

Prefer no new dependencies unless a library meaningfully simplifies a hard problem.

Frontend stack should be sufficient:

- React 19
- Tailwind 4
- `react-markdown`
- `remark-gfm`

Backend should also avoid new dependencies unless clearly necessary.

### Performance

- large report rendering should be memoized by category
- search and deduplication should be memoized
- Activity Stream should cap retained entries

### Backward Compatibility

- keep existing API behavior additive where possible
- preserve CLI compatibility
- ensure historical run files already on disk remain readable
- keep websocket protocol additive

## Success Criteria

- [ ] Reports render as a rich document with sidebar navigation
- [ ] Category sections show full content, not truncated content
- [ ] Verdict dashboard appears at the top of results
- [ ] Activity Stream feels live and readable
- [ ] Run history shows past runs with click-to-view
- [ ] Historical outputs load correctly from disk
- [ ] Dark mode works across all views
- [ ] Sources render as citations and structured source panels
- [ ] Search works across report content
- [ ] PDF export produces a readable printed document
- [ ] Existing functionality still works
- [ ] CLI compatibility remains intact
