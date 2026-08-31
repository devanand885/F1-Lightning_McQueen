import { screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "@/test-utils/renderWithProviders";
import DriversPage from "./DriversPage";

vi.mock("../api/drivers.api", () => ({
  getDrivers: vi.fn(),
}));
vi.mock("@/features/shared/api/seasons.api", () => ({
  getSeasons: vi.fn(),
}));

import { getDrivers } from "../api/drivers.api";
import { getSeasons } from "@/features/shared/api/seasons.api";

describe("DriversPage", () => {
  beforeEach(() => {
    vi.mocked(getSeasons).mockResolvedValue({ count: 2, items: [2026, 2025] });
  });

  it("shows a loading state before data arrives", () => {
    vi.mocked(getDrivers).mockReturnValue(new Promise(() => {}));

    renderWithProviders(<DriversPage />);

    expect(screen.getByText(/Loading driver intelligence/i)).toBeInTheDocument();
  });

  it("renders real driver data once loaded, not a fabricated placeholder", async () => {
    vi.mocked(getDrivers).mockResolvedValue({
      count: 1,
      items: [
        {
          season: 2025,
          position: 1,
          driver_number: 1,
          full_name: "Max Verstappen",
          name_acronym: "VER",
          headshot_url: null,
          country_code: null,
          team_id: 1,
          team_name: "Red Bull Racing",
          team_colour: "3671C6",
          points: 400,
          wins: 10,
          podiums: 15,
          avg_finish: 2.5,
          dnf_rate: 0.05,
        },
      ],
    });

    renderWithProviders(<DriversPage />);

    await waitFor(() => expect(screen.getByText("Max Verstappen")).toBeInTheDocument());
    // "Season 2025" also appears as a <select> option, so assert on the
    // combined header line to avoid an ambiguous multi-match query.
    expect(screen.getByText(/1 of 1 drivers.*Season 2025/i)).toBeInTheDocument();
  });

  it("shows an empty state rather than a fabricated table when there are no drivers", async () => {
    vi.mocked(getDrivers).mockResolvedValue({ count: 0, items: [] });

    renderWithProviders(<DriversPage />);

    await waitFor(() => expect(screen.getByText(/0 of 0 drivers/i)).toBeInTheDocument());
  });

  it("shows an error state instead of crashing when the backend is unreachable", async () => {
    vi.mocked(getDrivers).mockRejectedValue(new Error("network error"));

    renderWithProviders(<DriversPage />);

    await waitFor(() => expect(screen.getByText(/Unable to reach the F1 Lightning McQueen API/i)).toBeInTheDocument());
  });
});
