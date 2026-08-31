"use client";

import { useMemo, useState } from "react";

import Panel from "@/features/shared/components/ui/Panel";
import SeasonSelect from "@/features/shared/components/filters/SeasonSelect";
import { useSeasons } from "@/features/shared/hooks/useSeasons";
import DriverTable from "../components/DriverTable";
import { useDrivers } from "../hooks/useDrivers";

export default function DriversPage() {
  const [season, setSeason] = useState<number | undefined>(undefined);
  const [team, setTeam] = useState("all");

  const seasonsQuery = useSeasons();
  const { data, isLoading, isError } = useDrivers(season);

  const teams = useMemo(() => {
    if (!data) return [];
    const names = data.items.map((driver) => driver.team_name).filter((name): name is string => Boolean(name));
    return Array.from(new Set(names)).sort();
  }, [data]);

  if (isLoading) {
    return (
      <div className="text-xs uppercase tracking-widest text-text-muted py-8">
        Loading driver intelligence...
      </div>
    );
  }

  if (isError || !data) {
    return (
      <Panel className="text-xs uppercase tracking-widest text-text-muted">
        Unable to reach the F1 Lightning McQueen API. Confirm the backend is running.
      </Panel>
    );
  }

  const activeSeason = data.items[0]?.season ?? season;
  const filtered = team === "all" ? data.items : data.items.filter((driver) => driver.team_name === team);

  return (
    <div className="space-y-3">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div>
          <div className="text-[10px] uppercase tracking-[0.18em] text-primary font-semibold">
            Driver Intelligence
          </div>
          <h1 className="text-xl font-bold text-text-primary tracking-tight mt-0.5">
            Driver Directory
          </h1>
          <p className="text-xs text-text-muted mt-1">
            {filtered.length} of {data.count} drivers{activeSeason ? ` · Season ${activeSeason}` : ""}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <SeasonSelect seasons={seasonsQuery.data?.items ?? []} value={season} onChange={setSeason} />
          <select
            value={team}
            onChange={(event) => setTeam(event.target.value)}
            className="h-9 border border-border bg-bg-card px-2 text-xs text-text-secondary focus:border-primary/50 focus:outline-none"
          >
            <option value="all">All Teams</option>
            {teams.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <DriverTable drivers={filtered} />
    </div>
  );
}
