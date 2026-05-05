import { useState } from "react";
import { Brain, Stethoscope, Wrench, MessageSquare } from "lucide-react";

const TABS = [
  { id: "explanation", label: "Summary",       icon: MessageSquare },
  { id: "diagnosis",   label: "Diagnosis",     icon: Stethoscope },
  { id: "recommendation", label: "Actions",    icon: Wrench },
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

function parseRecommendations(text) {
  if (!text) return [];
  return text
    .split("\n")
    .filter(l => l.trim())
    .map(l => l.replace(/^\d+\.\s*/, "").trim())
    .filter(l => l.length > 0);
}

export default function AIPanel({ incident, thinking }) {
  const [activeTab, setActiveTab] = useState("explanation");

  const hasAgents = incident?.agents;
  const isActive = hasAgents || thinking;

  const diagnosis = hasAgents?.diagnosis || {};
  const recommendation = hasAgents?.recommendation || {};
  const explanation = hasAgents?.explanation || {};

  return (
    <div className={`ai-panel ${isActive ? "active" : ""}`}>
      {/* Header */}
      <div className="panel-header">
        <div className="panel-title">
          <Brain size={14} className="panel-title-icon" color="#06b6d4" />
          Gemma AI Multi-Agent Logic
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
              Monitoring critical infrastructure.<br />
              Agents activate on anomaly detection.
            </div>
          </div>
        )}

        {thinking && !hasAgents && (
          <div>
            <ThinkingIndicator label="🩺 Specialized Diagnosis Agent analyzing telemetry…" />
            <ThinkingIndicator label="🔧 Incident Commander formulating response…" />
            <ThinkingIndicator label="📢 Crisis Communicator generating report…" />
          </div>
        )}

        {hasAgents && activeTab === "explanation" && (
          <div>
            <div style={{
              background: `rgba(${explanation.status_color === 'red' ? '239,68,68' : '234,179,8'}, 0.08)`, 
              border: `1px solid rgba(${explanation.status_color === 'red' ? '239,68,68' : '234,179,8'}, 0.2)`,
              borderRadius: 8, padding: "10px 12px", marginBottom: 14
            }}>
              <div style={{ fontSize: 10, color: explanation.status_color === 'red' ? '#ef4444' : '#eab308', fontWeight: 700, marginBottom: 4, textTransform: "uppercase" }}>
                System Status: Investigation Active
              </div>
              <div style={{ fontSize: 13, fontWeight: 600, color: "#f1f5f9" }}>
                {diagnosis.issue || "Investigating Incident"}
              </div>
              <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 4 }}>
                Estimated Resolution: <strong>{explanation.eta_guess || "TBD"}</strong>
              </div>
            </div>
            <p className="ai-text">{explanation.summary}</p>
          </div>
        )}

        {hasAgents && activeTab === "diagnosis" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div className="ai-data-row">
              <span className="ai-label">ISSUE:</span>
              <span className="ai-value">{diagnosis.issue}</span>
            </div>
            <div className="ai-data-row">
              <span className="ai-label">ROOT CAUSE:</span>
              <span className="ai-value">{diagnosis.root_cause}</span>
            </div>
            <div className="ai-data-row">
              <span className="ai-label">IMPACT:</span>
              <span className="ai-value" style={{ color: "#ef4444" }}>{diagnosis.impact}</span>
            </div>
            <div style={{ marginTop: 8 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "#64748b", marginBottom: 4 }}>
                <span>ANALYSIS CONFIDENCE</span>
                <span>{diagnosis.confidence}</span>
              </div>
              <div style={{ height: 4, background: "#1e2d4a", borderRadius: 2, overflow: "hidden" }}>
                <div style={{ 
                  height: "100%", background: "#06b6d4", 
                  width: diagnosis.confidence || "0%",
                  transition: "width 1s ease-out"
                }} />
              </div>
            </div>
          </div>
        )}

        {hasAgents && activeTab === "recommendation" && (
          <div>
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
                    <span style={{ fontSize: 9, color: "#475569" }}>Difficulty: {item.difficulty}</span>
                  </div>
                </div>
              </div>
            )) : <p className="ai-text">Formulating actions...</p>}
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
              Agent Memory Context (Last {incident.memory.length} Events)
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
                  <div style={{ color: "#f1f5f9", fontWeight: 500, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
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
