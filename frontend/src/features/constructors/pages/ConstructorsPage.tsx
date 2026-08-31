"use client";

import { useState } from "react";

import Panel from "@/features/shared/components/ui/Panel";
import SeasonSelect from "@/features/shared/components/filters/SeasonSelect";
import { useSeasons } from "@/features/shared/hooks/useSeasons";
import ConstructorsTable from "../components/ConstructorsTable";
import { useConstructors } from "../hooks/useConstructors";

export default function ConstructorsPage() {
  const [season, setSeason] = useState<number | undefined>(undefined);
  const seasonsQuery = useSeasons();
  const { data, isLoading, isError } = useConstructors(season);

  if (isLoading) {
    return (
      <div className="text-xs uppercase tracking-widest text-text-muted py-8">
        Loading constructor intelligence...
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

  return (
    <div className="mx-auto max-w-[1600px] space-y-3">
      <header className="flex flex-col justify-between gap-3 border-b border-border pb-4 sm:flex-row sm:items-end">
        <div>
          <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-primary">Constructor Intelligence</div>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-text-primary">Constructor Directory</h1>
          <p className="mt-1 text-xs text-text-muted">
            {data.count} active teams{activeSeason ? ` · Season ${activeSeason}` : ""}
          </p>
        </div>

        <SeasonSelect seasons={seasonsQuery.data?.items ?? []} value={season} onChange={setSeason} />
      </header>
      <ConstructorsTable constructors={data.items} />
    </div>
  );
}
