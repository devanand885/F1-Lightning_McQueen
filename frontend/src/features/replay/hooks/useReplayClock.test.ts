import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useReplayClock } from "./useReplayClock";

describe("useReplayClock", () => {
  it("starts paused at time zero", () => {
    const { result } = renderHook(() => useReplayClock({ frameCount: 100, gridStepSeconds: 0.5 }));
    expect(result.current.currentTime).toBe(0);
    expect(result.current.isPlaying).toBe(false);
    expect(result.current.speed).toBe(1);
    expect(result.current.totalDuration).toBeCloseTo(49.5);
  });

  it("seek clamps to [0, totalDuration] and updates frameIndex/frameFraction", () => {
    const { result } = renderHook(() => useReplayClock({ frameCount: 10, gridStepSeconds: 1 }));

    act(() => result.current.seek(3.4));
    expect(result.current.currentTime).toBeCloseTo(3.4);
    expect(result.current.frameIndex).toBe(3);
    expect(result.current.frameFraction).toBeCloseTo(0.4);

    act(() => result.current.seek(-5));
    expect(result.current.currentTime).toBe(0);

    act(() => result.current.seek(9999));
    expect(result.current.currentTime).toBe(result.current.totalDuration);
    expect(Number.isFinite(result.current.currentTime)).toBe(true);
  });

  it("toggle flips play state, restart resets to zero and pauses", () => {
    const { result } = renderHook(() => useReplayClock({ frameCount: 10, gridStepSeconds: 1 }));

    act(() => result.current.toggle());
    expect(result.current.isPlaying).toBe(true);

    act(() => result.current.seek(5));
    act(() => result.current.restart());
    expect(result.current.currentTime).toBe(0);
    expect(result.current.isPlaying).toBe(false);
  });

  it("play is a no-op when there is no duration to play", () => {
    const { result } = renderHook(() => useReplayClock({ frameCount: 0, gridStepSeconds: 0.5 }));
    act(() => result.current.play());
    expect(result.current.isPlaying).toBe(false);
  });

  it("setSpeed updates the speed multiplier", () => {
    const { result } = renderHook(() => useReplayClock({ frameCount: 10, gridStepSeconds: 1 }));
    act(() => result.current.setSpeed(5));
    expect(result.current.speed).toBe(5);
  });

  it("frameIndex never exceeds the last frame", () => {
    const { result } = renderHook(() => useReplayClock({ frameCount: 5, gridStepSeconds: 1 }));
    act(() => result.current.seek(9999));
    expect(result.current.frameIndex).toBe(4);
  });
});
