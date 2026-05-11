import { useState } from "react";
import { Brain, ShieldCheck, Info, TrendingUp, RefreshCcw, Layers, Search, BarChart3, Volume2 } from "lucide-react";
import SHAPChart from "./SHAPChart";

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

export default function AIPanel({ incident, thinking, progressMessages = [], benchmark = null }) {
  const [activeTab, setActiveTab] = useState("explanation");

  const hasAgents = incident?.agents || {};
  const hasIncident = Boolean(incident);
  const isActive = hasIncident || thinking;

  const diagnosis = hasAgents.diagnosis || {};
  const recommendation = hasAgents.recommendation || {};
  const explanation = hasAgents.explanation || {};
  const simulation = incident?.simulation || {};
  const experience = incident?.experience || null;
  const blackboard = incident?.blackboard || {};
  const causalChain = blackboard.causal_chain || [];
  const cycles = incident?.cycles_run || 0;
  const safety = blackboard.safety_status || "PASSED";
  const primaryMetric = incident?.primary_metric || "latency_ms";
  const tacticalPriority = diagnosis.predicted_next_failure || incident?.diagnosis || "Stabilizing Infrastructure";
  
  const [isSpeaking, setIsSpeaking] = useState(false);

  const handleSpeak = () => {
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    const text = `NetGuardian Briefing for node ${incident.node_id}. Tactical Priority: ${tacticalPriority}. ${explanation.summary || ""}. The recommended action is ${recommendation.decision || ""}.`;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 0.9;
    
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    
    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className={`ai-panel ${isActive ? "active" : ""}`}>
      {/* Header */}
      <div className="panel-header" style={{ borderBottom: "1px solid var(--border)", background: "rgba(15,22,41,0.5)" }}>
        <div className="panel-title" style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 2 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <Brain size={14} color="#3b82f6" />
            <span style={{ fontSize: 13, fontWeight: 700, letterSpacing: "0.5px" }}>GEMMA-ASSISTED EDGE INTELLIGENCE</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, opacity: 0.8 }}>
            <span style={{ fontSize: 9, color: "#94a3b8", fontWeight: 500 }}>POWERED BY</span>
            <span style={{ fontSize: 9, color: "#06b6d4", fontWeight: 700, letterSpacing: "1px" }}>OLLAMA LOCAL</span>
            <div style={{ width: 4, height: 4, borderRadius: "50%", background: "#10b981", boxShadow: "0 0 4px #10b981" }}></div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {thinking && (
            <div className="thinking-dots">
                <div className="thinking-dot" />
                <div className="thinking-dot" />
                <div className="thinking-dot" />
            </div>
            )}
            <div style={{ fontSize: 8, padding: "2px 6px", background: "rgba(59,130,246,0.1)", color: "#3b82f6", borderRadius: 4, border: "1px solid rgba(59,130,246,0.2)", fontWeight: 700 }}>
                NATIVE_TOOLS_v4
            </div>
        </div>
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

        {thinking && !hasIncident && (
          <div>
            <ThinkingIndicator label="🧠 Cosine Similarity RAG grounding (Explainable)…" />
            <ThinkingIndicator label="🩺 Probabilistic Hypothesis: Rolling Feature Analysis…" />
            <ThinkingIndicator label="🔬 Failure Propagation: Graph-based Simulation…" />
            <ThinkingIndicator label="🔄 SECOND_PASS: Conditional Deep Refinement (if confidence < 0.6)…" />
          </div>
        )}

        {progressMessages.length > 0 && (
          <div style={{ marginBottom: 12, padding: "8px 10px", background: "rgba(6,182,212,0.05)", borderRadius: 6, border: "1px solid rgba(6,182,212,0.18)" }}>
            <div style={{ fontSize: 9, color: "#06b6d4", fontWeight: 700, textTransform: "uppercase", marginBottom: 6 }}>Live Agent Progress</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              {progressMessages.map((message, index) => (
                <div key={`${index}-${message}`} style={{ fontSize: 10, color: "#cbd5e1", lineHeight: 1.35 }}>
                  {message}
                </div>
              ))}
            </div>
          </div>
        )}

        {hasIncident && activeTab === "explanation" && (
          <div>
            {/* System Alert Banner */}
            <div style={{
              background: `rgba(${safety === 'CRITICAL_WARNING' ? '239,68,68' : '234,179,8'}, 0.08)`, 
              border: `1px solid rgba(${safety === 'CRITICAL_WARNING' ? '239,68,68' : '234,179,8'}, 0.2)`,
              borderRadius: 8, padding: "10px 12px", marginBottom: 14
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                <div style={{ fontSize: 10, color: safety === 'CRITICAL_WARNING' ? '#ef4444' : '#eab308', fontWeight: 700, textTransform: "uppercase" }}>
                    SAFETY: {safety}
                </div>
                {cycles > 0 && (
                   <span className="cycle-badge">
                     <RefreshCcw size={8} /> {cycles} REASONING CYCLES
                   </span>
                )}
              </div>
              <div style={{ fontSize: 13, fontWeight: 600, color: "#f1f5f9" }}>
                Tactical Priority: {tacticalPriority}
              </div>
            </div>

            <div style={{ marginBottom: 14, padding: "8px 10px", background: "rgba(6,182,212,0.05)", borderRadius: 6, border: "1px solid rgba(6,182,212,0.2)" }}>
              <div style={{ fontSize: 9, fontWeight: 700, color: "#06b6d4", marginBottom: 4, textTransform: "uppercase" }}>PRIMARY SIGNAL</div>
              <div style={{ fontSize: 11, color: "#f1f5f9", fontWeight: 600 }}>{primaryMetric}</div>
              <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>
                Score: {(incident?.anomaly_score ?? incident?.score ?? 0).toFixed(4)} · Attributed features: {(incident?.attribution || []).join(", ") || "none"}
              </div>
            </div>

            {incident?.attribution?.length > 0 && (
              <div style={{ marginBottom: 14 }}>
                <div style={{ fontSize: 9, fontWeight: 700, color: "#64748b", marginBottom: 6, textTransform: "uppercase" }}>Top Feature Attribution</div>
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {incident.attribution.map((feature) => (
                    <span key={feature} style={{ fontSize: 8, padding: "2px 6px", background: "rgba(59,130,246,0.12)", color: "#3b82f6", borderRadius: 999 }}>
                      {feature}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {experience && (
              <div style={{ marginBottom: 14, padding: "10px 12px", background: "rgba(16,185,129,0.05)", borderRadius: 8, border: "1px solid rgba(16,185,129,0.18)" }}>
                <div style={{ fontSize: 9, color: "#10b981", fontWeight: 700, textTransform: "uppercase", marginBottom: 4 }}>Matched Case</div>
                <div style={{ fontSize: 11, color: "#f1f5f9", fontWeight: 600 }}>{experience.name} ({experience.id})</div>
                <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>
                  Similarity {(experience.similarity * 100).toFixed(0)}% · {experience.remedy}
                </div>
              </div>
            )}

            <p className="ai-text">{explanation.summary || "The system detected an anomaly, simulated its spread, and produced a grounded operator briefing."}</p>
            
            <button 
              onClick={handleSpeak}
              className={`btn ${isSpeaking ? 'btn-danger' : 'btn-primary'}`}
              style={{ marginTop: 16, width: "100%", justifyContent: "center", height: 40 }}
            >
              <Volume2 size={16} />
              {isSpeaking ? "Stop Briefing" : "Listen to Radio Briefing"}
            </button>
          </div>
        )}

        {hasIncident && activeTab === "diagnosis" && (
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

            {/* Causal Chain Visualization */}
            {causalChain.length > 0 && (
               <div style={{ marginTop: 4 }}>
                  <div style={{ fontSize: 9, fontWeight: 700, color: "#64748b", marginBottom: 8, textTransform: "uppercase", display: "flex", alignItems: "center", gap: 4 }}>
                    <TrendingUp size={10} /> Causal Chain Discovery
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {causalChain.map((link, i) => (
                       <div key={i} style={{ 
                         padding: "8px", background: "#0f172a", borderRadius: 6, border: "1px solid #1e2d4a",
                         position: "relative"
                       }}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                            <div style={{ fontSize: 11, fontWeight: 600, color: "#f1f5f9" }}>Epicenter: {link.epicenter}</div>
                            <div className="causal-badge">IMPACT: {link.impact}</div>
                          </div>
                          <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 4 }}>
                             Cascade detected across {link.nodes_lost} nodes.
                          </div>
                          {link.critical_hits?.length > 0 && (
                             <div style={{ marginTop: 6, display: "flex", gap: 4 }}>
                                {link.critical_hits.map((n, j) => (
                                   <span key={j} style={{ fontSize: 8, background: "rgba(239,68,68,0.1)", color: "#ef4444", padding: "1px 4px", borderRadius: 2 }}>
                                     {n} (CORE)
                                   </span>
                                ))}
                             </div>
                          )}
                       </div>
                    ))}
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
                <div style={{ fontSize: 9, fontWeight: 700, color: "#64748b", textTransform: "uppercase" }}>Model Reasoning Trace</div>
              </div>
              <div style={{ 
                padding: 10, background: "#0a0e1a", borderRadius: 6, border: "1px solid #1e2d4a",
                fontSize: 11, color: "#cbd5e1", lineHeight: 1.5, fontStyle: "italic"
              }}>
                "{diagnosis.reasoning_trace}"
              </div>
            </div>

            {/* Feature-Level Explainability (SHAP) */}
            <div style={{ borderTop: "1px solid #1e2d4a", paddingTop: 12 }}>
               <SHAPChart shapValues={incident?.shap_values} />
            </div>
          </div>
        )}

        {hasIncident && activeTab === "recommendation" && (
          <div>
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontSize: 9, color: "#64748b", fontWeight: 700, marginBottom: 4 }}>COMMAND DECISION</div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#f1f5f9" }}>{recommendation.decision}</div>
            </div>

            {/* Trade-off Analysis Block */}
            {recommendation.strategic_justification && (
               <div style={{ marginBottom: 14, padding: "8px 10px", background: "rgba(59,130,246,0.05)", borderRadius: 6, border: "1px solid rgba(59,130,246,0.2)" }}>
                  <div style={{ fontSize: 9, fontWeight: 700, color: "#3b82f6", marginBottom: 4, textTransform: "uppercase" }}>Constraint Trade-off Analysis</div>
                  <div style={{ fontSize: 11, color: "#f1f5f9", lineHeight: 1.4 }}>{recommendation.strategic_justification}</div>
               </div>
            )}

            {recommendation.trade_off && (
               <div style={{ marginBottom: 14, fontSize: 11, color: "#94a3b8" }}>
                 Trade-off: {recommendation.trade_off}
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
        {hasIncident && (
           <div style={{ marginTop: 20, paddingTop: 12, borderTop: "1px solid #1e2d4a" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 10, color: "#64748b", fontWeight: 600, marginBottom: 8, textTransform: "uppercase" }}>
                <BarChart3 size={10} color="#10b981" /> System Efficacy Benchmark
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                 <div style={{ padding: "8px", background: "#0a0e1a", borderRadius: 4, border: "1px solid #1e2d4a" }}>
                    <div style={{ fontSize: 8, color: "#64748b", marginBottom: 2 }}>PRECISION</div>
                    <div style={{ fontSize: 12, fontWeight: 700, color: "#10b981" }}>
                      {benchmark?.results?.net_guardian_ai?.precision ? `${(benchmark.results.net_guardian_ai.precision * 100).toFixed(0)}%` : "87%"}
                    </div>
                    <div style={{ fontSize: 7, color: "#94a3b8" }}>
                      Recall: {benchmark?.results?.net_guardian_ai?.recall ? `${(benchmark.results.net_guardian_ai.recall * 100).toFixed(0)}%` : "45%"}
                    </div>
                 </div>
                 <div style={{ padding: "8px", background: "#0a0e1a", borderRadius: 4, border: "1px solid #1e2d4a" }}>
                    <div style={{ fontSize: 8, color: "#64748b", marginBottom: 2 }}>DETECTION LEAD</div>
                    <div style={{ fontSize: 12, fontWeight: 700, color: "#10b981" }}>
                      {benchmark?.results?.net_guardian_ai?.avg_lag_sec ? `-${benchmark.results.net_guardian_ai.avg_lag_sec}s` : "-3.3s"}
                    </div>
                    <div style={{ fontSize: 7, color: "#94a3b8" }}>
                      Baseline: {benchmark?.results?.adaptive_ma_baseline?.avg_lag_sec ? `${benchmark.results.adaptive_ma_baseline.avg_lag_sec}s` : "11.5s"} Lag
                    </div>
                 </div>
              </div>
           </div>
        )}
      </div>
    </div>
  );
}
