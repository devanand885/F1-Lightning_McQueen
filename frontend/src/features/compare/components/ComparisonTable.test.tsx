import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ComparisonTable from "./ComparisonTable";
import { ComparisonResponse } from "../types/compare.types";

const comparison: ComparisonResponse = {
  entity_type: "driver",
  season: 2025,
  entities: [
    { id: 1, label: "Max Verstappen", colour: "3671C6" },
    { id: 44, label: "Lewis Hamilton", colour: "E80020" },
  ],
  metrics: [
    { key: "points", label: "Points", unit: null, values: [400, 250] },
    { key: "avg_finish", label: "Average Finish", unit: "position", values: [2.456, null] },
    { key: "dnf_rate", label: "DNF Rate", unit: "%", values: [0.05, 0.2] },
  ],
};

describe("ComparisonTable", () => {
  it("renders both entity names as column headers", () => {
    render(<ComparisonTable comparison={comparison} />);

    expect(screen.getByText("Max Verstappen")).toBeInTheDocument();
    expect(screen.getByText("Lewis Hamilton")).toBeInTheDocument();
  });

  it("formats a percent-unit metric as a real percentage, not a raw fraction", () => {
    render(<ComparisonTable comparison={comparison} />);

    expect(screen.getByText("5.0%")).toBeInTheDocument();
    expect(screen.getByText("20.0%")).toBeInTheDocument();
  });

  it("rounds plain numeric metrics and keeps one decimal for average finish", () => {
    render(<ComparisonTable comparison={comparison} />);

    expect(screen.getByText("400")).toBeInTheDocument();
    expect(screen.getByText("2.5")).toBeInTheDocument();
  });

  it("shows a dash instead of fabricating a missing value", () => {
    render(<ComparisonTable comparison={comparison} />);

    expect(screen.getByText("—")).toBeInTheDocument();
  });
});
