import { fireEvent, render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import CircuitReplaySvg from "./CircuitReplaySvg";
import { DriverFrames, ReplayResponse } from "../types/replay.types";

function makeDriver(driver_number: number, x: (number | null)[], y: (number | null)[]): DriverFrames {
  return {
    driver_number,
    full_name: `Driver ${driver_number}`,
    name_acronym: `D${driver_number}`,
    constructor_name: "Team",
    team_colour: "3671C6",
    x,
    y,
    speed: x.map(() => 200),
    throttle: x.map(() => 100),
    brake: x.map(() => 0),
    gear: x.map(() => 6),
    drs: x.map(() => 0),
    lap: x.map(() => 1),
    position: x.map((_, i) => i + 1),
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
    frame_count: 2,
    timestamps: [0, 0.5],
    total_laps: 10,
    circuit_outline: [
      [0, 0],
      [500, 500],
      [1000, 0],
    ],
    bounds: { min_x: 0, max_x: 1000, min_y: 0, max_y: 1000, span: 1000, space: 1000 },
    has_car_data: true,
    drivers: Object.fromEntries(drivers.map((d) => [String(d.driver_number), d])),
  };
}

describe("CircuitReplaySvg", () => {
  it("renders one dot per car with valid data, and never emits NaN/undefined in the transform", () => {
    const data = replay([makeDriver(1, [100, 200], [100, 200]), makeDriver(2, [300, 400], [300, 400])]);
    const { container } = render(
      <CircuitReplaySvg replay={data} frameIndex={0} frameFraction={0} selectedDriverNumber={null} onSelectDriver={() => {}} />,
    );

    const carGroups = container.querySelectorAll("g[data-car-number]");
    expect(carGroups.length).toBe(2);
    carGroups.forEach((g) => {
      const transform = g.getAttribute("transform") ?? "";
      expect(transform).not.toMatch(/NaN|undefined/);
    });
  });

  it("does not render a car with no position data at this frame, rather than drawing a fake dot", () => {
    const data = replay([makeDriver(1, [100, 200], [100, 200]), makeDriver(2, [null, null], [null, null])]);
    const { container } = render(
      <CircuitReplaySvg replay={data} frameIndex={0} frameFraction={0} selectedDriverNumber={null} onSelectDriver={() => {}} />,
    );

    expect(container.querySelectorAll("g[data-car-number]").length).toBe(1);
  });

  it("interpolates position between the two bracketing frames using frameFraction", () => {
    const data = replay([makeDriver(1, [0, 100], [0, 0])]);
    const { container } = render(
      <CircuitReplaySvg replay={data} frameIndex={0} frameFraction={0.5} selectedDriverNumber={null} onSelectDriver={() => {}} />,
    );

    const g = container.querySelector("g[data-car-number]");
    expect(g?.getAttribute("transform")).toContain("50");
  });

  it("calls onSelectDriver when a car is clicked", () => {
    const data = replay([makeDriver(9, [100], [100])]);
    const onSelect = vi.fn();
    const { container } = render(
      <CircuitReplaySvg
        replay={{ ...data, frame_count: 1, timestamps: [0] }}
        frameIndex={0}
        frameFraction={0}
        selectedDriverNumber={null}
        onSelectDriver={onSelect}
      />,
    );

    const g = container.querySelector("g[data-car-number]");
    if (g) fireEvent.click(g);
    expect(onSelect).toHaveBeenCalledWith(9);
  });
});
