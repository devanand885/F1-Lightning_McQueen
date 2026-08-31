import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import Leaderboard from "./Leaderboard";
import { DriverFrames, ReplayResponse } from "../types/replay.types";

function makeDriver(driver_number: number, full_name: string, position: number | null): DriverFrames {
  return {
    driver_number,
    full_name,
    name_acronym: full_name.slice(0, 3).toUpperCase(),
    constructor_name: "Team",
    team_colour: "FF0000",
    x: [0],
    y: [0],
    speed: [0],
    throttle: [0],
    brake: [0],
    gear: [0],
    drs: [0],
    lap: [1],
    position: [position],
  };
}

function replay(drivers: DriverFrames[]): ReplayResponse {
  return {
    available: true,
    reason: null,
    session_key: 1,
    meeting_name: "Test GP",
    season: 2099,
    date_from: null,
    date_to: null,
    grid_step_seconds: 0.5,
    frame_count: 1,
    timestamps: [0],
    total_laps: 10,
    circuit_outline: [],
    bounds: { min_x: 0, max_x: 1, min_y: 0, max_y: 1, span: 1, space: 1000 },
    has_car_data: true,
    drivers: Object.fromEntries(drivers.map((d) => [String(d.driver_number), d])),
  };
}

describe("Leaderboard", () => {
  it("orders drivers by real current position, not a fixed order", () => {
    const data = replay([makeDriver(1, "Driver A", 3), makeDriver(2, "Driver B", 1), makeDriver(3, "Driver C", 2)]);
    render(<Leaderboard replay={data} frameIndex={0} selectedDriverNumber={null} onSelectDriver={() => {}} />);

    const rows = screen.getAllByRole("button").map((el) => el.textContent);
    expect(rows[0]).toContain("Driver B");
    expect(rows[1]).toContain("Driver C");
    expect(rows[2]).toContain("Driver A");
  });

  it("excludes drivers with no position data at this frame rather than showing a fake rank", () => {
    const data = replay([makeDriver(1, "Driver A", 1), makeDriver(2, "Driver B", null)]);
    render(<Leaderboard replay={data} frameIndex={0} selectedDriverNumber={null} onSelectDriver={() => {}} />);

    expect(screen.getByText("Driver A")).toBeInTheDocument();
    expect(screen.queryByText("Driver B")).not.toBeInTheDocument();
  });

  it("calls onSelectDriver when a row is clicked", () => {
    const data = replay([makeDriver(7, "Driver Seven", 1)]);
    const onSelect = vi.fn();
    render(<Leaderboard replay={data} frameIndex={0} selectedDriverNumber={null} onSelectDriver={onSelect} />);

    fireEvent.click(screen.getByText("Driver Seven"));
    expect(onSelect).toHaveBeenCalledWith(7);
  });
});
