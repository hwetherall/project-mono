import { useState } from 'react';
import Layout from './components/Layout';
import InputForm from './components/InputForm';
import ProgressPanel from './components/ProgressPanel';
import OutputViewer from './components/OutputViewer';
import useResearchRun from './hooks/useResearchRun';

export default function App() {
  const [view, setView] = useState('input'); // input | running | results
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
    setView('input');
  };

  return (
    <Layout>
      {view === 'input' && (
        <InputForm onSubmit={handleSubmit} />
      )}
      {view === 'running' && (
        <ProgressPanel run={run} onComplete={handleComplete} />
      )}
      {view === 'results' && (
        <OutputViewer run={run} onNewRun={handleNewRun} />
      )}
    </Layout>
  );
}
