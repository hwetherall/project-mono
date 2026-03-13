import { useState, useCallback } from 'react';
import Layout from './components/Layout';
import InputForm from './components/InputForm';
import ProgressPanel from './components/ProgressPanel';
import ChainProgressPanel from './components/ChainProgressPanel';
import OutputViewer from './components/OutputViewer';
import RunHistory from './components/RunHistory';
import useResearchRun from './hooks/useResearchRun';
import useChainRun from './hooks/useChainRun';

export default function App() {
  // Views: input | running | chainRunning | results | chainResults | history
  const [view, setView] = useState('input');
  const [historicalRunId, setHistoricalRunId] = useState(null);
  const [historicalChainId, setHistoricalChainId] = useState(null);
  const run = useResearchRun();
  const chain = useChainRun();

  const handleSubmit = async (formData) => {
    if (formData.research_mode === 'run_all') {
      await chain.startChain(formData);
      setView('chainRunning');
    } else {
      await run.startRun(formData);
      setView('running');
    }
  };

  const handleComplete = () => {
    setView('results');
  };

  const handleChainComplete = () => {
    setView('chainResults');
  };

  const handleNewRun = () => {
    run.resetRun();
    chain.resetChain();
    setHistoricalRunId(null);
    setHistoricalChainId(null);
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
    setHistoricalChainId(null);
    setView('results');
  }, []);

  const handleViewHistoricalChain = useCallback((chainId, chainSteps) => {
    setHistoricalChainId({ chainId, steps: chainSteps });
    setHistoricalRunId(null);
    setView('chainResults');
  }, []);

  return (
    <Layout onNavigate={handleNavigate} currentView={view}>
      {view === 'input' && (
        <InputForm onSubmit={handleSubmit} />
      )}
      {view === 'running' && (
        <ProgressPanel run={run} onComplete={handleComplete} />
      )}
      {view === 'chainRunning' && (
        <ChainProgressPanel chain={chain} onComplete={handleChainComplete} />
      )}
      {view === 'results' && (
        <OutputViewer
          run={run}
          onNewRun={handleNewRun}
          historicalRunId={historicalRunId}
        />
      )}
      {view === 'chainResults' && (
        <OutputViewer
          run={run}
          onNewRun={handleNewRun}
          chainSteps={historicalChainId ? historicalChainId.steps : chain.steps}
          chainId={historicalChainId ? historicalChainId.chainId : chain.chainId}
        />
      )}
      {view === 'history' && (
        <RunHistory
          onViewRun={handleViewHistoricalRun}
          onViewChain={handleViewHistoricalChain}
          onNewRun={handleNewRun}
        />
      )}
    </Layout>
  );
}
