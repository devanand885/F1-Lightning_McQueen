import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import PlaceholderPanel from "./PlaceholderPanel";

describe("PlaceholderPanel", () => {
  it("renders the title and an honest 'not available' badge instead of fake data", () => {
    render(<PlaceholderPanel title="Performance Efficiency" description="Needs a real methodology." />);

    expect(screen.getByText("Performance Efficiency")).toBeInTheDocument();
    expect(screen.getByText("Not yet available")).toBeInTheDocument();
    expect(screen.getByText("Needs a real methodology.")).toBeInTheDocument();
  });

  it("falls back to a generic honesty message when no description is given", () => {
    render(<PlaceholderPanel title="Some Metric" />);

    expect(
      screen.getByText(/needs a defined analytical methodology before F1 Lightning McQueen can show it honestly/i),
    ).toBeInTheDocument();
  });

  it("renders an optional subtitle", () => {
    render(<PlaceholderPanel title="Some Metric" subtitle="Aero load / lap delta correlation" />);

    expect(screen.getByText("Aero load / lap delta correlation")).toBeInTheDocument();
  });
});
