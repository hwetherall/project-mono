import { useState, useEffect } from 'react';
import CategoryCard from './CategoryCard';

const PHASE_CATEGORIES = {
  FOUNDATION: ['EC-01', 'EC-02', 'EC-05', 'EC-06', 'EC-10'],
  COMPETITOR_DEPENDENT: ['EC-03', 'EC-04', 'EC-11'],
  SYNTHESIS: ['EC-07', 'EC-08', 'EC-09', 'EC-12', 'EC-13'],
};

const PHASE_LABELS = {
  FOUNDATION: 'Phase 1: Foundation',
  COMPETITOR_DEPENDENT: 'Phase 2: Competitor-Dependent',
  SYNTHESIS: 'Phase 3: Synthesis',
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
      // Small delay so final events render
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

  const activePhases = run.phases.map((p) => p.name);
  const currentPhase = run.phases.find((p) => p.status === 'running')?.name || '';

  // Determine which phases to show
  const phasesToShow = Object.keys(PHASE_CATEGORIES).filter(
    (p) => activePhases.includes(p) || PHASE_CATEGORIES[p].some((cid) => run.categories[cid])
  );

  const statusLabel =
    run.status === 'complete'
      ? 'Complete'
      : run.status === 'error'
        ? 'Failed'
        : currentPhase
          ? `Running - ${PHASE_LABELS[currentPhase] || currentPhase}`
          : 'Starting...';

  const statusColor =
    run.status === 'complete'
      ? 'bg-green-100 text-green-700'
      : run.status === 'error'
        ? 'bg-red-100 text-red-700'
        : 'bg-blue-100 text-blue-700';

  return (
    <div className="space-y-6">
      {/* Top status bar */}
      <div className="flex items-center justify-between bg-white p-4 rounded-lg border border-slate-200">
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColor}`}>
            {statusLabel}
          </span>
          {run.status === 'running' && (
            <span className="inline-block w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          )}
        </div>
        <div className="text-sm text-slate-500 font-mono">
          {formatElapsed(elapsed)}
        </div>
      </div>

      {/* Context info */}
      {run.contextInfo && (
        <div className="bg-white p-4 rounded-lg border border-slate-200">
          <h3 className="text-sm font-semibold text-slate-700 mb-2">Context Extracted</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div>
              <span className="text-slate-400">Venture:</span>{' '}
              <span className="font-medium">{run.contextInfo.venture_name}</span>
            </div>
            <div>
              <span className="text-slate-400">Industry:</span>{' '}
              <span className="font-medium">{run.contextInfo.industry}</span>
            </div>
            <div>
              <span className="text-slate-400">Competitors:</span>{' '}
              <span className="font-medium">{run.contextInfo.competitor_count}</span>
            </div>
            <div>
              <span className="text-slate-400">Keywords:</span>{' '}
              <span className="font-medium">{run.contextInfo.keyword_count}</span>
            </div>
          </div>
        </div>
      )}

      {/* Error display */}
      {run.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-700 font-medium">Error</p>
          <p className="text-sm text-red-600 mt-1">{run.error}</p>
        </div>
      )}

      {/* Phase sections */}
      {Object.entries(PHASE_CATEGORIES).map(([phaseName, categoryIds]) => {
        const phaseInfo = run.phases.find((p) => p.name === phaseName);
        const isActive = phasesToShow.includes(phaseName);
        if (!isActive && !phaseInfo) return null;

        return (
          <div key={phaseName}>
            <div className="flex items-center gap-2 mb-3">
              <h3 className="text-sm font-semibold text-slate-700">
                {PHASE_LABELS[phaseName] || phaseName}
              </h3>
              {phaseInfo?.status === 'complete' && (
                <span className="text-xs text-green-600 font-medium">Complete</span>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
              {categoryIds.map((cid) => (
                <CategoryCard
                  key={cid}
                  categoryId={cid}
                  category={run.categories[cid]}
                  onRetry={run.retryCategory}
                />
              ))}
            </div>

            {/* Competitor list between Phase 1 and 2 */}
            {phaseName === 'FOUNDATION' && run.competitorList.length > 0 && (
              <div className="mt-3 p-3 bg-purple-50 border border-purple-200 rounded-lg text-sm">
                <span className="font-medium text-purple-700">
                  Extracted {run.competitorList.length} competitors from EC-02:
                </span>{' '}
                <span className="text-purple-600">{run.competitorList.join(', ')}</span>
              </div>
            )}
          </div>
        );
      })}

      {/* Event log */}
      {run.events.length > 0 && (
        <details className="bg-white border border-slate-200 rounded-lg">
          <summary className="px-4 py-2 text-sm text-slate-500 cursor-pointer hover:bg-slate-50">
            Event Log ({run.events.length} events)
          </summary>
          <div className="px-4 pb-3 max-h-48 overflow-auto">
            {run.events.map((evt, i) => (
              <div key={i} className="text-xs text-slate-500 font-mono py-0.5 border-b border-slate-50">
                {evt.type}{evt.category_id ? ` [${evt.category_id}]` : ''}{evt.message ? `: ${evt.message}` : ''}
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
