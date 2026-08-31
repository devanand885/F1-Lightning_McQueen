"use client";

import { useMemo } from "react";

import { interpolatedPosition } from "../utils/replayFrame";
import { ReplayResponse } from "../types/replay.types";

interface Props {
  replay: ReplayResponse;
  frameIndex: number;
  frameFraction: number;
  selectedDriverNumber: number | null;
  onSelectDriver: (driverNumber: number) => void;
}

const DEFAULT_COLOUR = "8d6f67";

export default function CircuitReplaySvg({ replay, frameIndex, frameFraction, selectedDriverNumber, onSelectDriver }: Props) {
  const bounds = replay.bounds;
  const circuitOutline = replay.circuit_outline;
  const outlinePath = useMemo(() => {
    if (circuitOutline.length === 0) return "";
    return circuitOutline.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x},${y}`).join(" ");
  }, [circuitOutline]);

  // The backend normalizes coordinates into a fixed 0..1000 square (the
  // larger axis fills it, the smaller one only partially does), so a
  // viewBox of "0 0 1000 1000" wastes space on whichever axis is smaller -
  // on top of whatever letterboxing the container's own aspect ratio
  // already adds. Sizing the viewBox to the content's own bounding box
  // (plus a small padding margin for labels) removes that first, avoidable
  // layer of empty space entirely, so the track fills as much of the
  // container as its shape and the container's aspect ratio allow.
  const { viewBox, viewSize, aspectRatio } = useMemo(() => {
    if (!bounds) return { viewBox: "0 0 1000 1000", viewSize: 1000, aspectRatio: 1 };
    const scale = bounds.span > 0 ? bounds.space / bounds.span : 1;
    const contentWidth = (bounds.max_x - bounds.min_x) * scale;
    const contentHeight = (bounds.max_y - bounds.min_y) * scale;
    const padding = Math.max(contentWidth, contentHeight) * 0.08;
    const totalWidth = contentWidth + 2 * padding;
    const totalHeight = contentHeight + 2 * padding;
    return {
      viewBox: `${-padding} ${-padding} ${totalWidth} ${totalHeight}`,
      viewSize: Math.max(totalWidth, totalHeight),
      aspectRatio: totalWidth / totalHeight,
    };
  }, [bounds]);
  const space = viewSize;

  const driversByNumber = replay.drivers;
  const cars = useMemo(() => {
    return Object.values(driversByNumber)
      .map((driver) => {
        const pos = interpolatedPosition(driver, frameIndex, frameFraction);
        if (pos === null) return null;
        return { driver, pos };
      })
      .filter((c): c is { driver: (typeof driversByNumber)[string]; pos: { x: number; y: number } } => c !== null);
  }, [driversByNumber, frameIndex, frameFraction]);

  return (
    <div
      className="relative mx-auto w-full max-h-[clamp(420px,calc(100vh-260px),1000px)]"
      style={{ aspectRatio }}
    >
      <svg viewBox={viewBox} className="h-full w-full" preserveAspectRatio="xMidYMid meet">
        <path d={outlinePath} fill="none" stroke="#3a2f2a" strokeWidth={space * 0.012} strokeLinejoin="round" strokeLinecap="round" />

        {cars.map(({ driver, pos }) => {
          const isSelected = driver.driver_number === selectedDriverNumber;
          const colour = driver.team_colour ? `#${driver.team_colour}` : `#${DEFAULT_COLOUR}`;
          const r = space * (isSelected ? 0.016 : 0.011);
          return (
            <g
              key={driver.driver_number}
              data-car-number={driver.driver_number}
              transform={`translate(${pos.x}, ${pos.y})`}
              onClick={() => onSelectDriver(driver.driver_number)}
              className="cursor-pointer"
            >
              {isSelected && <circle r={r * 1.8} fill="none" stroke={colour} strokeWidth={space * 0.003} opacity={0.6} />}
              <circle r={r} fill={colour} stroke="#0d0d0d" strokeWidth={space * 0.002} />
              <text
                x={0}
                y={-r - space * 0.006}
                textAnchor="middle"
                fontSize={space * 0.02}
                fill="#f5e8e1"
                className="select-none"
              >
                {driver.name_acronym ?? driver.driver_number}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
