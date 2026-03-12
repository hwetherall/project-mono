import { useState, useMemo, useCallback, useRef, useEffect } from 'react';

export default function ReportSearch({ categories = [], onJumpTo }) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const debounceRef = useRef(null);
  const [debouncedQuery, setDebouncedQuery] = useState('');

  const handleChange = useCallback((e) => {
    const val = e.target.value;
    setQuery(val);
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => setDebouncedQuery(val), 300);
  }, []);

  const results = useMemo(() => {
    if (!debouncedQuery || debouncedQuery.length < 2) return [];
    const q = debouncedQuery.toLowerCase();

    return categories
      .map((cat) => {
        const text = cat.raw_report_markdown || '';
        const matches = [];
        let idx = 0;
        const lower = text.toLowerCase();
        while (idx < lower.length) {
          const pos = lower.indexOf(q, idx);
          if (pos === -1) break;
          // Extract surrounding context
          const start = Math.max(0, pos - 40);
          const end = Math.min(text.length, pos + q.length + 40);
          matches.push(text.slice(start, end));
          idx = pos + q.length;
        }
        if (matches.length === 0) return null;
        return {
          category_id: cat.category_id,
          category_name: cat.category_name,
          matchCount: matches.length,
          snippets: matches.slice(0, 3),
        };
      })
      .filter(Boolean);
  }, [debouncedQuery, categories]);

  const totalMatches = results.reduce((sum, r) => sum + r.matchCount, 0);

  useEffect(() => {
    return () => clearTimeout(debounceRef.current);
  }, []);

  return (
    <div className="relative">
      <div className="flex items-center gap-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2">
        <span className="text-slate-400 dark:text-slate-500 text-sm">Search</span>
        <input
          type="text"
          value={query}
          onChange={handleChange}
          onFocus={() => setIsOpen(true)}
          placeholder="Search results..."
          className="flex-1 bg-transparent outline-none text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500"
        />
        {query && (
          <button
            onClick={() => { setQuery(''); setDebouncedQuery(''); }}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 text-sm"
          >
            x
          </button>
        )}
      </div>

      {isOpen && debouncedQuery.length >= 2 && (
        <div className="absolute z-20 top-full mt-1 left-0 right-0 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg max-h-80 overflow-auto">
          {results.length === 0 ? (
            <div className="px-4 py-3 text-sm text-slate-400 dark:text-slate-500">
              No matches for "{debouncedQuery}"
            </div>
          ) : (
            <>
              <div className="px-4 py-2 text-xs text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700">
                {totalMatches} matches across {results.length} categories
              </div>
              {results.map((r) => (
                <button
                  key={r.category_id}
                  onClick={() => {
                    onJumpTo?.(r.category_id);
                    setIsOpen(false);
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-slate-50 dark:hover:bg-slate-800 border-b border-slate-100 dark:border-slate-800 last:border-0 transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                      <span className="font-mono text-slate-400 dark:text-slate-500 mr-1">{r.category_id}</span>
                      {r.category_name}
                    </span>
                    <span className="text-xs text-slate-400 dark:text-slate-500">{r.matchCount} matches</span>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
                    ...{r.snippets[0]}...
                  </p>
                </button>
              ))}
            </>
          )}
        </div>
      )}

      {/* Click-outside handler */}
      {isOpen && (
        <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />
      )}
    </div>
  );
}

/** Highlight search terms in text content */
export function highlightText(text, searchTerm) {
  if (!searchTerm || searchTerm.length < 2) return text;
  const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return text.replace(regex, '<mark class="search-highlight">$1</mark>');
}
