"use client";

import { Pause, Play, RotateCcw } from "lucide-react";

import Panel from "@/features/shared/components/ui/Panel";
import { PLAYBACK_SPEEDS } from "../hooks/useReplayClock";

interface Props {
  isPlaying: boolean;
  currentTime: number;
  totalDuration: number;
  speed: number;
  currentLap: number | null;
  totalLaps: number | null;
  onToggle: () => void;
  onRestart: () => void;
  onSeek: (time: number) => void;
  onSetSpeed: (speed: number) => void;
}

function formatClock(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function PlaybackControls({
  isPlaying,
  currentTime,
  totalDuration,
  speed,
  currentLap,
  totalLaps,
  onToggle,
  onRestart,
  onSeek,
  onSetSpeed,
}: Props) {
  return (
    <Panel>
      <div className="mb-2 flex items-center justify-between text-xs">
        <span className="text-text-secondary">
          {currentLap !== null && totalLaps !== null ? `LAP ${currentLap} / ${totalLaps}` : "LAP —"}
        </span>
        <span className="font-mono text-text-muted">
          {formatClock(currentTime)} / {formatClock(totalDuration)}
        </span>
      </div>

      <input
        type="range"
        min={0}
        max={totalDuration}
        step={0.1}
        value={currentTime}
        onChange={(e) => onSeek(Number(e.target.value))}
        className="w-full accent-primary"
        aria-label="Replay timeline"
      />

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <button
          onClick={onRestart}
          aria-label="Restart"
          className="flex h-8 w-8 items-center justify-center border border-border bg-bg-card text-text-secondary transition-colors hover:text-text-primary"
        >
          <RotateCcw size={14} />
        </button>
        <button
          onClick={onToggle}
          aria-label={isPlaying ? "Pause" : "Play"}
          className="flex h-8 w-8 items-center justify-center border border-primary/40 bg-primary/10 text-primary transition-colors hover:bg-primary/20"
        >
          {isPlaying ? <Pause size={14} /> : <Play size={14} />}
        </button>

        <div className="ml-2 flex items-center gap-1">
          {PLAYBACK_SPEEDS.map((s) => (
            <button
              key={s}
              onClick={() => onSetSpeed(s)}
              className={`h-8 min-w-9 border px-2 text-xs transition-colors ${
                speed === s
                  ? "border-primary/40 bg-primary/10 text-primary"
                  : "border-border bg-bg-card text-text-secondary hover:text-text-primary"
              }`}
            >
              {s}×
            </button>
          ))}
        </div>
      </div>
    </Panel>
  );
}
