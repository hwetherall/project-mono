import { useState, useEffect } from 'react';

export default function ReportSidebar({ categories = [], activeSection }) {
  const sidebarSections = [
    { id: 'section-verdict', label: 'Verdict Dashboard' },
    { id: 'section-summary', label: 'Executive Summary' },
    ...categories.map((cat) => ({
      id: `section-${cat.category_id}`,
      label: `${cat.category_id}: ${cat.category_name}`,
      short: cat.category_id,
    })),
    { id: 'section-gaps', label: 'Gap Inventory' },
    { id: 'section-sources', label: 'Sources' },
  ];

  return (
    <nav className="report-sidebar space-y-0.5 text-sm sticky top-4">
      {sidebarSections.map((sec) => {
        const isActive = activeSection === sec.id;
        return (
          <a
            key={sec.id}
            href={`#${sec.id}`}
            className={`block px-3 py-1.5 rounded-md transition-colors truncate ${
              isActive
                ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 font-medium'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
            }`}
            title={sec.label}
          >
            {sec.short ? (
              <>
                <span className="font-mono text-xs text-slate-400 dark:text-slate-500 mr-1">{sec.short}</span>
                <span className="hidden lg:inline">{sec.label.replace(`${sec.short}: `, '')}</span>
              </>
            ) : (
              sec.label
            )}
          </a>
        );
      })}

      <div className="pt-4 space-y-1.5">
        <button
          onClick={() => window.print()}
          className="w-full text-left px-3 py-1.5 text-xs text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md transition-colors"
        >
          Export PDF
        </button>
      </div>
    </nav>
  );
}
