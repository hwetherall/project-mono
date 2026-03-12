import { useState, useCallback } from 'react';
import Layout from './components/Layout';
import InputForm from './components/InputForm';
import ProgressPanel from './components/ProgressPanel';
import OutputViewer from './components/OutputViewer';
import RunHistory from './components/RunHistory';
import useResearchRun from './hooks/useResearchRun';

export default function App() {
  // Views: input | running | results | history
  const [view, setView] = useState('input');
  const [historicalRunId, setHistoricalRunId] = useState(null);
  const run = useResearchRun();

  const handleSubmit = async (formData) => {
    await run.startRun(formData);
    setView('running');
  };

  const handleComplete = () => {
    setView('results');
  };

  const handleNewRun = () => {
    run.resetRun();
    setHistoricalRunId(null);
    setView('input');
  };

  const handleNavigate = useCallback((target) => {
    if (target === 'input') {
      handleNewRun();
    } else if (target === 'history') {
      setView('history');
    }
  }, []);

  const handleViewHistoricalRun = useCallback((runId) => {
    setHistoricalRunId(runId);
    setView('results');
  }, []);

  return (
    <Layout onNavigate={handleNavigate} currentView={view}>
      {view === 'input' && (
        <InputForm onSubmit={handleSubmit} />
      )}
      {view === 'running' && (
        <ProgressPanel run={run} onComplete={handleComplete} />
      )}
      {view === 'results' && (
        <OutputViewer
          run={run}
          onNewRun={handleNewRun}
          historicalRunId={historicalRunId}
        />
      )}
      {view === 'history' && (
        <RunHistory
          onViewRun={handleViewHistoricalRun}
          onNewRun={handleNewRun}
        />
      )}
    </Layout>
  );
}
