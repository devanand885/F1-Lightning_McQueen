import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import DriverTable from "./DriverTable";
import { Driver } from "../types/driver.types";

function makeDriver(overrides: Partial<Driver>): Driver {
  return {
    season: 2025,
    position: null,
    driver_number: 1,
    full_name: "Test Driver",
    name_acronym: "TST",
    headshot_url: null,
    country_code: null,
    team_id: null,
    team_name: "Test Team",
    team_colour: "FF0000",
    points: 0,
    wins: 0,
    podiums: 0,
    avg_finish: null,
    dnf_rate: null,
    ...overrides,
  };
}

const drivers: Driver[] = [
  makeDriver({ driver_number: 1, full_name: "Max Verstappen", position: 1, points: 400, avg_finish: 2.0 }),
  makeDriver({ driver_number: 4, full_name: "Lando Norris", position: 2, points: 350, avg_finish: 3.5 }),
  makeDriver({ driver_number: 44, full_name: "Lewis Hamilton", position: 3, points: 100, avg_finish: 6.0 }),
];

function driverNamesInOrder() {
  const rows = screen.getAllByRole("row").slice(1); // skip header row
  return rows.map((row) => within(row).getByText(/Verstappen|Norris|Hamilton/).textContent);
}

describe("DriverTable", () => {
  it("sorts by position by default", () => {
    render(<DriverTable drivers={[...drivers].reverse()} />);
    expect(driverNamesInOrder()).toEqual(["Max Verstappen", "Lando Norris", "Lewis Hamilton"]);
  });

  it("sorts by points descending on first click, and toggles to ascending on a second click", async () => {
    const user = userEvent.setup();
    render(<DriverTable drivers={drivers} />);

    await user.click(screen.getByRole("button", { name: /Pts/i }));
    expect(driverNamesInOrder()).toEqual(["Max Verstappen", "Lando Norris", "Lewis Hamilton"]);

    await user.click(screen.getByRole("button", { name: /Pts/i }));
    expect(driverNamesInOrder()).toEqual(["Lewis Hamilton", "Lando Norris", "Max Verstappen"]);
  });

  it("shows a dash for drivers with no avg_finish yet instead of a fabricated number", () => {
    render(
      <DriverTable
        drivers={[makeDriver({ driver_number: 99, full_name: "New Driver", position: 20, avg_finish: null })]}
      />,
    );
    const row = screen.getByText("New Driver").closest("tr");
    const cells = within(row!).getAllByRole("cell");
    expect(cells.at(-1)).toHaveTextContent("—");
  });
});
