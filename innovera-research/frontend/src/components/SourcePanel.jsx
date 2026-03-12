import { useMemo } from 'react';

function extractDomain(url) {
  try {
    const u = new URL(url);
    return u.hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
}

export default function SourcePanel({ categories = [] }) {
  const aggregated = useMemo(() => {
    const sourceMap = new Map();

    for (const cat of categories) {
      for (const src of (cat.sources || [])) {
        const url = src.url || src;
        if (!url || typeof url !== 'string') continue;
        const domain = extractDomain(url);

        if (sourceMap.has(url)) {
          const existing = sourceMap.get(url);
          existing.citedBy.add(cat.category_id);
          existing.count++;
        } else {
          sourceMap.set(url, {
            url,
            domain,
            citedBy: new Set([cat.category_id]),
            count: 1,
          });
        }
      }
    }

    return Array.from(sourceMap.values())
      .map((s) => ({ ...s, citedBy: Array.from(s.citedBy) }))
      .sort((a, b) => b.count - a.count);
  }, [categories]);

  if (aggregated.length === 0) return null;

  // Group by domain
  const byDomain = useMemo(() => {
    const map = new Map();
    for (const src of aggregated) {
      if (!map.has(src.domain)) {
        map.set(src.domain, { domain: src.domain, sources: [], totalCitations: 0, categories: new Set() });
      }
      const group = map.get(src.domain);
      group.sources.push(src);
      group.totalCitations += src.count;
      src.citedBy.forEach((c) => group.categories.add(c));
    }
    return Array.from(map.values())
      .map((g) => ({ ...g, categories: Array.from(g.categories) }))
      .sort((a, b) => b.totalCitations - a.totalCitations);
  }, [aggregated]);

  return (
    <div id="section-sources" className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl p-6">
      <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-4">All Sources ({aggregated.length} unique)</h2>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700">
              <th className="pb-2 pr-4 font-medium">#</th>
              <th className="pb-2 pr-4 font-medium">Domain</th>
              <th className="pb-2 pr-4 font-medium">Cited By</th>
              <th className="pb-2 font-medium text-right">Citations</th>
            </tr>
          </thead>
          <tbody>
            {byDomain.slice(0, 30).map((group, i) => (
              <tr key={group.domain} className="border-b border-slate-100 dark:border-slate-800">
                <td className="py-2 pr-4 text-slate-400 dark:text-slate-500 font-mono text-xs">{i + 1}</td>
                <td className="py-2 pr-4">
                  <span className="text-slate-700 dark:text-slate-300 font-medium">{group.domain}</span>
                  <span className="text-slate-400 dark:text-slate-500 ml-1 text-xs">({group.sources.length} URLs)</span>
                </td>
                <td className="py-2 pr-4">
                  <div className="flex flex-wrap gap-1">
                    {group.categories.map((cid) => (
                      <span
                        key={cid}
                        className="px-1.5 py-0.5 text-xs rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-mono"
                      >
                        {cid}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="py-2 text-right font-mono font-medium text-slate-700 dark:text-slate-300">{group.totalCitations}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {byDomain.length > 30 && (
        <p className="mt-3 text-xs text-slate-400 dark:text-slate-500">
          Showing top 30 of {byDomain.length} domains
        </p>
      )}
    </div>
  );
}

/** Render sources as clickable chips for a single category */
export function SourceChips({ sources = [] }) {
  if (sources.length === 0) return null;

  const unique = [...new Map(sources.map((s) => {
    const url = s.url || s;
    return [url, { url, domain: extractDomain(url) }];
  })).values()];

  return (
    <div className="flex flex-wrap gap-1.5">
      {unique.map((src, i) => (
        <a
          key={i}
          href={src.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 px-2 py-1 text-xs rounded-full bg-slate-100 dark:bg-slate-800 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors border border-slate-200 dark:border-slate-700"
          title={src.url}
        >
          <span className="truncate max-w-[150px]">{src.domain}</span>
        </a>
      ))}
    </div>
  );
}
