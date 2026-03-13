import { useState, useEffect } from 'react';
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

const STEP_COLORS = {
  pending: 'bg-slate-200 dark:bg-slate-700 text-slate-500 dark:text-slate-400',
  running: 'bg-blue-500 text-white',
  completed: 'bg-green-500 text-white',
  failed: 'bg-red-500 text-white',
};

const CONNECTOR_COLORS = {
  completed: 'bg-green-400',
  failed: 'bg-red-400',
  default: 'bg-slate-300 dark:bg-slate-600',
};

function formatElapsed(ms) {
  const totalSecs = Math.floor(ms / 1000);
  const h = Math.floor(totalSecs / 3600);
  const m = Math.floor((totalSecs % 3600) / 60);
  const s = totalSecs % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  return `${m}:${String(s).padStart(2, '0')}`;
}

export default function ChainProgressPanel({ chain, onComplete }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (chain.status === 'complete' || chain.status === 'error') {
      const t = setTimeout(() => onComplete(), 2000);
      return () => clearTimeout(t);
    }
  }, [chain.status, onComplete]);

  useEffect(() => {
    if (!chain.startTime) return;
    const interval = setInterval(() => {
      setElapsed(Date.now() - chain.startTime);
    }, 1000);
    return () => clearInterval(interval);
  }, [chain.startTime]);

  const currentStep = chain.steps[chain.currentStepIndex];
  const currentMode = currentStep?.mode;
  const isTableStep = currentMode === 'competitive_table';
  const PHASE_CATEGORIES = PHASE_CATEGORIES_BY_MODE[currentMode] || {};
  const PHASE_LABELS = PHASE_LABELS_BY_MODE[currentMode] || {};

  const activePhases = chain.phases.map((p) => p.name);
  const phasesToShow = Object.keys(PHASE_CATEGORIES).filter(
    (p) => activePhases.includes(p) || (PHASE_CATEGORIES[p] || []).some((cid) => chain.categories[cid])
  );

  const completedSteps = chain.steps.filter((s) => s.status === 'completed').length;
  const failedSteps = chain.steps.filter((s) => s.status === 'failed').length;

  const overallStatus =
    chain.status === 'complete'
      ? `All chapters complete${failedSteps > 0 ? ` (${failedSteps} failed)` : ''}`
      : chain.status === 'error'
        ? 'Chain failed'
        : chain.status === 'starting'
          ? 'Starting chain...'
          : currentStep
            ? `Running: ${currentStep.mode_label}`
            : 'Initializing...';

  const statusColor =
    chain.status === 'complete'
      ? 'bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300'
      : chain.status === 'error'
        ? 'bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300'
        : 'bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300';

  return (
    <div className="space-y-6">
      {/* Top status bar */}
      <div className="flex items-center justify-between bg-white dark:bg-slate-900 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColor}`}>
            {overallStatus}
          </span>
          {chain.status === 'running' && (
            <span className="inline-block w-4 h-4 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin" />
          )}
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs text-slate-400 dark:text-slate-500">
            {completedSteps}/{chain.steps.length} chapters
          </span>
          <span className="text-sm text-slate-500 dark:text-slate-400 font-mono">
            {formatElapsed(elapsed)}
          </span>
        </div>
      </div>

      {/* Step tracker */}
      <div className="bg-white dark:bg-slate-900 p-5 rounded-lg border border-slate-200 dark:border-slate-700">
        <div className="flex items-center justify-center gap-0">
          {chain.steps.map((step, i) => (
            <div key={step.mode} className="flex items-center">
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all ${STEP_COLORS[step.status]}
                    ${step.status === 'running' ? 'ring-4 ring-blue-200 dark:ring-blue-800' : ''}`}
                >
                  {step.status === 'completed' ? (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : step.status === 'failed' ? (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  ) : (
                    i + 1
                  )}
                </div>
                <span className={`mt-2 text-xs font-medium ${
                  step.status === 'running'
                    ? 'text-blue-600 dark:text-blue-400'
                    : step.status === 'completed'
                      ? 'text-green-600 dark:text-green-400'
                      : step.status === 'failed'
                        ? 'text-red-600 dark:text-red-400'
                        : 'text-slate-400 dark:text-slate-500'
                }`}>
                  {step.mode_label}
                </span>
              </div>
              {i < chain.steps.length - 1 && (
                <div className={`w-16 md:w-24 h-1 mx-2 mb-6 rounded-full transition-colors ${
                  step.status === 'completed'
                    ? CONNECTOR_COLORS.completed
                    : step.status === 'failed'
                      ? CONNECTOR_COLORS.failed
                      : CONNECTOR_COLORS.default
                }`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Context info */}
      {chain.contextInfo && (
        <div className="bg-white dark:bg-slate-900 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
          <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Context Extracted (shared)</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div>
              <span className="text-slate-400 dark:text-slate-500">Venture:</span>{' '}
              <span className="font-medium text-slate-700 dark:text-slate-300">{chain.contextInfo.venture_name}</span>
            </div>
            <div>
              <span className="text-slate-400 dark:text-slate-500">Industry:</span>{' '}
              <span className="font-medium text-slate-700 dark:text-slate-300">{chain.contextInfo.industry}</span>
            </div>
            <div>
              <span className="text-slate-400 dark:text-slate-500">Competitors:</span>{' '}
              <span className="font-medium text-slate-700 dark:text-slate-300">{chain.contextInfo.competitor_count}</span>
            </div>
            <div>
              <span className="text-slate-400 dark:text-slate-500">Keywords:</span>{' '}
              <span className="font-medium text-slate-700 dark:text-slate-300">{chain.contextInfo.keyword_count}</span>
            </div>
          </div>
        </div>
      )}

      {/* Error display */}
      {chain.error && (
        <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-sm text-red-700 dark:text-red-300 font-medium">Error</p>
          <p className="text-sm text-red-600 dark:text-red-400 mt-1">{chain.error}</p>
        </div>
      )}

      {/* Competitive Table Progress (for CT step) */}
      {chain.competitiveTableStatus && isTableStep && (
        <div className="bg-white dark:bg-slate-900 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">Competitive Table</h3>
            {chain.competitiveTableStatus.status === 'building' && (
              <span className="inline-block w-3 h-3 border-2 border-purple-600 border-t-transparent rounded-full animate-spin" />
            )}
            {chain.competitiveTableStatus.status === 'complete' && (
              <span className="text-xs text-green-600 dark:text-green-400 font-medium">Complete</span>
            )}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400">
            {chain.competitiveTableStatus.step === 'schema_generation' && 'Generating competitive framework...'}
            {chain.competitiveTableStatus.step === 'competitor_discovery' && (
              chain.competitiveTableStatus.found
                ? `Found ${chain.competitiveTableStatus.found} competitors`
                : 'Discovering competitors...'
            )}
            {chain.competitiveTableStatus.step === 'population' && (
              `Populating data: ${chain.competitiveTableStatus.completed || 0}/${chain.competitiveTableStatus.total || '?'} competitors`
            )}
            {chain.competitiveTableStatus.step === 'done' && (
              `${chain.competitiveTableStatus.competitors} competitors, ${chain.competitiveTableStatus.attributes} attributes, ${chain.competitiveTableStatus.coverage?.toFixed(0)}% coverage`
            )}
          </div>
        </div>
      )}

      {/* Category Grid (for MR/DV steps) */}
      {!isTableStep && Object.keys(chain.categories).length > 0 && (
        <div className="space-y-4">
          {Object.entries(PHASE_CATEGORIES).map(([phaseName, categoryIds]) => {
            const phaseInfo = chain.phases.find((p) => p.name === phaseName);
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
                      category={chain.categories[cid]}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

    </div>
  );
}
