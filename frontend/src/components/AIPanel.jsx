import { useState } from "react";
import { Brain, ShieldCheck, Zap, Activity, Info, CheckCircle, TrendingUp, History } from "lucide-react";

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
  const evolution = incident?.belief_evolution;

  return (
    <div className={`ai-panel ${isActive ? "active" : ""}`}>
      {/* Header */}
      <div className="panel-header">
        <div className="panel-title">
          <Activity size={14} className="panel-title-icon" color="#06b6d4" />
          Predictive Resilience Engine v4
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
              Iterative reasoning active.
            </div>
          </div>
        )}

        {thinking && !hasAgents && (
          <div>
            <ThinkingIndicator label="🧠 RAG Grounding in past case files…" />
            <ThinkingIndicator label="🩺 Forming initial hypothesis (Belief T1)…" />
            <ThinkingIndicator label="🔬 Evolving belief via tool simulation (T2)…" />
            <ThinkingIndicator label="🔧 Weighing tactical trade-offs…" />
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
                  <CheckCircle size={10} /> PROACTIVE PREVENTION EXECUTED
               </div>
               <div style={{ fontSize: 11, color: "#f1f5f9", fontWeight: 600 }}>{mitigations[0].intervention}</div>
               <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>Target: {mitigations[0].target}</div>
             </div>
            )}

            {/* Experience Grounding (Provable) */}
            {experience.id && (
              <div style={{ marginBottom: 14, padding: "8px 10px", background: "rgba(6,182,212,0.05)", borderRadius: 6, border: "1px solid rgba(6,182,212,0.2)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                    <div style={{ fontSize: 9, fontWeight: 700, color: "#06b6d4" }}>GROUNDED CASE: {experience.id}</div>
                    <div style={{ fontSize: 9, color: "#06b6d4" }}>SIMILARITY: {(experience.similarity * 100).toFixed(0)}%</div>
                </div>
                <div style={{ fontSize: 11, color: "#f1f5f9", fontWeight: 600 }}>{experience.name}</div>
                <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>{experience.description}</div>
              </div>
            )}

            <p className="ai-text">{explanation.summary}</p>
          </div>
        )}

        {hasAgents && activeTab === "diagnosis" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            
            {/* Belief Evolution Visualizer */}
            {evolution && (
              <div style={{ marginBottom: 4 }}>
                <div style={{ fontSize: 9, fontWeight: 700, color: "#64748b", marginBottom: 8, textTransform: "uppercase", display: "flex", alignItems: "center", gap: 4 }}>
                  <TrendingUp size={10} /> Belief Evolution (Iterative Reasoning)
                </div>
                <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
                   <div style={{ flex: 1, padding: 8, background: "#0f172a", borderRadius: 4, border: "1px solid #1e2d4a" }}>
                      <div style={{ fontSize: 8, color: "#64748b", marginBottom: 2 }}>T1: HYPOTHESIS</div>
                      <div style={{ fontSize: 10, fontWeight: 600, color: "#f1f5f9" }}>{evolution.initial.risk_level} Risk</div>
                      <div style={{ fontSize: 9, color: "#94a3b8" }}>{evolution.initial.confidence} Confidence</div>
                   </div>
                   <div style={{ color: "#334155" }}>→</div>
                   <div style={{ flex: 1, padding: 8, background: "rgba(6,182,212,0.05)", borderRadius: 4, border: "1px solid #06b6d4" }}>
                      <div style={{ fontSize: 8, color: "#06b6d4", marginBottom: 2 }}>T2: REFINED (POST-TOOL)</div>
                      <div style={{ fontSize: 10, fontWeight: 600, color: "#f1f5f9" }}>{evolution.refined.risk_level} Risk</div>
                      <div style={{ fontSize: 9, color: "#06b6d4" }}>{evolution.refined.confidence} Confidence</div>
                   </div>
                </div>
              </div>
            )}

            <div className="ai-data-row">
              <span className="ai-label">PREDICTED NEXT FAILURE:</span>
              <span className="ai-value" style={{ color: "#ef4444" }}>{diagnosis.predicted_next_failure}</span>
            </div>

            {/* Simulation Block */}
            {simulation && (
               <div style={{ padding: "8px 10px", background: "rgba(245,158,11,0.05)", borderRadius: 6, border: "1px dashed rgba(245,158,11,0.3)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <div style={{ fontSize: 9, fontWeight: 700, color: "#f59e0b" }}>SIMULATION DATA (RE-GROUNDED T2)</div>
                    <Zap size={10} color="#f59e0b" />
                  </div>
                  <div style={{ fontSize: 11, color: "#f1f5f9" }}><strong>Outcome:</strong> {simulation.predicted_outcome}</div>
                  <div style={{ fontSize: 10, color: "#94a3b8" }}>Critical failure window: {simulation.time_to_critical_failure}</div>
               </div>
            )}

            {/* Reasoning Trace */}
            <div style={{ marginTop: 4 }}>
              <div style={{ fontSize: 9, fontWeight: 700, color: "#64748b", marginBottom: 6, textTransform: "uppercase" }}>Internal reasoning Trace</div>
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
              <div style={{ fontSize: 9, color: "#64748b", fontWeight: 700, marginBottom: 4 }}>COMMAND DECISION</div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#f1f5f9" }}>{recommendation.decision}</div>
            </div>

            {/* Trade-off Analysis Block */}
            {recommendation.trade_off_analysis && (
               <div style={{ marginBottom: 14, padding: "8px 10px", background: "rgba(59,130,246,0.05)", borderRadius: 6, border: "1px solid rgba(59,130,246,0.2)" }}>
                  <div style={{ fontSize: 9, fontWeight: 700, color: "#3b82f6", marginBottom: 4, textTransform: "uppercase" }}>Trade-off Analysis</div>
                  <div style={{ fontSize: 11, color: "#f1f5f9", lineHeight: 1.4 }}>{recommendation.trade_off_analysis}</div>
               </div>
            )}

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
                      <span style={{ fontSize: 9, color: "#10b981", background: "rgba(16,185,129,0.1)", padding: "1px 6px", borderRadius: 3 }}>
                        Tool: {item.tool}
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
              textTransform: "uppercase"
            }}>
              <History size={10} color="#06b6d4" />
              Event Timeline (Last {incident.memory.length})
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
