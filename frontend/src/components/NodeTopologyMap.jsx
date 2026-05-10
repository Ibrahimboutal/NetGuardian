import React, { useMemo } from "react";
import { Wifi, WifiOff, AlertTriangle, CheckCircle2 } from "lucide-react";

const NODE_GRID = [
  { id: "Core-DC-01",    role: "core",    x: 3, y: 0 },
  { id: "Core-DC-02",    role: "core",    x: 5, y: 0 },
  { id: "Router-Edge-01", role: "edge",   x: 1, y: 1 },
  { id: "Router-Edge-02", role: "edge",   x: 3, y: 1 },
  { id: "Router-Edge-03", role: "edge",   x: 5, y: 1 },
  { id: "Router-Edge-04", role: "edge",   x: 7, y: 1 },
  { id: "Router-01",     role: "router",  x: 0, y: 2 },
  { id: "Router-02",     role: "router",  x: 2, y: 2 },
  { id: "Router-03",     role: "router",  x: 4, y: 2 },
  { id: "Router-04",     role: "router",  x: 6, y: 2 },
  { id: "Router-14",     role: "router",  x: 8, y: 2 },
  { id: "Leaf-01",       role: "leaf",    x: 1, y: 3 },
  { id: "Leaf-02",       role: "leaf",    x: 3, y: 3 },
  { id: "Leaf-03",       role: "leaf",    x: 5, y: 3 },
  { id: "Leaf-04",       role: "leaf",    x: 7, y: 3 },
];

const ROLE_COLORS = {
  core:   { bg: "rgba(59,130,246,0.15)",  border: "#3b82f6", label: "#3b82f6" },
  edge:   { bg: "rgba(6,182,212,0.12)",   border: "#06b6d4", label: "#06b6d4" },
  router: { bg: "rgba(16,185,129,0.10)",  border: "#10b981", label: "#10b981" },
  leaf:   { bg: "rgba(100,116,139,0.10)", border: "#475569", label: "#64748b" },
};

const STATUS_COLORS = {
  healthy:   { dot: "#10b981", glow: "0 0 6px #10b981" },
  warning:   { dot: "#f59e0b", glow: "0 0 6px #f59e0b" },
  critical:  { dot: "#ef4444", glow: "0 0 8px #ef4444" },
  offline:   { dot: "#475569", glow: "none" },
};

function nodeStatus(nodeId, anomalies) {
  const recentHits = anomalies.filter(a => a.node_id === nodeId);
  if (recentHits.length === 0) return "healthy";
  const worst = recentHits.reduce((prev, cur) =>
    (cur.anomaly_score ?? 0) > (prev.anomaly_score ?? 0) ? cur : prev
  );
  const sev = worst.severity;
  if (sev === "critical") return "critical";
  if (sev === "high")     return "warning";
  return "warning";
}

function NodeDot({ node, anomalies }) {
  const status = nodeStatus(node.id, anomalies);
  const roleStyle = ROLE_COLORS[node.role];
  const statusStyle = STATUS_COLORS[status];

  return (
    <div
      title={`${node.id} (${node.role}) — ${status}`}
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 4,
        cursor: "default",
      }}
    >
      <div style={{
        width: 36,
        height: 36,
        borderRadius: node.role === "core" ? 8 : "50%",
        background: status === "critical" ? "rgba(239,68,68,0.15)" : roleStyle.bg,
        border: `1.5px solid ${status === "critical" ? "#ef4444" : status === "warning" ? "#f59e0b" : roleStyle.border}`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        transition: "all 0.3s ease",
        boxShadow: status === "critical" ? "0 0 12px rgba(239,68,68,0.4)" : "none",
        animation: status === "critical" ? "pulse-node 1.5s infinite" : "none",
      }}>
        {status === "offline" ? (
          <WifiOff size={14} color="#475569" />
        ) : status === "critical" ? (
          <AlertTriangle size={14} color="#ef4444" />
        ) : status === "warning" ? (
          <Wifi size={14} color="#f59e0b" />
        ) : (
          <CheckCircle2 size={14} color={roleStyle.label} />
        )}
        <div style={{
          position: "absolute",
          top: -3,
          right: -3,
          width: 8,
          height: 8,
          borderRadius: "50%",
          background: statusStyle.dot,
          boxShadow: statusStyle.glow,
          border: "1.5px solid #0a0e1a",
        }} />
      </div>
      <div style={{
        fontSize: 7,
        color: "#64748b",
        textAlign: "center",
        maxWidth: 50,
        lineHeight: 1.2,
        fontWeight: 500,
        letterSpacing: "0.2px",
      }}>
        {node.id.replace("Router-", "R-").replace("Leaf-0", "L-").replace("Core-DC-0", "C-")}
      </div>
    </div>
  );
}

export default function NodeTopologyMap({ anomalies = [], activeIncident = null }) {
  const recentAnomalies = useMemo(() => anomalies.slice(-30), [anomalies]);

  const statusCounts = useMemo(() => {
    const counts = { healthy: 0, warning: 0, critical: 0, offline: 0 };
    NODE_GRID.forEach(n => {
      counts[nodeStatus(n.id, recentAnomalies)]++;
    });
    return counts;
  }, [recentAnomalies]);

  const cascadeNodes = useMemo(() => {
    if (!activeIncident?.blackboard?.causal_chain) return new Set();
    const nodes = new Set();
    activeIncident.blackboard.causal_chain.forEach(link => {
      nodes.add(link.epicenter);
      if (link.critical_hits) link.critical_hits.forEach(n => nodes.add(n));
    });
    return nodes;
  }, [activeIncident]);

  // Group nodes by row (y value)
  const rows = useMemo(() => {
    const map = {};
    NODE_GRID.forEach(n => {
      if (!map[n.y]) map[n.y] = [];
      map[n.y].push(n);
    });
    return Object.entries(map).sort(([a], [b]) => Number(a) - Number(b));
  }, []);

  return (
    <div style={{
      background: "rgba(19, 25, 41, 0.6)",
      border: "1px solid rgba(255,255,255,0.05)",
      borderRadius: 12,
      overflow: "hidden",
      backdropFilter: "blur(12px)",
      WebkitBackdropFilter: "blur(12px)",
      boxShadow: "0 8px 32px 0 rgba(0, 0, 0, 0.2)",
      width: "100%",
      minWidth: 0,
    }}>
      {/* Header */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: 8,
        padding: "12px 16px",
        borderBottom: "1px solid rgba(255,255,255,0.05)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Wifi size={14} color="#06b6d4" />
          <span style={{ fontSize: 13, fontWeight: 600, color: "#f1f5f9" }}>Node Topology</span>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
          {[
            { key: "healthy",  color: "#10b981", label: "Healthy"  },
            { key: "warning",  color: "#f59e0b", label: "Warning"  },
            { key: "critical", color: "#ef4444", label: "Critical" },
          ].map(({ key, color, label }) => (
            <div key={key} style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: color, boxShadow: `0 0 4px ${color}` }} />
              <span style={{ fontSize: 9, color: "#94a3b8", fontWeight: 500 }}>
                {statusCounts[key]} {label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Topology grid */}
      <div style={{ padding: "12px 8px", display: "flex", flexDirection: "column", gap: 12 }}>
        {rows.map(([y, nodes]) => (
          <div key={y} style={{
            display: "flex",
            justifyContent: "center",
            gap: 10,
            flexWrap: "wrap",
          }}>
            {nodes.sort((a, b) => a.x - b.x).map(node => {
              const isInCascade = cascadeNodes.has(node.id);
              return (
                <div key={node.id} style={{
                  position: "relative",
                  animation: isInCascade ? "cascade-ripple 2s infinite" : "none",
                  borderRadius: 12,
                }}>
                  <NodeDot node={node} anomalies={recentAnomalies} />
                  {isInCascade && (
                    <div style={{
                      position: "absolute",
                      inset: -4,
                      border: "2px solid #ef4444",
                      borderRadius: "50%",
                      animation: "ripple-effect 2s infinite",
                      pointerEvents: "none",
                    }} />
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>

      <style>{`
        @keyframes pulse-node {
          0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
          50% { box-shadow: 0 0 12px 4px rgba(239,68,68,0.35); }
        }
        @keyframes ripple-effect {
          0% { transform: scale(0.8); opacity: 0.8; }
          100% { transform: scale(1.6); opacity: 0; }
        }
        @keyframes cascade-ripple {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }
      `}</style>
    </div>
  );
}

