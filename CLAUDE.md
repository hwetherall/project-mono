# Innovera Research — Web Frontend v2 Build Spec (Project Mono)

## Overview

This spec covers **v2 improvements** to the existing Innovera Research web frontend. The backend (FastAPI) and research pipeline already work. The frontend (React + Vite + Tailwind) already has a working input form, progress panel, and output viewer. This build focuses on eight improvement areas that transform the app from a functional prototype into a polished, professional research tool.

**Do not rewrite the existing pipeline or backend logic.** All changes are frontend-focused with minimal backend additions (new API endpoints for history, search, and export). The existing components should be refactored in-place, not replaced from scratch.

---

## Current Architecture (unchanged)

```
innovera-research/
├── api/                           # FastAPI backend (mostly unchanged)
│   ├── app.py
│   ├── routes.py                  # Add new endpoints here
│   ├── models.py
│   ├── websocket.py
│   └── progress_bridge.py
├── frontend/                      # React app (major changes)
│   ├── src/
│   │   ├── App.jsx               # Add routing, dark mode provider
│   │   ├── main.jsx
│   │   ├── components/
│   │   │   ├── InputForm.jsx     # Minor tweaks
│   │   │   ├── ProgressPanel.jsx # Major overhaul
│   │   │   ├── OutputViewer.jsx  # Major overhaul
│   │   │   ├── CategoryCard.jsx  # Enhanced
│   │   │   ├── Layout.jsx        # Add nav, dark mode toggle
│   │   │   └── [new components]  # See below
│   │   ├── hooks/
│   │   │   └── useResearchRun.js # Enhanced with log streaming
│   │   └── index.css
│   └── ...
├── output/
│   └── markdown_formatter.py      # Enhanced report structure
└── run_web.py
```

---

## Improvement 1: Report UI Overhaul

### Problem

The current OutputViewer renders raw markdown with `react-markdown` using basic `prose prose-slate` typography. Reports look like a wall of text — no visual hierarchy, truncated content, flat source lists, and no data visualization. The Summary Dashboard tab has four plain stat cards and a basic HTML table.

### Solution

Replace the three-tab OutputViewer with a rich, multi-section report layout that treats the evidence package as a first-class document, not a markdown dump.

### 1.1 New Report Layout Structure

Replace the current tab system with a single scrollable report with a sticky sidebar table of contents:

```
┌─────────────────────────────────────────────────────────┐
│  [Sticky left sidebar]     │  [Main content area]       │
│                            │                            │
│  ▸ Verdict Dashboard       │  ┌──────────────────────┐  │
│  ▸ Executive Summary       │  │  VERDICT DASHBOARD   │  │
│  ▸ Context Signals         │  │  (visual scoring)    │  │
│  ▸ EC-01: Market Sizing    │  └──────────────────────┘  │
│  ▸ EC-02: Competitors      │                            │
│  ▸ EC-03: Investment       │  ┌──────────────────────┐  │
│  ▸ ...                     │  │  EXECUTIVE SUMMARY   │  │
│  ▸ Gap Inventory           │  │  (key findings)      │  │
│  ▸ Sources                 │  └──────────────────────┘  │
│                            │                            │
│  [Download] [Export PDF]   │  ┌──────────────────────┐  │
│  [New Run]                 │  │  EVIDENCE SECTIONS   │  │
│                            │  │  (per category)      │  │
│                            │  └──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Verdict Dashboard (new section at top of report)

A visual scorecard that replaces the basic stat cards. For each of the 13 evidence categories, show:

- **Category name** and ID
- **Status indicator**: green checkmark / red X / amber warning
- **Confidence signal**: a small horizontal bar (green/amber/red) based on source count and gap count
  - 10+ sources, 0 gaps → green (high confidence)
  - 5-9 sources, 0-1 gaps → amber (moderate)
  - <5 sources or 2+ gaps → red (low confidence)
- **One-line key finding**: extracted from the raw report's first substantive paragraph

Layout: a 2-column or 3-column grid of compact cards, each ~120px tall. Color-coded borders. Clicking a card scrolls to that category's section below.

### 1.3 Enhanced Category Sections

Each evidence category section should be rendered as a rich card, not raw markdown. Structure:

```
┌─────────────────────────────────────────────────────────┐
│  EC-01  Market Sizing & Growth                    ✅ 88.6s │
│─────────────────────────────────────────────────────────│
│                                                         │
│  [Key Metrics Bar]                                      │
│  TAM: $2.4-3.0B  |  CAGR: 12-14%  |  Sources: 13      │
│                                                         │
│  [Report Content — rendered markdown, FULL not truncated]│
│  Tables, charts references, analysis text...            │
│                                                         │
│  [Collapsible: Raw GPT Researcher Report]               │
│                                                         │
│  [Gaps] (if any, shown as amber callout cards)          │
│                                                         │
│  [Sources] (clickable links with favicons, grouped)     │
│─────────────────────────────────────────────────────────│
│  ◀ EC-00  Previous  |  Next  EC-02 ▶                    │
└─────────────────────────────────────────────────────────┘
```

**Key changes from current:**
- Show FULL report content, not truncated at 5000 chars. The raw markdown is already available via the `/api/research/{run_id}/output/raw/{category_id}` endpoint — fetch each category's full raw report and render it inline.
- Add a "Key Metrics" extraction bar at the top of each category card. This should be parsed client-side from the raw report content (look for common patterns like TAM values, CAGR percentages, competitor counts). If parsing fails, just skip the metrics bar — it's a progressive enhancement.
- Sources rendered as clickable pills/chips with the domain name visible, not bare URLs in a bullet list.
- Gaps shown as distinct amber/red callout boxes, not plain bullets.
- Next/Previous navigation between categories.

### 1.4 Source Quality Panel

Add a new section at the bottom of the report (or as a collapsible panel):

- Group all sources across all categories
- Deduplicate by URL
- Show: domain, title (if parseable from URL), which categories cited it, and a "freshness" indicator based on any dates in the URL
- Sort by citation count (most-cited sources first)

### 1.5 Backend Changes for Reports

**Modify `output/markdown_formatter.py`:**
- Remove the 5000-char truncation on raw reports — the full report should be available in the main markdown output
- Add a `## Key Metrics` section per category if structured findings are available

**Add new endpoint `GET /api/research/{run_id}/output/structured`:**
Returns a JSON representation of the evidence package optimized for the frontend:

```json
{
  "venture_name": "...",
  "metadata": { "generated_at": "...", "industry": "...", ... },
  "context_signals": { "problem_summary": "...", "solution_summary": "...", ... },
  "categories": [
    {
      "category_id": "EC-01",
      "category_name": "Market Sizing & Growth",
      "status": "success",
      "execution_time_seconds": 88.6,
      "source_count": 13,
      "gap_count": 0,
      "gaps": [],
      "sources": [{"url": "...", "domain": "..."}, ...],
      "raw_report_markdown": "full report text..."
    }
  ],
  "gap_inventory": { "critical": [...], "moderate": [...] }
}
```

This endpoint reads from the YAML evidence package and raw report files. It lets the frontend render a rich structured UI without parsing markdown.

### 1.6 Typography and Visual Polish

- Use a serif font for report body text (e.g., `Georgia`, `Crimson Text`, or `Source Serif Pro` from Google Fonts) to make reports feel like documents, not apps.
- Use a monospace font for data tables, metrics, and category IDs.
- Increase line-height in report content to 1.7 for readability.
- Add subtle left-border color coding to category sections (green for success, red for failed).
- Use proper typographic hierarchy: larger, bolder section headers; lighter body text; accent colors for key metrics.

---

## Improvement 2: Live Process Stream

### Problem

The current ProgressPanel has a collapsible `<details>` event log at the bottom that shows raw event types like `phase_start [FOUNDATION]`. It doesn't feel like watching something happen — it's a hidden debug log. The user wants to see "what's happening under the hood."

### Solution

Add a real-time activity stream that looks like a terminal/build log, prominently placed, not hidden.

### 2.1 Activity Stream Component (`components/ActivityStream.jsx`)

A new component that renders a scrolling, auto-tailing log of human-readable activity messages:

```
┌─────────────────────────────────────────────────────────┐
│  Activity Stream                              [Pause] ▼ │
│─────────────────────────────────────────────────────────│
│  10:14:02  ● Extracting context from venture documents  │
│  10:14:38  ✓ Context ready — LGIT Medical (MedTech)     │
│  10:14:38  ● Starting Phase 1: Foundation               │
│  10:14:39  → EC-01 Market Sizing & Growth started       │
│  10:14:39  → EC-02 Competitor Landscape started         │
│  10:16:08  ✓ EC-01 completed (88.6s, 13 sources)       │
│  10:17:22  ⚠ EC-02 rate limited — waiting 23s (2/6)    │
│  10:17:45  → EC-02 retrying...                          │
│  10:19:51  ✓ EC-02 completed (315.2s, 22 sources)      │
│  10:19:52  📋 Extracted 5 competitors from EC-02        │
│  10:19:52  ● Starting Phase 2: Competitor-Dependent     │
│  ...                                                    │
│                                          [auto-scroll ▼]│
└─────────────────────────────────────────────────────────┘
```

**Design specifications:**
- Dark background (`slate-900` or `gray-900`) with colored text — like a terminal
- Fixed height (~300px) with overflow scroll and auto-scroll to bottom
- Timestamps in `HH:MM:SS` format (from event time, not system clock)
- Different prefix icons by event type:
  - `●` (blue) = phase/process starting
  - `→` (cyan) = category starting
  - `✓` (green) = success
  - `✗` (red) = failure
  - `⚠` (amber) = rate limit / warning
  - `📋` (purple) = info extraction
  - `…` (gray) = general log message
- Each line is a single human-readable sentence, not raw JSON
- "Pause" button stops auto-scroll (lets user read history)
- Monospace font (`JetBrains Mono` or `Fira Code` from Google Fonts, or system mono)

### 2.2 Enhanced WebSocket Events for Streaming

**Add new event type `log_detail`** from the progress bridge. Currently, the bridge emits `log` events but they're sparse. Enhance the bridge to emit more detailed operational events:

```python
# In progress_bridge.py — add these new emission points:

# When context extraction starts
await self._emit({"type": "log_detail", "level": "info", "message": "Extracting context signals from venture documents..."})

# When context extraction completes
await self._emit({"type": "log_detail", "level": "success", "message": f"Context ready — {venture_name} ({industry})"})

# When a category's GPT Researcher query is constructed
await self._emit({"type": "log_detail", "level": "info", "message": f"Building research query for {category_name}..."})

# When GPT Researcher starts deep research
await self._emit({"type": "log_detail", "level": "info", "message": f"GPT Researcher running deep research for {category_id}..."})

# When a category's report is being parsed
await self._emit({"type": "log_detail", "level": "info", "message": f"Parsing findings from {category_id} report..."})

# When competitor extraction happens
await self._emit({"type": "log_detail", "level": "info", "message": f"Extracting competitor list from EC-02 results..."})

# Package assembly
await self._emit({"type": "log_detail", "level": "info", "message": "Assembling evidence package..."})
await self._emit({"type": "log_detail", "level": "info", "message": "Writing YAML output..."})
await self._emit({"type": "log_detail", "level": "info", "message": "Writing Markdown report..."})
```

These should be emitted from `routes.py` within the `run_pipeline()` function at each pipeline stage, **not** by modifying the existing pipeline code. The route handler wraps each pipeline call and emits before/after events through the progress bridge.

### 2.3 Revised Progress Panel Layout

Restructure ProgressPanel to show the activity stream prominently alongside the category grid:

```
┌─────────────────────────────────────────────────────────┐
│  [Status bar: Running — Phase 1: Foundation    12:34]   │
│─────────────────────────────────────────────────────────│
│  [Context info bar — venture name, industry, etc.]      │
│─────────────────────────────────────────────────────────│
│                        │                                │
│  [Category Grid]       │  [Activity Stream]             │
│  Phase 1: Foundation   │  10:14:02  ● Extracting...     │
│  ┌─────┐ ┌─────┐     │  10:14:38  ✓ Context ready      │
│  │EC-01│ │EC-02│     │  10:14:39  → EC-01 started       │
│  │ ✅  │ │ 🔄  │     │  ...                             │
│  └─────┘ └─────┘     │                                  │
│  ┌─────┐ ┌─────┐     │                                  │
│  │EC-05│ │EC-06│     │                                  │
│  │ ⏳  │ │ ⏳  │     │                                  │
│  └─────┘ └─────┘     │                                  │
│                        │                                │
│  Phase 2: Competitor   │                                │
│  (waiting...)          │                                │
│                        │                                │
└─────────────────────────────────────────────────────────┘
```

On smaller screens (< 1024px), stack the category grid above the activity stream instead of side-by-side.

### 2.4 Hook Changes

In `useResearchRun.js`, add:

```javascript
const [activityLog, setActivityLog] = useState([]);

// In the WebSocket message handler:
case 'log_detail':
case 'log':
  setActivityLog(prev => [...prev, {
    timestamp: Date.now(),
    level: event.level || 'info',
    message: event.message,
  }]);
  break;

// Also generate human-readable log entries from existing events:
case 'phase_start':
  setActivityLog(prev => [...prev, {
    timestamp: Date.now(),
    level: 'info',
    message: `Starting ${formatPhaseName(event.phase)}`,
  }]);
  break;

case 'category_start':
  setActivityLog(prev => [...prev, {
    timestamp: Date.now(),
    level: 'start',
    message: `${event.category_id} ${event.category_name} started`,
  }]);
  break;

case 'category_end':
  const msg = event.status === 'success'
    ? `${event.category_id} completed (${event.elapsed_seconds.toFixed(1)}s, ${event.source_count} sources)`
    : `${event.category_id} failed: ${event.error || 'unknown error'}`;
  setActivityLog(prev => [...prev, {
    timestamp: Date.now(),
    level: event.status === 'success' ? 'success' : 'error',
    message: msg,
  }]);
  break;

case 'rate_limit':
  setActivityLog(prev => [...prev, {
    timestamp: Date.now(),
    level: 'warning',
    message: `${event.category_id} rate limited — waiting ${event.wait_seconds}s (attempt ${event.attempt}/${event.max_attempts})`,
  }]);
  break;
```

Return `activityLog` from the hook.

---

## Improvement 3: Run History

### Problem

There is no way to view past runs. The `/api/runs` endpoint exists and `run_meta.json` files are saved to disk, but the frontend has no history UI. Every time you click "New Run," the previous run is gone.

### Solution

Add a full run history system with a sidebar or dedicated view.

### 3.1 History Panel (`components/RunHistory.jsx`)

A list view of past runs, accessible from the main navigation:

```
┌─────────────────────────────────────────────────────────┐
│  Run History                                            │
│─────────────────────────────────────────────────────────│
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  LGIT Medical Device Expansion                  │    │
│  │  Mar 11, 2026 · 13/13 categories · 87 min      │    │
│  │  ✅ Complete · 160 sources · 0 critical gaps     │    │
│  │                                        [View →] │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  AquaSense Technologies                         │    │
│  │  Mar 10, 2026 · 8/13 categories · 52 min       │    │
│  │  ⚠ Partial · 95 sources · 2 critical gaps       │    │
│  │                                        [View →] │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  [Load More]                                            │
└─────────────────────────────────────────────────────────┘
```

Each run card shows:
- Venture name (from run_meta.json)
- Date and time
- Category success/fail count
- Total duration
- Status badge (Complete / Partial / Failed)
- Source count and gap summary
- Click to view the full report

### 3.2 Navigation Changes

Currently the app has no routing — just a state machine (`input | running | results`). Add simple client-side routing:

**Option A (recommended): Hash-based routing** — no library needed.

Add a lightweight routing mechanism to `App.jsx`:

```javascript
// States: input, running, results, history, history/{runId}
const [view, setView] = useState('input');
const [historicalRunId, setHistoricalRunId] = useState(null);
```

Update `Layout.jsx` header to include navigation links:

```
┌─────────────────────────────────────────────────────────┐
│  [IR] Innovera Research    [New Run] [History] [⚙]     │
└─────────────────────────────────────────────────────────┘
```

- "New Run" → goes to input form
- "History" → shows RunHistory panel
- Clicking a historical run → loads it into OutputViewer

### 3.3 Loading Historical Runs

When viewing a historical run, the frontend needs to reconstruct the run state. Add a new backend endpoint:

**`GET /api/research/{run_id}/full`** — Returns everything needed to render the output viewer for a past run:

```json
{
  "run_id": "5c5d6f83-...",
  "venture_name": "LGIT Medical Device Expansion",
  "started_at": "2026-03-11T06:17:34Z",
  "completed_at": "2026-03-11T07:44:52Z",
  "status": "completed",
  "categories_succeeded": 13,
  "categories_failed": 0,
  "total_sources": 160,
  "request": { /* original ResearchRequest */ },
  "categories": {
    "EC-01": {
      "category_id": "EC-01",
      "category_name": "Market Sizing & Growth",
      "status": "success",
      "source_count": 13,
      "gap_count": 0,
      "elapsed_seconds": 88.6
    }
    /* ... all 13 categories ... */
  }
}
```

This endpoint reads from `run_meta.json` and the YAML evidence package on disk. It does NOT require the run to be in `active_runs` memory.

Also update the existing output endpoints (`/output/yaml`, `/output/markdown`, `/output/raw/{category_id}`) to work for historical runs by looking up file paths from disk when the run isn't in `active_runs`.

### 3.4 Backend Changes for History

In `api/routes.py`:

1. **Enhance `GET /api/runs`** to return richer metadata (currently minimal).
2. **Add `GET /api/research/{run_id}/full`** endpoint.
3. **Fix output endpoints** to fall back to disk-based file lookup when run is not in `active_runs`:
   - Read `run_meta.json` to find the venture slug
   - Glob for `*.yaml`, `*.md`, and `raw_reports/*.md` in `output_packages/{run_id}/`
   - Serve the files

### 3.5 Delete Run

Add `DELETE /api/research/{run_id}` that removes the run directory from disk. Show a delete button (with confirmation) on each history card.

---

## Improvement 4: Source Citations & Quality Panel

### Problem

Sources are currently displayed as bare URL bullet lists at the bottom of each category. There's no deduplication, no domain indicators, no way to assess source quality.

### Solution

### 4.1 Inline Source Citations

Within the rendered markdown content, where source URLs appear, render them as numbered citation footnotes:

```
The global CGM market reached $15.3B in 2026 [1][2], with a projected
CAGR of 15.4% through 2031 [1].
```

At the bottom of each category section, show the citation list:

```
Sources:
[1] mordorintelligence.com — Continuous Glucose Monitoring Market
[2] straitsresearch.com — Glucose Monitoring Devices Market Report
[3] linkedin.com — Neurostimulation Device Market Analysis
```

**Implementation approach:** This is a client-side post-processing step. After fetching the raw report markdown, scan for URL patterns and replace them with numbered footnote references. Create a custom `react-markdown` component that handles this transformation.

### 4.2 Aggregated Source Panel

Add a collapsible "All Sources" section at the end of the report:

- Deduplicate URLs across all categories
- Group by domain
- Show which categories cite each source
- Sort by citation frequency (most-cited first)
- Display as a clean table:

```
| # | Domain              | Cited By              | Citations |
|---|---------------------|-----------------------|-----------|
| 1 | mordorintelligence  | EC-01, EC-05, EC-13   | 7         |
| 2 | linkedin.com        | EC-02, EC-03, EC-11   | 5         |
| 3 | grandviewresearch   | EC-01, EC-12          | 3         |
```

---

## Improvement 5: Dark Mode

### Problem

Research runs take 30-90 minutes. Users monitor progress during late hours. The current UI is light-only with hardcoded `bg-slate-50` and `text-slate-900`.

### Solution

### 5.1 Dark Mode Implementation

Use Tailwind's `dark:` variant classes. Add a `ThemeProvider` context:

```javascript
// hooks/useTheme.js
const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'system';
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
```

### 5.2 Color Palette

Define dark mode equivalents for all current colors:

| Element | Light | Dark |
|---------|-------|------|
| Page background | `bg-slate-50` | `dark:bg-slate-950` |
| Card background | `bg-white` | `dark:bg-slate-900` |
| Card border | `border-slate-200` | `dark:border-slate-700` |
| Primary text | `text-slate-900` | `dark:text-slate-100` |
| Secondary text | `text-slate-500` | `dark:text-slate-400` |
| Header | `bg-white` | `dark:bg-slate-900` |
| Activity stream | `bg-slate-900` | `dark:bg-black` |
| Code/mono | `bg-slate-100` | `dark:bg-slate-800` |

### 5.3 Toggle Location

Add a theme toggle button (sun/moon icon) to the Layout header, next to the navigation links.

### 5.4 Activity Stream in Dark Mode

The activity stream already uses a dark background — in light mode it uses `slate-900`, in dark mode use `black` or `slate-950`. This component looks naturally good in both modes.

---

## Improvement 6: Search Within Results

### Problem

Evidence reports can be 1000+ lines across 13 categories. Finding specific information (e.g., a competitor name, a market figure) requires scrolling through everything.

### Solution

### 6.1 Search Bar in OutputViewer

Add a search input at the top of the report view:

```
┌─────────────────────────────────────────────────────────┐
│  🔍 Search results...     [x]                           │
│─────────────────────────────────────────────────────────│
│  Found 7 matches for "CAGR" across 4 categories        │
│  ▸ EC-01 Market Sizing (3 matches)                      │
│  ▸ EC-05 Problem Prevalence (2 matches)                 │
│  ▸ EC-07 Technology Trends (1 match)                    │
│  ▸ EC-13 Proxy Markets (1 match)                        │
└─────────────────────────────────────────────────────────┘
```

Clicking a search result scrolls to and highlights that section. Highlights are shown with a yellow/amber background on matching text within the rendered markdown.

### 6.2 Implementation

- Search operates client-side on the fetched report content
- Debounce input (300ms)
- Use `mark.js` or a custom React component to highlight matches
- Show match count per category
- Keyboard shortcut: `Ctrl+F` when the report is focused could open this search (or just let the browser's native search work and add the custom search as a category-level filter)

---

## Improvement 7: PDF Export

### Problem

Stakeholders who receive research output need it as a PDF, not as a web page or raw markdown file.

### Solution

### 7.1 Client-Side PDF Generation

Use the browser's `window.print()` with a print-optimized stylesheet. This is the simplest approach that produces good results:

**Add a `@media print` section to `index.css`:**

```css
@media print {
  /* Hide UI chrome */
  header, nav, .no-print, button { display: none !important; }
  
  /* Full width content */
  main { max-width: 100% !important; padding: 0 !important; }
  
  /* Clean typography for print */
  .prose { font-size: 11pt; line-height: 1.5; }
  
  /* Page breaks between categories */
  .category-section { page-break-before: always; }
  .category-section:first-child { page-break-before: avoid; }
  
  /* Ensure tables don't break */
  table { page-break-inside: avoid; }
  
  /* Dark backgrounds to white for print */
  * { background: white !important; color: black !important; }
  
  /* Show URLs after links */
  a[href]::after { content: " (" attr(href) ")"; font-size: 9pt; color: #666; }
}
```

**Add a "Export PDF" button** that calls `window.print()`. The user can then save as PDF from the print dialog.

### 7.2 Stretch Goal: Server-Side PDF

For a more polished PDF, add a backend endpoint that uses `weasyprint` or `pdfkit` to generate a styled PDF. This is a stretch goal — the print stylesheet approach works well for v2.

---

## Improvement 8: Executive Verdict Dashboard

### Problem

The current Summary Dashboard tab has four generic stat cards (succeeded, failed, total sources, total time). It doesn't help the user answer their core strategic question.

### Solution

### 8.1 Verdict Header

At the very top of the results view, show a prominent verdict card that directly addresses the user's `core_question`:

```
┌─────────────────────────────────────────────────────────┐
│  📊 Research Verdict                                    │
│                                                         │
│  "Should we invest in LGIT's medical device expansion?" │
│                                                         │
│  Evidence Collected: 160 sources across 13 categories   │
│  Duration: 87 minutes                                   │
│  Critical Gaps: 0  |  Moderate Gaps: 2                  │
│                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                │
│  │ ✅ 13   │  │ ❌ 0    │  │ ⚠ 2     │                │
│  │succeeded│  │ failed  │  │ gaps    │                │
│  └─────────┘  └─────────┘  └─────────┘                │
│                                                         │
│  Success Criteria Assessment:                           │
│  ✅ TAM > $500M — Supported (TAM $2.4-3.0B, EC-01)    │
│  ✅ ≥3 competitors funded — Supported (5 identified)    │
│  ⚠ Regulatory tailwind — Inconclusive (mixed signals)  │
└─────────────────────────────────────────────────────────┘
```

### 8.2 Success Criteria Evaluation

The user's `success_criteria` are stored in the `ResearchRequest`. Display them alongside a simple heuristic evaluation:

- Pull each criterion text from the request
- Display with a status icon: ✅ / ⚠ / ❌ / ❓
- For v2, the status is manually inferred client-side by keyword-matching criteria against report content (e.g., if criterion mentions "TAM" and EC-01 report contains a number > threshold, mark as supported)
- For v3, add an LLM evaluation step on the backend

### 8.3 Category Confidence Grid

Below the verdict, show a compact visual grid of all 13 categories with confidence indicators:

```
  EC-01  EC-02  EC-03  EC-04  EC-05  EC-06  EC-07
  🟢     🟢     🟡     🟢     🟢     🟢     🟡

  EC-08  EC-09  EC-10  EC-11  EC-12  EC-13
  🟢     🟢     🟡     🟢     🟢     🟢
```

Color coding:
- 🟢 Green: success + 10+ sources + 0 gaps
- 🟡 Yellow: success + <10 sources OR >0 gaps
- 🔴 Red: failed

Hovering shows a tooltip with the category name and key stats.

---

## Build Order

### Step 1: Backend Enhancements (prerequisite for everything)
1. Add `GET /api/research/{run_id}/full` endpoint
2. Add `GET /api/research/{run_id}/output/structured` endpoint
3. Fix output endpoints to work for historical runs (disk fallback)
4. Add `DELETE /api/research/{run_id}` endpoint
5. Enhance `GET /api/runs` to return richer metadata
6. Add `log_detail` events to progress bridge
7. Remove 5000-char truncation from markdown formatter
8. **Test:** Verify all endpoints work with existing run data on disk

### Step 2: Dark Mode + Theme Infrastructure
1. Create `useTheme.js` hook and `ThemeProvider`
2. Update `Layout.jsx` with theme toggle and navigation links
3. Update `index.css` with dark mode CSS variables
4. Add `dark:` variants to all existing components
5. Add print stylesheet to `index.css`
6. **Test:** Toggle dark mode, verify all components render correctly

### Step 3: Navigation + History
1. Add view routing to `App.jsx` (add `history` and `history/{runId}` views)
2. Create `RunHistory.jsx` component
3. Wire up history view to `GET /api/runs` endpoint
4. Wire up historical run loading to `GET /api/research/{run_id}/full`
5. Update Layout header with New Run / History links
6. Add delete functionality to history cards
7. **Test:** View history, click into a past run, see its results

### Step 4: Activity Stream
1. Create `ActivityStream.jsx` component
2. Update `useResearchRun.js` to track `activityLog`
3. Add human-readable log generation from existing WebSocket events
4. Restructure `ProgressPanel.jsx` to side-by-side layout with stream
5. Add pause/resume scroll functionality
6. **Test:** Start a run, verify activity stream shows real-time events

### Step 5: Report UI Overhaul
1. Create the structured report endpoint data fetching
2. Build sidebar table of contents component
3. Build enhanced category section cards
4. Build verdict dashboard component
5. Build source quality panel
6. Replace current OutputViewer tabs with new scrollable layout
7. Add next/previous category navigation
8. **Test:** View a completed run, verify all sections render correctly

### Step 6: Search + Citations
1. Build search bar component for results view
2. Implement client-side text search across categories
3. Add match highlighting
4. Build source citation footnote system
5. Build aggregated source panel
6. **Test:** Search for terms, verify highlighting and navigation

### Step 7: Polish + PDF
1. Wire up PDF export button with print stylesheet
2. Add responsive breakpoints for all new components
3. Polish dark mode for all new components
4. Add loading states and error boundaries
5. Performance: ensure large reports don't lag (virtualize if needed)
6. Build production frontend (`npm run build`)
7. **Test:** Full end-to-end flow: start run → watch progress → view results → export PDF → view in history

---

## Key Implementation Notes

### No New Dependencies (Frontend)

Try to avoid adding new npm packages. The existing stack (React 19, Tailwind 4, react-markdown, remark-gfm) is sufficient for all features described. If a library is truly needed (e.g., `mark.js` for search highlighting), that's fine — but prefer vanilla implementations.

### No New Dependencies (Backend)

No new Python packages needed. All new endpoints use existing FastAPI, Pydantic, and file I/O.

### Performance Considerations

- Large reports (1000+ lines of markdown) can be slow to render with `react-markdown`. Consider splitting rendering by category section and using `React.memo` to avoid re-renders.
- The activity stream can accumulate hundreds of entries during a long run. Cap the display at the most recent 500 entries and use a virtualized list if performance is an issue.
- Source deduplication and search should be computed once and memoized with `useMemo`.

### Backward Compatibility

- All existing API endpoints remain unchanged in behavior
- The existing CLI (`python run_research.py`) still works unchanged
- Existing `run_meta.json` files on disk should be readable by the new history system
- The WebSocket protocol is additive — new event types are added, none removed

### File Changes Summary

**Backend (modify):**
- `api/routes.py` — add 3 new endpoints, fix disk fallback on output endpoints
- `api/models.py` — add response models for new endpoints
- `api/progress_bridge.py` — add `log_detail` emission capability
- `output/markdown_formatter.py` — remove truncation

**Frontend (modify):**
- `src/App.jsx` — add routing, theme provider
- `src/components/Layout.jsx` — add nav, dark mode toggle
- `src/components/ProgressPanel.jsx` — restructure with activity stream
- `src/components/OutputViewer.jsx` — complete rewrite to structured layout
- `src/components/CategoryCard.jsx` — add dark mode classes
- `src/components/InputForm.jsx` — add dark mode classes
- `src/hooks/useResearchRun.js` — add activityLog, enhance event handling
- `src/index.css` — dark mode, print styles, typography

**Frontend (new):**
- `src/components/ActivityStream.jsx`
- `src/components/RunHistory.jsx`
- `src/components/VerdictDashboard.jsx`
- `src/components/SourcePanel.jsx`
- `src/components/ReportSearch.jsx`
- `src/components/ReportSidebar.jsx`
- `src/hooks/useTheme.js`

---

## Success Criteria for This Build

- [ ] Report output has a rich, document-like layout with sidebar TOC, not a flat markdown dump
- [ ] Each evidence category renders as a structured card with full (non-truncated) content
- [ ] Verdict dashboard shows at top of results with success criteria assessment
- [ ] Activity stream shows real-time, human-readable progress during a run
- [ ] Activity stream has terminal-like dark styling with colored status icons
- [ ] Run history shows all past runs with click-to-view
- [ ] Historical runs load fully with all output viewable
- [ ] Dark mode works across all views and persists in localStorage
- [ ] Sources are displayed as clickable citation chips, not bare URLs
- [ ] Aggregated source panel shows cross-category source statistics
- [ ] Search within results finds and highlights matches across categories
- [ ] PDF export produces a clean, readable document
- [ ] All existing functionality (input form, progress, downloads) still works
- [ ] The existing CLI (`python run_research.py`) still works unchanged
