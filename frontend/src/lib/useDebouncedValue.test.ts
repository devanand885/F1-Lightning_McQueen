import { renderHook } from "@testing-library/react";
import { act } from "react";
import { describe, expect, it, vi } from "vitest";

import { useDebouncedValue } from "./useDebouncedValue";

describe("useDebouncedValue", () => {
  it("only updates after the delay has passed, so rapid typing doesn't fire a request per keystroke", () => {
    vi.useFakeTimers();
    try {
      const { result, rerender } = renderHook(({ value }) => useDebouncedValue(value, 300), {
        initialProps: { value: "v" },
      });

      expect(result.current).toBe("v");

      rerender({ value: "ve" });
      rerender({ value: "ver" });
      rerender({ value: "vers" });

      act(() => {
        vi.advanceTimersByTime(299);
      });
      expect(result.current).toBe("v");

      act(() => {
        vi.advanceTimersByTime(1);
      });
      expect(result.current).toBe("vers");
    } finally {
      vi.useRealTimers();
    }
  });
});
