"use client";

import { useMemo } from "react";

import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { nearestValue } from "../utils/replayFrame";
import { ReplayResponse } from "../types/replay.types";

interface Props {
  replay: ReplayResponse;
  frameIndex: number;
  selectedDriverNumber: number | null;
  onSelectDriver: (driverNumber: number) => void;
}

export default function Leaderboard({ replay, frameIndex, selectedDriverNumber, onSelectDriver }: Props) {
  const ranked = useMemo(() => {
    return Object.values(replay.drivers)
      .map((driver) => ({ driver, position: nearestValue(driver.position, frameIndex) }))
      .filter((r) => r.position !== null)
      .sort((a, b) => (a.position as number) - (b.position as number));
  }, [replay.drivers, frameIndex]);

  return (
    <Panel className="flex h-[clamp(520px,calc(100vh-260px),1050px)] flex-col overflow-hidden p-0">
      <div className="p-4 pb-2">
        <PanelHeader title="Leaderboard" subtitle="Live race position at this timestamp" />
      </div>
      <div className="flex-1 overflow-y-auto px-2 pb-2">
        {ranked.length === 0 && <p className="px-2 py-4 text-xs text-text-muted">No position data yet.</p>}
        {ranked.map(({ driver, position }) => {
          const isSelected = driver.driver_number === selectedDriverNumber;
          const colour = driver.team_colour ? `#${driver.team_colour}` : "#8d6f67";
          return (
            <button
              key={driver.driver_number}
              onClick={() => onSelectDriver(driver.driver_number)}
              className={`flex w-full items-center gap-2 rounded px-2 py-1.5 text-left text-xs transition-colors ${
                isSelected ? "bg-primary/10 text-text-primary" : "text-text-secondary hover:bg-bg-hover"
              }`}
            >
              <span className="w-5 shrink-0 font-mono text-text-muted">P{position}</span>
              <span className="h-3 w-1 shrink-0" style={{ background: colour }} />
              <span className="truncate">{driver.full_name}</span>
            </button>
          );
        })}
      </div>
    </Panel>
  );
}
