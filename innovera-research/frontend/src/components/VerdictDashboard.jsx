import { useMemo } from 'react';

function getConfidenceLevel(sourceCount, gapCount) {
  if (sourceCount >= 10 && gapCount === 0) return 'high';
  if (sourceCount >= 5 && gapCount <= 1) return 'moderate';
  return 'low';
}

const CONFIDENCE_COLORS = {
  high: 'bg-green-500',
  moderate: 'bg-amber-500',
  low: 'bg-red-500',
};

const CONFIDENCE_BG = {
  high: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
  moderate: 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800',
  low: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
};

export default function VerdictDashboard({ structuredData, categories, result, request }) {
  const cats = Object.values(categories || {});
  const succeeded = cats.filter((c) => c.status === 'success').length;
  const failed = cats.filter((c) => c.status === 'failed').length;
  const totalSources = cats.reduce((sum, c) => sum + (c.source_count || 0), 0);
  const totalGaps = cats.reduce((sum, c) => sum + (c.gap_count || 0), 0);
  const criticalGaps = structuredData?.gap_inventory?.critical?.length || 0;
  const moderateGaps = structuredData?.gap_inventory?.moderate?.length || 0;

  const totalTime = result?.elapsed_seconds
    ? `${Math.floor(result.elapsed_seconds / 60)} min`
    : '';

  const coreQuestion = request?.core_question || structuredData?.request?.core_question || '';
  const successCriteria = request?.success_criteria || structuredData?.request?.success_criteria || [];

  // Build category confidence grid
  const categoryGrid = useMemo(() => {
    if (!structuredData?.categories) return [];
    return structuredData.categories.map((cat) => {
      const confidence = cat.status === 'success'
        ? getConfidenceLevel(cat.source_count, cat.gap_count)
        : 'low';
      return { ...cat, confidence };
    });
  }, [structuredData]);

  return (
    <div className="space-y-6">
      {/* Verdict Header */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl p-6">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-3">Research Verdict</h2>

        {coreQuestion && (
          <p className="text-slate-600 dark:text-slate-400 italic mb-4 text-sm leading-relaxed">
            "{coreQuestion}"
          </p>
        )}

        {/* Summary Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 mb-4">
          <StatBox label="Evidence" value={`${totalSources} sources`} sub={`${succeeded + failed} categories`} />
          <StatBox label="Succeeded" value={succeeded} color="text-green-600 dark:text-green-400" />
          <StatBox label="Failed" value={failed} color="text-red-600 dark:text-red-400" />
          <StatBox label="Critical Gaps" value={criticalGaps} color={criticalGaps > 0 ? 'text-red-600 dark:text-red-400' : 'text-slate-600 dark:text-slate-400'} />
          <StatBox label="Duration" value={totalTime || '-'} />
        </div>

        {/* Success Criteria */}
        {successCriteria.length > 0 && (
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Success Criteria</h3>
            <div className="space-y-1.5">
              {successCriteria.map((criterion, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <span className="shrink-0 text-slate-400">-</span>
                  <span className="text-slate-700 dark:text-slate-300">{criterion}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Category Confidence Grid */}
      {categoryGrid.length > 0 && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Category Confidence</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
            {categoryGrid.map((cat) => (
              <a
                key={cat.category_id}
                href={`#section-${cat.category_id}`}
                className={`p-3 rounded-lg border transition-colors cursor-pointer ${CONFIDENCE_BG[cat.confidence]} hover:opacity-80`}
              >
                <div className="flex items-center gap-1.5 mb-1">
                  <span className="text-xs font-mono text-slate-500 dark:text-slate-400">{cat.category_id}</span>
                  {cat.status === 'success' ? (
                    <span className="text-green-600 dark:text-green-400 text-xs">OK</span>
                  ) : (
                    <span className="text-red-600 dark:text-red-400 text-xs">FAIL</span>
                  )}
                </div>
                <div className="text-xs text-slate-700 dark:text-slate-300 truncate font-medium">{cat.category_name}</div>
                <div className="mt-1.5 flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${CONFIDENCE_COLORS[cat.confidence]}`}
                      style={{ width: cat.confidence === 'high' ? '100%' : cat.confidence === 'moderate' ? '60%' : '25%' }}
                    />
                  </div>
                  <span className="text-xs text-slate-500 dark:text-slate-400">{cat.source_count}src</span>
                </div>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StatBox({ label, value, sub, color = 'text-slate-900 dark:text-slate-100' }) {
  return (
    <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-3">
      <p className="text-xs text-slate-400 dark:text-slate-500 uppercase tracking-wide">{label}</p>
      <p className={`text-xl font-bold ${color}`}>{value}</p>
      {sub && <p className="text-xs text-slate-400 dark:text-slate-500">{sub}</p>}
    </div>
  );
}
