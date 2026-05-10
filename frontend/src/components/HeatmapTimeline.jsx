import { useMemo } from "react";
import { Activity } from "lucide-react";

/** Group anomaly events into 5-minute buckets and render a heatmap */
export default function HeatmapTimeline({ anomalies = [], onBucketClick }) {
  const BUCKET_MINUTES = 5;
  const NUM_BUCKETS = 48; // 4 hours of 5-min slots

  const buckets = useMemo(() => {
    const now = Date.now();
    const bucketMs = BUCKET_MINUTES * 60 * 1000;
    const slots = Array.from({ length: NUM_BUCKETS }, (_, i) => ({
      index: i,
      startMs: now - (NUM_BUCKETS - i) * bucketMs,
      endMs:   now - (NUM_BUCKETS - i - 1) * bucketMs,
      count: 0,
      worst: null,
    }));

    for (const ev of anomalies) {
      const t = ev.timestamp ? new Date(ev.timestamp).getTime() : now;
      for (const slot of slots) {
        if (t >= slot.startMs && t < slot.endMs) {
          slot.count++;
          const sevOrder = { critical: 4, high: 3, medium: 2, low: 1 };
          const cur = sevOrder[ev.severity] || 0;
          const prev = sevOrder[slot.worst] || 0;
          if (cur > prev) slot.worst = ev.severity;
          break;
        }
      }
    }
    return slots;
  }, [anomalies]);

  const maxCount = Math.max(1, ...buckets.map(b => b.count));

  function cellColor(bucket) {
    if (bucket.count === 0) return "rgba(255,255,255,0.04)";
    const intensity = bucket.count / maxCount;
    if (bucket.worst === "critical") return `rgba(239,68,68,${0.25 + intensity * 0.65})`;
    if (bucket.worst === "high")     return `rgba(249,115,22,${0.2 + intensity * 0.6})`;
    if (bucket.worst === "medium")   return `rgba(234,179,8,${0.2 + intensity * 0.55})`;
    return `rgba(16,185,129,${0.2 + intensity * 0.5})`;
  }

  function cellBorder(bucket) {
    if (bucket.count === 0) return "1px solid rgba(255,255,255,0.03)";
    if (bucket.worst === "critical") return "1px solid rgba(239,68,68,0.5)";
    if (bucket.worst === "high")     return "1px solid rgba(249,115,22,0.45)";
    return "1px solid rgba(234,179,8,0.35)";
  }

  function formatTime(ms) {
    const d = new Date(ms);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  const totalAnomalies = buckets.reduce((s, b) => s + b.count, 0);

  return (
    <div style={{
      background: "rgba(19,25,41,0.6)",
      border: "1px solid rgba(255,255,255,0.05)",
      borderRadius: 12,
      overflow: "hidden",
      backdropFilter: "blur(12px)",
      WebkitBackdropFilter: "blur(12px)",
      boxShadow: "0 8px 32px rgba(0,0,0,0.2)",
    }}>
      {/* Header */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "10px 16px", borderBottom: "1px solid rgba(255,255,255,0.05)",
        flexWrap: "wrap", gap: 8,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Activity size={13} color="#06b6d4" />
          <span style={{ fontSize: 12, fontWeight: 600, color: "#f1f5f9" }}>Anomaly Heatmap</span>
          <span style={{ fontSize: 10, color: "#64748b" }}>4h window · {BUCKET_MINUTES}min slots</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {/* Legend */}
          {[
            { label: "Normal", color: "rgba(255,255,255,0.07)" },
            { label: "Low",      color: "rgba(16,185,129,0.5)" },
            { label: "Medium",   color: "rgba(234,179,8,0.55)" },
            { label: "High",     color: "rgba(249,115,22,0.6)" },
            { label: "Critical", color: "rgba(239,68,68,0.75)" },
          ].map(l => (
            <div key={l.label} style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <div style={{ width: 10, height: 10, borderRadius: 2, background: l.color }} />
              <span style={{ fontSize: 9, color: "#64748b" }}>{l.label}</span>
            </div>
          ))}
          <span style={{
            fontSize: 10, color: totalAnomalies > 0 ? "#ef4444" : "#64748b",
            fontWeight: totalAnomalies > 0 ? 700 : 400,
          }}>
            {totalAnomalies} anomalies
          </span>
        </div>
      </div>

      {/* Heatmap grid */}
      <div style={{ padding: "10px 16px 12px" }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: `repeat(${NUM_BUCKETS}, 1fr)`,
          gap: 2,
        }}>
          {buckets.map(bucket => (
            <div
              key={bucket.index}
              title={`${formatTime(bucket.startMs)} — ${bucket.count} anomalies${bucket.worst ? ` (worst: ${bucket.worst})` : ""}`}
              onClick={() => onBucketClick && onBucketClick(bucket)}
              style={{
                height: 18,
                borderRadius: 2,
                background: cellColor(bucket),
                border: cellBorder(bucket),
                cursor: bucket.count > 0 ? "pointer" : "default",
                transition: "transform 0.15s, opacity 0.15s",
                boxShadow: bucket.count > 0 && bucket.worst === "critical"
                  ? "0 0 4px rgba(239,68,68,0.5)" : "none",
              }}
              onMouseEnter={e => { if (bucket.count > 0) e.target.style.transform = "scaleY(1.3)"; }}
              onMouseLeave={e => { e.target.style.transform = "scaleY(1)"; }}
            />
          ))}
        </div>

        {/* Time axis labels */}
        <div style={{
          display: "flex", justifyContent: "space-between",
          marginTop: 4, paddingTop: 2,
        }}>
          {[0, 12, 24, 36, 47].map(i => (
            <span key={i} style={{ fontSize: 8, color: "#475569" }}>
              {formatTime(buckets[i]?.startMs ?? Date.now())}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
