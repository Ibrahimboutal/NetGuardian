import { useState, useEffect, useCallback } from "react";
import { CheckCircle2, Clock, ShieldAlert, RefreshCcw, User, FileText } from "lucide-react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const API_TOKEN = import.meta.env.VITE_API_TOKEN || "";

const SEVERITY_COLORS = {
  critical: { bg: "rgba(239,68,68,0.12)", border: "rgba(239,68,68,0.35)", text: "#ef4444" },
  high:     { bg: "rgba(249,115,22,0.10)", border: "rgba(249,115,22,0.3)",  text: "#f97316" },
  medium:   { bg: "rgba(234,179,8,0.08)",  border: "rgba(234,179,8,0.25)",  text: "#eab308" },
  low:      { bg: "rgba(16,185,129,0.08)", border: "rgba(16,185,129,0.2)",  text: "#10b981" },
};

const COLUMNS = [
  { id: "open",         label: "Open",         icon: ShieldAlert, color: "#ef4444" },
  { id: "acknowledged", label: "Acknowledged",  icon: Clock,       color: "#f59e0b" },
  { id: "resolved",     label: "Resolved",      icon: CheckCircle2, color: "#10b981" },
];

function IncidentCard({ incident, onAck, onResolve, isDragging, onDragStart }) {
  const sev = SEVERITY_COLORS[incident.severity] || SEVERITY_COLORS.low;
  const score = (incident.anomaly_score ?? incident.score ?? 0).toFixed(3);
  const ts = incident.timestamp
    ? new Date(incident.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    : "—";
  const state = incident.incident_state || "open";

  return (
    <div
      draggable
      onDragStart={() => onDragStart(incident)}
      style={{
        background: sev.bg,
        border: `1px solid ${sev.border}`,
        borderRadius: 8,
        padding: "10px 12px",
        cursor: "grab",
        opacity: isDragging ? 0.45 : 1,
        transition: "opacity 0.2s, transform 0.2s",
        userSelect: "none",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
        <span style={{ fontSize: 10, fontWeight: 700, color: sev.text, textTransform: "uppercase" }}>
          {incident.severity || "unknown"}
        </span>
        <span style={{ fontSize: 9, color: "#64748b" }}>{ts}</span>
      </div>

      <div style={{ fontSize: 12, fontWeight: 600, color: "#f1f5f9", marginBottom: 3 }}>
        {incident.primary_metric || "network"} anomaly
      </div>

      <div style={{ fontSize: 10, color: "#94a3b8", marginBottom: 6 }}>
        Node: {incident.node_id || "—"} · Score: {score}
      </div>

      {incident.assigned_to && (
        <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 9, color: "#64748b", marginBottom: 6 }}>
          <User size={9} /> {incident.assigned_to}
        </div>
      )}

      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {state === "open" && (
          <button
            onClick={() => onAck(incident.incident_id)}
            style={{
              fontSize: 9, padding: "2px 8px", borderRadius: 4, border: "1px solid rgba(234,179,8,0.4)",
              background: "rgba(234,179,8,0.08)", color: "#eab308", cursor: "pointer",
            }}
          >
            Acknowledge
          </button>
        )}
        {state !== "resolved" && (
          <button
            onClick={() => onResolve(incident.incident_id)}
            style={{
              fontSize: 9, padding: "2px 8px", borderRadius: 4, border: "1px solid rgba(16,185,129,0.4)",
              background: "rgba(16,185,129,0.08)", color: "#10b981", cursor: "pointer",
            }}
          >
            Resolve
          </button>
        )}
      </div>
    </div>
  );
}

function KanbanColumn({ column, incidents, onAck, onResolve, draggingId, onDragStart, onDrop }) {
  const Icon = column.icon;

  return (
    <div
      onDragOver={e => e.preventDefault()}
      onDrop={() => onDrop(column.id)}
      style={{
        flex: 1,
        minWidth: 0,
        background: "rgba(15,22,41,0.5)",
        border: "1px solid rgba(255,255,255,0.06)",
        borderRadius: 10,
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      {/* Column header */}
      <div style={{
        display: "flex", alignItems: "center", gap: 8,
        padding: "10px 14px", borderBottom: "1px solid rgba(255,255,255,0.05)",
        background: "rgba(10,14,26,0.4)",
      }}>
        <Icon size={13} color={column.color} />
        <span style={{ fontSize: 12, fontWeight: 600, color: "#f1f5f9" }}>{column.label}</span>
        <span style={{
          marginLeft: "auto", fontSize: 10, fontWeight: 700,
          background: `${column.color}22`, color: column.color,
          padding: "1px 7px", borderRadius: 10,
        }}>
          {incidents.length}
        </span>
      </div>

      {/* Cards */}
      <div style={{
        flex: 1, overflowY: "auto", padding: 10,
        display: "flex", flexDirection: "column", gap: 8, minHeight: 120,
      }}>
        {incidents.length === 0 ? (
          <div style={{
            flex: 1, display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 11, color: "#475569", padding: 16, textAlign: "center",
          }}>
            No incidents
          </div>
        ) : incidents.map(inc => (
          <IncidentCard
            key={inc.incident_id || inc.timestamp}
            incident={inc}
            onAck={onAck}
            onResolve={onResolve}
            isDragging={draggingId === inc.incident_id}
            onDragStart={onDragStart}
          />
        ))}
      </div>
    </div>
  );
}

export default function IncidentKanban() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(null);
  const [error, setError] = useState("");

  const headers = API_TOKEN ? { "X-API-Key": API_TOKEN } : {};

  const fetchIncidents = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/incidents/recent?limit=100`);
      const json = await res.json();
      setIncidents(Array.isArray(json?.data) ? json.data : []);
      setError("");
    } catch {
      setError("Failed to load incidents");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchIncidents(); }, [fetchIncidents]);

  const ackIncident = async (id) => {
    try {
      await fetch(`${API}/api/incidents/${id}/ack?assigned_to=operator`, { method: "POST", headers });
      setIncidents(prev => prev.map(i => i.incident_id === id ? { ...i, incident_state: "acknowledged", assigned_to: "operator" } : i));
    } catch { setError("Acknowledge failed"); }
  };

  const resolveIncident = async (id) => {
    try {
      await fetch(`${API}/api/incidents/${id}/resolve?resolution_note=resolved_via_kanban`, { method: "POST", headers });
      setIncidents(prev => prev.map(i => i.incident_id === id ? { ...i, incident_state: "resolved" } : i));
    } catch { setError("Resolve failed"); }
  };

  const handleDrop = async (targetState) => {
    if (!dragging) return;
    const id = dragging.incident_id;
    if (targetState === "acknowledged" && dragging.incident_state === "open") await ackIncident(id);
    if (targetState === "resolved" && dragging.incident_state !== "resolved") await resolveIncident(id);
    setDragging(null);
  };

  const byState = (state) => incidents.filter(i => (i.incident_state || "open") === state);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 0 }}>
      {/* Header */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "14px 18px", borderBottom: "1px solid rgba(255,255,255,0.05)",
        background: "rgba(15,22,41,0.6)", backdropFilter: "blur(16px)",
        flexShrink: 0,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <FileText size={15} color="#3b82f6" />
          <span style={{ fontSize: 14, fontWeight: 700, color: "#f1f5f9" }}>Incident Kanban</span>
          <span style={{ fontSize: 10, color: "#64748b", marginLeft: 4 }}>
            {incidents.length} total
          </span>
        </div>
        <button
          onClick={fetchIncidents}
          disabled={loading}
          style={{
            display: "flex", alignItems: "center", gap: 5,
            fontSize: 11, padding: "5px 12px", borderRadius: 6,
            border: "1px solid rgba(255,255,255,0.08)", background: "transparent",
            color: "#94a3b8", cursor: "pointer",
          }}
        >
          <RefreshCcw size={11} style={{ animation: loading ? "spin 1s linear infinite" : "none" }} />
          Refresh
        </button>
      </div>

      {error && (
        <div style={{ padding: "8px 18px", fontSize: 11, color: "#fca5a5", background: "rgba(239,68,68,0.07)", flexShrink: 0 }}>
          {error}
        </div>
      )}

      {/* Board */}
      <div style={{
        flex: 1, overflowY: "auto", padding: 16,
        display: "flex", gap: 14,
        alignItems: "stretch",
      }}>
        {COLUMNS.map(col => (
          <KanbanColumn
            key={col.id}
            column={col}
            incidents={byState(col.id)}
            onAck={ackIncident}
            onResolve={resolveIncident}
            draggingId={dragging?.incident_id}
            onDragStart={setDragging}
            onDrop={handleDrop}
          />
        ))}
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
