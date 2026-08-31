import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "@/test-utils/renderWithProviders";
import SimulatorPage from "./SimulatorPage";

vi.mock("../api/simulator.api", () => ({
  getChampionshipSimulation: vi.fn(),
}));

import { getChampionshipSimulation } from "../api/simulator.api";

describe("SimulatorPage", () => {
  it("shows a loading state before data arrives", () => {
    vi.mocked(getChampionshipSimulation).mockReturnValue(new Promise(() => {}));

    renderWithProviders(<SimulatorPage />);

    expect(screen.getByText(/Running simulation/i)).toBeInTheDocument();
  });

  it("renders real simulation results once loaded, including the not-a-prediction disclaimer", async () => {
    vi.mocked(getChampionshipSimulation).mockResolvedValue({
      available: true,
      reason: null,
      season: 2026,
      n_remaining_races: 16,
      n_completed_races: 15,
      n_simulations: 10000,
      seed: 42,
      drivers: [
        {
          driver_number: 4,
          full_name: "Lando Norris",
          current_points: 551,
          expected_points: 702,
          expected_championship_position: 1.3,
          championship_win_probability: 0.75,
          championship_podium_probability: 0.99,
          race_win_probability: 0.03,
          race_podium_probability: 0.27,
        },
      ],
    });

    renderWithProviders(<SimulatorPage />);

    await waitFor(() => expect(screen.getByText("Lando Norris")).toBeInTheDocument());
    expect(screen.getByText(/This is a simulation, not a prediction/i)).toBeInTheDocument();
    expect(screen.getByText(/16 races remaining/i)).toBeInTheDocument();
  });

  it("shows an honest unavailable state when the season has no remaining races", async () => {
    vi.mocked(getChampionshipSimulation).mockResolvedValue({
      available: false,
      reason: "Season 2025 has no remaining races to simulate - all 24 are complete.",
      season: 2025,
      n_remaining_races: null,
      n_completed_races: null,
      n_simulations: null,
      seed: null,
      drivers: [],
    });

    renderWithProviders(<SimulatorPage />);

    await waitFor(() => expect(screen.getByText(/no remaining races to simulate/i)).toBeInTheDocument());
  });

  it("shows an error state instead of crashing when the backend is unreachable", async () => {
    vi.mocked(getChampionshipSimulation).mockRejectedValue(new Error("network error"));

    renderWithProviders(<SimulatorPage />);

    await waitFor(() => expect(screen.getByText(/Unable to reach the F1 Lightning McQueen API/i)).toBeInTheDocument());
  });
});
