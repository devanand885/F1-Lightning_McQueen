import { afterEach, describe, expect, it, vi } from "vitest";

import { downloadExport } from "./downloadExport";

describe("downloadExport", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("fetches the export URL with format and season, then triggers a real file download", async () => {
    const blob = new Blob(["a,b\n1,2"], { type: "text/csv" });
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, blob: async () => blob });
    vi.stubGlobal("fetch", fetchMock);
    // jsdom doesn't implement these browser-only statics - add them to the
    // real URL constructor rather than replacing URL itself (which would
    // break `new URL(...)` used to build the fetch request).
    URL.createObjectURL = vi.fn(() => "blob:mock-url");
    URL.revokeObjectURL = vi.fn();

    const clickSpy = vi.fn();
    const originalCreateElement = document.createElement.bind(document);
    vi.spyOn(document, "createElement").mockImplementation((tag: string) => {
      const el = originalCreateElement(tag);
      if (tag === "a") el.click = clickSpy;
      return el;
    });

    await downloadExport("constructors", "csv", 2025);

    const calledUrl = new URL(fetchMock.mock.calls[0][0]);
    expect(calledUrl.pathname).toContain("/export/constructors");
    expect(calledUrl.searchParams.get("format")).toBe("csv");
    expect(calledUrl.searchParams.get("season")).toBe("2025");
    expect(clickSpy).toHaveBeenCalledTimes(1);
  });

  it("throws instead of silently failing when the export request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500, statusText: "Server Error" }));

    await expect(downloadExport("drivers", "json", 2025)).rejects.toThrow(/Export failed/);
  });
});
