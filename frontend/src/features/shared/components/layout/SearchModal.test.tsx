import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

const pushMock = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock }),
}));

vi.mock("../../api/search.api", () => ({
  search: vi.fn(),
}));

import { renderWithProviders } from "@/test-utils/renderWithProviders";
import SearchModal from "./SearchModal";
import { search } from "../../api/search.api";

describe("SearchModal", () => {
  beforeEach(() => {
    pushMock.mockClear();
  });

  it("shows a prompt before the user types anything", () => {
    renderWithProviders(<SearchModal onClose={vi.fn()} />);

    expect(screen.getByText(/Start typing to search/i)).toBeInTheDocument();
  });

  it("shows real results after typing, not fabricated suggestions", async () => {
    vi.mocked(search).mockResolvedValue({
      count: 1,
      items: [{ type: "driver", id: 1, title: "Max Verstappen", subtitle: "VER" }],
    });
    const user = userEvent.setup();

    renderWithProviders(<SearchModal onClose={vi.fn()} />);
    await user.type(screen.getByPlaceholderText(/Search drivers/i), "verstappen");

    await waitFor(() => expect(screen.getByText("Max Verstappen")).toBeInTheDocument(), { timeout: 2000 });
  });

  it("shows a 'no results' message rather than pretending something was found", async () => {
    vi.mocked(search).mockResolvedValue({ count: 0, items: [] });
    const user = userEvent.setup();

    renderWithProviders(<SearchModal onClose={vi.fn()} />);
    await user.type(screen.getByPlaceholderText(/Search drivers/i), "zzzznotfound");

    await waitFor(() => expect(screen.getByText(/No results for/i)).toBeInTheDocument(), { timeout: 2000 });
  });

  it("navigates to the driver page and closes when a result is clicked", async () => {
    vi.mocked(search).mockResolvedValue({
      count: 1,
      items: [{ type: "driver", id: 1, title: "Max Verstappen", subtitle: "VER" }],
    });
    const onClose = vi.fn();
    const user = userEvent.setup();

    renderWithProviders(<SearchModal onClose={onClose} />);
    await user.type(screen.getByPlaceholderText(/Search drivers/i), "verstappen");
    await waitFor(() => screen.getByText("Max Verstappen"), { timeout: 2000 });

    await user.click(screen.getByText("Max Verstappen"));

    expect(pushMock).toHaveBeenCalledWith("/drivers/1");
    expect(onClose).toHaveBeenCalled();
  });

  it("closes without navigating on Escape", async () => {
    const onClose = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(<SearchModal onClose={onClose} />);

    await user.keyboard("{Escape}");

    expect(onClose).toHaveBeenCalled();
    expect(pushMock).not.toHaveBeenCalled();
  });

  it("does not make meeting/session results clickable since no detail page exists for them yet", async () => {
    vi.mocked(search).mockResolvedValue({
      count: 1,
      items: [{ type: "meeting", id: 9, title: "Australian Grand Prix", subtitle: null }],
    });
    const user = userEvent.setup();

    renderWithProviders(<SearchModal onClose={vi.fn()} />);
    await user.type(screen.getByPlaceholderText(/Search drivers/i), "australian");

    const resultButton = await screen.findByRole("button", { name: /Australian Grand Prix/i }, { timeout: 2000 });
    expect(resultButton).toBeDisabled();
  });
});
