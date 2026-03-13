import { useState, useRef, useCallback, useEffect } from 'react';

const MODE_LABELS = {
  competitive_table: 'Competitive Table',
  market_research: 'Market Research',
  demand_validation: 'Demand Validation',
};

const PHASE_NAMES = {
  FOUNDATION: 'Phase 1: Foundation',
  COMPETITOR_DEPENDENT: 'Phase 2: Competitor-Dependent',
  SYNTHESIS: 'Phase 3: Synthesis',
  STRUCTURAL: 'Phase 2: Structural',
  COMMERCIAL: 'Phase 3: Commercial',
};

export default function useChainRun() {
  const [chainId, setChainId] = useState(null);
  const [status, setStatus] = useState('idle');
  const [steps, setSteps] = useState([]);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [phases, setPhases] = useState([]);
  const [categories, setCategories] = useState({});
  const [activityLog, setActivityLog] = useState([]);
  const [contextInfo, setContextInfo] = useState(null);
  const [competitorList, setCompetitorList] = useState([]);
  const [competitiveTableStatus, setCompetitiveTableStatus] = useState(null);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const startTimeRef = useRef(null);
  const statusRef = useRef('idle');

  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  const addLogEntry = useCallback((level, message) => {
    setActivityLog((prev) => {
      const next = [...prev, { timestamp: Date.now(), level, message }];
      return next.length > 800 ? next.slice(-800) : next;
    });
  }, []);

  const handleMessage = useCallback((event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'ping') return;

    switch (data.type) {
      case 'context_ready':
        setContextInfo(data);
        break;

      case 'chain_step_start':
        setCurrentStepIndex(data.step_index);
        setSteps((prev) =>
          prev.map((s, i) =>
            i === data.step_index ? { ...s, run_id: data.run_id, status: 'running' } : s
          )
        );
        // Reset per-step state
        setPhases([]);
        setCategories({});
        setCompetitorList([]);
        setCompetitiveTableStatus(null);
        addLogEntry('info', `Starting chapter ${data.step_index + 1}/${data.total_steps}: ${data.mode_label}`);
        break;

      case 'chain_step_complete':
        setSteps((prev) =>
          prev.map((s, i) =>
            i === data.step_index
              ? { ...s, status: data.status, succeeded: data.succeeded, failed: data.failed, error: data.error }
              : s
          )
        );
        if (data.status === 'completed') {
          addLogEntry('success', `${data.mode_label} completed`);
        } else {
          addLogEntry('error', `${data.mode_label} failed: ${data.error || 'unknown'}`);
        }
        break;

      case 'chain_complete':
        setStatus('complete');
        addLogEntry('success', `All chapters complete (${data.elapsed_seconds?.toFixed(1)}s total)`);
        break;

      case 'phase_start':
        setPhases((prev) => [...prev, { name: data.phase, categories: data.categories, status: 'running' }]);
        data.categories.forEach((cid) => {
          setCategories((prev) => ({
            ...prev,
            [cid]: { ...prev[cid], category_id: cid, status: prev[cid]?.status || 'pending' },
          }));
        });
        addLogEntry('info', `Starting ${PHASE_NAMES[data.phase] || data.phase}`);
        break;

      case 'category_start':
        setCategories((prev) => ({
          ...prev,
          [data.category_id]: {
            ...prev[data.category_id],
            category_id: data.category_id,
            category_name: data.category_name,
            status: 'running',
            startedAt: Date.now(),
          },
        }));
        addLogEntry('start', `${data.category_id} ${data.category_name} started`);
        break;

      case 'category_end':
        setCategories((prev) => ({
          ...prev,
          [data.category_id]: {
            ...prev[data.category_id],
            category_id: data.category_id,
            status: data.status,
            elapsed_seconds: data.elapsed_seconds,
            source_count: data.source_count || 0,
            gap_count: data.gap_count || 0,
            error: data.error || null,
          },
        }));
        if (data.status === 'success') {
          addLogEntry('success', `${data.category_id} completed (${data.elapsed_seconds?.toFixed(1)}s, ${data.source_count || 0} sources)`);
        } else {
          addLogEntry('error', `${data.category_id} failed: ${data.error || 'unknown error'}`);
        }
        break;

      case 'phase_end':
        setPhases((prev) =>
          prev.map((p) => (p.name === data.phase ? { ...p, status: 'complete' } : p))
        );
        addLogEntry('success', `${PHASE_NAMES[data.phase] || data.phase} complete`);
        break;

      case 'competitor_list':
        setCompetitorList(data.competitors || []);
        break;

      case 'competitive_table_status':
        setCompetitiveTableStatus(data);
        if (data.status === 'complete') {
          addLogEntry('success', `Competitive table complete: ${data.competitors} competitors, ${data.attributes} attributes`);
        }
        break;

      case 'rate_limit':
        setCategories((prev) => ({
          ...prev,
          [data.category_id]: {
            ...prev[data.category_id],
            rateLimitInfo: {
              attempt: data.attempt,
              max_attempts: data.max_attempts,
              wait_seconds: data.wait_seconds,
            },
          },
        }));
        addLogEntry('warning', `${data.category_id} rate limited — waiting ${data.wait_seconds}s`);
        break;

      case 'run_error':
        setStatus('error');
        setError(data.error);
        addLogEntry('error', `Chain failed: ${data.error}`);
        break;

      case 'log_detail':
        addLogEntry(data.level || 'info', data.message);
        break;

      case 'log':
        addLogEntry('info', data.message);
        break;

      case 'terminal_line':
        setActivityLog((prev) => {
          if (prev.length > 0 && prev[prev.length - 1].message === data.message) return prev;
          const next = [...prev, { timestamp: Date.now(), level: data.level || 'info', message: data.message, source: 'terminal' }];
          return next.length > 800 ? next.slice(-800) : next;
        });
        break;
    }
  }, [addLogEntry]);

  const startChain = useCallback(async (formData) => {
    setStatus('starting');
    setError(null);
    setSteps([]);
    setCurrentStepIndex(0);
    setPhases([]);
    setCategories({});
    setActivityLog([]);
    setContextInfo(null);
    setCompetitorList([]);
    setCompetitiveTableStatus(null);
    startTimeRef.current = Date.now();

    const hasPrebuiltTable = !!formData.prebuilt_competitive_table;
    addLogEntry('info', hasPrebuiltTable
      ? 'Initializing chain pipeline (MR → DV, CT pre-loaded)...'
      : 'Initializing chain pipeline (CT → MR → DV)...'
    );

    try {
      const payload = {
        document_text: formData.document_text,
        additional_context: formData.additional_context,
        core_question: formData.core_question,
        success_criteria: formData.success_criteria,
        venture_name: formData.venture_name,
        max_concurrent: formData.max_concurrent,
      };
      if (hasPrebuiltTable) {
        payload.prebuilt_competitive_table = formData.prebuilt_competitive_table;
      }

      const res = await fetch('/api/research/chain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to start chain');
      }

      const data = await res.json();
      setChainId(data.chain_id);
      setSteps(data.steps);
      setStatus('running');

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/chain/${data.chain_id}`;
      const ws = new WebSocket(wsUrl);
      ws.onmessage = handleMessage;
      ws.onerror = () => {
        if (statusRef.current === 'running') {
          addLogEntry('warning', 'Live connection interrupted.');
        }
      };
      ws.onclose = () => {
        wsRef.current = null;
        if (['starting', 'running'].includes(statusRef.current)) {
          addLogEntry('warning', 'Live connection closed. Chain continues on server...');
        }
      };
      wsRef.current = ws;
    } catch (err) {
      setStatus('error');
      setError(err.message);
    }
  }, [handleMessage, addLogEntry]);

  const resetChain = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setChainId(null);
    setStatus('idle');
    setSteps([]);
    setCurrentStepIndex(0);
    setPhases([]);
    setCategories({});
    setActivityLog([]);
    setContextInfo(null);
    setCompetitorList([]);
    setCompetitiveTableStatus(null);
    setError(null);
    startTimeRef.current = null;
  }, []);

  return {
    chainId,
    status,
    steps,
    currentStepIndex,
    phases,
    categories,
    activityLog,
    contextInfo,
    competitorList,
    competitiveTableStatus,
    error,
    startTime: startTimeRef.current,
    startChain,
    resetChain,
  };
}
