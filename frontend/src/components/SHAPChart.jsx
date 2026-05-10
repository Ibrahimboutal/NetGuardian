import React from "react";

/**
 * SHAP (SHapley Additive exPlanations) Chart
 * Visualizes feature contributions to the anomaly score.
 */
export default function SHAPChart({ shapValues }) {
  if (!shapValues || Object.keys(shapValues).length === 0) {
    return (
      <div style={{ padding: "10px", fontSize: "11px", color: "#64748b", fontStyle: "italic" }}>
        No attribution data available for this sample.
      </div>
    );
  }

  // Convert to array and sort by absolute value
  const features = Object.entries(shapValues)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, 5); // Show top 5 features

  const maxValue = Math.max(...features.map(f => Math.abs(f.value)), 0.001);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ fontSize: 9, fontWeight: 700, color: "#64748b", textTransform: "uppercase" }}>
          Feature Attribution (SHAP)
        </div>
        <div style={{ fontSize: 8, color: "#94a3b8" }}>
          <span style={{ color: "#ef4444" }}>●</span> Anomaly <span style={{ marginLeft: 6, color: "#3b82f6" }}>●</span> Normal
        </div>
      </div>
      
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {features.map((feature, idx) => {
          const percentage = (Math.abs(feature.value) / maxValue) * 100;
          const isAnomalyContribution = feature.value < 0; // In Isolation Forest, negative = anomaly

          return (
            <div key={idx} style={{ display: "flex", flexDirection: "column", gap: 2 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10 }}>
                <span style={{ color: "#cbd5e1" }}>{feature.name}</span>
                <span style={{ color: isAnomalyContribution ? "#ef4444" : "#3b82f6", fontWeight: 600 }}>
                  {feature.value.toFixed(4)}
                </span>
              </div>
              <div style={{ 
                height: 4, 
                width: "100%", 
                background: "rgba(30,41,59,0.5)", 
                borderRadius: 2, 
                overflow: "hidden",
                position: "relative"
              }}>
                <div style={{ 
                  position: "absolute",
                  left: "50%",
                  height: "100%",
                  width: "1px",
                  background: "rgba(255,255,255,0.1)",
                  zIndex: 1
                }} />
                <div style={{ 
                  position: "absolute",
                  left: isAnomalyContribution ? `${50 - percentage/2}%` : "50%",
                  width: `${percentage/2}%`,
                  height: "100%",
                  background: isAnomalyContribution ? "linear-gradient(90deg, #ef4444, #f87171)" : "linear-gradient(90deg, #3b82f6, #60a5fa)",
                  borderRadius: 2,
                  transition: "width 0.5s ease-out, left 0.5s ease-out"
                }} />
              </div>
            </div>
          );
        })}
      </div>
      
      <div style={{ fontSize: 8, color: "#475569", lineHeight: 1.4, padding: "4px 0" }}>
        <i>SHAP values indicate how each feature shifted the prediction away from the model's base expectation.</i>
      </div>
    </div>
  );
}
