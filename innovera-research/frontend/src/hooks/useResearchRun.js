import { useState, useRef, useCallback } from 'react';

export default function useResearchRun() {
  const [runId, setRunId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle | starting | running | complete | error
  const [phases, setPhases] = useState([]);
  const [categories, setCategories] = useState({});
  const [events, setEvents] = useState([]);
  const [contextInfo, setContextInfo] = useState(null);
  const [competitorList, setCompetitorList] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const startTimeRef = useRef(null);

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
        break;

      case 'phase_end':
        setPhases((prev) =>
          prev.map((p) => (p.name === data.phase ? { ...p, status: 'complete' } : p))
        );
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
        break;

      case 'run_complete':
        setStatus('complete');
        setResult(data);
        break;

      case 'run_error':
        setStatus('error');
        setError(data.error);
        break;

      case 'log':
        // Already added to events
        break;
    }
  }, []);

  const startRun = useCallback(async (formData) => {
    setStatus('starting');
    setError(null);
    startTimeRef.current = Date.now();

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
      ws.onerror = () => setError('WebSocket connection error');
      ws.onclose = () => {};
      wsRef.current = ws;
    } catch (err) {
      setStatus('error');
      setError(err.message);
    }
  }, [handleMessage]);

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
