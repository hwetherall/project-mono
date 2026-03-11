import { useState, useEffect } from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function OutputViewer({ run, onNewRun }) {
  const [activeTab, setActiveTab] = useState('markdown');
  const [markdownContent, setMarkdownContent] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!run.runId) return;
    setLoading(true);
    fetch(`/api/research/${run.runId}/output/markdown`)
      .then((res) => {
        if (!res.ok) throw new Error('Not available');
        return res.text();
      })
      .then(setMarkdownContent)
      .catch(() => setMarkdownContent('*Report not yet available.*'))
      .finally(() => setLoading(false));
  }, [run.runId]);

  const handleDownload = async (type) => {
    const url = `/api/research/${run.runId}/output/${type}`;
    const res = await fetch(url);
    if (!res.ok) return;
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = type === 'yaml' ? 'evidence.yaml' : 'evidence.md';
    a.click();
    URL.revokeObjectURL(a.href);
  };

  // Build summary data
  const categories = Object.values(run.categories);
  const succeeded = categories.filter((c) => c.status === 'success').length;
  const failed = categories.filter((c) => c.status === 'failed').length;
  const totalSources = categories.reduce((sum, c) => sum + (c.source_count || 0), 0);
  const totalTime = run.result?.elapsed_seconds
    ? `${Math.floor(run.result.elapsed_seconds / 60)}m ${Math.floor(run.result.elapsed_seconds % 60)}s`
    : '-';
  const gapCategories = categories.filter((c) => (c.gap_count || 0) > 0);

  const tabs = [
    { id: 'markdown', label: 'Markdown Report' },
    { id: 'summary', label: 'Summary Dashboard' },
    { id: 'raw', label: 'Raw Reports' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-slate-900">Research Results</h2>
        <div className="flex gap-2">
          <button
            onClick={() => handleDownload('markdown')}
            className="px-4 py-2 text-sm border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
          >
            Download Markdown
          </button>
          <button
            onClick={() => handleDownload('yaml')}
            className="px-4 py-2 text-sm border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
          >
            Download YAML
          </button>
          <button
            onClick={onNewRun}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            New Run
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Markdown Tab */}
      {activeTab === 'markdown' && (
        <div className="bg-white border border-slate-200 rounded-lg p-6 prose prose-slate max-w-none overflow-auto">
          {loading ? (
            <p className="text-slate-400">Loading report...</p>
          ) : (
            <Markdown remarkPlugins={[remarkGfm]}>{markdownContent}</Markdown>
          )}
        </div>
      )}

      {/* Summary Tab */}
      {activeTab === 'summary' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <SummaryCard label="Succeeded" value={succeeded} color="text-green-600" />
            <SummaryCard label="Failed" value={failed} color="text-red-600" />
            <SummaryCard label="Total Sources" value={totalSources} color="text-blue-600" />
            <SummaryCard label="Total Time" value={totalTime} color="text-slate-700" />
          </div>

          {gapCategories.length > 0 && (
            <div className="bg-white border border-slate-200 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-slate-700 mb-3">Gap Inventory</h3>
              <div className="space-y-2">
                {gapCategories.map((cat) => (
                  <div key={cat.category_id} className="flex items-center gap-2 text-sm">
                    <span className="font-mono text-slate-400">{cat.category_id}</span>
                    <span className="text-slate-700">{cat.category_name}</span>
                    <span className="text-amber-600 font-medium">{cat.gap_count} gaps</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Category breakdown */}
          <div className="bg-white border border-slate-200 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-slate-700 mb-3">Category Breakdown</h3>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-slate-100">
                  <th className="pb-2">Category</th>
                  <th className="pb-2">Status</th>
                  <th className="pb-2">Sources</th>
                  <th className="pb-2">Gaps</th>
                  <th className="pb-2">Time</th>
                </tr>
              </thead>
              <tbody>
                {categories.map((cat) => (
                  <tr key={cat.category_id} className="border-b border-slate-50">
                    <td className="py-2">
                      <span className="font-mono text-slate-400 mr-2">{cat.category_id}</span>
                      {cat.category_name}
                    </td>
                    <td className={`py-2 ${cat.status === 'success' ? 'text-green-600' : cat.status === 'failed' ? 'text-red-600' : 'text-slate-400'}`}>
                      {cat.status}
                    </td>
                    <td className="py-2">{cat.source_count || 0}</td>
                    <td className={`py-2 ${(cat.gap_count || 0) > 0 ? 'text-amber-600' : ''}`}>
                      {cat.gap_count || 0}
                    </td>
                    <td className="py-2">
                      {cat.elapsed_seconds ? `${Math.floor(cat.elapsed_seconds / 60)}m ${Math.floor(cat.elapsed_seconds % 60)}s` : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Raw Reports Tab */}
      {activeTab === 'raw' && (
        <div className="space-y-2">
          {categories
            .filter((c) => c.status === 'success')
            .map((cat) => (
              <RawReportAccordion key={cat.category_id} runId={run.runId} category={cat} />
            ))}
          {categories.filter((c) => c.status === 'success').length === 0 && (
            <p className="text-slate-400 text-sm">No successful category reports available.</p>
          )}
        </div>
      )}
    </div>
  );
}

function SummaryCard({ label, value, color }) {
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4">
      <p className="text-xs text-slate-400 uppercase">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
    </div>
  );
}

function RawReportAccordion({ runId, category }) {
  const [open, setOpen] = useState(false);
  const [content, setContent] = useState(null);

  const load = () => {
    if (content !== null) {
      setOpen(!open);
      return;
    }
    fetch(`/api/research/${runId}/output/raw/${category.category_id}`)
      .then((res) => (res.ok ? res.text() : 'Report not available.'))
      .then((text) => {
        setContent(text);
        setOpen(true);
      });
  };

  return (
    <div className="bg-white border border-slate-200 rounded-lg">
      <button
        onClick={load}
        className="w-full px-4 py-3 flex items-center justify-between text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        <span>
          <span className="font-mono text-slate-400 mr-2">{category.category_id}</span>
          {category.category_name}
        </span>
        <span className="text-slate-400">{open ? '\u25B2' : '\u25BC'}</span>
      </button>
      {open && content && (
        <div className="px-4 pb-4 border-t border-slate-100 prose prose-sm prose-slate max-w-none overflow-auto">
          <Markdown remarkPlugins={[remarkGfm]}>{content}</Markdown>
        </div>
      )}
    </div>
  );
}
