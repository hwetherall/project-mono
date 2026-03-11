export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">IR</span>
            </div>
            <h1 className="text-lg font-semibold text-slate-900">Innovera Research</h1>
          </div>
          <span className="text-sm text-slate-400">Evidence Pipeline v1</span>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-6 py-8">
        {children}
      </main>
    </div>
  );
}
