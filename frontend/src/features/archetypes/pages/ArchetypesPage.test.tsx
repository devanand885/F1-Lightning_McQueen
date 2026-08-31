import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "@/test-utils/renderWithProviders";
import ArchetypesPage from "./ArchetypesPage";

vi.mock("../api/archetypes.api", () => ({
  getArchetypes: vi.fn(),
}));

import { getArchetypes } from "../api/archetypes.api";

describe("ArchetypesPage", () => {
  it("shows a loading state before data arrives", () => {
    vi.mocked(getArchetypes).mockReturnValue(new Promise(() => {}));

    renderWithProviders(<ArchetypesPage />);

    expect(screen.getByText(/Loading archetypes/i)).toBeInTheDocument();
  });

  it("renders real clusters once loaded", async () => {
    vi.mocked(getArchetypes).mockResolvedValue({
      available: true,
      reason: null,
      run_id: "2026-08-25",
      features: ["race_pace_teammate_relative"],
      silhouette: 0.18,
      pca_explained_variance_ratio: [0.31, 0.26],
      n_eligible: 2,
      n_population: 3,
      clusters: [
        {
          cluster: 0,
          name: "Consistent Race Pace",
          size: 2,
          centroid: { race_pace_teammate_relative: -0.5 },
          drivers: [
            { driver_id: 1, full_name: "Driver Alpha", pca_x: 0.1, pca_y: 0.2 },
            { driver_id: 2, full_name: "Driver Beta", pca_x: -0.1, pca_y: 0.3 },
          ],
        },
      ],
      excluded_drivers: [
        { driver_id: 3, full_name: "Driver Gamma", race_sessions: 4, usable_race_laps: 100, race_stints: 3 },
      ],
    });

    renderWithProviders(<ArchetypesPage />);

    await waitFor(() => expect(screen.getByText("Consistent Race Pace")).toBeInTheDocument());
    expect(screen.getByText("Driver Alpha")).toBeInTheDocument();
    expect(screen.getByText(/2 of 3 drivers classified/i)).toBeInTheDocument();
    expect(screen.getByText(/Excluded from classification/i)).toBeInTheDocument();
    expect(screen.getByText("Driver Gamma")).toBeInTheDocument();
  });

  it("shows an honest unavailable state when no model has been trained", async () => {
    vi.mocked(getArchetypes).mockResolvedValue({
      available: false,
      reason: "No trained archetype model available. Run ml/models/train_archetypes.py.",
      run_id: null,
      features: null,
      silhouette: null,
      pca_explained_variance_ratio: null,
      n_eligible: null,
      n_population: null,
      clusters: [],
      excluded_drivers: [],
    });

    renderWithProviders(<ArchetypesPage />);

    await waitFor(() => expect(screen.getByText(/No trained archetype model available/i)).toBeInTheDocument());
  });

  it("shows an error state instead of crashing when the backend is unreachable", async () => {
    vi.mocked(getArchetypes).mockRejectedValue(new Error("network error"));

    renderWithProviders(<ArchetypesPage />);

    await waitFor(() => expect(screen.getByText(/Unable to reach the F1 Lightning McQueen API/i)).toBeInTheDocument());
  });
});
