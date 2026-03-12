import { useState, useEffect, useRef } from 'react';

const LEVEL_CONFIG = {
  info:    { icon: '\u25CF', color: 'text-blue-400' },
  start:   { icon: '\u2192', color: 'text-cyan-400' },
  success: { icon: '\u2713', color: 'text-green-400' },
  error:   { icon: '\u2717', color: 'text-red-400' },
  warning: { icon: '\u26A0', color: 'text-amber-400' },
  extract: { icon: '\u{1F4CB}', color: 'text-purple-400' },
};

function formatTimestamp(ts) {
  const d = new Date(ts);
  return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

export default function ActivityStream({ entries = [] }) {
  const [paused, setPaused] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (!paused && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [entries.length, paused]);

  const displayEntries = entries.slice(-500);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-3 py-2 border-b border-slate-700">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">Activity Stream</span>
        <button
          onClick={() => setPaused(!paused)}
          className="text-xs text-slate-500 hover:text-slate-300 transition-colors px-2 py-0.5 rounded"
        >
          {paused ? 'Resume' : 'Pause'}
        </button>
      </div>
      <div
        ref={scrollRef}
        className="activity-stream flex-1 overflow-auto px-3 py-2 bg-slate-900 dark:bg-black min-h-0"
      >
        {displayEntries.length === 0 && (
          <div className="text-slate-600 text-xs py-2">Waiting for events...</div>
        )}
        {displayEntries.map((entry, i) => {
          const config = LEVEL_CONFIG[entry.level] || LEVEL_CONFIG.info;
          return (
            <div key={i} className="flex gap-2 py-0.5 leading-relaxed">
              <span className="text-slate-600 shrink-0 text-xs">{formatTimestamp(entry.timestamp)}</span>
              <span className={`shrink-0 ${config.color}`}>{config.icon}</span>
              <span className="text-slate-300 text-xs">{entry.message}</span>
            </div>
          );
        })}
      </div>
      {paused && (
        <div className="text-center py-1 bg-amber-900/30 text-amber-400 text-xs">
          Auto-scroll paused
        </div>
      )}
    </div>
  );
}
