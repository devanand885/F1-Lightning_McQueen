import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import TelemetryPanel from "./TelemetryPanel";
import { DriverFrames } from "../types/replay.types";

function driver(overrides: Partial<DriverFrames> = {}): DriverFrames {
  return {
    driver_number: 1,
    full_name: "Max Verstappen",
    name_acronym: "VER",
    constructor_name: "Red Bull Racing",
    team_colour: "3671C6",
    x: [0],
    y: [0],
    speed: [318],
    throttle: [100],
    brake: [0],
    gear: [8],
    drs: [12],
    lap: [12],
    position: [1],
    ...overrides,
  };
}

describe("TelemetryPanel", () => {
  it("shows a prompt when no car is selected", () => {
    render(<TelemetryPanel driver={null} frameIndex={0} hasCarData />);
    expect(screen.getByText(/No car selected/i)).toBeInTheDocument();
  });

  it("shows real telemetry values for the selected car at the current frame", () => {
    render(<TelemetryPanel driver={driver()} frameIndex={0} hasCarData />);
    expect(screen.getByText("Max Verstappen")).toBeInTheDocument();
    expect(screen.getByText("P1")).toBeInTheDocument();
    expect(screen.getByText("318 km/h")).toBeInTheDocument();
    expect(screen.getByText("100%")).toBeInTheDocument();
    expect(screen.getByText("ON")).toBeInTheDocument();
  });

  it("shows N/A rather than fabricating a value when telemetry is missing at this frame", () => {
    const d = driver({ speed: [null], throttle: [null], brake: [null], gear: [null], drs: [null] });
    render(<TelemetryPanel driver={d} frameIndex={0} hasCarData />);
    expect(screen.getAllByText("N/A").length).toBeGreaterThan(0);
  });

  it("discloses when a session has no car telemetry at all", () => {
    render(<TelemetryPanel driver={driver()} frameIndex={0} hasCarData={false} />);
    expect(screen.getByText(/no car telemetry/i)).toBeInTheDocument();
  });
});
