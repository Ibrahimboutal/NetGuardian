import { Suspense, lazy, useState, useEffect, useRef, useCallback } from "react";
import "./index.css";
import StatusBadge from "./components/StatusBadge";
import MetricChart from "./components/MetricChart";
import {
  Activity, Play, Square, Zap, Wifi, Clock,
  BarChart2, AlertTriangle, Server
} from "lucide-react";

const AnomalyFeed = lazy(() => import("./components/AnomalyFeed"));
const AIPanel = lazy(() => import("./components/AIPanel"));
const OperationsSummary = lazy(() => import("./components/OperationsSummary"));

const API = "http://127.0.0.1:8000";
const MAX_DATA_POINTS = 120;
const MAX_ANOMALIES = 50;

function StatCard({ icon: Icon, label, value, unit, trend, iconClass, isAnomaly }) {
  return (
    <div className={`stat-card ${isAnomaly ? "anomaly" : ""}`}>
      <div className={`stat-icon ${iconClass}`}>
        <Icon size={16} />
      </div>
      <div>
        <div className="stat-label">{label}</div>
        <div className="stat-value">
          {value ?? "—"}
          {unit && <span className="stat-unit">{unit}</span>}
        </div>
        {trend && (
          <div className={`stat-trend ${trend.dir}`}>{trend.label}</div>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [streaming, setStreaming] = useState(false);
  const [status, setStatus] = useState("connecting");
  const [data, setData] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [latest, setLatest] = useState(null);
  const [latestIncident, setLatestIncident] = useState(null);
  const [thinking, setThinking] = useState(false);
  const [activeMetric, setActiveMetric] = useState("latency_ms");
  const [clock, setClock] = useState(new Date());
  const [injectLoading, setInjectLoading] = useState(false);
  const [systemSummary, setSystemSummary] = useState(null);
  const [incidentInsights, setIncidentInsights] = useState(null);
  const [incidentForecast, setIncidentForecast] = useState(null);
  const [recentIncidents, setRecentIncidents] = useState([]);
  const [benchmark, setBenchmark] = useState(null);
  const [benchmarkLoading, setBenchmarkLoading] = useState(false);
  const [agentProgress, setAgentProgress] = useState([]);

  const eventSourceRef = useRef(null);

  const refreshOperationalData = useCallback(async () => {
    try {
      const [summaryRes, incidentsRes, insightsRes, forecastRes] = await Promise.all([
        fetch(`${API}/api/system/summary`),
        fetch(`${API}/api/incidents/recent?limit=5`),
        fetch(`${API}/api/incidents/insights`),
        fetch(`${API}/api/incidents/forecast`),
      ]);
      const summaryJson = await summaryRes.json();
      const incidentsJson = await incidentsRes.json();
      const insightsJson = await insightsRes.json();
      const forecastJson = await forecastRes.json();
      setSystemSummary(summaryJson);
      setRecentIncidents(Array.isArray(incidentsJson?.data) ? incidentsJson.data : []);
      setIncidentInsights(insightsJson);
      setIncidentForecast(forecastJson);
    } catch (err) {
      console.error("Refresh operational data failed:", err);
    }
  }, []);

  const runBenchmark = useCallback(async () => {
    setBenchmarkLoading(true);
    try {
      const res = await fetch(`${API}/api/evaluation/benchmark?refresh=true`);
      const json = await res.json();
      setBenchmark(json);
    } catch (err) {
      console.error("Benchmark failed:", err);
    } finally {
      setBenchmarkLoading(false);
    }
  }, []);

  const downloadReport = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/incidents/export`);
      const json = await res.json();
      const blob = new Blob([JSON.stringify(json, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `netguardian-report-${new Date().toISOString().replace(/[:.]/g, "-")}.json`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download report failed:", err);
    }
  }, []);

  // Clock
  useEffect(() => {
    const t = setInterval(() => setClock(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  // Load history on mount
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [historyRes, summaryRes, incidentsRes, insightsRes, forecastRes] = await Promise.all([
          fetch(`${API}/api/metrics/history`),
          fetch(`${API}/api/system/summary`),
          fetch(`${API}/api/incidents/recent?limit=5`),
          fetch(`${API}/api/incidents/insights`),
          fetch(`${API}/api/incidents/forecast`),
        ]);

        const historyJson = await historyRes.json();
        const summaryJson = await summaryRes.json();
        const incidentsJson = await incidentsRes.json();
        const insightsJson = await insightsRes.json();
        const forecastJson = await forecastRes.json();

        setData(historyJson.data.slice(-MAX_DATA_POINTS));
        setSystemSummary(summaryJson);
        setRecentIncidents(Array.isArray(incidentsJson?.data) ? incidentsJson.data : []);
        setIncidentInsights(insightsJson);
        setIncidentForecast(forecastJson);
        setStatus("stable");
      } catch {
        setStatus("stable");
      }
    };

    loadInitialData();
  }, []);

  // SSE stream
  const startStream = useCallback(() => {
    if (eventSourceRef.current) return;
    const es = new EventSource(`${API}/api/stream?speed=1`);
    eventSourceRef.current = es;
    setStreaming(true);

    es.addEventListener("metric", e => {
      const event = JSON.parse(e.data);
      setLatest(event);

      setData(prev => {
        const next = [...prev, event];
        return next.length > MAX_DATA_POINTS ? next.slice(-MAX_DATA_POINTS) : next;
      });

      if (event.anomaly) {
        setStatus("anomaly");
        setAnomalies(prev => {
          const next = [...prev, event];
          return next.length > MAX_ANOMALIES ? next.slice(-MAX_ANOMALIES) : next;
        });
        setRecentIncidents(prev => {
          const next = [event, ...prev];
          return next.slice(0, 5);
        });

        if (event.agents) {
          setLatestIncident(event);
          setThinking(false);
        } else {
          setThinking(true);
        }

        setAgentProgress([]);
        refreshOperationalData().catch(() => {});
      } else {
        setStatus("stable");
      }
    });

    es.addEventListener("agent_status", e => {
      const payload = JSON.parse(e.data);
      if (payload?.message) {
        setAgentProgress(prev => {
          const next = [...prev, payload.message];
          return next.length > 4 ? next.slice(-4) : next;
        });
      }
      setThinking(true);
    });

    es.onerror = () => {
      es.close();
      eventSourceRef.current = null;
      setStreaming(false);
      setStatus("stable");
    };
  }, []);

  const stopStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    fetch(`${API}/api/stream/stop`, { method: "POST" }).catch(() => {});
    setStreaming(false);
    setStatus("stable");
    setThinking(false);
    setAgentProgress([]);
  }, []);

  const injectAnomaly = useCallback(async () => {
    setInjectLoading(true);
    setThinking(true);
    setStatus("anomaly");
    try {
      const res = await fetch(`${API}/api/inject-anomaly`, { method: "POST" });
      const event = await res.json();
      setLatestIncident(event);
      setAnomalies(prev => [...prev, event].slice(-MAX_ANOMALIES));
      setData(prev => [...prev, event].slice(-MAX_DATA_POINTS));
      setLatest(event);
      setRecentIncidents(prev => [event, ...prev].slice(0, 5));
      refreshOperationalData().catch(() => {});
    } catch (err) {
      console.error("Inject failed:", err);
    } finally {
      setThinking(false);
      setAgentProgress([]);
      setInjectLoading(false);
    }
  }, []);

  const lat = latest?.latency_ms?.toFixed(0) ?? "—";
  const thr = latest?.throughput_mbps?.toFixed(0) ?? "—";
  const loss = latest?.packet_loss_pct?.toFixed(1) ?? "—";
  const jit = latest?.jitter_ms?.toFixed(0) ?? "—";

  return (
    <div className="app">
      {/* ─── Header ─── */}
      <header className="header">
        <div className="header-logo">
          <div className="header-logo-icon">🛡</div>
          <div>
            <div className="header-title">NetGuardian</div>
            <div className="header-subtitle">Offline AI Network Incident Response</div>
          </div>
        </div>

        <div className="header-right">
          <div className="header-time">
            {clock.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
          </div>
          <StatusBadge status={status} anomalyCount={anomalies.length} />
        </div>
      </header>

      {/* ─── Main ─── */}
      <main className="main">

        {/* Stats Bar */}
        <div className="stats-bar">
          <StatCard icon={Clock}        label="Latency"     value={lat}  unit="ms"   iconClass="blue"   isAnomaly={latest?.latency_ms > 100} />
          <StatCard icon={Wifi}         label="Throughput"  value={thr}  unit="Mbps" iconClass="cyan"   isAnomaly={latest?.throughput_mbps < 300} />
          <StatCard icon={Activity}     label="Packet Loss" value={loss} unit="%"    iconClass="red"    isAnomaly={latest?.packet_loss_pct > 5} />
          <StatCard icon={BarChart2}    label="Jitter"      value={jit}  unit="ms"   iconClass="orange" isAnomaly={latest?.jitter_ms > 20} />
          <StatCard icon={AlertTriangle} label="Anomalies"  value={anomalies.length} unit="" iconClass="red" isAnomaly={anomalies.length > 0} />
        </div>

        {/* Chart Panel */}
        <div className="chart-panel">
          <div className="panel-header">
            <div className="panel-title">
              <Activity size={14} color="#06b6d4" />
              Real-Time Network Metrics
              {streaming && (
                <span style={{ marginLeft: 8, fontSize: 10, color: "#10b981", fontWeight: 400 }}>
                  ● LIVE
                </span>
              )}
            </div>
            <div className="panel-actions">
              {!streaming ? (
                <button id="btn-start-stream" className="btn btn-primary" onClick={startStream}>
                  <Play size={12} /> Start Stream
                </button>
              ) : (
                <button id="btn-stop-stream" className="btn btn-ghost" onClick={stopStream}>
                  <Square size={12} /> Stop
                </button>
              )}
              <button
                id="btn-inject-anomaly"
                className="btn btn-danger"
                onClick={injectAnomaly}
                disabled={injectLoading}
              >
                <Zap size={12} />
                {injectLoading ? "Injecting…" : "Inject Anomaly"}
              </button>
            </div>
          </div>

          <MetricChart
            data={data}
            activeMetric={activeMetric}
            onMetricChange={setActiveMetric}
          />
        </div>

        {/* Right Column */}
        <div className="right-panel">
          <Suspense fallback={<div className="feed-panel" style={{ minHeight: 260, display: "flex", alignItems: "center", justifyContent: "center", color: "#94a3b8" }}>Loading operations snapshot…</div>}>
            <OperationsSummary
              summary={systemSummary}
              insights={incidentInsights}
              forecast={incidentForecast}
              recentIncidents={recentIncidents}
              benchmark={benchmark}
              benchmarkLoading={benchmarkLoading}
              onRefresh={refreshOperationalData}
              onRunBenchmark={runBenchmark}
              onDownloadReport={downloadReport}
            />
          </Suspense>

          {/* Anomaly Feed */}
          <Suspense fallback={<div className="feed-panel" style={{ minHeight: 180, display: "flex", alignItems: "center", justifyContent: "center", color: "#94a3b8" }}>Loading anomaly feed…</div>}>
            <div className="feed-panel">
              <div className="panel-header">
                <div className="panel-title">
                  <AlertTriangle size={14} color="#ef4444" />
                  Anomaly Feed
                </div>
                {anomalies.length > 0 && (
                  <span className="anomaly-count-badge">{anomalies.length}</span>
                )}
              </div>
              <AnomalyFeed events={anomalies} />
            </div>
          </Suspense>

          {/* AI Panel */}
          <Suspense fallback={<div className="ai-panel" style={{ minHeight: 320, display: "flex", alignItems: "center", justifyContent: "center", color: "#94a3b8" }}>Loading reasoning panel…</div>}>
            <AIPanel incident={latestIncident} thinking={thinking} progressMessages={agentProgress} />
          </Suspense>
        </div>
      </main>
    </div>
  );
}
