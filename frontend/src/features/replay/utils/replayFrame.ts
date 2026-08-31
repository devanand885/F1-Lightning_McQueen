import { DriverFrames } from "../types/replay.types";

/** Car position is interpolated between the two bracketing real frames for
 * smooth motion - this is the "interpolate positions between nearby
 * telemetry frames" the plan explicitly allows. If the car has no data at
 * this frame (not yet on track, or telemetry ended), returns null and the
 * caller simply doesn't draw it - no fabricated position. */
export function interpolatedPosition(
  driver: DriverFrames,
  frameIndex: number,
  frameFraction: number,
): { x: number; y: number } | null {
  const x0 = driver.x[frameIndex];
  const y0 = driver.y[frameIndex];
  if (x0 == null || y0 == null) return null;

  const x1 = driver.x[frameIndex + 1];
  const y1 = driver.y[frameIndex + 1];
  if (x1 == null || y1 == null || frameFraction <= 0) {
    return { x: x0, y: y0 };
  }
  return { x: x0 + (x1 - x0) * frameFraction, y: y0 + (y1 - y0) * frameFraction };
}

/** Telemetry-panel values are never interpolated (only positions are) -
 * this returns the nearest real sample at-or-before the current frame, or
 * null if genuinely unavailable, so the UI can show "N/A" honestly. */
export function nearestValue(values: (number | null)[], frameIndex: number): number | null {
  return values[frameIndex] ?? null;
}

export function formatTelemetry(value: number | null, unit: string, decimals = 0): string {
  if (value === null) return "N/A";
  return `${value.toFixed(decimals)}${unit}`;
}
