import { Activity, BarChart3, History, RefreshCcw, ShieldAlert, Sparkles } from "lucide-react";

function SmallMetric({ label, value, note, tone = "blue" }) {
  return (
    <div style={{
      padding: "10px 12px",
      borderRadius: 8,
      border: "1px solid #1e2d4a",
      background: "#0f1629",
      minHeight: 68,
    }}>
      <div style={{ fontSize: 9, color: "#64748b", fontWeight: 700, textTransform: "uppercase", marginBottom: 4 }}>
        {label}
      </div>
      <div style={{ fontSize: 18, fontWeight: 800, color: tone === "green" ? "#10b981" : tone === "red" ? "#ef4444" : tone === "cyan" ? "#06b6d4" : "#3b82f6" }}>
        {value}
      </div>
      {note && <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>{note}</div>}
    </div>
  );
}

function IncidentRow({ incident }) {
  const score = (incident.anomaly_score ?? incident.score ?? 0).toFixed(3);
  return (
    <div style={{
      display: "flex",
      justifyContent: "space-between",
      gap: 10,
      alignItems: "center",
      padding: "8px 10px",
      borderRadius: 8,
      border: "1px solid #1e2d4a",
      background: "#0a0e1a",
    }}>
      <div style={{ minWidth: 0 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: "#f1f5f9" }}>
          {incident.primary_metric || "network"} anomaly
        </div>
        <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>
          {incident.severity || "unknown"} · score {score}
        </div>
      </div>
      <div style={{ fontSize: 9, color: "#06b6d4", background: "rgba(6,182,212,0.08)", padding: "2px 6px", borderRadius: 999, whiteSpace: "nowrap" }}>
        {incident.timestamp ? new Date(incident.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "—"}
      </div>
    </div>
  );
}

export default function OperationsSummary({
  summary,
  recentIncidents,
  benchmark,
  benchmarkLoading,
  onRefresh,
  onRunBenchmark,
  onDownloadReport,
}) {
  const aiMetrics = benchmark?.results?.net_guardian_ai;
  const baseMetrics = benchmark?.results?.adaptive_ma_baseline;

  return (
    <div className="feed-panel" style={{ maxHeight: 340 }}>
      <div className="panel-header">
        <div className="panel-title">
          <Sparkles size={14} color="#10b981" />
          Operations Snapshot
        </div>
        <div className="panel-actions">
          <button className="btn btn-ghost" onClick={onRefresh}>
            <RefreshCcw size={12} /> Refresh
          </button>
          <button className="btn btn-ghost" onClick={onDownloadReport}>
            <Activity size={12} /> Report
          </button>
          <button className="btn btn-primary" onClick={onRunBenchmark} disabled={benchmarkLoading}>
            <BarChart3 size={12} /> {benchmarkLoading ? "Running…" : "Benchmark"}
          </button>
        </div>
      </div>

      <div style={{ padding: 12, display: "flex", flexDirection: "column", gap: 10, overflow: "hidden" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 8 }}>
          <SmallMetric
            label="Incidents"
            value={summary?.total_incidents ?? 0}
            note={`Recorded alerts`}
            tone="red"
          />
          <SmallMetric
            label="Avg Score"
            value={summary?.average_score ?? 0}
            note="Anomaly severity baseline"
            tone="cyan"
          />
          <SmallMetric
            label="Dataset"
            value={summary?.data_points ?? 0}
            note={summary?.stream_active ? "streaming" : "idle"}
            tone="green"
          />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          <div style={{ padding: 10, borderRadius: 8, border: "1px solid #1e2d4a", background: "rgba(59,130,246,0.05)" }}>
            <div style={{ fontSize: 9, color: "#64748b", fontWeight: 700, textTransform: "uppercase", marginBottom: 6 }}>AI Lead</div>
            <div style={{ fontSize: 18, fontWeight: 800, color: "#10b981" }}>{aiMetrics?.avg_lag_sec ?? "—"}s</div>
            <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>
              precision {aiMetrics?.precision ?? "—"} · recall {aiMetrics?.recall ?? "—"}
            </div>
          </div>
          <div style={{ padding: 10, borderRadius: 8, border: "1px solid #1e2d4a", background: "rgba(239,68,68,0.05)" }}>
            <div style={{ fontSize: 9, color: "#64748b", fontWeight: 700, textTransform: "uppercase", marginBottom: 6 }}>Baseline Lag</div>
            <div style={{ fontSize: 18, fontWeight: 800, color: "#ef4444" }}>{baseMetrics?.avg_lag_sec ?? "—"}s</div>
            <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>
              precision {baseMetrics?.precision ?? "—"} · recall {baseMetrics?.recall ?? "—"}
            </div>
          </div>
        </div>

        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}>
            <History size={12} color="#06b6d4" />
            <div style={{ fontSize: 10, color: "#64748b", fontWeight: 700, textTransform: "uppercase" }}>Recent Incidents</div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6, maxHeight: 120, overflowY: "auto", paddingRight: 4 }}>
            {(recentIncidents || []).length > 0 ? (
              recentIncidents.map((incident, index) => <IncidentRow key={`${incident.timestamp || index}-${index}`} incident={incident} />)
            ) : (
              <div style={{ padding: "12px 10px", borderRadius: 8, border: "1px dashed #1e2d4a", color: "#94a3b8", fontSize: 11, display: "flex", alignItems: "center", gap: 8 }}>
                <ShieldAlert size={12} color="#64748b" />
                No incidents recorded yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}