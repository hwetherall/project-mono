import { useState, useEffect } from 'react';

const CATEGORY_NAMES = {
  'EC-01': 'Market Sizing & Growth',
  'EC-02': 'Competitor Landscape & Positioning',
  'EC-03': 'Investment & Financial Signals',
  'EC-04': 'Alternative Solution Failures & Reviews',
  'EC-05': 'Problem Prevalence & Cost Data',
  'EC-06': 'Regulatory & Compliance Environment',
  'EC-07': 'Enabling Technology Trends',
  'EC-08': 'Urgency Drivers & Forcing Functions',
  'EC-09': 'Industry Analyst & Expert Coverage',
  'EC-10': 'Voice of Market',
  'EC-11': 'Search & Hiring Trends',
  'EC-12': 'Budget & Procurement Context',
  'EC-13': 'Proxy Market Trajectories',
  'MR-01a': 'Market Definition & Boundaries',
  'MR-01b': 'Market Sizing & Methodology',
  'MR-02': 'SAM / SOM / Reachability',
  'MR-03': 'Segments & Concentration',
  'MR-04': 'Trends & Growth Quality',
  'MR-05': 'Value Chain & Whitespace',
  'MR-06a': 'Competitor Identification',
  'MR-06b': 'Competitive Intelligence',
  'MR-07': 'Buying Process, Budget & Pricing',
  'MR-08': 'Adoption & Expansion Dynamics',
  'MR-09': 'Regulation & Platform Shifts',
  'MR-10': 'Barriers, Saturation & Ecosystem Power',
};

const STATUS_CONFIG = {
  pending:  { icon: '\u23F3', bg: 'bg-slate-50 dark:bg-slate-800', border: 'border-slate-200 dark:border-slate-700' },
  running:  { icon: '',       bg: 'bg-blue-50 dark:bg-blue-900/20', border: 'border-blue-200 dark:border-blue-800' },
  success:  { icon: '\u2705', bg: 'bg-green-50 dark:bg-green-900/20', border: 'border-green-200 dark:border-green-800' },
  failed:   { icon: '\u274C', bg: 'bg-red-50 dark:bg-red-900/20', border: 'border-red-200 dark:border-red-800' },
  skipped:  { icon: '\u23ED', bg: 'bg-slate-50 dark:bg-slate-800', border: 'border-slate-200 dark:border-slate-700' },
};

function formatTime(seconds) {
  if (!seconds || seconds < 1) return '';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

export default function CategoryCard({ categoryId, category, onRetry, onResume }) {
  const [showError, setShowError] = useState(false);
  const [elapsed, setElapsed] = useState(0);

  const status = category?.status || 'pending';
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.pending;
  const name = category?.category_name || CATEGORY_NAMES[categoryId] || categoryId;

  useEffect(() => {
    if (status !== 'running' || !category?.startedAt) {
      if (category?.elapsed_seconds) setElapsed(category.elapsed_seconds);
      return;
    }
    const interval = setInterval(() => {
      setElapsed((Date.now() - category.startedAt) / 1000);
    }, 1000);
    return () => clearInterval(interval);
  }, [status, category?.startedAt, category?.elapsed_seconds]);

  return (
    <div className={`p-3 rounded-lg border ${config.border} ${config.bg} transition-all`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 min-w-0">
          {status === 'running' ? (
            <span className="inline-block w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          ) : (
            <span className="text-sm">{config.icon}</span>
          )}
          <span className="text-xs font-mono text-slate-400 dark:text-slate-500">{categoryId}</span>
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300 truncate">{name}</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400 shrink-0">
          {elapsed > 0 && <span>{formatTime(elapsed)}</span>}
          {status === 'success' && category?.source_count > 0 && (
            <span>{category.source_count} sources</span>
          )}
          {category?.gap_count > 0 && (
            <span className="text-amber-600 dark:text-amber-400">{category.gap_count} gaps</span>
          )}
        </div>
      </div>

      {category?.rateLimitInfo && status === 'running' && (
        <div className="mt-2 text-xs text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/30 px-2 py-1 rounded">
          Waiting {category.rateLimitInfo.wait_seconds}s (attempt {category.rateLimitInfo.attempt}/{category.rateLimitInfo.max_attempts})
        </div>
      )}

      {status === 'failed' && category?.error && (
        <div className="mt-2">
          <button
            onClick={() => setShowError(!showError)}
            className="text-xs text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
          >
            {showError ? 'Hide error' : 'Show error'}
          </button>
          {showError && (
            <pre className="mt-1 text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/30 p-2 rounded overflow-auto max-h-24">
              {category.error}
            </pre>
          )}
          {category.can_resume && category.checkpoint_stage && (
            <div className="mt-1 text-xs text-blue-600 dark:text-blue-400">
              Progress saved at: {category.checkpoint_stage}
            </div>
          )}
          <div className="flex gap-2 mt-1">
            {category.can_resume && onResume && (
              <button
                onClick={() => onResume(categoryId)}
                className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-900/70 transition-colors"
              >
                Continue
              </button>
            )}
            {onRetry && (
              <button
                onClick={() => onRetry(categoryId)}
                className="text-xs px-2 py-1 bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 rounded hover:bg-red-200 dark:hover:bg-red-900/70 transition-colors"
              >
                Retry
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
