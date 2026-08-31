"use client";

import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import PlaceholderPanel from "@/features/shared/components/ui/PlaceholderPanel";
import { DriverResult } from "../types/driver.types";

interface Props {
  results: DriverResult[];
}

interface DeltaRow {
  meeting: string;
  delta: number | null;
  label: string;
}

function buildDeltaRows(results: DriverResult[]): DeltaRow[] {
  const byMeeting = new Map<string, { quali?: DriverResult; race?: DriverResult }>();

  for (const result of results) {
    const entry = byMeeting.get(result.meeting_name) ?? {};
    if (result.session_type === "Qualifying") entry.quali = result;
    if (result.session_type === "Race") entry.race = result;
    byMeeting.set(result.meeting_name, entry);
  }

  const rows: DeltaRow[] = [];
  for (const [meeting, { quali, race }] of byMeeting) {
    if (!race) continue;

    if (race.dnf || race.dns || race.dsq) {
      rows.push({ meeting, delta: null, label: race.dsq ? "DSQ" : race.dns ? "DNS" : "DNF" });
      continue;
    }

    if (!quali?.position || !race.position) continue;

    const delta = quali.position - race.position;
    rows.push({
      meeting,
      delta,
      label: delta === 0 ? `P${race.position} → P${race.position}` : delta > 0 ? `+${delta}` : `${delta}`,
    });
  }

  return rows;
}

export default function GridToFinishDelta({ results }: Props) {
  const rows = buildDeltaRows(results);

  if (rows.length === 0) {
    return (
      <PlaceholderPanel
        title="Qualifying → Race Delta"
        description="No completed race weekends with both a qualifying and race result yet this season."
      />
    );
  }

  const maxDelta = Math.max(...rows.map((r) => Math.abs(r.delta ?? 0)), 1);

  return (
    <Panel className="h-full">
      <PanelHeader
        title="Qualifying → Race Delta"
        subtitle="Position change, qualifying to race finish"
      />

      <div className="space-y-2">
        {rows.map((row) => {
          const isDnf = row.delta === null;
          const isNeutral = row.delta === 0;
          const barWidth = isNeutral || isDnf ? 0 : (Math.abs(row.delta as number) / maxDelta) * 100;

          return (
            <div key={row.meeting} className="flex items-center gap-3">
              <span
                className="w-24 truncate text-[10px] font-mono uppercase text-text-muted shrink-0"
                title={row.meeting}
              >
                {row.meeting}
              </span>

              <div className="flex-1 h-5 relative bg-bg-hover">
                {!isNeutral && !isDnf && (row.delta as number) > 0 && (
                  <div
                    className="absolute inset-y-0 left-0 bg-primary/80"
                    style={{ width: `${barWidth}%` }}
                  />
                )}
                {!isNeutral && !isDnf && (row.delta as number) < 0 && (
                  <div
                    className="absolute inset-y-0 right-0 bg-danger/60"
                    style={{ width: `${barWidth}%` }}
                  />
                )}
              </div>

              <span
                className={`
                  w-14 text-right text-xs font-mono shrink-0
                  ${isDnf ? "text-danger" : isNeutral ? "text-text-muted" : "text-primary"}
                `}
              >
                {row.label}
              </span>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}
