import { useState, useMemo } from 'react';

const CONFIDENCE_COLORS = {
  high: 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-300',
  medium: 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300',
  low: 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-300',
  unknown: 'bg-slate-50 dark:bg-slate-800/50 text-slate-500 dark:text-slate-400',
};

const TIER_LABELS = { 0: 'Venture', 1: 'Tier 1', 2: 'Tier 2', 3: 'Tier 3' };

const TYPE_COLORS = {
  venture: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300',
  direct: 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300',
  substitute: 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300',
  adjacent: 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300',
  emerging: 'bg-cyan-100 dark:bg-cyan-900/40 text-cyan-700 dark:text-cyan-300',
  incumbent: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300',
};

function CellContent({ cell }) {
  if (!cell || cell.value == null) {
    return <span className="text-slate-300 dark:text-slate-600">—</span>;
  }

  const val = Array.isArray(cell.value) ? cell.value.join(', ') : String(cell.value);
  const truncated = val.length > 80 ? val.slice(0, 77) + '...' : val;
  const confColor = CONFIDENCE_COLORS[cell.confidence] || CONFIDENCE_COLORS.unknown;

  return (
    <div className="group relative">
      <span className={`text-xs ${confColor} rounded px-1 py-0.5`}>{truncated}</span>
      {(cell.notes || cell.source_url) && (
        <div className="absolute z-20 hidden group-hover:block bottom-full left-0 mb-1 w-64 p-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg text-xs">
          {cell.notes && <p className="text-slate-600 dark:text-slate-400 mb-1">{cell.notes}</p>}
          {cell.source_url && (
            <a href={cell.source_url} target="_blank" rel="noreferrer" className="text-blue-500 underline break-all">
              {cell.source_url}
            </a>
          )}
          <p className="text-slate-400 mt-1">Confidence: {cell.confidence}</p>
        </div>
      )}
    </div>
  );
}

export default function CompetitiveTable({ table }) {
  const [sortAttr, setSortAttr] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [filterTier, setFilterTier] = useState('all');
  const [filterGroup, setFilterGroup] = useState('all');

  const hasData = table && table.attributes?.length > 0 && table.competitors?.length > 0;

  const allEntries = useMemo(() => {
    if (!hasData) return [];
    let entries = [...table.competitors];

    if (filterType !== 'all') {
      entries = entries.filter((c) => c.competitor_type === filterType);
    }
    if (filterTier !== 'all') {
      entries = entries.filter((c) => c.tier === parseInt(filterTier));
    }
    if (sortAttr) {
      entries.sort((a, b) => {
        const aVal = a.attributes?.[sortAttr]?.value;
        const bVal = b.attributes?.[sortAttr]?.value;
        if (aVal == null && bVal == null) return 0;
        if (aVal == null) return 1;
        if (bVal == null) return -1;
        return String(aVal).localeCompare(String(bVal));
      });
    }
    if (table.venture_entry) {
      entries = [table.venture_entry, ...entries];
    }
    return entries;
  }, [hasData, table, sortAttr, filterType, filterTier]);

  const filteredAttributes = useMemo(() => {
    if (!hasData) return [];
    if (filterGroup === 'all') return table.attributes;
    return table.attributes.filter((a) => a.group === filterGroup);
  }, [hasData, table, filterGroup]);

  const groups = useMemo(() => {
    if (!hasData) return [];
    const set = new Set(table.attributes.map((a) => a.group));
    return Array.from(set);
  }, [hasData, table]);

  const competitorTypes = useMemo(() => {
    if (!hasData) return [];
    const set = new Set(table.competitors.map((c) => c.competitor_type));
    return Array.from(set);
  }, [hasData, table]);

  if (!hasData) return null;

  const md = table.metadata;

  return (
    <div id="section-competitive-table" className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="p-5 border-b border-slate-200 dark:border-slate-700">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-2">
          Competitive Landscape
        </h2>

        {md?.table_summary && (
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-3 whitespace-pre-line">
            {md.table_summary}
          </p>
        )}

        <div className="flex flex-wrap gap-4 text-xs text-slate-500 dark:text-slate-400 font-mono">
          <span>Competitors: <span className="font-bold text-slate-700 dark:text-slate-300">{md?.competitor_count || table.competitors.length}</span></span>
          <span>Attributes: <span className="font-bold text-slate-700 dark:text-slate-300">{md?.attribute_count || table.attributes.length}</span></span>
          <span>Coverage: <span className="font-bold text-slate-700 dark:text-slate-300">{md?.coverage_percent?.toFixed(0) || '—'}%</span></span>
          <span>Sources: <span className="font-bold text-slate-700 dark:text-slate-300">{md?.total_sources || '—'}</span></span>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 px-5 py-3 border-b border-slate-100 dark:border-slate-800 text-sm">
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-2 py-1 border border-slate-300 dark:border-slate-600 rounded bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs"
        >
          <option value="all">All Types</option>
          {competitorTypes.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>

        <select
          value={filterTier}
          onChange={(e) => setFilterTier(e.target.value)}
          className="px-2 py-1 border border-slate-300 dark:border-slate-600 rounded bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs"
        >
          <option value="all">All Tiers</option>
          <option value="1">Tier 1</option>
          <option value="2">Tier 2</option>
          <option value="3">Tier 3</option>
        </select>

        <select
          value={filterGroup}
          onChange={(e) => setFilterGroup(e.target.value)}
          className="px-2 py-1 border border-slate-300 dark:border-slate-600 rounded bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs"
        >
          <option value="all">All Attribute Groups</option>
          {groups.map((g) => (
            <option key={g} value={g}>{g}</option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="overflow-auto max-h-[600px]">
        <table className="w-full text-xs border-collapse">
          <thead className="sticky top-0 z-10 bg-slate-50 dark:bg-slate-800">
            <tr>
              <th className="sticky left-0 z-20 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-left font-semibold text-slate-700 dark:text-slate-300 border-b border-r border-slate-200 dark:border-slate-700 min-w-[160px]">
                Attribute
              </th>
              {allEntries.map((entry) => {
                const isVenture = entry.competitor_id === table.venture_entry?.competitor_id;
                return (
                  <th
                    key={entry.competitor_id}
                    className={`px-3 py-2 text-left font-semibold border-b border-slate-200 dark:border-slate-700 min-w-[140px] ${
                      isVenture
                        ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200'
                        : 'text-slate-700 dark:text-slate-300'
                    }`}
                  >
                    <div className="flex flex-col gap-0.5">
                      <span>{entry.name}</span>
                      <div className="flex gap-1">
                        <span className={`px-1 py-0.5 rounded text-[10px] ${TYPE_COLORS[entry.competitor_type] || TYPE_COLORS.direct}`}>
                          {entry.competitor_type}
                        </span>
                        <span className="px-1 py-0.5 rounded text-[10px] bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400">
                          {TIER_LABELS[entry.tier] || `Tier ${entry.tier}`}
                        </span>
                      </div>
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {filteredAttributes.map((attr, idx) => (
              <tr
                key={attr.attribute_id}
                className={idx % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-slate-50/50 dark:bg-slate-800/30'}
              >
                <td
                  className="sticky left-0 z-10 px-3 py-2 font-medium text-slate-700 dark:text-slate-300 border-r border-slate-100 dark:border-slate-800 bg-inherit cursor-pointer hover:text-blue-600"
                  onClick={() => setSortAttr(sortAttr === attr.attribute_id ? null : attr.attribute_id)}
                  title={`${attr.description}\nClick to sort`}
                >
                  {attr.name}
                  {sortAttr === attr.attribute_id && ' \u2191'}
                </td>
                {allEntries.map((entry) => {
                  const isVenture = entry.competitor_id === table.venture_entry?.competitor_id;
                  const cell = entry.attributes?.[attr.attribute_id];
                  return (
                    <td
                      key={entry.competitor_id}
                      className={`px-3 py-2 ${isVenture ? 'bg-blue-50/50 dark:bg-blue-900/10' : ''}`}
                    >
                      <CellContent cell={cell} />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Strengths / Weaknesses / Dangerous Competitors */}
      {md && (md.venture_strengths?.length > 0 || md.venture_weaknesses?.length > 0 || md.dangerous_competitors?.length > 0) && (
        <div className="p-5 border-t border-slate-200 dark:border-slate-700 grid grid-cols-1 md:grid-cols-3 gap-4">
          {md.venture_strengths?.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-green-700 dark:text-green-400 mb-2">Venture Strengths</h4>
              <ul className="space-y-1 text-xs text-slate-600 dark:text-slate-400">
                {md.venture_strengths.map((s, i) => (
                  <li key={i} className="flex gap-1"><span className="text-green-500">+</span> {s}</li>
                ))}
              </ul>
            </div>
          )}
          {md.venture_weaknesses?.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-red-700 dark:text-red-400 mb-2">Venture Weaknesses</h4>
              <ul className="space-y-1 text-xs text-slate-600 dark:text-slate-400">
                {md.venture_weaknesses.map((w, i) => (
                  <li key={i} className="flex gap-1"><span className="text-red-500">-</span> {w}</li>
                ))}
              </ul>
            </div>
          )}
          {md.dangerous_competitors?.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-amber-700 dark:text-amber-400 mb-2">Most Dangerous</h4>
              <ul className="space-y-1 text-xs text-slate-600 dark:text-slate-400">
                {md.dangerous_competitors.map((d, i) => (
                  <li key={i} className="flex gap-1"><span className="text-amber-500">!</span> {d}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
