import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import PerformanceTrendChart from "./PerformanceTrendChart";
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

describe("PerformanceTrendChart", () => {
  it("shows a loading state", () => {
    render(<PerformanceTrendChart analytics={undefined} isLoading />);
    expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });

  it("shows an insufficient-data state when too few sessions have pace data", () => {
    const analytics = baseAnalytics({
      pace_trend: [
        { session_id: 1, meeting_name: "Race A", date_start: "2026-01-01", race_pace_field_relative: 0.99, qualifying_pace_field_relative: null },
      ],
    });

    render(<PerformanceTrendChart analytics={analytics} isLoading={false} />);

    expect(screen.getByText(/Insufficient data/i)).toBeInTheDocument();
  });

  it("renders the chart once there are enough sessions", () => {
    const point = (n: number) => ({
      session_id: n,
      meeting_name: `Race ${n}`,
      date_start: `2026-0${n}-01`,
      race_pace_field_relative: 0.98 + n * 0.001,
      qualifying_pace_field_relative: null,
    });
    const analytics = baseAnalytics({ pace_trend: [1, 2, 3, 4, 5].map(point) });

    render(<PerformanceTrendChart analytics={analytics} isLoading={false} />);

    expect(screen.getByText("Performance Trend")).toBeInTheDocument();
    expect(screen.queryByText(/Insufficient data/i)).not.toBeInTheDocument();
  });
});
