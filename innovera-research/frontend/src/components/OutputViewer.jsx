import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import VerdictDashboard from './VerdictDashboard';
import ReportSidebar from './ReportSidebar';
import ReportSearch from './ReportSearch';
import SourcePanel, { SourceChips } from './SourcePanel';
import CompetitiveTable from './CompetitiveTable';

export default function OutputViewer({ run, onNewRun, historicalRunId, chainSteps, chainId }) {
  const [structuredData, setStructuredData] = useState(null);
  const [historicalData, setHistoricalData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState('section-verdict');
  const [searchTerm, setSearchTerm] = useState('');
  const contentRef = useRef(null);

  // --- Chain tab state ---
  const isChainView = !!(chainSteps && chainSteps.length > 0);
  const completedChainSteps = isChainView
    ? chainSteps.filter((s) => s.status === 'completed' || s.status === 'failed')
    : [];
  const [activeChainTab, setActiveChainTab] = useState(0);

  // Determine active sub-run ID for chain view
  const activeChainStep = isChainView ? chainSteps[activeChainTab] : null;
  const chainSubRunId = activeChainStep?.run_id;

  // Determine run ID — either chain sub-run, historical, or active run
  const runId = isChainView ? chainSubRunId : (historicalRunId || run.runId);

  // Load structured data
  useEffect(() => {
    if (!runId) {
      setLoading(false);
      return;
    }
    setLoading(true);

    const fetches = [
      fetch(`/api/research/${runId}/output/structured`).then((r) => r.ok ? r.json() : null),
    ];

    if (historicalRunId && !isChainView) {
      fetches.push(
        fetch(`/api/research/${runId}/full`).then((r) => r.ok ? r.json() : null)
      );
    }

    Promise.all(fetches)
      .then(([structured, historical]) => {
        setStructuredData(structured);
        if (historical) setHistoricalData(historical);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [runId, historicalRunId, isChainView]);

  // Use historical categories if viewing past run
  const categories = historicalRunId && historicalData
    ? historicalData.categories
    : run.categories;

  const result = historicalRunId && historicalData
    ? { elapsed_seconds: historicalData.duration_seconds || 0, succeeded: historicalData.categories_succeeded, failed: historicalData.categories_failed }
    : run.result;

  const request = historicalRunId && historicalData
    ? historicalData.request
    : null;

  // Handle download
  const handleDownload = async (type) => {
    const url = `/api/research/${runId}/output/${type}`;
    const res = await fetch(url);
    if (!res.ok) return;
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = type === 'yaml' ? 'evidence.yaml' : 'evidence.md';
    a.click();
    URL.revokeObjectURL(a.href);
  };

  // Scroll tracking for sidebar
  useEffect(() => {
    const container = contentRef.current;
    if (!container) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        }
      },
      { root: null, rootMargin: '-100px 0px -60% 0px', threshold: 0.1 }
    );

    const sections = container.querySelectorAll('[id^="section-"]');
    sections.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, [structuredData, loading]);

  const handleJumpTo = useCallback((categoryId) => {
    const el = document.getElementById(`section-${categoryId}`);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, []);

  if (loading) {
    return (
      <div className="text-center py-12 text-slate-400 dark:text-slate-500">Loading report...</div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header bar */}
      <div className="flex items-center justify-between no-print">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
          {structuredData?.venture_name || 'Research Results'}
          {isChainView && (
            <span className="ml-3 text-sm font-normal text-emerald-600 dark:text-emerald-400">
              Run All Chapters
            </span>
          )}
        </h2>
        <div className="flex gap-2">
          {structuredData?.categories?.length > 0 && (
            <>
              <button
                onClick={() => handleDownload('markdown')}
                className="px-3 py-1.5 text-sm border border-slate-300 dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-colors"
              >
                Download MD
              </button>
              <button
                onClick={() => handleDownload('yaml')}
                className="px-3 py-1.5 text-sm border border-slate-300 dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-colors"
              >
                Download YAML
              </button>
            </>
          )}
          <button
            onClick={() => window.print()}
            className="px-3 py-1.5 text-sm border border-slate-300 dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-colors"
          >
            Export PDF
          </button>
          <button
            onClick={onNewRun}
            className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            New Run
          </button>
        </div>
      </div>

      {/* Chain Tab Bar */}
      {isChainView && (
        <div className="flex gap-1 p-1 bg-slate-100 dark:bg-slate-800 rounded-lg no-print">
          {chainSteps.map((step, i) => {
            const isActive = i === activeChainTab;
            const stepStatus = step.status;
            const statusDot =
              stepStatus === 'completed' ? 'bg-green-500'
              : stepStatus === 'failed' ? 'bg-red-500'
              : stepStatus === 'running' ? 'bg-blue-500 animate-pulse'
              : 'bg-slate-400';

            return (
              <button
                key={step.mode}
                onClick={() => {
                  setActiveChainTab(i);
                  setActiveSection('section-verdict');
                }}
                disabled={!step.run_id}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-md text-sm font-medium transition-colors
                  ${isActive
                    ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 shadow-sm'
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'
                  }
                  ${!step.run_id ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                `}
              >
                <span className={`w-2 h-2 rounded-full ${statusDot}`} />
                {step.mode_label}
              </button>
            );
          })}
        </div>
      )}

      {/* Search */}
      {structuredData?.categories && (
        <div className="no-print">
          <ReportSearch
            categories={structuredData.categories}
            onJumpTo={handleJumpTo}
            onSearchChange={setSearchTerm}
          />
        </div>
      )}

      {/* Main layout: sidebar + content */}
      <div className="flex gap-6">
        {/* Sidebar */}
        {structuredData?.categories && (
          <div className="hidden xl:block w-56 shrink-0 no-print">
            <ReportSidebar
              categories={structuredData.categories}
              activeSection={activeSection}
              hasCompetitiveTable={!!structuredData.competitive_table}
            />
          </div>
        )}

        {/* Content */}
        <div ref={contentRef} className="flex-1 min-w-0 space-y-6 report-scroll">
          {/* Verdict Dashboard */}
          <div id="section-verdict">
            <VerdictDashboard
              structuredData={structuredData}
              categories={categories}
              result={result}
              request={request}
            />
          </div>

          {/* Executive Summary */}
          {structuredData?.context_signals && (
            <div id="section-summary" className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl p-6">
              <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-4">Executive Summary</h2>
              <div className="space-y-3 text-sm text-slate-700 dark:text-slate-300">
                {structuredData.context_signals.problem_summary && (
                  <div>
                    <span className="font-semibold text-slate-900 dark:text-slate-100">Problem:</span>{' '}
                    {structuredData.context_signals.problem_summary}
                  </div>
                )}
                {structuredData.context_signals.solution_summary && (
                  <div>
                    <span className="font-semibold text-slate-900 dark:text-slate-100">Solution:</span>{' '}
                    {structuredData.context_signals.solution_summary}
                  </div>
                )}
                {structuredData.context_signals.target_customer_summary && (
                  <div>
                    <span className="font-semibold text-slate-900 dark:text-slate-100">Target Customer:</span>{' '}
                    {structuredData.context_signals.target_customer_summary}
                  </div>
                )}
                {structuredData.context_signals.problem_keywords?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {structuredData.context_signals.problem_keywords.map((kw, i) => (
                      <span key={i} className="px-2 py-0.5 text-xs rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                        {kw}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Competitive Table */}
          {structuredData?.competitive_table && (
            <CompetitiveTable table={structuredData.competitive_table} />
          )}

          {/* Category Sections */}
          {structuredData?.categories?.map((cat, idx) => (
            <CategorySection
              key={cat.category_id}
              category={cat}
              runId={runId}
              prevCat={structuredData.categories[idx - 1]}
              nextCat={structuredData.categories[idx + 1]}
              onJumpTo={handleJumpTo}
              searchTerm={searchTerm}
            />
          ))}

          {/* Gap Inventory */}
          {structuredData?.gap_inventory && (
            <GapInventory gaps={structuredData.gap_inventory} />
          )}

          {/* Source Panel */}
          {structuredData?.categories && (
            <SourcePanel categories={structuredData.categories} />
          )}
        </div>
      </div>
    </div>
  );
}

function CategorySection({ category, runId, prevCat, nextCat, onJumpTo, searchTerm }) {
  const [expanded, setExpanded] = useState(true);
  const statusIcon = category.status === 'success' ? '\u2705' : category.status === 'failed' ? '\u274C' : '\u26A0\uFE0F';
  const borderColor = category.status === 'success'
    ? 'border-l-green-500'
    : category.status === 'failed'
      ? 'border-l-red-500'
      : 'border-l-amber-500';

  const timeStr = category.execution_time_seconds
    ? `${category.execution_time_seconds.toFixed(1)}s`
    : '';

  return (
    <div
      id={`section-${category.category_id}`}
      className={`category-section bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden border-l-4 ${borderColor}`}
    >
      {/* Header */}
      <div className="p-5 pb-3">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-sm font-mono text-slate-400 dark:text-slate-500 font-bold">{category.category_id}</span>
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">{category.category_name}</h3>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            <span>{statusIcon}</span>
            {timeStr && <span className="font-mono">{timeStr}</span>}
          </div>
        </div>

        {/* Key metrics bar */}
        <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400 font-mono pb-3 border-b border-slate-100 dark:border-slate-800">
          <span>Sources: <span className="font-bold text-slate-700 dark:text-slate-300">{category.source_count}</span></span>
          <span>Gaps: <span className={`font-bold ${category.gap_count > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-slate-700 dark:text-slate-300'}`}>{category.gap_count}</span></span>
        </div>
      </div>

      {/* Report content */}
      {category.raw_report_markdown && (
        <div className="px-5 pb-4">
          <div className="report-prose prose prose-slate dark:prose-invert max-w-none text-sm">
            <Markdown
              remarkPlugins={[remarkGfm]}
              components={searchTerm && searchTerm.length >= 2 ? {
                text: ({ children }) => {
                  if (typeof children !== 'string') return children;
                  const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
                  const parts = children.split(regex);
                  if (parts.length <= 1) return children;
                  return parts.map((part, i) =>
                    regex.test(part) ? <mark key={i} className="search-highlight">{part}</mark> : part
                  );
                },
              } : undefined}
            >{category.raw_report_markdown}</Markdown>
          </div>
        </div>
      )}

      {/* Gaps */}
      {category.gaps?.length > 0 && (
        <div className="px-5 pb-4">
          <h4 className="text-sm font-semibold text-amber-700 dark:text-amber-400 mb-2">Gaps Identified</h4>
          <div className="space-y-1.5">
            {category.gaps.map((gap, i) => (
              <div key={i} className="px-3 py-2 text-sm bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg text-amber-800 dark:text-amber-300">
                {gap}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sources as chips */}
      {category.sources?.length > 0 && (
        <div className="px-5 pb-4">
          <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Sources</h4>
          <SourceChips sources={category.sources} />
        </div>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between px-5 py-3 border-t border-slate-100 dark:border-slate-800 text-sm no-print">
        {prevCat ? (
          <button
            onClick={() => onJumpTo(prevCat.category_id)}
            className="text-blue-600 dark:text-blue-400 hover:underline"
          >
            &larr; {prevCat.category_id}
          </button>
        ) : <span />}
        {nextCat ? (
          <button
            onClick={() => onJumpTo(nextCat.category_id)}
            className="text-blue-600 dark:text-blue-400 hover:underline"
          >
            {nextCat.category_id} &rarr;
          </button>
        ) : <span />}
      </div>
    </div>
  );
}

function GapInventory({ gaps }) {
  const criticalGaps = gaps.critical || [];
  const moderateGaps = gaps.moderate || [];

  if (criticalGaps.length === 0 && moderateGaps.length === 0) return null;

  return (
    <div id="section-gaps" className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl p-6">
      <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-4">Gap Inventory</h2>

      {criticalGaps.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-semibold text-red-700 dark:text-red-400 mb-2">Critical Gaps</h3>
          <div className="space-y-1.5">
            {criticalGaps.map((gap, i) => (
              <div key={i} className="px-3 py-2 text-sm bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-800 dark:text-red-300">
                <span className="font-mono text-xs text-red-500 dark:text-red-400 mr-2">{gap.category_id}</span>
                {gap.gap}
              </div>
            ))}
          </div>
        </div>
      )}

      {moderateGaps.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-amber-700 dark:text-amber-400 mb-2">Moderate Gaps</h3>
          <div className="space-y-1.5">
            {moderateGaps.map((gap, i) => (
              <div key={i} className="px-3 py-2 text-sm bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg text-amber-800 dark:text-amber-300">
                <span className="font-mono text-xs text-amber-500 dark:text-amber-400 mr-2">{gap.category_id}</span>
                {gap.gap}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
