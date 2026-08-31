"use client";

import { useState } from "react";
import { Search } from "lucide-react";

import Panel from "@/features/shared/components/ui/Panel";
import SeasonSelect from "@/features/shared/components/filters/SeasonSelect";
import { useSeasons } from "@/features/shared/hooks/useSeasons";
import { useDebouncedValue } from "@/lib/useDebouncedValue";
import CircuitsGrid from "../components/CircuitsGrid";
import { useCircuits } from "../hooks/useCircuits";

export default function CircuitsPage() {
  const [season, setSeason] = useState<number | undefined>(undefined);
  const [location, setLocation] = useState("");
  const debouncedLocation = useDebouncedValue(location, 300);

  const seasonsQuery = useSeasons();
  const { data, isLoading, isError } = useCircuits(season, debouncedLocation);

  if (isLoading) {
    return (
      <div className="text-xs uppercase tracking-widest text-text-muted py-8">
        Loading circuit intelligence...
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

  return (
    <div className="space-y-3">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div>
          <div className="text-[10px] uppercase tracking-[0.18em] text-primary font-semibold">
            Circuit Intelligence
          </div>
          <h1 className="text-xl font-bold text-text-primary tracking-tight mt-0.5">
            Circuit Directory
          </h1>
          <p className="text-xs text-text-muted mt-1">{data.count} circuits</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <SeasonSelect seasons={seasonsQuery.data?.items ?? []} value={season} onChange={setSeason} />
          <div className="flex h-9 items-center gap-1.5 border border-border bg-bg-card px-2">
            <Search size={12} className="text-text-muted" />
            <input
              value={location}
              onChange={(event) => setLocation(event.target.value)}
              placeholder="Filter by location..."
              className="w-40 bg-transparent text-xs text-text-primary outline-none placeholder:text-text-muted"
            />
          </div>
        </div>
      </div>

      <CircuitsGrid circuits={data.items} />
    </div>
  );
}
