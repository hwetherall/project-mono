import { useState, useRef, useCallback, useEffect } from 'react';

const PHASE_NAMES = {
  FOUNDATION: 'Phase 1: Foundation',
  COMPETITOR_DEPENDENT: 'Phase 2: Competitor-Dependent',
  SYNTHESIS: 'Phase 3: Synthesis',
  STRUCTURAL: 'Phase 2: Structural',
  COMMERCIAL: 'Phase 3: Commercial',
};

export default function useResearchRun() {
  const [runId, setRunId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle | starting | running | complete | error
  const [phases, setPhases] = useState([]);
  const [categories, setCategories] = useState({});
  const [events, setEvents] = useState([]);
  const [activityLog, setActivityLog] = useState([]);
  const [contextInfo, setContextInfo] = useState(null);
  const [competitorList, setCompetitorList] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const startTimeRef = useRef(null);
  const statusRef = useRef('idle');
  const errorRef = useRef(null);

  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  useEffect(() => {
    errorRef.current = error;
  }, [error]);

  const addLogEntry = useCallback((level, message) => {
    setActivityLog((prev) => {
      const next = [...prev, {
        timestamp: Date.now(),
        level,
        message,
      }];
      return next.length > 500 ? next.slice(-500) : next;
    });
  }, []);

  const syncRunStatus = useCallback(async (targetRunId, options = {}) => {
    if (!targetRunId) return { resolved: false };

    try {
      const res = await fetch(`/api/research/${targetRunId}/status`);

      if (!res.ok) {
        if (res.status === 404 && options.failIfMissing && ['starting', 'running'].includes(statusRef.current)) {
          const message = 'The backend restarted and lost the active run. Please start the research again.';
          setStatus('error');
          setError(message);
          if (errorRef.current !== message) {
            addLogEntry('error', message);
          }
          return { resolved: true, status: 'error' };
        }

        return { resolved: false };
      }

      const data = await res.json();

      if (data.categories) {
        setCategories((prev) => {
          const next = { ...prev };
          Object.entries(data.categories).forEach(([categoryId, category]) => {
            next[categoryId] = {
              ...prev[categoryId],
              ...category,
              category_id: category.category_id || categoryId,
            };
          });
          return next;
        });
      }

      if (data.status === 'completed') {
        const categoryList = Object.values(data.categories || {});
        const succeeded = categoryList.filter((category) => category.status === 'success').length;
        const failed = categoryList.filter((category) => category.status === 'failed').length;

        setStatus('complete');
        setResult({
          elapsed_seconds: data.elapsed_seconds,
          succeeded,
          failed,
        });
        setError(null);
        return { resolved: true, status: 'complete' };
      }

      if (data.status === 'failed') {
        const message = data.error || 'Research run failed.';
        setStatus('error');
        setError(message);
        if (errorRef.current !== message) {
          addLogEntry('error', `Run failed: ${message}`);
        }
        return { resolved: true, status: 'error' };
      }

      return { resolved: data.status === 'running', status: data.status };
    } catch {
      return { resolved: false };
    }
  }, [addLogEntry]);

  const handleMessage = useCallback((event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'ping') return;

    setEvents((prev) => [...prev, data]);

    switch (data.type) {
      case 'context_ready':
        setContextInfo(data);
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

      case 'category_end': {
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
      }

      case 'phase_end':
        setPhases((prev) =>
          prev.map((p) => (p.name === data.phase ? { ...p, status: 'complete' } : p))
        );
        addLogEntry('success', `${PHASE_NAMES[data.phase] || data.phase} complete`);
        break;

      case 'competitor_list':
        setCompetitorList(data.competitors || []);
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
        addLogEntry('warning', `${data.category_id} rate limited — waiting ${data.wait_seconds}s (${data.attempt}/${data.max_attempts})`);
        break;

      case 'run_complete':
        setStatus('complete');
        setResult(data);
        addLogEntry('success', `Run complete — ${data.succeeded} succeeded, ${data.failed} failed (${data.elapsed_seconds?.toFixed(1)}s)`);
        break;

      case 'run_error':
        setStatus('error');
        setError(data.error);
        addLogEntry('error', `Run failed: ${data.error}`);
        break;

      case 'log_detail':
        addLogEntry(data.level || 'info', data.message);
        break;

      case 'log':
        addLogEntry('info', data.message);
        break;
    }
  }, [addLogEntry]);

  const startRun = useCallback(async (formData) => {
    setStatus('starting');
    setError(null);
    setPhases([]);
    setCategories({});
    setEvents([]);
    setActivityLog([]);
    setContextInfo(null);
    setCompetitorList([]);
    setResult(null);
    startTimeRef.current = Date.now();

    addLogEntry('info', 'Initializing research pipeline...');

    try {
      const res = await fetch('/api/research/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to start research');
      }

      const data = await res.json();
      setRunId(data.run_id);
      setStatus('running');

      // Connect WebSocket
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/${data.run_id}`;
      const ws = new WebSocket(wsUrl);
      ws.onmessage = handleMessage;
      ws.onerror = () => {
        if (statusRef.current === 'running') {
          addLogEntry('warning', 'Live connection interrupted. Checking run status...');
        }
      };
      ws.onclose = async () => {
        wsRef.current = null;

        if (!['starting', 'running'].includes(statusRef.current)) {
          return;
        }

        addLogEntry('warning', 'Live connection closed. Checking run status...');
        const outcome = await syncRunStatus(data.run_id, { failIfMissing: true });

        if (!outcome.resolved && ['starting', 'running'].includes(statusRef.current)) {
          const message = 'Connection to the backend was lost while the run was still in progress.';
          setStatus('error');
          setError(message);
          addLogEntry('error', message);
        }
      };
      wsRef.current = ws;
    } catch (err) {
      setStatus('error');
      setError(err.message);
    }
  }, [handleMessage, addLogEntry, syncRunStatus]);

  useEffect(() => {
    if (!runId || status !== 'running') return undefined;

    const interval = setInterval(() => {
      const socketReadyState = wsRef.current?.readyState;
      if (socketReadyState !== WebSocket.OPEN) {
        void syncRunStatus(runId, { failIfMissing: true });
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [runId, status, syncRunStatus]);

  const retryCategory = useCallback(async (categoryId) => {
    if (!runId) return;
    try {
      const res = await fetch(`/api/research/${runId}/retry/${categoryId}`, {
        method: 'POST',
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Retry failed');
      }
      setCategories((prev) => ({
        ...prev,
        [categoryId]: { ...prev[categoryId], status: 'running', error: null },
      }));
    } catch (err) {
      console.error('Retry failed:', err);
    }
  }, [runId]);

  const resetRun = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setRunId(null);
    setStatus('idle');
    setPhases([]);
    setCategories({});
    setEvents([]);
    setActivityLog([]);
    setContextInfo(null);
    setCompetitorList([]);
    setResult(null);
    setError(null);
    startTimeRef.current = null;
  }, []);

  return {
    runId,
    status,
    phases,
    categories,
    events,
    activityLog,
    contextInfo,
    competitorList,
    result,
    error,
    startTime: startTimeRef.current,
    startRun,
    retryCategory,
    resetRun,
  };
}
