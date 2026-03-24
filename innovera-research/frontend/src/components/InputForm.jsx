import { useState, useEffect, useMemo } from 'react';

const DEMAND_VALIDATION_PHASES = {
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

const MARKET_RESEARCH_PHASES = {
  'Phase 1: Foundation': [
    { id: 'MR-01a', name: 'Market Definition & Boundaries' },
    { id: 'MR-01b', name: 'Market Sizing & Methodology' },
    { id: 'MR-04', name: 'Trends & Growth Quality' },
    { id: 'MR-06a', name: 'Competitor Identification' },
    { id: 'MR-06b', name: 'Competitive Intelligence' },
    { id: 'MR-09', name: 'Regulation & Platform Shifts' },
  ],
  'Phase 2: Structural': [
    { id: 'MR-02', name: 'SAM / SOM / Reachability' },
    { id: 'MR-03', name: 'Segments & Concentration' },
    { id: 'MR-05', name: 'Value Chain & Whitespace' },
  ],
  'Phase 3: Commercial': [
    { id: 'MR-07', name: 'Buying Process, Budget & Pricing' },
    { id: 'MR-08', name: 'Adoption & Expansion Dynamics' },
    { id: 'MR-10', name: 'Barriers, Saturation & Ecosystem Power' },
  ],
};

export default function InputForm({ onSubmit }) {
  const [researchMode, setResearchMode] = useState('demand_validation');
  const [savedBriefSource, setSavedBriefSource] = useState('');
  const [documentText, setDocumentText] = useState('');
  const [additionalContext, setAdditionalContext] = useState('');
  const [coreQuestion, setCoreQuestion] = useState('');
  const [successCriteria, setSuccessCriteria] = useState(['', '', '']);
  const [ventureName, setVentureName] = useState('');
  const [maxConcurrent, setMaxConcurrent] = useState(2);
  const [configOpen, setConfigOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [loadingSavedBrief, setLoadingSavedBrief] = useState(false);
  const [savedBriefMessage, setSavedBriefMessage] = useState('');
  const [savedBriefError, setSavedBriefError] = useState('');
  const [prebuiltTable, setPrebuiltTable] = useState(null);
  const [prebuiltTableError, setPrebuiltTableError] = useState('');
  const [mustIncludeCompanies, setMustIncludeCompanies] = useState(['']);
  const [customParameters, setCustomParameters] = useState(['']);

  const categoryPhases = researchMode === 'market_research' ? MARKET_RESEARCH_PHASES : DEMAND_VALIDATION_PHASES;
  const allCategoryIds = useMemo(
    () => Object.values(categoryPhases).flat().map((c) => c.id),
    [categoryPhases]
  );
  const [selectedCategories, setSelectedCategories] = useState(new Set(allCategoryIds));

  useEffect(() => {
    setSelectedCategories(new Set(allCategoryIds));
  }, [researchMode, allCategoryIds]);

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

  const handleLoadSavedBrief = async () => {
    if (!savedBriefSource.trim() || loadingSavedBrief) return;

    setLoadingSavedBrief(true);
    setSavedBriefError('');
    setSavedBriefMessage('');

    try {
      const res = await fetch(`/api/venture-brief/load?source=${encodeURIComponent(savedBriefSource.trim())}`);
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Failed to load saved brief');
      }

      setDocumentText(data.content || '');
      setSavedBriefMessage(`Loaded saved brief from ${data.resolved_path}`);
    } catch (err) {
      setSavedBriefError(err.message || 'Failed to load saved brief');
    } finally {
      setLoadingSavedBrief(false);
    }
  };

  const handleTableUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPrebuiltTableError('');
    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const parsed = JSON.parse(ev.target.result);
        if (!parsed.competitors || !Array.isArray(parsed.competitors)) {
          throw new Error('Missing "competitors" array');
        }
        if (!parsed.attributes || !Array.isArray(parsed.attributes)) {
          throw new Error('Missing "attributes" array');
        }
        setPrebuiltTable(parsed);
      } catch (err) {
        setPrebuiltTableError(`Invalid competitive table JSON: ${err.message}`);
        setPrebuiltTable(null);
      }
    };
    reader.readAsText(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isValid || submitting) return;

    setSubmitting(true);
    try {
      const categoriesToRun =
        selectedCategories.size === allCategoryIds.length
          ? []
          : Array.from(selectedCategories);

      const validCompanies = mustIncludeCompanies.filter((c) => c.trim());
      const validParams = customParameters.filter((p) => p.trim());

      await onSubmit({
        research_mode: researchMode,
        document_text: documentText,
        additional_context: additionalContext,
        core_question: coreQuestion,
        success_criteria: validCriteria,
        venture_name: ventureName,
        max_concurrent: maxConcurrent,
        categories_to_run: categoriesToRun,
        ...(prebuiltTable ? { prebuilt_competitive_table: prebuiltTable } : {}),
        ...(validCompanies.length ? { must_include_companies: validCompanies } : {}),
        ...(validParams.length ? { custom_parameters: validParams } : {}),
      });
    } catch {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-1">New Research Run</h2>
        <p className="text-slate-500 dark:text-slate-400">
          {researchMode === 'run_all'
            ? 'Provide your venture details once. All three chapters will run sequentially overnight.'
            : researchMode === 'competitive_table'
              ? 'Provide your venture details to build a dynamic competitor matrix.'
              : researchMode === 'market_research'
                ? 'Provide a market or topic briefing to begin market research.'
                : 'Provide your venture details to begin the evidence pipeline.'}
        </p>
      </div>

      {/* Research Mode Selector */}
      <section className="space-y-3">
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
          Research Mode
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <label
            className={`border rounded-lg p-4 cursor-pointer flex items-start gap-3 transition-colors ${
              researchMode === 'demand_validation'
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
            }`}
          >
            <input
              type="radio"
              name="research_mode"
              checked={researchMode === 'demand_validation'}
              onChange={() => setResearchMode('demand_validation')}
              className="mt-1 accent-blue-600"
            />
            <div>
              <div className="font-medium text-slate-900 dark:text-slate-100">Demand Validation</div>
              <div className="text-sm text-slate-500 dark:text-slate-400">Test a specific venture or thesis against 13 evidence categories.</div>
            </div>
          </label>
          <label
            className={`border rounded-lg p-4 cursor-pointer flex items-start gap-3 transition-colors ${
              researchMode === 'market_research'
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
            }`}
          >
            <input
              type="radio"
              name="research_mode"
              checked={researchMode === 'market_research'}
              onChange={() => setResearchMode('market_research')}
              className="mt-1 accent-blue-600"
            />
            <div>
              <div className="font-medium text-slate-900 dark:text-slate-100">Market Research</div>
              <div className="text-sm text-slate-500 dark:text-slate-400">Map a market's structure, economics, and GTM dynamics across 10 categories.</div>
            </div>
          </label>
          <label
            className={`border rounded-lg p-4 cursor-pointer flex items-start gap-3 transition-colors ${
              researchMode === 'competitive_table'
                ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
            }`}
          >
            <input
              type="radio"
              name="research_mode"
              checked={researchMode === 'competitive_table'}
              onChange={() => setResearchMode('competitive_table')}
              className="mt-1 accent-purple-600"
            />
            <div>
              <div className="font-medium text-slate-900 dark:text-slate-100">Competitive Table</div>
              <div className="text-sm text-slate-500 dark:text-slate-400">Build a dynamic competitor matrix with tiered research depth. No category reports.</div>
            </div>
          </label>
        </div>

        <label
          className={`border-2 rounded-lg p-4 cursor-pointer flex items-start gap-3 transition-colors ${
            researchMode === 'run_all'
              ? 'border-emerald-500 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20'
              : 'border-dashed border-slate-300 dark:border-slate-600 hover:border-emerald-400 dark:hover:border-emerald-600'
          }`}
        >
          <input
            type="radio"
            name="research_mode"
            checked={researchMode === 'run_all'}
            onChange={() => setResearchMode('run_all')}
            className="mt-1 accent-emerald-600"
          />
          <div className="flex-1">
            <div className="font-medium text-slate-900 dark:text-slate-100">Run All Chapters</div>
            <div className="text-sm text-slate-500 dark:text-slate-400">
              Chain all three chapters sequentially: Competitive Table → Market Research → Demand Validation.
              Runs overnight on the server — you can close your browser.
            </div>
            <div className="mt-2 flex gap-2 text-xs">
              <span className="px-2 py-0.5 rounded-full bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300">CT</span>
              <span className="text-slate-400 dark:text-slate-500">→</span>
              <span className="px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300">MR</span>
              <span className="text-slate-400 dark:text-slate-500">→</span>
              <span className="px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300">DV</span>
            </div>
          </div>
        </label>

        {researchMode !== 'competitive_table' && (
          <div className="border border-slate-200 dark:border-slate-700 rounded-lg p-4 bg-white dark:bg-slate-900 space-y-3">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Pre-built Competitive Table <span className="text-slate-400 dark:text-slate-500 font-normal">(optional)</span>
            </label>
            <p className="text-xs text-slate-400 dark:text-slate-500">
              Upload a competitive_table.json from a previous run to skip building it from scratch.
            </p>
            {!prebuiltTable ? (
              <div>
                <input
                  type="file"
                  accept=".json"
                  onChange={handleTableUpload}
                  className="block w-full text-sm text-slate-500 dark:text-slate-400
                             file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0
                             file:text-sm file:font-medium
                             file:bg-purple-50 dark:file:bg-purple-900/30
                             file:text-purple-700 dark:file:text-purple-300
                             hover:file:bg-purple-100 dark:hover:file:bg-purple-900/50
                             file:cursor-pointer"
                />
                {prebuiltTableError && (
                  <p className="mt-2 text-xs text-red-600 dark:text-red-400">{prebuiltTableError}</p>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-between p-3 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                <div className="text-sm">
                  <span className="font-medium text-purple-700 dark:text-purple-300">
                    {prebuiltTable.venture_name || 'Competitive Table'}
                  </span>
                  <span className="text-purple-500 dark:text-purple-400 ml-2">
                    {prebuiltTable.competitors?.length || 0} competitors, {prebuiltTable.attributes?.length || 0} attributes
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => { setPrebuiltTable(null); setPrebuiltTableError(''); }}
                  className="text-sm text-purple-600 dark:text-purple-400 hover:text-red-600 dark:hover:text-red-400 font-medium"
                >
                  Remove
                </button>
              </div>
            )}
          </div>
        )}
      </section>

      {/* Must-Include Companies & Custom Parameters (CT / Run All modes) */}
      {(researchMode === 'competitive_table' || researchMode === 'run_all') && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Must-Include Companies (Y Axis) */}
          <div className="border border-purple-200 dark:border-purple-800 rounded-lg p-4 bg-purple-50/30 dark:bg-purple-900/10 space-y-3">
            <label className="block text-sm font-medium text-purple-700 dark:text-purple-300">
              Must-Include Companies <span className="text-slate-400 dark:text-slate-500 font-normal">(Y axis)</span>
            </label>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Companies guaranteed to appear in the table as Tier 1, even if not auto-discovered.
            </p>
            <div className="space-y-2">
              {mustIncludeCompanies.map((company, index) => (
                <div key={index} className="flex gap-2">
                  <input
                    type="text"
                    className="flex-1 p-2 border border-slate-300 dark:border-slate-600 rounded text-sm
                               bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                               focus:ring-2 focus:ring-purple-500 focus:border-purple-500
                               placeholder-slate-400 dark:placeholder-slate-500"
                    placeholder={`e.g., ${index === 0 ? 'Abbott' : index === 1 ? 'Medtronic' : 'Company name'}`}
                    value={company}
                    onChange={(e) =>
                      setMustIncludeCompanies((prev) =>
                        prev.map((c, i) => (i === index ? e.target.value : c))
                      )
                    }
                  />
                  {mustIncludeCompanies.length > 1 && (
                    <button
                      type="button"
                      onClick={() =>
                        setMustIncludeCompanies((prev) => prev.filter((_, i) => i !== index))
                      }
                      className="px-2 text-slate-400 hover:text-red-500 transition-colors"
                    >
                      &times;
                    </button>
                  )}
                </div>
              ))}
            </div>
            <button
              type="button"
              onClick={() => setMustIncludeCompanies((prev) => [...prev, ''])}
              className="text-sm text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 font-medium"
            >
              + Add company
            </button>
          </div>

          {/* Custom Parameters (X Axis) */}
          <div className="border border-indigo-200 dark:border-indigo-800 rounded-lg p-4 bg-indigo-50/30 dark:bg-indigo-900/10 space-y-3">
            <label className="block text-sm font-medium text-indigo-700 dark:text-indigo-300">
              Custom Parameters <span className="text-slate-400 dark:text-slate-500 font-normal">(X axis)</span>
            </label>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Custom attributes added to the matrix columns alongside auto-generated ones.
            </p>
            <div className="space-y-2">
              {customParameters.map((param, index) => (
                <div key={index} className="flex gap-2">
                  <input
                    type="text"
                    className="flex-1 p-2 border border-slate-300 dark:border-slate-600 rounded text-sm
                               bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                               focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                               placeholder-slate-400 dark:placeholder-slate-500"
                    placeholder={`e.g., ${index === 0 ? 'ESG Rating' : index === 1 ? 'API Availability' : 'Parameter name'}`}
                    value={param}
                    onChange={(e) =>
                      setCustomParameters((prev) =>
                        prev.map((p, i) => (i === index ? e.target.value : p))
                      )
                    }
                  />
                  {customParameters.length > 1 && (
                    <button
                      type="button"
                      onClick={() =>
                        setCustomParameters((prev) => prev.filter((_, i) => i !== index))
                      }
                      className="px-2 text-slate-400 hover:text-red-500 transition-colors"
                    >
                      &times;
                    </button>
                  )}
                </div>
              ))}
            </div>
            <button
              type="button"
              onClick={() => setCustomParameters((prev) => [...prev, ''])}
              className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-medium"
            >
              + Add parameter
            </button>
          </div>
        </div>
      )}

      <section className="space-y-2">
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
          Load Saved Brief
        </label>
        <div className="flex flex-col md:flex-row gap-2">
          <input
            type="text"
            className="flex-1 p-3 border border-slate-300 dark:border-slate-600 rounded-lg text-sm
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                       bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                       placeholder-slate-400 dark:placeholder-slate-500"
            placeholder="Run ID or path to venture_brief.md"
            value={savedBriefSource}
            onChange={(e) => setSavedBriefSource(e.target.value)}
          />
          <button
            type="button"
            onClick={handleLoadSavedBrief}
            disabled={!savedBriefSource.trim() || loadingSavedBrief}
            className="px-4 py-3 rounded-lg text-sm font-medium border border-slate-300 dark:border-slate-600
                       bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200
                       hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loadingSavedBrief ? 'Loading...' : 'Load'}
          </button>
        </div>
        <p className="text-xs text-slate-400 dark:text-slate-500">
          Use a saved run folder ID like `1b8049da-0a72-457d-a0a8-b831213d07d1` or a full path under `venture_docs`.
        </p>
        {savedBriefMessage && (
          <p className="text-xs text-green-600 dark:text-green-400">{savedBriefMessage}</p>
        )}
        {savedBriefError && (
          <p className="text-xs text-red-600 dark:text-red-400">{savedBriefError}</p>
        )}
      </section>

      <section className="space-y-2">
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
          Document Content <span className="text-red-500">*</span>
        </label>
        <textarea
          className="w-full min-h-[250px] p-4 border border-slate-300 dark:border-slate-600 rounded-lg text-sm
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y
                     bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                     placeholder-slate-400 dark:placeholder-slate-500"
          placeholder={researchMode === 'market_research'
            ? 'Paste your market briefing, industry overview, or research brief here...'
            : 'Paste your venture brief, pitch deck text, or proposal content here...'}
          value={documentText}
          onChange={(e) => setDocumentText(e.target.value)}
        />
        <p className="text-xs text-slate-400 dark:text-slate-500">
          {researchMode === 'market_research'
            ? 'Describe the market, product category, or industry you want to research. Markdown formatting is preserved.'
            : 'Extract the text from your documents and paste it here. Markdown formatting is preserved.'}
        </p>
      </section>

      <section className="space-y-2">
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
          Additional Context
        </label>
        <textarea
          className="w-full min-h-[120px] p-4 border border-slate-300 dark:border-slate-600 rounded-lg text-sm
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y
                     bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                     placeholder-slate-400 dark:placeholder-slate-500"
          placeholder="Any additional context — team background, prior decisions, internal notes, constraints..."
          value={additionalContext}
          onChange={(e) => setAdditionalContext(e.target.value)}
        />
        <p className="text-xs text-slate-400 dark:text-slate-500">
          Optional. Anything that would help the analysis but isn't in the document.
        </p>
      </section>

      <section className="space-y-2">
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
          Strategic Question <span className="text-red-500">*</span>
        </label>
        <textarea
          className="w-full p-4 border border-slate-300 dark:border-slate-600 rounded-lg text-sm
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none
                     bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                     placeholder-slate-400 dark:placeholder-slate-500"
          rows={2}
          placeholder={researchMode === 'market_research'
            ? 'e.g., What does the U.S. remote patient monitoring market look like structurally, commercially, and competitively?'
            : 'e.g., Should we invest $2M in this opportunity?'}
          value={coreQuestion}
          onChange={(e) => setCoreQuestion(e.target.value)}
        />
        <p className="text-xs text-slate-400 dark:text-slate-500">
          The single question this research memo is designed to answer.
        </p>
      </section>

      <section className="space-y-2">
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
          How Do You Measure Success? <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {successCriteria.map((criterion, index) => (
            <div key={index} className="flex gap-2">
              <input
                type="text"
                className="flex-1 p-3 border border-slate-300 dark:border-slate-600 rounded-lg text-sm
                           focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                           bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                           placeholder-slate-400 dark:placeholder-slate-500"
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
          className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
        >
          + Add criterion
        </button>
        <p className="text-xs text-slate-400 dark:text-slate-500">
          Define specific, measurable criteria. At least one required.
        </p>
      </section>

      <section className="border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900">
        <button
          type="button"
          onClick={() => setConfigOpen(!configOpen)}
          className="w-full px-4 py-3 flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800"
        >
          <span>Configuration</span>
          <span className="text-slate-400">{configOpen ? '\u25B2' : '\u25BC'}</span>
        </button>
        {configOpen && (
          <div className="px-4 pb-4 space-y-4 border-t border-slate-100 dark:border-slate-700">
            <div className="pt-4 space-y-1">
              <label className="block text-sm text-slate-600 dark:text-slate-400">Venture Name Override</label>
              <input
                type="text"
                className="w-full p-2 border border-slate-300 dark:border-slate-600 rounded text-sm
                           bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                           focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Auto-detected from documents if empty"
                value={ventureName}
                onChange={(e) => setVentureName(e.target.value)}
              />
            </div>

            <div className="space-y-1">
              <label className="block text-sm text-slate-600 dark:text-slate-400">
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
              <div className="flex justify-between text-xs text-slate-400 dark:text-slate-500">
                <span>1 (safe)</span>
                <span>4 (fast)</span>
              </div>
            </div>

            {researchMode !== 'competitive_table' && researchMode !== 'run_all' && <div className="space-y-3">
              <label className="block text-sm text-slate-600 dark:text-slate-400">Categories to Run</label>
              {Object.entries(categoryPhases).map(([phase, cats]) => (
                <div key={phase}>
                  <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">{phase}</p>
                  <div className="space-y-1">
                    {cats.map((cat) => (
                      <label key={cat.id} className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={selectedCategories.has(cat.id)}
                          onChange={() => toggleCategory(cat.id)}
                          className="accent-blue-600"
                        />
                        <span className="text-slate-400 dark:text-slate-500 font-mono text-xs">{cat.id}</span>
                        {cat.name}
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>}
          </div>
        )}
      </section>

      <div className="flex items-center gap-4">
        <button
          type="submit"
          disabled={!isValid || submitting}
          className="px-8 py-3 bg-blue-600 text-white font-medium rounded-lg
                     hover:bg-blue-700 disabled:bg-slate-300 dark:disabled:bg-slate-700 disabled:cursor-not-allowed
                     transition-colors text-sm"
        >
          {submitting
            ? 'Starting...'
            : researchMode === 'run_all'
              ? 'Run All Chapters'
              : researchMode === 'competitive_table'
                ? 'Build Competitive Table'
                : 'Start Research'}
        </button>
        <span className="text-xs text-slate-400 dark:text-slate-500">
          {researchMode === 'run_all'
            ? (prebuiltTable
                ? 'Estimated: 1-2.5 hours \u00B7 $20-40 \u00B7 CT step skipped'
                : 'Estimated: 2-4 hours \u00B7 $30-55 \u00B7 Runs on server overnight')
            : researchMode === 'competitive_table'
              ? 'Estimated: 15-45 minutes'
              : prebuiltTable
                ? 'Estimated: 30-90 minutes \u00B7 $12-22 \u00B7 CT table pre-loaded'
                : 'Estimated: 30-90 minutes \u00B7 $12-22'}
        </span>
      </div>
    </form>
  );
}
