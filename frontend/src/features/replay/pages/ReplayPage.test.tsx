import { fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "@/test-utils/renderWithProviders";
import ReplayPage from "./ReplayPage";

vi.mock("../api/replay.api", () => ({
  getReplayRaces: vi.fn(),
  getReplay: vi.fn(),
}));

import { getReplay, getReplayRaces } from "../api/replay.api";

const RACES = {
  items: [
    { session_key: 100, season: 2025, meeting_name: "Australian Grand Prix", circuit_short_name: "Melbourne", date_start: "2025-03-16" },
  ],
};

describe("ReplayPage", () => {
  it("shows a prompt to load a race before any is selected", async () => {
    vi.mocked(getReplayRaces).mockResolvedValue(RACES);
    renderWithProviders(<ReplayPage />);

    await waitFor(() => expect(screen.getByText(/Australian Grand Prix/)).toBeInTheDocument());
    expect(screen.getByText(/No race loaded/i)).toBeInTheDocument();
  });

  it("shows a loading state while telemetry is being fetched", async () => {
    vi.mocked(getReplayRaces).mockResolvedValue(RACES);
    vi.mocked(getReplay).mockReturnValue(new Promise(() => {}));
    renderWithProviders(<ReplayPage />);

    await waitFor(() => expect(screen.getByText(/Australian Grand Prix/)).toBeInTheDocument());
    fireEvent.click(screen.getByText("Load Replay"));

    await waitFor(() => expect(screen.getByText(/Loading historical telemetry/i)).toBeInTheDocument());
  });

  it("shows an honest unavailable state when OpenF1 has no telemetry for the session", async () => {
    vi.mocked(getReplayRaces).mockResolvedValue(RACES);
    vi.mocked(getReplay).mockResolvedValue({
      available: false,
      reason: "OpenF1 has no usable car-position telemetry for this session.",
      session_key: null,
      meeting_name: null,
      season: null,
      date_from: null,
      date_to: null,
      grid_step_seconds: null,
      frame_count: null,
      timestamps: [],
      total_laps: null,
      circuit_outline: [],
      bounds: null,
      has_car_data: false,
      drivers: {},
    });
    renderWithProviders(<ReplayPage />);

    await waitFor(() => expect(screen.getByText(/Australian Grand Prix/)).toBeInTheDocument());
    fireEvent.click(screen.getByText("Load Replay"));

    await waitFor(() => expect(screen.getByText(/Telemetry unavailable for this session/i)).toBeInTheDocument());
  });

  it("renders the circuit, leaderboard, and playback controls once telemetry is available", async () => {
    vi.mocked(getReplayRaces).mockResolvedValue(RACES);
    vi.mocked(getReplay).mockResolvedValue({
      available: true,
      reason: null,
      session_key: 100,
      meeting_name: "Australian Grand Prix",
      season: 2025,
      date_from: "2025-03-16T04:18:22Z",
      date_to: "2025-03-16T06:00:29Z",
      grid_step_seconds: 0.5,
      frame_count: 2,
      timestamps: [0, 0.5],
      total_laps: 58,
      circuit_outline: [
        [0, 0],
        [500, 500],
      ],
      bounds: { min_x: 0, max_x: 1000, min_y: 0, max_y: 1000, span: 1000, space: 1000 },
      has_car_data: true,
      drivers: {
        "1": {
          driver_number: 1,
          full_name: "Max Verstappen",
          name_acronym: "VER",
          constructor_name: "Red Bull Racing",
          team_colour: "3671C6",
          x: [100, 110],
          y: [100, 110],
          speed: [300, 305],
          throttle: [100, 100],
          brake: [0, 0],
          gear: [8, 8],
          drs: [0, 0],
          lap: [1, 1],
          position: [1, 1],
        },
      },
    });
    renderWithProviders(<ReplayPage />);

    await waitFor(() => expect(screen.getByText(/Australian Grand Prix/)).toBeInTheDocument());
    fireEvent.click(screen.getByText("Load Replay"));

    await waitFor(() => expect(screen.getByText("Max Verstappen")).toBeInTheDocument());
    expect(screen.getByText(/LAP 1 \/ 58/)).toBeInTheDocument();
  });
});
