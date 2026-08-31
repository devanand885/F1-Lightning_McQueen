import { Timer } from "lucide-react";

import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import StatRow from "@/features/shared/components/ui/StatRow";
import type { ConstructorPitStop } from "../types/constructor.types";

interface Props {
  pitStops: ConstructorPitStop[];
}

function median(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

export default function PitLaneEfficiencyCard({ pitStops }: Props) {
  // Outside of races, OpenF1's pit_duration reflects long garage dwell time
  // rather than a competitive stop (e.g. testing/practice setup changes can
  // run to tens of minutes) - only race stops represent "pit lane speed".
  const raceDurations = pitStops
    .filter((p) => p.session_type === "Race")
    .map((p) => p.pit_duration)
    .filter((d): d is number => d != null);

  const typical = raceDurations.length > 0 ? median(raceDurations) : null;
  const fastest = raceDurations.length > 0 ? Math.min(...raceDurations) : null;

  return (
    <Panel className="h-full min-h-[300px] rounded-none">
      <PanelHeader
        title="Pit Lane Efficiency"
        subtitle="This team's race pit stops"
        action={<Timer size={14} className="text-primary" />}
      />
      {raceDurations.length > 0 ? (
        <div className="divide-y divide-border/70">
          <StatRow label="Race Pit Stops" value={String(raceDurations.length)} />
          <StatRow label="Typical Duration" value={`${typical!.toFixed(2)}s`} />
          <StatRow label="Fastest Stop" value={`${fastest!.toFixed(2)}s`} />
        </div>
      ) : (
        <p className="text-xs text-text-muted">No race pit stop data recorded yet this season.</p>
      )}
    </Panel>
  );
}
