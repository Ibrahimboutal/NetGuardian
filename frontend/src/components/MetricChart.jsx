import {
  XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine, Area, ComposedChart, Bar
} from "recharts";

const METRICS = [
  { key: "latency_ms",       label: "Latency",     unit: "ms",   color: "#3b82f6", normal: 15 },
  { key: "throughput_mbps",  label: "Throughput",  unit: "Mbps", color: "#06b6d4", normal: 950 },
  { key: "packet_loss_pct",  label: "Packet Loss", unit: "%",    color: "#ef4444", normal: 0.1 },
  { key: "jitter_ms",        label: "Jitter",      unit: "ms",   color: "#f97316", normal: 2 },
  { key: "connections",      label: "Connections", unit: "",     color: "#10b981", normal: 141 },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const p = payload[0];
  const isAnomaly = p.payload?.anomaly;
  return (
    <div style={{
      background: "#0f1629", border: `1px solid ${isAnomaly ? "#ef4444" : "#1e2d4a"}`,
      borderRadius: 8, padding: "10px 14px", fontSize: 12, minWidth: 160,
      boxShadow: "0 8px 24px rgba(0,0,0,0.5)"
    }}>
      <div style={{ color: "#94a3b8", marginBottom: 4, fontSize: 11 }}>{label}</div>
      <div style={{ color: p.color, fontWeight: 700, fontSize: 16 }}>
        {typeof p.value === "number" ? p.value.toFixed(2) : p.value}
        <span style={{ fontSize: 11, fontWeight: 400, marginLeft: 3, color: "#64748b" }}>
          {p.unit}
        </span>
      </div>
      {isAnomaly && (
        <div style={{
          marginTop: 6, padding: "3px 8px", background: "rgba(239,68,68,0.15)",
          color: "#ef4444", borderRadius: 4, fontSize: 10, fontWeight: 600
        }}>
          ⚠ ANOMALY
        </div>
      )}
    </div>
  );
};

export default function MetricChart({ data, activeMetric, onMetricChange }) {
  const metric = METRICS.find(m => m.key === activeMetric) || METRICS[0];

  const chartData = data.slice(-60).map(d => ({
    ...d,
    time: d.timestamp ? new Date(d.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "",
  }));

  const anomalyIndices = chartData
    .map((d, i) => d.anomaly ? i : null)
    .filter(i => i !== null);

  return (
    <>
      <div className="chart-tabs">
        {METRICS.map(m => (
          <button
            key={m.key}
            className={`tab ${activeMetric === m.key ? "active" : ""}`}
            onClick={() => onMetricChange(m.key)}
          >
            {m.label}
          </button>
        ))}
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="metricGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor={metric.color} stopOpacity={0.25} />
                <stop offset="95%" stopColor={metric.color} stopOpacity={0.02} />
              </linearGradient>
              <linearGradient id="anomalyGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#ef4444" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0.02} />
              </linearGradient>
            </defs>

            <CartesianGrid stroke="#1e2d4a" strokeDasharray="4 4" vertical={false} />

            <XAxis
              dataKey="time"
              tick={{ fill: "#475569", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              interval={Math.floor(chartData.length / 6)}
            />
            <YAxis
              tick={{ fill: "#475569", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              width={42}
              tickFormatter={v => metric.key === "throughput_mbps" ? `${(v/1000).toFixed(1)}G` : v}
            />

            <Tooltip content={<CustomTooltip />} />

            {/* Normal baseline reference line */}
            <ReferenceLine
              y={metric.normal}
              stroke={metric.color}
              strokeDasharray="6 3"
              strokeOpacity={0.3}
              label={{ value: "baseline", fill: "#475569", fontSize: 9, position: "insideTopRight" }}
            />

            {/* Mark anomaly points with red reference lines */}
            {anomalyIndices.map(i => (
              <ReferenceLine
                key={i}
                x={chartData[i]?.time}
                stroke="#ef4444"
                strokeOpacity={0.4}
                strokeWidth={1}
              />
            ))}

            <Area
              type="monotone"
              dataKey={metric.key}
              stroke={metric.color}
              strokeWidth={2}
              fill="url(#metricGradient)"
              dot={false}
              activeDot={{ r: 5, fill: metric.color, stroke: "#0a0e1a", strokeWidth: 2 }}
            />

            {/* Anomaly bars overlay */}
            <Bar
              dataKey={d => d.anomaly ? d[metric.key] : null}
              fill="url(#anomalyGradient)"
              stroke="#ef4444"
              strokeWidth={0}
              radius={[2,2,0,0]}
              maxBarSize={6}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
