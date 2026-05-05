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

  return (
    <div className={`ai-panel ${isActive ? "active" : ""}`}>
      {/* Header */}
      <div className="panel-header">
        <div className="panel-title">
          <Brain size={14} className="panel-title-icon" color="#06b6d4" />
          Gemma AI Response
        </div>
        {thinking && (
          <div style={{ display: "flex", gap: 4 }}>
            <div className="thinking-dot" />
            <div className="thinking-dot" />
            <div className="thinking-dot" />
          </div>
        )}
        {hasAgents && (
          <span style={{
            fontSize: 10, background: "rgba(16,185,129,0.15)", color: "#10b981",
            padding: "2px 8px", borderRadius: 4, fontWeight: 600
          }}>
            ✓ COMPLETE
          </span>
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
        {!isActive && !incident && (
          <div className="ai-empty">
            <div className="ai-empty-icon">🤖</div>
            <div className="ai-empty-text">
              Monitoring network traffic.<br />
              AI agents will activate on anomaly detection.
            </div>
          </div>
        )}

        {thinking && !hasAgents && (
          <div>
            <ThinkingIndicator label="Running Diagnosis Agent…" />
            <ThinkingIndicator label="Running Recommendation Agent…" />
            <ThinkingIndicator label="Generating Explanation…" />
          </div>
        )}

        {hasAgents && activeTab === "explanation" && (
          <div>
            {/* Incident metadata */}
            <div style={{
              background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.2)",
              borderRadius: 8, padding: "10px 12px", marginBottom: 14
            }}>
              <div style={{ fontSize: 11, color: "#ef4444", fontWeight: 700, marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                ⚠ Incident Report
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4px 12px" }}>
                {[
                  ["Severity", incident.severity?.toUpperCase()],
                  ["Latency",  `${incident.latency_ms}ms`],
                  ["Packet Loss", `${incident.packet_loss_pct}%`],
                  ["Throughput", `${incident.throughput_mbps} Mbps`],
                ].map(([k, v]) => (
                  <div key={k} style={{ fontSize: 11 }}>
                    <span style={{ color: "#64748b" }}>{k}: </span>
                    <span style={{ color: "#f1f5f9", fontWeight: 600 }}>{v}</span>
                  </div>
                ))}
              </div>
            </div>
            <p className="ai-text">{incident.agents.explanation}</p>
          </div>
        )}

        {hasAgents && activeTab === "diagnosis" && (
          <div>
            <div style={{ fontSize: 11, color: "#94a3b8", marginBottom: 10 }}>
              <span style={{ color: "#06b6d4", fontWeight: 600 }}>🩺 Root Cause Analysis</span>
            </div>
            <p className="ai-text">{incident.agents.diagnosis}</p>
          </div>
        )}

        {hasAgents && activeTab === "recommendation" && (
          <div>
            <div style={{ fontSize: 11, color: "#94a3b8", marginBottom: 10 }}>
              <span style={{ color: "#3b82f6", fontWeight: 600 }}>🔧 Recommended Actions</span>
            </div>
            <div>
              {parseRecommendations(incident.agents.recommendation).map((action, i) => (
                <div key={i} className="ai-recommendation-item">
                  <div className="ai-rec-num">{i + 1}</div>
                  <div className="ai-rec-text">{action}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
