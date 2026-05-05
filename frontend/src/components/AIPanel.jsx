import { useState } from "react";
import { Brain, ShieldCheck, Zap, Activity, Info, AlertTriangle, CheckCircle } from "lucide-react";

const TABS = [
  { id: "explanation", label: "Briefing",       icon: Info },
  { id: "diagnosis",   label: "Reasoning",      icon: Brain },
  { id: "recommendation", label: "Intervention", icon: ShieldCheck },
];

function ThinkingIndicator({ label }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "12px 0", color: "#64748b" }}>
      <div className="thinking-dots">
        <div className="thinking-dot" />
        <div className="thinking-dot" />
        <div className="thinking-dot" />
      </div>
      <span style={{ fontSize: 12 }}>{label}</span>
    </div>
  );
}

export default function AIPanel({ incident, thinking }) {
  const [activeTab, setActiveTab] = useState("explanation");

  const hasAgents = incident?.agents;
  const isActive = hasAgents || thinking;

  const diagnosis = hasAgents?.diagnosis || {};
  const recommendation = hasAgents?.recommendation || {};
  const explanation = hasAgents?.explanation || {};
  const experience = incident?.grounded_experience || {};
  const simulation = incident?.simulation_results;
  const mitigations = incident?.mitigation_results || [];

  return (
    <div className={`ai-panel ${isActive ? "active" : ""}`}>
      {/* Header */}
      <div className="panel-header">
        <div className="panel-title">
          <Activity size={14} className="panel-title-icon" color="#06b6d4" />
          Predictive Resilience Engine
        </div>
        {thinking && (
          <div className="thinking-dots">
            <div className="thinking-dot" />
            <div className="thinking-dot" />
            <div className="thinking-dot" />
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="ai-tabs">
        {TABS.map(tab => (
          <button
            key={tab.id}
            className={`ai-tab ${activeTab === tab.id ? "active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <tab.icon size={11} style={{ display: "inline", marginRight: 4 }} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="ai-content">
        {!isActive && (
          <div className="ai-empty">
            <div className="ai-empty-icon">🛡️</div>
            <div className="ai-empty-text">
              <strong>Offline AI Sentinel</strong><br />
              Predicting cascading infrastructure failures.<br />
              Autonomous agents active.
            </div>
          </div>
        )}

        {thinking && !hasAgents && (
          <div>
            <ThinkingIndicator label="🧠 RAG Layer retrieving historical context…" />
            <ThinkingIndicator label="🩺 Reasoning Agent predicting failure cascade…" />
            <ThinkingIndicator label="🔬 Executing real-time impact simulation…" />
            <ThinkingIndicator label="🔧 Commander Agent executing tactical isolation…" />
          </div>
        )}

        {hasAgents && activeTab === "explanation" && (
          <div>
            {/* System Alert Banner */}
            <div style={{
              background: `rgba(${explanation.status_color === 'red' ? '239,68,68' : '234,179,8'}, 0.08)`, 
              border: `1px solid rgba(${explanation.status_color === 'red' ? '239,68,68' : '234,179,8'}, 0.2)`,
              borderRadius: 8, padding: "10px 12px", marginBottom: 14
            }}>
              <div style={{ fontSize: 10, color: explanation.status_color === 'red' ? '#ef4444' : '#eab308', fontWeight: 700, marginBottom: 4, textTransform: "uppercase" }}>
                Status: {diagnosis.risk_level || "Investigating"}
              </div>
              <div style={{ fontSize: 13, fontWeight: 600, color: "#f1f5f9" }}>
                Intervened: {diagnosis.predicted_next_failure || "Unknown Cascade"}
              </div>
            </div>

            {/* Tactical Execution Moment */}
            {mitigations.length > 0 && (
               <div style={{ marginBottom: 14, padding: "8px 10px", background: "rgba(16,185,129,0.05)", borderRadius: 6, borderLeft: "3px solid #10b981" }}>
               <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 9, fontWeight: 700, color: "#10b981", marginBottom: 4 }}>
                  <CheckCircle size={10} /> AUTONOMOUS MITIGATION SUCCESSFUL
               </div>
               <div style={{ fontSize: 11, color: "#f1f5f9", fontWeight: 600 }}>{mitigations[0].intervention}</div>
               <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>Target: {mitigations[0].target} | Recovery: {mitigations[0].impact_recovery_est}</div>
             </div>
            )}

            <p className="ai-text">{explanation.summary}</p>
          </div>
        )}

        {hasAgents && activeTab === "diagnosis" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div className="ai-data-row">
              <span className="ai-label">RISK LEVEL:</span>
              <span className="ai-value" style={{ color: diagnosis.risk_level === 'CRITICAL' ? '#ef4444' : '#eab308' }}>{diagnosis.risk_level}</span>
            </div>
            <div className="ai-data-row">
              <span className="ai-label">PREDICTED FAILURE:</span>
              <span className="ai-value">{diagnosis.predicted_next_failure}</span>
            </div>

            {/* Simulation Block */}
            {simulation && (
               <div style={{ padding: "8px 10px", background: "rgba(245,158,11,0.05)", borderRadius: 6, border: "1px dashed rgba(245,158,11,0.3)" }}>
                  <div style={{ fontSize: 9, fontWeight: 700, color: "#f59e0b", marginBottom: 4 }}>SIMULATION OUTPUT</div>
                  <div style={{ fontSize: 11, color: "#f1f5f9" }}><strong>Outcome:</strong> {simulation.predicted_outcome}</div>
                  <div style={{ fontSize: 10, color: "#94a3b8" }}>Cascade in {simulation.time_to_critical_failure}</div>
               </div>
            )}

            {/* Reasoning Trace */}
            <div style={{ marginTop: 8 }}>
              <div style={{ fontSize: 9, fontWeight: 700, color: "#64748b", marginBottom: 6, textTransform: "uppercase" }}>Reasoning Trace</div>
              <div style={{ 
                padding: 10, background: "#0a0e1a", borderRadius: 6, border: "1px solid #1e2d4a",
                fontSize: 11, color: "#cbd5e1", lineHeight: 1.5, fontStyle: "italic"
              }}>
                "{diagnosis.reasoning_trace}"
              </div>
            </div>
          </div>
        )}

        {hasAgents && activeTab === "recommendation" && (
          <div>
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontSize: 9, color: "#64748b", fontWeight: 700, marginBottom: 4 }}>TACTICAL DECISION</div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#f1f5f9" }}>{recommendation.decision}</div>
            </div>

            {Array.isArray(recommendation.actions) ? recommendation.actions.map((item, i) => (
              <div key={i} className="ai-recommendation-item">
                <div className="ai-rec-num">{i + 1}</div>
                <div className="ai-rec-text">
                  <div style={{ fontWeight: 600, color: "#f1f5f9" }}>{item.action}</div>
                  <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
                    <span style={{ 
                      fontSize: 9, padding: "1px 6px", borderRadius: 3, 
                      background: item.priority === 'CRITICAL' ? 'rgba(239,68,68,0.2)' : 'rgba(59,130,246,0.2)',
                      color: item.priority === 'CRITICAL' ? '#ef4444' : '#3b82f6'
                    }}>
                      {item.priority}
                    </span>
                    {item.tool && (
                      <span style={{ fontSize: 9, color: "#06b6d4", background: "rgba(6,182,212,0.1)", padding: "1px 6px", borderRadius: 3, display: "flex", alignItems: "center", gap: 3 }}>
                        <Zap size={8} /> Tool: {item.tool}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            )) : <p className="ai-text">Formulating intervention...</p>}
          </div>
        )}

        {/* Memory Context Visualization */}
        {hasAgents && incident.memory && incident.memory.length > 0 && (
          <div style={{ 
            marginTop: 20, 
            paddingTop: 12, 
            borderTop: "1px solid #1e2d4a",
          }}>
            <div style={{ 
              display: "flex", 
              alignItems: "center", 
              gap: 6, 
              fontSize: 10, 
              color: "#64748b", 
              fontWeight: 600, 
              marginBottom: 8,
              textTransform: "uppercase",
              letterSpacing: "0.05em"
            }}>
              <Brain size={10} color="#06b6d4" />
              Temporal Event Memory (Last {incident.memory.length})
            </div>
            <div style={{ display: "flex", gap: 6, overflowX: "auto", paddingBottom: 4 }}>
              {incident.memory.map((m, i) => (
                <div key={i} style={{ 
                  flex: "0 0 auto",
                  width: 100,
                  padding: "6px 8px",
                  background: "#0f172a",
                  borderRadius: 4,
                  border: "1px solid #1e2d4a",
                  fontSize: 9
                }}>
                  <div style={{ color: "#94a3b8", marginBottom: 2 }}>{m.timestamp?.split('T')[1]?.split('.')[0] || "Past"}</div>
                  <div style={{ color: m.issue === 'CRITICAL' ? '#ef4444' : '#f1f5f9', fontWeight: 500, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {m.issue}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
