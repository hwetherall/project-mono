import { useState } from 'react';

const CATEGORY_PHASES = {
  'Phase 1: Foundation': [
    { id: 'EC-01', name: 'Market Sizing & Growth' },
    { id: 'EC-02', name: 'Competitor Landscape & Positioning' },
    { id: 'EC-05', name: 'Problem Prevalence & Cost Data' },
    { id: 'EC-06', name: 'Regulatory & Compliance Environment' },
    { id: 'EC-10', name: 'Voice of Market' },
  ],
  'Phase 2: Competitor-Dependent': [
    { id: 'EC-03', name: 'Investment & Financial Signals' },
    { id: 'EC-04', name: 'Alternative Solution Failures & Reviews' },
    { id: 'EC-11', name: 'Search & Hiring Trends' },
  ],
  'Phase 3: Synthesis': [
    { id: 'EC-07', name: 'Enabling Technology Trends' },
    { id: 'EC-08', name: 'Urgency Drivers & Forcing Functions' },
    { id: 'EC-09', name: 'Industry Analyst & Expert Coverage' },
    { id: 'EC-12', name: 'Budget & Procurement Context' },
    { id: 'EC-13', name: 'Proxy Market Trajectories' },
  ],
};

const ALL_CATEGORY_IDS = Object.values(CATEGORY_PHASES).flat().map((c) => c.id);

export default function InputForm({ onSubmit }) {
  const [documentText, setDocumentText] = useState('');
  const [additionalContext, setAdditionalContext] = useState('');
  const [coreQuestion, setCoreQuestion] = useState('');
  const [successCriteria, setSuccessCriteria] = useState(['', '', '']);
  const [ventureName, setVentureName] = useState('');
  const [maxConcurrent, setMaxConcurrent] = useState(2);
  const [selectedCategories, setSelectedCategories] = useState(new Set(ALL_CATEGORY_IDS));
  const [configOpen, setConfigOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const validCriteria = successCriteria.filter((c) => c.trim());
  const isValid = documentText.trim() && coreQuestion.trim() && validCriteria.length >= 1;

  const addCriterion = () => setSuccessCriteria((prev) => [...prev, '']);
  const removeCriterion = (index) =>
    setSuccessCriteria((prev) => prev.filter((_, i) => i !== index));
  const updateCriterion = (index, value) =>
    setSuccessCriteria((prev) => prev.map((c, i) => (i === index ? value : c)));

  const toggleCategory = (id) => {
    setSelectedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isValid || submitting) return;

    setSubmitting(true);
    try {
      const categoriesToRun =
        selectedCategories.size === ALL_CATEGORY_IDS.length
          ? []
          : Array.from(selectedCategories);

      await onSubmit({
        document_text: documentText,
        additional_context: additionalContext,
        core_question: coreQuestion,
        success_criteria: validCriteria,
        venture_name: ventureName,
        max_concurrent: maxConcurrent,
        categories_to_run: categoriesToRun,
      });
    } catch {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-1">New Research Run</h2>
        <p className="text-slate-500">Provide your venture details to begin the evidence pipeline.</p>
      </div>

      {/* Section 1: Document Content */}
      <section className="space-y-2">
        <label className="block text-sm font-medium text-slate-700">
          Document Content <span className="text-red-500">*</span>
        </label>
        <textarea
          className="w-full min-h-[250px] p-4 border border-slate-300 rounded-lg text-sm
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y bg-white"
          placeholder="Paste your venture brief, pitch deck text, or proposal content here as plain text or markdown..."
          value={documentText}
          onChange={(e) => setDocumentText(e.target.value)}
        />
        <p className="text-xs text-slate-400">
          Extract the text from your documents and paste it here. Markdown formatting is preserved.
        </p>
      </section>

      {/* Section 2: Additional Context */}
      <section className="space-y-2">
        <label className="block text-sm font-medium text-slate-700">
          Additional Context
        </label>
        <textarea
          className="w-full min-h-[120px] p-4 border border-slate-300 rounded-lg text-sm
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y bg-white"
          placeholder="Any additional context — team background, prior decisions, internal notes, constraints..."
          value={additionalContext}
          onChange={(e) => setAdditionalContext(e.target.value)}
        />
        <p className="text-xs text-slate-400">
          Optional. Anything that would help the analysis but isn't in the document.
        </p>
      </section>

      {/* Section 3: Core Question */}
      <section className="space-y-2">
        <label className="block text-sm font-medium text-slate-700">
          Strategic Question <span className="text-red-500">*</span>
        </label>
        <textarea
          className="w-full p-4 border border-slate-300 rounded-lg text-sm
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none bg-white"
          rows={2}
          placeholder="e.g., Should we invest $2M in this opportunity?"
          value={coreQuestion}
          onChange={(e) => setCoreQuestion(e.target.value)}
        />
        <p className="text-xs text-slate-400">
          The single question this research memo is designed to answer.
        </p>
      </section>

      {/* Section 4: Success Criteria */}
      <section className="space-y-2">
        <label className="block text-sm font-medium text-slate-700">
          How Do You Measure Success? <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {successCriteria.map((criterion, index) => (
            <div key={index} className="flex gap-2">
              <input
                type="text"
                className="flex-1 p-3 border border-slate-300 rounded-lg text-sm
                           focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                placeholder={`e.g., TAM exceeds $500M`}
                value={criterion}
                onChange={(e) => updateCriterion(index, e.target.value)}
              />
              {successCriteria.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeCriterion(index)}
                  className="px-3 text-slate-400 hover:text-red-500 transition-colors"
                >
                  &times;
                </button>
              )}
            </div>
          ))}
        </div>
        <button
          type="button"
          onClick={addCriterion}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          + Add criterion
        </button>
        <p className="text-xs text-slate-400">
          Define specific, measurable criteria. At least one required.
        </p>
      </section>

      {/* Configuration Accordion */}
      <section className="border border-slate-200 rounded-lg bg-white">
        <button
          type="button"
          onClick={() => setConfigOpen(!configOpen)}
          className="w-full px-4 py-3 flex items-center justify-between text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          <span>Configuration</span>
          <span className="text-slate-400">{configOpen ? '\u25B2' : '\u25BC'}</span>
        </button>
        {configOpen && (
          <div className="px-4 pb-4 space-y-4 border-t border-slate-100">
            {/* Venture Name Override */}
            <div className="pt-4 space-y-1">
              <label className="block text-sm text-slate-600">Venture Name Override</label>
              <input
                type="text"
                className="w-full p-2 border border-slate-300 rounded text-sm bg-white
                           focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Auto-detected from documents if empty"
                value={ventureName}
                onChange={(e) => setVentureName(e.target.value)}
              />
            </div>

            {/* Max Concurrent */}
            <div className="space-y-1">
              <label className="block text-sm text-slate-600">
                Max Concurrent Categories: <span className="font-medium">{maxConcurrent}</span>
              </label>
              <input
                type="range"
                min={1}
                max={4}
                value={maxConcurrent}
                onChange={(e) => setMaxConcurrent(Number(e.target.value))}
                className="w-full accent-blue-600"
              />
              <div className="flex justify-between text-xs text-slate-400">
                <span>1 (safe)</span>
                <span>4 (fast)</span>
              </div>
            </div>

            {/* Category Selection */}
            <div className="space-y-3">
              <label className="block text-sm text-slate-600">Categories to Run</label>
              {Object.entries(CATEGORY_PHASES).map(([phase, cats]) => (
                <div key={phase}>
                  <p className="text-xs font-semibold text-slate-500 uppercase mb-1">{phase}</p>
                  <div className="space-y-1">
                    {cats.map((cat) => (
                      <label key={cat.id} className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={selectedCategories.has(cat.id)}
                          onChange={() => toggleCategory(cat.id)}
                          className="accent-blue-600"
                        />
                        <span className="text-slate-400 font-mono text-xs">{cat.id}</span>
                        {cat.name}
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* Submit */}
      <div className="flex items-center gap-4">
        <button
          type="submit"
          disabled={!isValid || submitting}
          className="px-8 py-3 bg-blue-600 text-white font-medium rounded-lg
                     hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed
                     transition-colors text-sm"
        >
          {submitting ? 'Starting...' : 'Start Research'}
        </button>
        <span className="text-xs text-slate-400">
          Estimated: 30-90 minutes &middot; $12-22
        </span>
      </div>
    </form>
  );
}
