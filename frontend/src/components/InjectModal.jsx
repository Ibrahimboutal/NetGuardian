import { useState } from "react";
import { Zap, X, AlertTriangle } from "lucide-react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const ALL_NODES = [
  "Core-DC-01", "Core-DC-02",
  "Router-Edge-01", "Router-Edge-02", "Router-Edge-03", "Router-Edge-04",
  "Router-01", "Router-02", "Router-03", "Router-04", "Router-14",
  "Leaf-01", "Leaf-02", "Leaf-03", "Leaf-04",
];

const METRICS = ["latency_ms", "packet_loss_pct", "jitter_ms", "throughput_mbps", "connections"];

const PRESETS = {
  mild:     { latency_ms: 110, packet_loss_pct: 3,  jitter_ms: 22, throughput_mbps: 280, connections: 400 },
  high:     { latency_ms: 260, packet_loss_pct: 12, jitter_ms: 48, throughput_mbps: 160, connections: 750 },
  critical: { latency_ms: 390, packet_loss_pct: 24, jitter_ms: 68, throughput_mbps: 60,  connections: 980 },
};

export default function InjectModal({ onClose, onInjected }) {
  const [node, setNode] = useState("Core-DC-01");
  const [severity, setSeverity] = useState("high");
  const [metric, setMetric] = useState("latency_ms");
  const [values, setValues] = useState({ ...PRESETS.high });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const applyPreset = (level) => {
    setSeverity(level);
    setValues({ ...PRESETS[level] || PRESETS.high });
  };

  const handleInject = async () => {
    setLoading(true);
    setError("");
    try {
      const body = {
        node_id: node,
        severity,
        primary_metric: metric,
        ...values,
      };
      const res = await fetch(
        `${API}/api/inject-anomaly?node_id=${encodeURIComponent(node)}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const event = await res.json();
      onInjected && onInjected(event);
      onClose();
    } catch (err) {
      setError(`Injection failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const sevColors = {
    mild:     { bg: "rgba(16,185,129,0.12)",  border: "rgba(16,185,129,0.4)",  text: "#10b981" },
    high:     { bg: "rgba(249,115,22,0.12)",  border: "rgba(249,115,22,0.4)",  text: "#f97316" },
    critical: { bg: "rgba(239,68,68,0.12)",   border: "rgba(239,68,68,0.4)",   text: "#ef4444" },
  };

  return (
    /* Backdrop */
    <div
      onClick={e => { if (e.target === e.currentTarget) onClose(); }}
      style={{
        position: "fixed", inset: 0, zIndex: 1000,
        background: "rgba(0,0,0,0.7)",
        display: "flex", alignItems: "center", justifyContent: "center",
        padding: 16,
        backdropFilter: "blur(4px)",
      }}
    >
      <div style={{
        background: "rgba(15,22,41,0.97)",
        border: "1px solid rgba(239,68,68,0.3)",
        borderRadius: 14,
        width: "100%",
        maxWidth: 480,
        boxShadow: "0 24px 80px rgba(239,68,68,0.15), 0 8px 32px rgba(0,0,0,0.5)",
        overflow: "hidden",
        animation: "slideUp 0.2s ease",
      }}>
        {/* Header */}
        <div style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "16px 20px", borderBottom: "1px solid rgba(255,255,255,0.06)",
          background: "rgba(239,68,68,0.05)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.3)",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <Zap size={16} color="#ef4444" />
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 700, color: "#f1f5f9" }}>Inject Anomaly</div>
              <div style={{ fontSize: 10, color: "#94a3b8" }}>Scripted fault injection for demo / testing</div>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{ background: "transparent", border: "none", color: "#64748b", cursor: "pointer", padding: 4 }}
          >
            <X size={18} />
          </button>
        </div>

        <div style={{ padding: 20, display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Severity presets */}
          <div>
            <label style={{ fontSize: 10, color: "#64748b", fontWeight: 700, textTransform: "uppercase", display: "block", marginBottom: 8 }}>
              Severity Preset
            </label>
            <div style={{ display: "flex", gap: 8 }}>
              {Object.keys(PRESETS).map(lvl => {
                const c = sevColors[lvl];
                return (
                  <button
                    key={lvl}
                    onClick={() => applyPreset(lvl)}
                    style={{
                      flex: 1, padding: "8px 0", borderRadius: 8,
                      background: severity === lvl ? c.bg : "rgba(255,255,255,0.03)",
                      border: `1px solid ${severity === lvl ? c.border : "rgba(255,255,255,0.06)"}`,
                      color: severity === lvl ? c.text : "#64748b",
                      fontSize: 11, fontWeight: 700, textTransform: "uppercase",
                      cursor: "pointer", transition: "all 0.2s",
                    }}
                  >
                    {lvl}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Target node */}
          <div>
            <label style={{ fontSize: 10, color: "#64748b", fontWeight: 700, textTransform: "uppercase", display: "block", marginBottom: 6 }}>
              Target Node
            </label>
            <select
              value={node}
              onChange={e => setNode(e.target.value)}
              style={{
                width: "100%", padding: "8px 10px", borderRadius: 7,
                background: "rgba(10,14,26,0.8)", border: "1px solid rgba(255,255,255,0.08)",
                color: "#f1f5f9", fontSize: 12,
              }}
            >
              {ALL_NODES.map(n => <option key={n} value={n}>{n}</option>)}
            </select>
          </div>

          {/* Primary metric */}
          <div>
            <label style={{ fontSize: 10, color: "#64748b", fontWeight: 700, textTransform: "uppercase", display: "block", marginBottom: 6 }}>
              Primary Metric
            </label>
            <select
              value={metric}
              onChange={e => setMetric(e.target.value)}
              style={{
                width: "100%", padding: "8px 10px", borderRadius: 7,
                background: "rgba(10,14,26,0.8)", border: "1px solid rgba(255,255,255,0.08)",
                color: "#f1f5f9", fontSize: 12,
              }}
            >
              {METRICS.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>

          {/* Metric sliders */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            {[
              { key: "latency_ms",        label: "Latency",    min: 1,   max: 500, unit: "ms" },
              { key: "packet_loss_pct",   label: "Pkt Loss",   min: 0,   max: 30,  unit: "%" },
              { key: "jitter_ms",         label: "Jitter",     min: 0,   max: 100, unit: "ms" },
              { key: "throughput_mbps",   label: "Throughput", min: 10,  max: 500, unit: "Mbps" },
            ].map(({ key, label, min, max, unit }) => (
              <div key={key}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                  <span style={{ fontSize: 9, color: "#64748b", fontWeight: 700, textTransform: "uppercase" }}>{label}</span>
                  <span style={{ fontSize: 10, color: "#06b6d4", fontWeight: 600 }}>{values[key]}{unit}</span>
                </div>
                <input
                  type="range" min={min} max={max}
                  value={values[key]}
                  onChange={e => setValues(v => ({ ...v, [key]: Number(e.target.value) }))}
                  style={{ width: "100%", accentColor: "#3b82f6" }}
                />
              </div>
            ))}
          </div>

          {error && (
            <div style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "8px 12px", borderRadius: 6,
              background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.2)",
              fontSize: 11, color: "#fca5a5",
            }}>
              <AlertTriangle size={12} /> {error}
            </div>
          )}

          {/* Actions */}
          <div style={{ display: "flex", gap: 10 }}>
            <button
              onClick={onClose}
              style={{
                flex: 1, padding: "10px 0", borderRadius: 8,
                background: "transparent", border: "1px solid rgba(255,255,255,0.08)",
                color: "#94a3b8", fontSize: 12, fontWeight: 500, cursor: "pointer",
              }}
            >
              Cancel
            </button>
            <button
              onClick={handleInject}
              disabled={loading}
              style={{
                flex: 2, padding: "10px 0", borderRadius: 8,
                background: loading ? "rgba(239,68,68,0.3)" : "rgba(239,68,68,0.85)",
                border: "1px solid rgba(239,68,68,0.5)",
                color: "white", fontSize: 12, fontWeight: 700, cursor: "pointer",
                display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                transition: "background 0.2s",
              }}
            >
              <Zap size={13} />
              {loading ? "Injecting…" : `Inject ${severity.toUpperCase()} anomaly → ${node}`}
            </button>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
