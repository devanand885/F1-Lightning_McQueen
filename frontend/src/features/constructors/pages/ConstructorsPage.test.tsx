import { screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "@/test-utils/renderWithProviders";
import ConstructorsPage from "./ConstructorsPage";

// ConstructorTableRow uses useRouter() for click-to-navigate rows, which
// throws outside a mounted Next.js App Router - stub it for these tests.
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("../api/constructors.api", () => ({
  getConstructors: vi.fn(),
}));
vi.mock("@/features/shared/api/seasons.api", () => ({
  getSeasons: vi.fn(),
}));

import { getConstructors } from "../api/constructors.api";
import { getSeasons } from "@/features/shared/api/seasons.api";

describe("ConstructorsPage", () => {
  beforeEach(() => {
    vi.mocked(getSeasons).mockResolvedValue({ count: 2, items: [2026, 2025] });
  });

  it("shows a loading state before data arrives", () => {
    vi.mocked(getConstructors).mockReturnValue(new Promise(() => {}));

    renderWithProviders(<ConstructorsPage />);

    expect(screen.getByText(/Loading constructor intelligence/i)).toBeInTheDocument();
  });

  it("renders real Finish Rate data, not a fabricated Reliability score", async () => {
    vi.mocked(getConstructors).mockResolvedValue({
      count: 1,
      items: [
        {
          season: 2025,
          position: 1,
          constructor_id: 1,
          name: "Red Bull Racing",
          team_colour: "3671C6",
          points: 500,
          wins: 12,
          podiums: 20,
          avg_finish: 2.1,
          dnf_rate: 0.1,
        },
      ],
    });

    renderWithProviders(<ConstructorsPage />);

    await waitFor(() => expect(screen.getByText("Red Bull Racing")).toBeInTheDocument());
    expect(screen.getByText("90.0%")).toBeInTheDocument(); // (1 - dnf_rate) * 100
    expect(screen.queryByText(/reliability/i)).not.toBeInTheDocument();
  });

  it("shows an error state instead of crashing when the backend is unreachable", async () => {
    vi.mocked(getConstructors).mockRejectedValue(new Error("network error"));

    renderWithProviders(<ConstructorsPage />);

    await waitFor(() => expect(screen.getByText(/Unable to reach the F1 Lightning McQueen API/i)).toBeInTheDocument());
  });
});
