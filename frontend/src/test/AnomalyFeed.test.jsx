import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import AnomalyFeed from "../components/AnomalyFeed";

const makeEvent = (overrides = {}) => ({
  node_id: "Router-01",
  primary_metric: "latency_ms",
  severity: "high",
  anomaly_score: 0.88,
  metrics: { latency_ms: 350, throughput_mbps: 200 },
  timestamp: new Date().toISOString(),
  ...overrides,
});

describe("AnomalyFeed", () => {
  it("shows empty state when no events", () => {
    render(<AnomalyFeed events={[]} />);
    expect(screen.getByText(/No anomalies/i)).toBeInTheDocument();
  });

  it("renders a feed item for each event", () => {
    const events = [makeEvent(), makeEvent({ severity: "medium", node_id: "Router-02" })];
    render(<AnomalyFeed events={events} />);
    expect(screen.getByText(/Router-01/)).toBeInTheDocument();
    expect(screen.getByText(/Router-02/)).toBeInTheDocument();
  });

  it("shows severity badges for events", () => {
    render(<AnomalyFeed events={[makeEvent({ severity: "high" })]} />);
    expect(screen.getByText(/high/i)).toBeInTheDocument();
  });

  it("shows the primary metric name", () => {
    render(<AnomalyFeed events={[makeEvent({ primary_metric: "packet_loss_pct" })]} />);
    // The component maps "packet_loss_pct" → "Packet Loss"
    expect(screen.getByText(/Packet Loss/)).toBeInTheDocument();
  });
});
