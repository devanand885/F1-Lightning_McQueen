import { screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "@/test-utils/renderWithProviders";
import CircuitsPage from "./CircuitsPage";

vi.mock("../api/circuits.api", () => ({
  getCircuits: vi.fn(),
}));
vi.mock("@/features/shared/api/seasons.api", () => ({
  getSeasons: vi.fn(),
}));

import { getCircuits } from "../api/circuits.api";
import { getSeasons } from "@/features/shared/api/seasons.api";

describe("CircuitsPage", () => {
  beforeEach(() => {
    vi.mocked(getSeasons).mockResolvedValue({ count: 2, items: [2026, 2025] });
  });

  it("shows a loading state before data arrives", () => {
    vi.mocked(getCircuits).mockReturnValue(new Promise(() => {}));

    renderWithProviders(<CircuitsPage />);

    expect(screen.getByText(/Loading circuit intelligence/i)).toBeInTheDocument();
  });

  it("renders real circuit data once loaded", async () => {
    vi.mocked(getCircuits).mockResolvedValue({
      count: 1,
      items: [
        {
          circuit_id: 1,
          circuit_key: 10,
          circuit_short_name: "Melbourne",
          location: "Melbourne",
          country_name: "Australia",
          country_code: "AUS",
          seasons: [2025, 2026],
        },
      ],
    });

    renderWithProviders(<CircuitsPage />);

    await waitFor(() => expect(screen.getByText("Melbourne")).toBeInTheDocument());
    expect(screen.getByText(/Melbourne, Australia/)).toBeInTheDocument();
  });

  it("shows an empty state when no circuits match the filters", async () => {
    vi.mocked(getCircuits).mockResolvedValue({ count: 0, items: [] });

    renderWithProviders(<CircuitsPage />);

    await waitFor(() => expect(screen.getByText(/0 circuits/i)).toBeInTheDocument());
  });

  it("shows an error state instead of crashing when the backend is unreachable", async () => {
    vi.mocked(getCircuits).mockRejectedValue(new Error("network error"));

    renderWithProviders(<CircuitsPage />);

    await waitFor(() => expect(screen.getByText(/Unable to reach the F1 Lightning McQueen API/i)).toBeInTheDocument());
  });
});
