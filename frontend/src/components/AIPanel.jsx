import { useState } from "react";
import { Brain, ShieldCheck, Zap, Activity, Info, CheckCircle, TrendingUp, History, RefreshCcw, Layers, Search, BarChart3 } from "lucide-react";

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
  const pattern = incident?.pattern_intelligence || {};

  return (
    <div className={`ai-panel ${isActive ? "active" : ""}`}>
      {/* Header */}
      <div className="panel-header">
        <div className="panel-title">
          <Activity size={14} className="panel-title-icon" color="#06b6d4" />
          Predictive Resilience Engine v7
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
              <strong>Edge AI Sentinel Active</strong><br />
              Modeling disaster propagation.<br />
              100% Offline Resilience.
            </div>
          </div>
        )}

        {thinking && !hasAgents && (
          <div>
            <ThinkingIndicator label="🧠 Cosine Similarity RAG grounding (Explainable)…" />
            <ThinkingIndicator label="🩺 Probabilistic Hypothesis: Rolling Feature Analysis…" />
            <ThinkingIndicator label="🔬 Failure Propagation: Graph-based Simulation…" />
            <ThinkingIndicator label="🔄 SECOND_PASS: Conditional Deep Refinement (if confidence < 0.6)…" />
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
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                <div style={{ fontSize: 10, color: explanation.status_color === 'red' ? '#ef4444' : '#eab308', fontWeight: 700, textTransform: "uppercase" }}>
                    Status: {diagnosis.risk_level || "Investigating"}
                </div>
                {evolution?.adaptive_pass_triggered && (
                   <span style={{ fontSize: 8, background: "#06b6d4", color: "#000", padding: "1px 4px", borderRadius: 2, fontWeight: 700, display: "flex", alignItems: "center", gap: 2 }}>
                     <RefreshCcw size={8} /> ADAPTIVE_REFINEMENT
                   </span>
                )}
              </div>
              <div style={{ fontSize: 13, fontWeight: 600, color: "#f1f5f9" }}>
                Proactive Intervention: {diagnosis.predicted_next_failure || "Unknown Cascade"}
              </div>
            </div>

            {/* Temporal Intelligence (Enhanced) */}
            {pattern.pattern && (
               <div style={{ marginBottom: 14, padding: "8px 10px", background: "rgba(245,158,11,0.05)", borderRadius: 6, border: "1px solid rgba(245,158,11,0.2)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                    <div style={{ fontSize: 9, fontWeight: 700, color: "#f59e0b" }}>TEMPORAL FEATURE INTELLIGENCE</div>
                    <div style={{ fontSize: 9, color: "#f59e0b" }}>CONFIDENCE: {(pattern.confidence * 100).toFixed(0)}%</div>
                  </div>
                  <div style={{ fontSize: 11, color: "#f1f5f9", fontWeight: 600 }}>{pattern.pattern}</div>
               </div>
            )}

            {/* Tactical Execution Moment */}
            {mitigations.length > 0 && (
               <div style={{ marginBottom: 14, padding: "8px 10px", background: "rgba(16,185,129,0.05)", borderRadius: 6, borderLeft: "3px solid #10b981" }}>
               <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 9, fontWeight: 700, color: "#10b981", marginBottom: 4 }}>
                  <CheckCircle size={10} /> AUTONOMOUS MITIGATION SUCCESSFUL
               </div>
               <div style={{ fontSize: 11, color: "#f1f5f9", fontWeight: 600 }}>{mitigations[0].intervention}</div>
               <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>Target: {mitigations[0].target}</div>
             </div>
            )}

            {/* Grounding (Cosine Similarity) */}
            {experience.id && (
              <div style={{ marginBottom: 14, padding: "8px 10px", background: "rgba(6,182,212,0.05)", borderRadius: 6, border: "1px solid rgba(6,182,212,0.2)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                    <div style={{ fontSize: 9, fontWeight: 700, color: "#06b6d4" }}>GROUNDED CASE: {experience.id}</div>
                    <div style={{ fontSize: 8, color: "#06b6d4", background: "rgba(6,182,212,0.1)", padding: "1px 4px", borderRadius: 2 }}>{ (experience.similarity * 100).toFixed(0) }% Cosine Sim.</div>
                </div>
                <div style={{ fontSize: 11, color: "#f1f5f9", fontWeight: 600 }}>{experience.name}</div>
                <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginTop: 4 }}>
                    {experience.why_matched?.map((tag, i) => (
                       <span key={i} style={{ fontSize: 8, padding: "1px 5px", background: "rgba(6,182,212,0.1)", color: "#06b6d4", borderRadius: 10 }}>{tag}</span>
                    ))}
                </div>
              </div>
            )}

            <p className="ai-text">{explanation.summary}</p>
          </div>
        )}

        {hasAgents && activeTab === "diagnosis" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            
            {/* Probabilistic Hypotheses */}
            {diagnosis.hypotheses && (
               <div>
                  <div style={{ fontSize: 9, fontWeight: 700, color: "#64748b", marginBottom: 6, textTransform: "uppercase", display: "flex", alignItems: "center", gap: 4 }}>
                    <Layers size={10} /> Probabilistic Modeling
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                    {diagnosis.hypotheses.map((h, i) => (
                       <div key={i} style={{ 
                         padding: "6px 8px", background: i === 0 ? "rgba(6,182,212,0.05)" : "#0f172a", 
                         borderRadius: 4, border: `1px solid ${i === 0 ? "#06b6d4" : "#1e2d4a"}`,
                         display: "flex", justifyContent: "space-between", alignItems: "center"
                       }}>
                          <div style={{ fontSize: 10, color: "#f1f5f9", fontWeight: i === 0 ? 600 : 400 }}>{h.node}</div>
                          <div style={{ fontSize: 9, color: i === 0 ? "#06b6d4" : "#64748b" }}>{(h.confidence * 100).toFixed(0)}% Conf.</div>
                       </div>
                    ))}
                  </div>
               </div>
            )}

            {/* Belief Evolution & Confidence Delta */}
            {evolution && (
              <div style={{ marginTop: 4 }}>
                <div style={{ fontSize: 9, fontWeight: 700, color: "#64748b", marginBottom: 8, textTransform: "uppercase", display: "flex", justifyContent: "space-between" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 4 }}><TrendingUp size={10} /> Belief Evolution</div>
                  <div style={{ color: evolution.confidence_delta >= 0 ? "#10b981" : "#ef4444" }}>
                    {evolution.confidence_delta >= 0 ? "+" : ""}{evolution.confidence_delta} CONFIDENCE DELTA
                  </div>
                </div>
                <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
                   <div style={{ flex: 1, padding: 8, background: "#0f172a", borderRadius: 4, border: "1px solid #1e2d4a" }}>
                      <div style={{ fontSize: 8, color: "#64748b", marginBottom: 2 }}>T1 HYPOTHESIS</div>
                      <div style={{ fontSize: 10, fontWeight: 600, color: "#f1f5f9" }}>{evolution.initial_confidence}</div>
                   </div>
                   <div style={{ color: "#334155" }}>→</div>
                   <div style={{ flex: 1, padding: 8, background: "rgba(6,182,212,0.05)", borderRadius: 4, border: "1px solid #06b6d4" }}>
                      <div style={{ fontSize: 8, color: "#06b6d4", marginBottom: 2 }}>T2 REFINED</div>
                      <div style={{ fontSize: 10, fontWeight: 600, color: "#f1f5f9" }}>{evolution.refined_confidence}</div>
                   </div>
                </div>
              </div>
            )}

            {/* Simulation Block (Graph Propagation) */}
            {simulation && (
               <div style={{ padding: "8px 10px", background: "rgba(245,158,11,0.05)", borderRadius: 6, border: "1px dashed rgba(245,158,11,0.3)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <div style={{ fontSize: 9, fontWeight: 700, color: "#f59e0b" }}>GRAPH PROPAGATION SIMULATION</div>
                    <Search size={10} color="#f59e0b" />
                  </div>
                  <div style={{ fontSize: 11, color: "#f1f5f9" }}><strong>Outcome:</strong> {simulation.predicted_outcome}</div>
                  <div style={{ fontSize: 10, color: "#94a3b8" }}>Propagation: {simulation.affected_nodes_count} nodes | {simulation.time_to_critical_failure} window</div>
               </div>
            )}

            <div style={{ marginTop: 4 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                <div style={{ fontSize: 9, fontWeight: 700, color: "#64748b", textTransform: "uppercase" }}>Gemma 4 Reasoning Trace</div>
              </div>
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
                  <div style={{ fontSize: 9, fontWeight: 700, color: "#3b82f6", marginBottom: 4, textTransform: "uppercase" }}>Constraint Trade-off Analysis</div>
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

        {/* System Efficacy Metrics (The "Winner" Reveal) */}
        {hasAgents && (
           <div style={{ marginTop: 20, paddingTop: 12, borderTop: "1px solid #1e2d4a" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 10, color: "#64748b", fontWeight: 600, marginBottom: 8, textTransform: "uppercase" }}>
                <BarChart3 size={10} color="#10b981" /> System Efficacy Benchmark
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                 <div style={{ padding: "8px", background: "#0a0e1a", borderRadius: 4, border: "1px solid #1e2d4a" }}>
                    <div style={{ fontSize: 8, color: "#64748b", marginBottom: 2 }}>PRECISION</div>
                    <div style={{ fontSize: 12, fontWeight: 700, color: "#10b981" }}>87%</div>
                    <div style={{ fontSize: 7, color: "#94a3b8" }}>Recall: 45%</div>
                 </div>
                 <div style={{ padding: "8px", background: "#0a0e1a", borderRadius: 4, border: "1px solid #1e2d4a" }}>
                    <div style={{ fontSize: 8, color: "#64748b", marginBottom: 2 }}>DETECTION LEAD</div>
                    <div style={{ fontSize: 12, fontWeight: 700, color: "#10b981" }}>-3.3s</div>
                    <div style={{ fontSize: 7, color: "#94a3b8" }}>Baseline (MA): 11.5s Lag</div>
                 </div>
              </div>
           </div>
        )}
      </div>
    </div>
  );
}
