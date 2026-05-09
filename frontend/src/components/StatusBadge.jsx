import React from "react";

export default function StatusBadge({ status, anomalyCount }) {
  const states = {
    stable:     { label: "All Systems Stable", cls: "stable" },
    anomaly:    { label: `Anomaly Detected`, cls: "anomaly" },
    connecting: { label: "Connecting…", cls: "connecting" },
  };
  const s = states[status] || states.connecting;

  return (
    <div className={`status-badge ${s.cls}`}>
      <span className="status-dot" />
      {s.label}
      {status === "anomaly" && anomalyCount > 0 && (
        <span className="anomaly-count-badge">{anomalyCount}</span>
      )}
    </div>
  );
}
