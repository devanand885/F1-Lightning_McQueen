import { afterEach, describe, expect, it, vi } from "vitest";

import { apiGet, ApiError } from "./client";

describe("apiGet", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns parsed JSON on a successful response", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ count: 1, items: [{ id: 1 }] }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await apiGet<{ count: number }>("/drivers");

    expect(result).toEqual({ count: 1, items: [{ id: 1 }] });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("appends only defined query params, dropping undefined ones", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) });
    vi.stubGlobal("fetch", fetchMock);

    await apiGet("/drivers", { season: 2025, team: undefined });

    const calledUrl = new URL(fetchMock.mock.calls[0][0]);
    expect(calledUrl.searchParams.get("season")).toBe("2025");
    expect(calledUrl.searchParams.has("team")).toBe(false);
  });

  it("throws an ApiError with the status code when the response is not ok", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(apiGet("/drivers/999999")).rejects.toBeInstanceOf(ApiError);
    await expect(apiGet("/drivers/999999")).rejects.toMatchObject({ status: 404 });
  });
});
