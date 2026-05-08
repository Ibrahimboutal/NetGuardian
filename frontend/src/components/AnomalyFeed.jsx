import { AlertTriangle, CheckCircle } from "lucide-react";

function FeedItem({ event }) {
  const sev = event.severity || "low";
  const ts = event.timestamp
    ? new Date(event.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
    : "—";

  const metricLabels = {
    latency_ms: "Latency",
    throughput_mbps: "Throughput",
    packet_loss_pct: "Packet Loss",
    jitter_ms: "Jitter",
    connections: "Connections",
  };

  return (
    <div className={`feed-item ${sev}`}>
      <span className={`feed-dot ${sev}`} />
      <div className="feed-content">
        <div className="feed-metric">
          {metricLabels[event.primary_metric] || event.primary_metric || "Network"} Anomaly
        </div>
        <div className="feed-values">
          Latency {event.latency_ms}ms · Loss {event.packet_loss_pct}% · Score {(event.anomaly_score ?? event.score ?? 0).toFixed(3)}
        </div>
        <div className="feed-time">{ts}</div>
      </div>
      <span className={`feed-badge badge-${sev}`}>{sev}</span>
    </div>
  );
}

export default function AnomalyFeed({ events }) {
  if (events.length === 0) {
    return (
      <div className="empty-feed">
        <CheckCircle size={20} color="#10b981" />
        <span>No anomalies detected</span>
      </div>
    );
  }

  return (
    <div className="feed-list">
      {[...events].reverse().map((evt, i) => (
        <FeedItem key={`${evt.timestamp}-${i}`} event={evt} />
      ))}
    </div>
  );
}
