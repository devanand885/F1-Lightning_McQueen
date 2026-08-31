import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import RaceSelector from "./RaceSelector";
import { RaceOption } from "../types/replay.types";

const races: RaceOption[] = [
  { session_key: 100, season: 2025, meeting_name: "Australian Grand Prix", circuit_short_name: "Melbourne", date_start: "2025-03-16" },
  { session_key: 200, season: 2026, meeting_name: "Bahrain Grand Prix", circuit_short_name: "Sakhir", date_start: "2026-04-12" },
];

describe("RaceSelector", () => {
  it("only offers seasons/races that are dynamically populated from the backend, defaulting to the latest season", () => {
    render(<RaceSelector races={races} onLoad={() => {}} />);
    expect(screen.getByText(/Bahrain Grand Prix/)).toBeInTheDocument();
  });

  it("calls onLoad with the selected race's session_key", () => {
    const onLoad = vi.fn();
    render(<RaceSelector races={races} onLoad={onLoad} />);

    fireEvent.click(screen.getByText("Load Replay"));
    expect(onLoad).toHaveBeenCalledWith(200);
  });

  it("disables Load Replay when there are no races to select", () => {
    render(<RaceSelector races={[]} onLoad={() => {}} />);
    expect(screen.getByText("Load Replay")).toBeDisabled();
  });
});
