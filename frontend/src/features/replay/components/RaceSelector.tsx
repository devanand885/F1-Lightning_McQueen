"use client";

import { useMemo, useState } from "react";

import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { RaceOption } from "../types/replay.types";

interface Props {
  races: RaceOption[];
  onLoad: (sessionKey: number) => void;
}

export default function RaceSelector({ races, onLoad }: Props) {
  const seasons = useMemo(() => [...new Set(races.map((r) => r.season))].sort((a, b) => b - a), [races]);
  const [season, setSeason] = useState<number | undefined>(seasons[0]);

  const racesInSeason = useMemo(
    () => races.filter((r) => r.season === (season ?? seasons[0])).sort((a, b) => (a.date_start ?? "").localeCompare(b.date_start ?? "")),
    [races, season, seasons],
  );
  const [sessionKey, setSessionKey] = useState<number | undefined>(racesInSeason[0]?.session_key);

  const effectiveSeason = season ?? seasons[0];
  const effectiveRaces = season === undefined ? racesInSeason : races.filter((r) => r.season === season);
  const selectedSessionKey = sessionKey ?? effectiveRaces[0]?.session_key;

  return (
    <Panel>
      <PanelHeader title="Race Replay" subtitle="Historical, full-race telemetry from OpenF1 - not live" />
      <div className="flex flex-wrap items-end gap-3">
        <div className="flex flex-col gap-1">
          <label className="text-[10px] uppercase tracking-[0.14em] text-text-muted">Season</label>
          <select
            value={effectiveSeason}
            onChange={(e) => {
              const year = Number(e.target.value);
              setSeason(year);
              const first = races.find((r) => r.season === year);
              setSessionKey(first?.session_key);
            }}
            className="h-9 border border-border bg-bg-card px-2 text-xs text-text-secondary focus:border-primary/50 focus:outline-none"
          >
            {seasons.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] uppercase tracking-[0.14em] text-text-muted">Race</label>
          <select
            value={selectedSessionKey ?? ""}
            onChange={(e) => setSessionKey(Number(e.target.value))}
            className="h-9 min-w-50 border border-border bg-bg-card px-2 text-xs text-text-secondary focus:border-primary/50 focus:outline-none"
          >
            {effectiveRaces.map((r) => (
              <option key={r.session_key} value={r.session_key}>
                {r.meeting_name}
                {r.circuit_short_name ? ` (${r.circuit_short_name})` : ""}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] uppercase tracking-[0.14em] text-text-muted">Session</label>
          <div className="flex h-9 items-center border border-border bg-bg-surface px-2 text-xs text-text-muted">
            Race
          </div>
        </div>

        <button
          onClick={() => selectedSessionKey && onLoad(selectedSessionKey)}
          disabled={!selectedSessionKey}
          className="h-9 border border-primary/40 bg-primary/10 px-4 text-xs font-semibold text-primary transition-colors hover:bg-primary/20 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Load Replay
        </button>
      </div>
    </Panel>
  );
}
