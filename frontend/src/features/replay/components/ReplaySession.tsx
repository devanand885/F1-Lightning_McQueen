"use client";

import { useMemo, useState } from "react";

import Panel from "@/features/shared/components/ui/Panel";
import PlaceholderPanel from "@/features/shared/components/ui/PlaceholderPanel";
import { useReplay } from "../hooks/useReplay";
import { useReplayClock } from "../hooks/useReplayClock";
import CircuitReplaySvg from "./CircuitReplaySvg";
import Leaderboard from "./Leaderboard";
import PlaybackControls from "./PlaybackControls";
import TelemetryPanel from "./TelemetryPanel";
import { nearestValue } from "../utils/replayFrame";

interface Props {
  sessionKey: number;
}

/** Everything below the race picker for one loaded race. Rendered with
 * `key={sessionKey}` by ReplayPage, so switching races remounts this
 * component with fresh state (selection, playback clock) instead of
 * needing effects to reset it. */
export default function ReplaySession({ sessionKey }: Props) {
  const replayQuery = useReplay(sessionKey);
  const replay = replayQuery.data;
  const [selectedDriverNumber, setSelectedDriverNumber] = useState<number | null>(null);

  const clock = useReplayClock({
    frameCount: replay?.frame_count ?? 0,
    gridStepSeconds: replay?.grid_step_seconds ?? 0.5,
  });

  const selectedDriver = useMemo(() => {
    if (!replay || selectedDriverNumber === null) return null;
    return replay.drivers[String(selectedDriverNumber)] ?? null;
  }, [replay, selectedDriverNumber]);

  const leaderDriver = useMemo(() => {
    if (!replay) return null;
    return Object.values(replay.drivers).find((d) => nearestValue(d.position, clock.frameIndex) === 1) ?? null;
  }, [replay, clock.frameIndex]);

  const lapReferenceDriver = selectedDriver ?? leaderDriver;
  const currentLap = lapReferenceDriver ? nearestValue(lapReferenceDriver.lap, clock.frameIndex) : null;

  if (replayQuery.isLoading) {
    return (
      <Panel className="text-xs text-text-muted">
        Loading historical telemetry from OpenF1... first-time loads for a race can take a while (tens of megabytes
        of raw telemetry); it&apos;s cached after that.
      </Panel>
    );
  }

  if (replayQuery.isError) {
    return <Panel className="text-xs text-text-muted">Unable to reach the F1 Lightning McQueen API. Confirm the backend is running.</Panel>;
  }

  if (!replay || !replay.available) {
    return <PlaceholderPanel title="Telemetry unavailable for this session." description={replay?.reason ?? undefined} />;
  }

  return (
    <>
      <div className="grid grid-cols-1 gap-3 xl:grid-cols-[1fr_320px] xl:items-start">
        <Panel>
          <div className="mb-2">
            <div className="text-[10px] uppercase tracking-[0.18em] text-primary font-semibold">{replay.season}</div>
            <h1 className="text-lg font-bold text-text-primary tracking-tight">{replay.meeting_name}</h1>
            <p className="mt-1 text-[11px] text-text-muted">
              Approximate telemetry-derived track position - not centimeter-accurate physical positioning.
            </p>
          </div>
          <CircuitReplaySvg
            replay={replay}
            frameIndex={clock.frameIndex}
            frameFraction={clock.frameFraction}
            selectedDriverNumber={selectedDriverNumber}
            onSelectDriver={setSelectedDriverNumber}
          />
        </Panel>

        <Leaderboard
          replay={replay}
          frameIndex={clock.frameIndex}
          selectedDriverNumber={selectedDriverNumber}
          onSelectDriver={setSelectedDriverNumber}
        />
      </div>

      <div className="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-[1fr_320px]">
        <PlaybackControls
          isPlaying={clock.isPlaying}
          currentTime={clock.currentTime}
          totalDuration={clock.totalDuration}
          speed={clock.speed}
          currentLap={currentLap}
          totalLaps={replay.total_laps}
          onToggle={clock.toggle}
          onRestart={clock.restart}
          onSeek={clock.seek}
          onSetSpeed={clock.setSpeed}
        />
        <TelemetryPanel driver={selectedDriver} frameIndex={clock.frameIndex} hasCarData={replay.has_car_data} />
      </div>
    </>
  );
}
