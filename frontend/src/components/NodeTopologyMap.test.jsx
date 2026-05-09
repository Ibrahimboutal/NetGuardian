import React from "react";
import { render, screen, within } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import NodeTopologyMap from "./NodeTopologyMap";

describe("NodeTopologyMap", () => {
  it("renders the topology header", () => {
    render(<NodeTopologyMap anomalies={[]} />);
    expect(screen.getByText("Node Topology")).toBeInTheDocument();
  });

  it("shows all healthy counts when no anomalies", () => {
    render(<NodeTopologyMap anomalies={[]} />);
    // 15 nodes, all healthy
    expect(screen.getByText(/15 Healthy/)).toBeInTheDocument();
    expect(screen.getByText(/0 Warning/)).toBeInTheDocument();
    expect(screen.getByText(/0 Critical/)).toBeInTheDocument();
  });

  it("upgrades a node to critical when an anomaly with severity=critical is present", () => {
    const anomalies = [
      { node_id: "Core-DC-01", severity: "critical", anomaly_score: 0.95 },
    ];
    render(<NodeTopologyMap anomalies={anomalies} />);
    expect(screen.getByText(/1 Critical/)).toBeInTheDocument();
  });

  it("upgrades a node to warning for high-severity anomalies", () => {
    const anomalies = [
      { node_id: "Router-01", severity: "high", anomaly_score: 0.75 },
    ];
    render(<NodeTopologyMap anomalies={anomalies} />);
    expect(screen.getByText(/1 Warning/)).toBeInTheDocument();
  });

  it("renders abbreviated node labels", () => {
    render(<NodeTopologyMap anomalies={[]} />);
    // "Core-DC-01" → "C-1", Router-01 → "R-01"
    expect(screen.getByText("C-1")).toBeInTheDocument();
    expect(screen.getByText("R-01")).toBeInTheDocument();
  });
});
