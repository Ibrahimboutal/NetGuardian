import { useState, useEffect, useRef, useCallback } from "react";
import "./index.css";
import StatusBadge from "./components/StatusBadge";
import MetricChart from "./components/MetricChart";
import AnomalyFeed from "./components/AnomalyFeed";
import AIPanel from "./components/AIPanel";
import {
  Activity, Play, Square, Zap, Wifi, Clock,
  BarChart2, AlertTriangle, Server
} from "lucide-react";

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

  const eventSourceRef = useRef(null);

  // Clock
  useEffect(() => {
    const t = setInterval(() => setClock(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  // Load history on mount
  useEffect(() => {
    fetch(`${API}/api/metrics/history`)
      .then(r => r.json())
      .then(({ data: rows }) => {
        setData(rows.slice(-MAX_DATA_POINTS));
        setStatus("stable");
      })
      .catch(() => setStatus("stable"));
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

        if (event.agents) {
          setLatestIncident(event);
          setThinking(false);
        } else {
          setThinking(true);
        }
      } else {
        setStatus("stable");
      }
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
    } catch (err) {
      console.error("Inject failed:", err);
    } finally {
      setThinking(false);
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
          {/* Anomaly Feed */}
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

          {/* AI Panel */}
          <AIPanel incident={latestIncident} thinking={thinking} />
        </div>
      </main>
    </div>
  );
}
