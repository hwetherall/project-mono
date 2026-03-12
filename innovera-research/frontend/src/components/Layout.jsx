import { useTheme } from '../hooks/useTheme.jsx';

export default function Layout({ children, onNavigate, currentView }) {
  const { theme, setTheme } = useTheme();

  const cycleTheme = () => {
    const next = theme === 'light' ? 'dark' : theme === 'dark' ? 'system' : 'light';
    setTheme(next);
  };

  const themeIcon = theme === 'dark' ? '\u{1F319}' : theme === 'light' ? '\u{2600}\u{FE0F}' : '\u{1F4BB}';
  const themeLabel = theme === 'dark' ? 'Dark' : theme === 'light' ? 'Light' : 'System';

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors">
      <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700 px-6 py-4 no-print">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">IR</span>
            </div>
            <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Innovera Research</h1>
          </div>
          <div className="flex items-center gap-2">
            {onNavigate && (
              <>
                <button
                  onClick={() => onNavigate('input')}
                  className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                    currentView === 'input'
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 font-medium'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  New Run
                </button>
                <button
                  onClick={() => onNavigate('history')}
                  className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                    currentView === 'history'
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 font-medium'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  History
                </button>
              </>
            )}
            <button
              onClick={cycleTheme}
              className="px-3 py-1.5 text-sm text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md transition-colors"
              title={`Theme: ${themeLabel}`}
            >
              {themeIcon}
            </button>
            <span className="text-sm text-slate-400 dark:text-slate-500 hidden sm:inline">v2</span>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-6 py-8">
        {children}
      </main>
    </div>
  );
}
