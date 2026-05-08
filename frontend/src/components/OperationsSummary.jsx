import { useEffect, useMemo, useState } from "react";
import { Activity, BarChart3, ChevronRight, History, RefreshCcw, ShieldAlert, Sparkles } from "lucide-react";

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
  insights,
  forecast,
  benchmarkLoading,
  onRefresh,
  onRunBenchmark,
  onDownloadReport,
}) {
  const aiMetrics = benchmark?.results?.net_guardian_ai;
  const baseMetrics = benchmark?.results?.adaptive_ma_baseline;
  const cascade = summary?.cascade || forecast?.cascade;
  const [activeStepIndex, setActiveStepIndex] = useState(0);

  const cascadeSteps = cascade?.steps || [];

  useEffect(() => {
    if (cascadeSteps.length === 0) {
      setActiveStepIndex(0);
      return;
    }

    if (activeStepIndex >= cascadeSteps.length) {
      setActiveStepIndex(0);
    }
  }, [activeStepIndex, cascadeSteps.length]);

  const activeStep = useMemo(() => {
    if (cascadeSteps.length === 0) return null;
    return cascadeSteps[Math.min(activeStepIndex, cascadeSteps.length - 1)];
  }, [activeStepIndex, cascadeSteps]);

  const cascadeTone = cascade?.risk_level === "high"
    ? "#ef4444"
    : cascade?.risk_level === "medium"
      ? "#f59e0b"
      : cascade?.risk_level === "low"
        ? "#10b981"
        : "#64748b";

  return (
    <div className="feed-panel" style={{ maxHeight: 420 }}>
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

        <div style={{ padding: 10, borderRadius: 8, border: "1px solid rgba(16,185,129,0.18)", background: "rgba(16,185,129,0.05)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center", marginBottom: 4 }}>
            <div style={{ fontSize: 9, color: "#10b981", fontWeight: 700, textTransform: "uppercase" }}>Recurring Pattern</div>
            <div style={{ fontSize: 8, color: "#94a3b8" }}>last {insights?.recurrence_window ?? 0} incidents</div>
          </div>
          <div style={{ fontSize: 12, fontWeight: 700, color: "#f1f5f9" }}>
            {insights?.recurring_case ? insights.recurring_case : "No dominant pattern yet"}
          </div>
          <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>
            {insights?.forecast || "Collecting memory"}
          </div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 8 }}>
            <span style={{ fontSize: 8, padding: "2px 6px", borderRadius: 999, background: "rgba(16,185,129,0.12)", color: "#10b981" }}>
              share {(insights?.recurring_case_rate ?? 0).toFixed(2)}
            </span>
            <span style={{ fontSize: 8, padding: "2px 6px", borderRadius: 999, background: "rgba(6,182,212,0.12)", color: "#06b6d4" }}>
              metric {insights?.dominant_metric || "—"}
            </span>
          </div>
        </div>

        <div style={{ padding: 10, borderRadius: 8, border: "1px solid rgba(249,115,22,0.2)", background: "rgba(249,115,22,0.05)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center", marginBottom: 4 }}>
            <div style={{ fontSize: 9, color: "#f59e0b", fontWeight: 700, textTransform: "uppercase" }}>60s Forecast</div>
            <div style={{ fontSize: 8, color: "#94a3b8" }}>{forecast?.window_size ?? 0} recent incidents</div>
          </div>
          <div style={{ fontSize: 12, fontWeight: 700, color: "#f1f5f9" }}>
            {forecast?.risk_level ? `${forecast.risk_level.toUpperCase()} risk` : "No forecast yet"}
          </div>
          <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>
            {forecast?.reason || "Need more history to forecast."}
          </div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 8 }}>
            <span style={{ fontSize: 8, padding: "2px 6px", borderRadius: 999, background: "rgba(249,115,22,0.12)", color: "#f59e0b" }}>
              confidence {(forecast?.confidence ?? 0).toFixed(2)}
            </span>
            <span style={{ fontSize: 8, padding: "2px 6px", borderRadius: 999, background: "rgba(59,130,246,0.12)", color: "#3b82f6" }}>
              next {forecast?.next_metric || "—"}
            </span>
          </div>
          <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 6 }}>
            Next action: {forecast?.next_action || "Collect telemetry"}
          </div>
        </div>

        <div style={{ padding: 10, borderRadius: 8, border: `1px solid ${cascadeTone}33`, background: `${cascadeTone}10` }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center", marginBottom: 4 }}>
            <div style={{ fontSize: 9, color: cascadeTone, fontWeight: 700, textTransform: "uppercase" }}>Cascade Timeline</div>
            <div style={{ fontSize: 8, color: "#94a3b8" }}>{cascade?.horizon_sec ?? 0}s spread view</div>
          </div>
          <div style={{ fontSize: 12, fontWeight: 700, color: "#f1f5f9" }}>
            {cascade?.summary || "No cascade signal yet"}
          </div>
          <div style={{ display: "grid", gap: 6, marginTop: 8 }}>
            {(cascade?.steps || []).length > 0 ? cascade.steps.map(step => (
              <button
                key={`${step.window_sec}-${step.label}`}
                type="button"
                onClick={() => setActiveStepIndex(cascadeSteps.findIndex(candidate => candidate.window_sec === step.window_sec && candidate.label === step.label))}
                style={{
                  display: "grid",
                  gridTemplateColumns: "42px 1fr",
                  gap: 8,
                  alignItems: "start",
                  width: "100%",
                  textAlign: "left",
                  background: activeStep?.window_sec === step.window_sec && activeStep?.label === step.label ? "rgba(59,130,246,0.08)" : "transparent",
                  border: activeStep?.window_sec === step.window_sec && activeStep?.label === step.label ? "1px solid rgba(59,130,246,0.35)" : "1px solid #1e2d4a",
                  borderRadius: 8,
                  padding: "8px 10px",
                  cursor: "pointer",
                }}
              >
                <div style={{ fontSize: 8, color: "#94a3b8", paddingTop: 2 }}>{step.window_sec}s</div>
                <div style={{ padding: 0, borderRadius: 8 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center" }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: "#f1f5f9" }}>{step.label}</div>
                    <ChevronRight size={10} color={cascadeTone} />
                  </div>
                  <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>
                    node {step.node || "—"} · signal {step.signal || "—"}
                  </div>
                  <div style={{ fontSize: 10, color: "#cbd5e1", marginTop: 4, lineHeight: 1.35 }}>
                    {step.effect}
                  </div>
                </div>
              </button>
            )) : (
              <div style={{ fontSize: 10, color: "#94a3b8" }}>Collecting enough memory to simulate spread.</div>
            )}
          </div>
          {activeStep && (
            <div style={{ marginTop: 8, padding: 10, borderRadius: 8, background: "#0a0e1a", border: "1px solid #1e2d4a" }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center" }}>
                <div style={{ fontSize: 9, color: cascadeTone, fontWeight: 700, textTransform: "uppercase" }}>Selected Phase</div>
                <div style={{ fontSize: 8, color: "#94a3b8" }}>{activeStep.window_sec}s</div>
              </div>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#f1f5f9", marginTop: 4 }}>{activeStep.label}</div>
              <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>
                node {activeStep.node || "—"} · signal {activeStep.signal || "—"}
              </div>
              <div style={{ fontSize: 10, color: "#cbd5e1", marginTop: 6, lineHeight: 1.35 }}>
                {activeStep.effect}
              </div>
            </div>
          )}
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