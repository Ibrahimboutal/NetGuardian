import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import React from "react";
import StatusBadge from "../components/StatusBadge";

describe("StatusBadge", () => {
  it("renders stable state", () => {
    render(<StatusBadge status="stable" anomalyCount={0} />);
    expect(screen.getByText("All Systems Stable")).toBeInTheDocument();
  });

  it("renders anomaly count when anomalous", () => {
    render(<StatusBadge status="anomaly" anomalyCount={3} />);
    expect(screen.getByText("Anomaly Detected")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });
});
