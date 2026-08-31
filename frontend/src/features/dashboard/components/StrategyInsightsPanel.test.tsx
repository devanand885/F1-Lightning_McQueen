import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "@/test-utils/renderWithProviders";
import StrategyInsightsPanel from "./StrategyInsightsPanel";

vi.mock("../api/strategy.api", () => ({
  getStrategyInsights: vi.fn(),
}));

import { getStrategyInsights } from "../api/strategy.api";

describe("StrategyInsightsPanel", () => {
  it("shows a loading state before data arrives", () => {
    vi.mocked(getStrategyInsights).mockReturnValue(new Promise(() => {}));

    renderWithProviders(<StrategyInsightsPanel />);

    expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });

  it("renders real, sourced insight sentences with their sample sizes", async () => {
    vi.mocked(getStrategyInsights).mockResolvedValue({
      insights: [
        { statement: "The most common race strategy this season was a 1-stop race.", sample_size: 927, metric: "stop_count_distribution" },
      ],
    });

    renderWithProviders(<StrategyInsightsPanel />);

    await waitFor(() => expect(screen.getByText(/most common race strategy/i)).toBeInTheDocument());
    expect(screen.getByText(/sample size: 927/i)).toBeInTheDocument();
    expect(screen.getByText(/Not live/i)).toBeInTheDocument();
  });

  it("shows an honest placeholder when there isn't enough data yet", async () => {
    vi.mocked(getStrategyInsights).mockResolvedValue({ insights: [] });

    renderWithProviders(<StrategyInsightsPanel />);

    await waitFor(() => expect(screen.getByText(/Not enough completed race data/i)).toBeInTheDocument());
  });
});
