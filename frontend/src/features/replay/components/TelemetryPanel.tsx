"use client";

import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { formatTelemetry, nearestValue } from "../utils/replayFrame";
import { DriverFrames } from "../types/replay.types";

interface Props {
  driver: DriverFrames | null;
  frameIndex: number;
  hasCarData: boolean;
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-border/60 py-2 last:border-b-0">
      <span className="text-[10px] uppercase tracking-[0.14em] text-text-muted">{label}</span>
      <span className="font-mono text-sm text-text-primary">{value}</span>
    </div>
  );
}

export default function TelemetryPanel({ driver, frameIndex, hasCarData }: Props) {
  if (!driver) {
    return (
      <Panel>
        <PanelHeader title="Car Telemetry" subtitle="Select a car on the circuit or leaderboard" />
        <p className="text-xs text-text-muted">No car selected.</p>
      </Panel>
    );
  }

  const position = nearestValue(driver.position, frameIndex);
  const speed = nearestValue(driver.speed, frameIndex);
  const throttle = nearestValue(driver.throttle, frameIndex);
  const brake = nearestValue(driver.brake, frameIndex);
  const gear = nearestValue(driver.gear, frameIndex);
  const drs = nearestValue(driver.drs, frameIndex);
  // OpenF1's raw DRS field is a status code, not a boolean (0/1 = off or
  // not eligible, 8 = eligible but closed, 10/12/14 = open) - >=10 is the
  // simplest honest "is it actually open right now" read.
  const drsOn = drs !== null && drs >= 10;

  return (
    <Panel>
      <PanelHeader
        title={driver.full_name}
        subtitle={`#${driver.driver_number} - ${driver.constructor_name}`}
        action={driver.team_colour ? <span className="h-3 w-3 rounded-full" style={{ background: `#${driver.team_colour}` }} /> : undefined}
      />
      {!hasCarData && (
        <p className="mb-2 text-[11px] text-text-muted">
          OpenF1 has no car telemetry (speed/throttle/brake/gear/DRS) for this session - only position data.
        </p>
      )}
      <div>
        <Row label="Position" value={position !== null ? `P${position}` : "N/A"} />
        <Row label="Speed" value={formatTelemetry(speed, " km/h")} />
        <Row label="Throttle" value={formatTelemetry(throttle, "%")} />
        <Row label="Brake" value={formatTelemetry(brake, "%")} />
        <Row label="Gear" value={gear !== null ? String(gear) : "N/A"} />
        <Row label="DRS" value={drs === null ? "N/A" : drsOn ? "ON" : "OFF"} />
      </div>
    </Panel>
  );
}
