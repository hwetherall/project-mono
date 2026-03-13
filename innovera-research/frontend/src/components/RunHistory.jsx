import { useState, useEffect } from 'react';

function formatDate(isoStr) {
  if (!isoStr) return '';
  const d = new Date(isoStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatDuration(seconds) {
  if (!seconds) return '';
  const m = Math.floor(seconds / 60);
  if (m < 1) return `${Math.floor(seconds)}s`;
  return `${m} min`;
}

export default function RunHistory({ onViewRun, onViewChain, onNewRun }) {
  const [runs, setRuns] = useState([]);
  const [chains, setChains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const fetchRuns = () => {
    setLoading(true);
    fetch('/api/runs')
      .then((res) => res.json())
      .then((data) => {
        setRuns(data.runs || []);
        setChains(data.chains || []);
      })
      .catch(() => { setRuns([]); setChains([]); })
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchRuns(); }, []);

  const handleDelete = async (runId) => {
    try {
      const res = await fetch(`/api/research/${runId}`, { method: 'DELETE' });
      if (res.ok) {
        setRuns((prev) => prev.filter((r) => r.run_id !== runId));
      }
    } catch {}
    setDeleteConfirm(null);
  };

  const statusBadge = (run) => {
    const s = run.status;
    if (s === 'completed') return <span className="px-2 py-0.5 text-xs rounded-full bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300 font-medium">Complete</span>;
    if (s === 'failed') return <span className="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 font-medium">Failed</span>;
    if (s === 'running') return <span className="px-2 py-0.5 text-xs rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 font-medium">Running</span>;
    return <span className="px-2 py-0.5 text-xs rounded-full bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300 font-medium">Partial</span>;
  };

  if (loading) {
    return (
      <div className="text-center py-12 text-slate-400 dark:text-slate-500">Loading history...</div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Run History</h2>
        <button
          onClick={onNewRun}
          className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          New Run
        </button>
      </div>

      {runs.length === 0 && chains.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-slate-400 dark:text-slate-500 mb-4">No research runs yet.</p>
          <button
            onClick={onNewRun}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            Start Your First Run
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {/* Chain runs */}
          {chains.map((chain) => (
            <div
              key={chain.chain_id}
              className="bg-white dark:bg-slate-900 border-2 border-emerald-200 dark:border-emerald-800 rounded-lg p-4 hover:border-emerald-400 dark:hover:border-emerald-600 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-slate-900 dark:text-slate-100 truncate">
                      {chain.venture_name || 'Chain Run'}
                    </h3>
                    {statusBadge(chain)}
                    <span className="px-2 py-0.5 text-xs rounded-full bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300 font-medium">
                      All Chapters
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-slate-500 dark:text-slate-400">
                    <span>{formatDate(chain.started_at)}</span>
                    {chain.total_elapsed_seconds && (
                      <span>{formatDuration(chain.total_elapsed_seconds)}</span>
                    )}
                  </div>
                  <div className="flex gap-2 mt-2">
                    {(chain.steps || []).map((step) => (
                      <span key={step.mode} className={`px-2 py-0.5 text-xs rounded-full font-medium ${
                        step.status === 'completed'
                          ? 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300'
                          : step.status === 'failed'
                            ? 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300'
                            : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400'
                      }`}>
                        {step.mode_label}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => onViewChain && onViewChain(chain.chain_id, chain.steps)}
                    className="px-4 py-1.5 text-sm bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                  >
                    View All
                  </button>
                </div>
              </div>
            </div>
          ))}

          {/* Individual runs */}
          {runs.map((run) => (
            <div
              key={run.run_id}
              className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-600 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-slate-900 dark:text-slate-100 truncate">
                      {run.venture_name || 'Untitled Run'}
                    </h3>
                    {statusBadge(run)}
                    {(run.research_mode || run.request?.research_mode) === 'market_research' && (
                      <span className="px-2 py-0.5 text-xs rounded-full bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300 font-medium">MR</span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-sm text-slate-500 dark:text-slate-400">
                    <span>{formatDate(run.started_at)}</span>
                    {run.categories_succeeded != null && (
                      <span>{run.categories_succeeded}/{(run.categories_succeeded || 0) + (run.categories_failed || 0)} categories</span>
                    )}
                    {run.duration_seconds && (
                      <span>{formatDuration(run.duration_seconds)}</span>
                    )}
                    {run.total_sources != null && (
                      <span>{run.total_sources} sources</span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {deleteConfirm === run.run_id ? (
                    <>
                      <button
                        onClick={() => handleDelete(run.run_id)}
                        className="px-3 py-1.5 text-xs bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                      >
                        Confirm Delete
                      </button>
                      <button
                        onClick={() => setDeleteConfirm(null)}
                        className="px-3 py-1.5 text-xs text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={() => setDeleteConfirm(run.run_id)}
                        className="px-3 py-1.5 text-xs text-slate-400 dark:text-slate-500 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                      >
                        Delete
                      </button>
                      <button
                        onClick={() => onViewRun(run.run_id)}
                        className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        View
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
