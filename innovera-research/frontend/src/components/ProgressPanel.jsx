import { useState, useEffect, useMemo } from 'react';
import CategoryCard from './CategoryCard';

const PHASE_CATEGORIES_BY_MODE = {
  demand_validation: {
    FOUNDATION: ['EC-01', 'EC-02', 'EC-05', 'EC-06', 'EC-10'],
    COMPETITOR_DEPENDENT: ['EC-03', 'EC-04', 'EC-11'],
    SYNTHESIS: ['EC-07', 'EC-08', 'EC-09', 'EC-12', 'EC-13'],
  },
  market_research: {
    FOUNDATION: ['MR-01a', 'MR-01b', 'MR-04', 'MR-06a', 'MR-06b', 'MR-09'],
    STRUCTURAL: ['MR-02', 'MR-03', 'MR-05'],
    COMMERCIAL: ['MR-07', 'MR-08', 'MR-10'],
  },
};

const PHASE_LABELS_BY_MODE = {
  demand_validation: {
    FOUNDATION: 'Phase 1: Foundation',
    COMPETITOR_DEPENDENT: 'Phase 2: Competitor-Dependent',
    SYNTHESIS: 'Phase 3: Synthesis',
  },
  market_research: {
    FOUNDATION: 'Phase 1: Foundation',
    STRUCTURAL: 'Phase 2: Structural',
    COMMERCIAL: 'Phase 3: Commercial',
  },
};

function formatElapsed(ms) {
  const totalSecs = Math.floor(ms / 1000);
  const m = Math.floor(totalSecs / 60);
  const s = totalSecs % 60;
  return `${m}:${String(s).padStart(2, '0')}`;
}

export default function ProgressPanel({ run, onComplete }) {
  const [elapsed, setElapsed] = useState(0);

  // Detect completion
  useEffect(() => {
    if (run.status === 'complete' || run.status === 'error') {
      const t = setTimeout(() => onComplete(), 1500);
      return () => clearTimeout(t);
    }
  }, [run.status, onComplete]);

  // Elapsed timer
  useEffect(() => {
    if (!run.startTime) return;
    const interval = setInterval(() => {
      setElapsed(Date.now() - run.startTime);
    }, 1000);
    return () => clearInterval(interval);
  }, [run.startTime]);

  // Detect research mode from category IDs present in run
  const detectedMode = useMemo(() => {
    const catIds = Object.keys(run.categories);
    if (catIds.length === 0 && run.competitiveTableStatus) return 'competitive_table';
    if (catIds.some((id) => id.startsWith('MR-'))) return 'market_research';
    return 'demand_validation';
  }, [run.categories, run.competitiveTableStatus]);

  const isTableOnly = detectedMode === 'competitive_table';
  const PHASE_CATEGORIES = PHASE_CATEGORIES_BY_MODE[detectedMode] || {};
  const PHASE_LABELS = PHASE_LABELS_BY_MODE[detectedMode] || {};

  const activePhases = run.phases.map((p) => p.name);
  const currentPhase = run.phases.find((p) => p.status === 'running')?.name || '';

  const phasesToShow = Object.keys(PHASE_CATEGORIES).filter(
    (p) => activePhases.includes(p) || PHASE_CATEGORIES[p].some((cid) => run.categories[cid])
  );

  const statusLabel =
    run.status === 'complete'
      ? 'Complete'
      : run.status === 'error'
        ? 'Failed'
        : isTableOnly
          ? 'Building Competitive Table'
          : currentPhase
            ? `Running - ${PHASE_LABELS[currentPhase] || currentPhase}`
            : 'Starting...';

  const statusColor =
    run.status === 'complete'
      ? 'bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300'
      : run.status === 'error'
        ? 'bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300'
        : 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300';

  return (
    <div className="space-y-6">
      {/* Top status bar */}
      <div className="flex items-center justify-between bg-white dark:bg-slate-900 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColor}`}>
            {statusLabel}
          </span>
          {run.status === 'running' && (
            <span className="inline-block w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          )}
        </div>
        <div className="text-sm text-slate-500 dark:text-slate-400 font-mono">
          {formatElapsed(elapsed)}
        </div>
      </div>

      {/* Context info */}
      {run.contextInfo && (
        <div className="bg-white dark:bg-slate-900 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
          <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Context Extracted</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div>
              <span className="text-slate-400 dark:text-slate-500">Venture:</span>{' '}
              <span className="font-medium text-slate-700 dark:text-slate-300">{run.contextInfo.venture_name}</span>
            </div>
            <div>
              <span className="text-slate-400 dark:text-slate-500">Industry:</span>{' '}
              <span className="font-medium text-slate-700 dark:text-slate-300">{run.contextInfo.industry}</span>
            </div>
            <div>
              <span className="text-slate-400 dark:text-slate-500">Competitors:</span>{' '}
              <span className="font-medium text-slate-700 dark:text-slate-300">{run.contextInfo.competitor_count}</span>
            </div>
            <div>
              <span className="text-slate-400 dark:text-slate-500">Keywords:</span>{' '}
              <span className="font-medium text-slate-700 dark:text-slate-300">{run.contextInfo.keyword_count}</span>
            </div>
          </div>
        </div>
      )}

      {/* Error display */}
      {run.error && (
        <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-sm text-red-700 dark:text-red-300 font-medium">Error</p>
          <p className="text-sm text-red-600 dark:text-red-400 mt-1">{run.error}</p>
        </div>
      )}

      {/* Competitive Table Progress */}
      {run.competitiveTableStatus && (
        <div className="bg-white dark:bg-slate-900 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">Competitive Table</h3>
            {run.competitiveTableStatus.status === 'building' && (
              <span className="inline-block w-3 h-3 border-2 border-purple-600 border-t-transparent rounded-full animate-spin" />
            )}
            {run.competitiveTableStatus.status === 'complete' && (
              <span className="text-xs text-green-600 dark:text-green-400 font-medium">Complete</span>
            )}
            {run.competitiveTableStatus.status === 'failed' && (
              <span className="text-xs text-amber-600 dark:text-amber-400 font-medium">Failed (non-blocking)</span>
            )}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400">
            {run.competitiveTableStatus.step === 'schema_generation' && 'Generating competitive framework...'}
            {run.competitiveTableStatus.step === 'competitor_discovery' && (
              run.competitiveTableStatus.found
                ? `Found ${run.competitiveTableStatus.found} competitors`
                : 'Discovering competitors...'
            )}
            {run.competitiveTableStatus.step === 'population' && (
              `Populating data: ${run.competitiveTableStatus.completed || 0}/${run.competitiveTableStatus.total || '?'} competitors`
            )}
            {run.competitiveTableStatus.step === 'done' && (
              `${run.competitiveTableStatus.competitors} competitors, ${run.competitiveTableStatus.attributes} attributes, ${run.competitiveTableStatus.coverage?.toFixed(0)}% coverage`
            )}
          </div>
        </div>
      )}

      {/* Category Grid (hidden in table-only mode) */}
      {!isTableOnly && <div className="space-y-4">
        {Object.entries(PHASE_CATEGORIES).map(([phaseName, categoryIds]) => {
          const phaseInfo = run.phases.find((p) => p.name === phaseName);
          const isActive = phasesToShow.includes(phaseName);
          if (!isActive && !phaseInfo) return null;

          return (
            <div key={phaseName}>
              <div className="flex items-center gap-2 mb-2">
                <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                  {PHASE_LABELS[phaseName] || phaseName}
                </h3>
                {phaseInfo?.status === 'complete' && (
                  <span className="text-xs text-green-600 dark:text-green-400 font-medium">Complete</span>
                )}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                {categoryIds.map((cid) => (
                  <CategoryCard
                    key={cid}
                    categoryId={cid}
                    category={run.categories[cid]}
                    onRetry={run.retryCategory}
                    onResume={run.resumeCategory}
                  />
                ))}
              </div>

              {phaseName === 'FOUNDATION' && run.competitorList.length > 0 && (
                <div className="mt-2 p-3 bg-purple-50 dark:bg-purple-900/30 border border-purple-200 dark:border-purple-800 rounded-lg text-sm">
                  <span className="font-medium text-purple-700 dark:text-purple-300">
                    Extracted {run.competitorList.length} competitors:
                  </span>{' '}
                  <span className="text-purple-600 dark:text-purple-400">{run.competitorList.join(', ')}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>}
    </div>
  );
}
