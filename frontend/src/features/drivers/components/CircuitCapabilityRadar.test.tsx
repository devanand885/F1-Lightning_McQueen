import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import CircuitCapabilityRadar from "./CircuitCapabilityRadar";
import { DriverAnalytics } from "../types/driverAnalytics.types";

function baseAnalytics(overrides: Partial<DriverAnalytics> = {}): DriverAnalytics {
  return {
    driver_number: 1,
    full_name: "Driver Alpha",
    eligible: true,
    eligibility_reason: null,
    race_sessions: 20,
    qualifying_sessions: 20,
    usable_race_laps: 900,
    race_stints: 40,
    race_pace_field_relative: 0.99,
    qualifying_pace_field_relative: 1.0,
    race_pace_teammate_relative: -0.01,
    qualifying_pace_teammate_relative: -0.01,
    degradation_slope: 0.02,
    degradation_stints_used: 30,
    consistency_cv: 0.08,
    start_performance_delta: 0.1,
    dry_laps: 850,
    wet_laps: 50,
    dry_pace_ratio: 0.99,
    wet_pace_ratio: 1.01,
    wet_sample_sufficient: true,
    wet_sample_threshold: 20,
    pace_trend: [],
    circuit_type_breakdown: [],
    archetype: null,
    ...overrides,
  };
}

describe("CircuitCapabilityRadar", () => {
  it("shows a loading state", () => {
    render(<CircuitCapabilityRadar analytics={undefined} isLoading />);
    expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });

  it("shows an insufficient-data state with fewer than 2 circuit types", () => {
    const analytics = baseAnalytics({
      circuit_type_breakdown: [{ circuit_type: "Low-Speed", race_pace_teammate_relative: -0.01, n_sessions: 5 }],
    });

    render(<CircuitCapabilityRadar analytics={analytics} isLoading={false} />);

    expect(screen.getByText(/Insufficient data/i)).toBeInTheDocument();
  });

  it("renders the radar once there are enough circuit types", () => {
    const analytics = baseAnalytics({
      circuit_type_breakdown: [
        { circuit_type: "Low-Speed", race_pace_teammate_relative: -0.01, n_sessions: 5 },
        { circuit_type: "Medium-Speed", race_pace_teammate_relative: 0.005, n_sessions: 4 },
        { circuit_type: "High-Speed", race_pace_teammate_relative: -0.02, n_sessions: 6 },
      ],
    });

    render(<CircuitCapabilityRadar analytics={analytics} isLoading={false} />);

    expect(screen.getByText("Circuit Capability")).toBeInTheDocument();
    expect(screen.queryByText(/Insufficient data/i)).not.toBeInTheDocument();
  });
});
