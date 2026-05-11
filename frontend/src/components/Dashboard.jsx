import React, { Suspense, lazy, useState, useEffect, useRef } from "react";
import StatusBadge from "./StatusBadge";
import {
  Activity, Play, Square, Zap, Wifi, Clock,
  BarChart2, AlertTriangle
} from "lucide-react";

const AnomalyFeed = lazy(() => import("./AnomalyFeed"));
const AIPanel = lazy(() => import("./AIPanel"));
const OperationsSummary = lazy(() => import("./OperationsSummary"));
const MetricChart = lazy(() => import("./MetricChart"));
const NodeTopologyMap = lazy(() => import("./NodeTopologyMap"));
const HeatmapTimeline = lazy(() => import("./HeatmapTimeline"));
const IncidentKanban = lazy(() => import("./IncidentKanban"));
const InjectModal = lazy(() => import("./InjectModal"));

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const API_TOKEN = import.meta.env.VITE_API_TOKEN || "";
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

export default function Dashboard() {
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
  const [showInjectModal, setShowInjectModal] = useState(false);
  const [view, setView] = useState("dashboard"); // "dashboard" or "kanban"
  const [systemSummary, setSystemSummary] = useState(null);
  const [incidentInsights, setIncidentInsights] = useState(null);
  const [incidentForecast, setIncidentForecast] = useState(null);
  const [recentIncidents, setRecentIncidents] = useState([]);
  const [benchmark, setBenchmark] = useState(null);
  const [benchmarkLoading, setBenchmarkLoading] = useState(false);
  const [agentProgress, setAgentProgress] = useState([]);
  const [errorMsg, setErrorMsg] = useState("");
  const [whatIfLoading, setWhatIfLoading] = useState(false);
  const reconnectTimerRef = useRef(null);
  const audioCtxRef = useRef(null);

  const eventSourceRef = useRef(null);

  const playAlert = useCallback((severity) => {
    try {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)();
      }
      const ctx = audioCtxRef.current;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      
      osc.type = severity === "critical" ? "sawtooth" : "sine";
      osc.frequency.setValueAtTime(severity === "critical" ? 180 : 440, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(severity === "critical" ? 40 : 220, ctx.currentTime + 0.5);
      
      gain.gain.setValueAtTime(0.1, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
      
      osc.connect(gain);
      gain.connect(ctx.destination);
      
      osc.start();
      osc.stop(ctx.currentTime + 0.5);
    } catch (e) {
      console.warn("Audio alert failed:", e);
    }
  }, []);

  const refreshOperationalData = async () => {
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
      setErrorMsg("");
    } catch (err) {
      console.error("Refresh operational data failed:", err);
      setErrorMsg("Failed to refresh operational data");
    }
  };

  const runBenchmark = async () => {
    setBenchmarkLoading(true);
    try {
      const res = await fetch(`${API}/api/evaluation/benchmark?refresh=true`);
      const json = await res.json();
      setBenchmark(json);
      setErrorMsg("");
    } catch (err) {
      console.error("Benchmark failed:", err);
      setErrorMsg("Benchmark request failed");
    } finally {
      setBenchmarkLoading(false);
    }
  };

  const downloadReport = async () => {
    try {
      const headers = API_TOKEN ? { "X-API-Key": API_TOKEN } : {};
      const res = await fetch(`${API}/api/incidents/export`, { headers });
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
      setErrorMsg("");
    } catch (err) {
      console.error("Download report failed:", err);
      setErrorMsg("Report export failed (API key may be required)");
    }
  };

  useEffect(() => {
    const t = setInterval(() => setClock(new Date()), 1000);
    return () => {
      clearInterval(t);
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
    };
  }, []);

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
        setErrorMsg("");
      } catch {
        setStatus("connecting");
        setErrorMsg("Initial load failed. Check backend availability.");
      }
    };

    loadInitialData();
  }, []);

  const startStream = () => {
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

        if (event.severity === "critical" || event.severity === "high") {
          playAlert(event.severity);
        }

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
      setErrorMsg("");
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
      setStatus("connecting");
      setErrorMsg("Stream disconnected. Retrying in 3s…");
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = setTimeout(() => {
        if (!eventSourceRef.current) startStream();
      }, 3000);
    };
  };

  const stopStream = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    fetch(`${API}/api/stream/stop`, { method: "POST" }).catch(() => {});
    setStreaming(false);
    setStatus("stable");
    setThinking(false);
    setAgentProgress([]);
    if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
  };

  const injectAnomaly = async () => {
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
      setErrorMsg("Anomaly injection failed");
    } finally {
      setThinking(false);
      setAgentProgress([]);
      setInjectLoading(false);
    }
  };

  const handleWhatIf = async (nodeId) => {
    if (whatIfLoading) return;
    setWhatIfLoading(true);
    setErrorMsg("");
    try {
      const res = await fetch(`${API}/api/simulate/what-if`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node_id: nodeId, magnitude: 180 })
      });
      const result = await res.json();
      
      // We'll wrap the simulation in a "pseudo-incident" to show it in the AI panel
      const pseudoIncident = {
        node_id: nodeId,
        anomaly: true,
        severity: "simulated",
        score: 0.0,
        simulation: result.prediction,
        agents: {
          explanation: { summary: `WHAT-IF SIMULATION: A failure on ${nodeId} was modeled. Impact score: ${result.prediction.impact_score}. Affected nodes: ${result.prediction.affected_nodes_count}.` },
          diagnosis: { reasoning_trace: "Manual sandbox trigger: Causal propagation analysis complete." }
        },
        attribution: ["manual_simulation"]
      };
      setLatestIncident(pseudoIncident);
    } catch (err) {
      console.error("What-if failed:", err);
      setErrorMsg("What-if simulation failed");
    } finally {
      setWhatIfLoading(false);
    }
  };

  const lat = latest?.latency_ms?.toFixed(0) ?? "—";
  const thr = latest?.throughput_mbps?.toFixed(0) ?? "—";
  const loss = latest?.packet_loss_pct?.toFixed(1) ?? "—";
  const jit = latest?.jitter_ms?.toFixed(0) ?? "—";

  return (
    <div className="app">
      <header className="header">
        <div className="header-logo">
          <div className="header-logo-icon">🛡</div>
          <div>
            <div className="header-title">NetGuardian</div>
            <div className="header-subtitle">Offline AI Network Incident Response</div>
          </div>
        </div>

        <div className="header-right">
          <nav style={{ display: "flex", gap: 12, marginRight: 24 }}>
            <button 
              className={`btn ${view === 'dashboard' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setView('dashboard')}
              style={{ fontSize: 11, padding: "4px 10px" }}
            >
              Dashboard
            </button>
            <button 
              className={`btn ${view === 'kanban' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setView('kanban')}
              style={{ fontSize: 11, padding: "4px 10px" }}
            >
              Incident Kanban
            </button>
          </nav>
          <div className="header-time">
            {clock.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
          </div>
          <StatusBadge status={status} anomalyCount={anomalies.length} />
        </div>
      </header>

      <main className="main">
        {view === "dashboard" ? (
          <>
            {/* ── Stats row ── */}
            <div className="stats-area stats-bar">
              <StatCard icon={Clock} label="Latency" value={lat} unit="ms" iconClass="blue" isAnomaly={latest?.latency_ms > 100} />
              <StatCard icon={Wifi} label="Throughput" value={thr} unit="Mbps" iconClass="cyan" isAnomaly={latest?.throughput_mbps < 300} />
              <StatCard icon={Activity} label="Packet Loss" value={loss} unit="%" iconClass="red" isAnomaly={latest?.packet_loss_pct > 5} />
              <StatCard icon={BarChart2} label="Jitter" value={jit} unit="ms" iconClass="orange" isAnomaly={latest?.jitter_ms > 20} />
              <StatCard icon={AlertTriangle} label="Anomalies" value={anomalies.length} unit="" iconClass="red" isAnomaly={anomalies.length > 0} />
            </div>

            {/* ── Topology row ── */}
            <div className="topo-area" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <Suspense fallback={<div style={{ height: 160, display: "flex", alignItems: "center", justifyContent: "center", color: "#94a3b8" }}>Loading topology…</div>}>
                <NodeTopologyMap 
                  anomalies={anomalies} 
                  activeIncident={latestIncident} 
                  onWhatIf={handleWhatIf}
                  whatIfLoading={whatIfLoading}
                />
              </Suspense>
              <Suspense fallback={<div style={{ height: 100, display: "flex", alignItems: "center", justifyContent: "center", color: "#94a3b8" }}>Loading heatmap…</div>}>
                <HeatmapTimeline anomalies={anomalies} />
              </Suspense>
            </div>

            {/* ── Chart column ── */}
            <div className="chart-area chart-panel">
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
                    onClick={() => setShowInjectModal(true)}
                  >
                    <Zap size={12} />
                    Inject Custom
                  </button>
                </div>
              </div>
              {errorMsg && (
                <div style={{ marginBottom: 10, color: "#fca5a5", fontSize: 12 }}>
                  {errorMsg}
                </div>
              )}

              <Suspense fallback={<div style={{ minHeight: 360, display: "flex", alignItems: "center", justifyContent: "center", color: "#94a3b8" }}>Loading chart…</div>}>
                <MetricChart data={data} activeMetric={activeMetric} onMetricChange={setActiveMetric} />
              </Suspense>
            </div>

            {/* ── Right column ── */}
            <div className="right-area right-panel">
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

              <Suspense fallback={<div className="ai-panel" style={{ minHeight: 320, display: "flex", alignItems: "center", justifyContent: "center", color: "#94a3b8" }}>Loading reasoning panel…</div>}>
                <AIPanel incident={latestIncident} thinking={thinking} progressMessages={agentProgress} benchmark={benchmark} />
              </Suspense>
            </div>
          </>
        ) : (
          <div style={{ gridArea: "1 / 1 / -1 / -1", minHeight: "calc(100vh - 100px)" }}>
             <Suspense fallback={<div>Loading board…</div>}>
                <IncidentKanban />
             </Suspense>
          </div>
        )}
      </main>

      {showInjectModal && (
        <Suspense fallback={null}>
          <InjectModal 
            onClose={() => setShowInjectModal(false)} 
            onInjected={(event) => {
              setLatest(event);
              setLatestIncident(event);
              setData(prev => [...prev, event].slice(-MAX_DATA_POINTS));
              setAnomalies(prev => [...prev, event].slice(-MAX_ANOMALIES));
              setRecentIncidents(prev => [event, ...prev].slice(0, 5));
              if (event.severity === "critical" || event.severity === "high") playAlert(event.severity);
              refreshOperationalData().catch(() => {});
            }} 
          />
        </Suspense>
      )}
    </div>
  );
}
