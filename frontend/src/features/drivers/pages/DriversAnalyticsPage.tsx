"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQueries } from "@tanstack/react-query";

import Panel from "@/features/shared/components/ui/Panel";
import EntityPickerModal from "@/features/compare/components/EntityPickerModal";
import { useSeasons } from "@/features/shared/hooks/useSeasons";
import { getDriver } from "../api/drivers.api";
import DriverHero from "../components/DriverHero";
import { DriverSecondaryKpis } from "../components/DriverKpiGrid";
import PerformanceTrendChart from "../components/PerformanceTrendChart";
import CircuitCapabilityRadar from "../components/CircuitCapabilityRadar";
import GridToFinishDelta from "../components/GridToFinishDelta";
import SeasonComparisonTable from "../components/SeasonComparisonTable";

import { useDriver } from "../hooks/useDriver";
import { useDriverAnalytics } from "../hooks/useDriverAnalytics";
import { useDriverResults } from "../hooks/useDriverResults";
import { useDrivers } from "../hooks/useDrivers";

interface Props {
  driverNumber: string;
}

export default function DriverAnalyticsPage({ driverNumber }: Props) {
  const router = useRouter();
  const [pickerOpen, setPickerOpen] = useState(false);

  const { data: driver, isLoading, isError } = useDriver(driverNumber);
  const { data: resultsResponse } = useDriverResults(driverNumber);
  const { data: allDriversResponse } = useDrivers();
  const { data: analytics, isLoading: analyticsLoading } = useDriverAnalytics(driverNumber);

  const seasonsQuery = useSeasons();
  const seasonYears = [...(seasonsQuery.data?.items ?? [])].sort((a, b) => a - b);
  const seasonQueries = useQueries({
    queries: seasonYears.map((year) => ({
      queryKey: ["driver", driverNumber, year],
      queryFn: () => getDriver(driverNumber, year),
      enabled: Boolean(driverNumber),
    })),
  });

  if (isLoading) {
    return (
      <div className="text-xs uppercase tracking-widest text-text-muted py-8">
        Loading driver intelligence...
      </div>
    );
  }

  if (isError || !driver) {
    return (
      <Panel className="text-xs uppercase tracking-widest text-text-muted">
        Driver not found, or the backend is unreachable.
      </Panel>
    );
  }

  const results = resultsResponse?.items ?? [];
  const allDrivers = allDriversResponse?.items ?? [];

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-3">
        <DriverHero driver={driver} onCompareClick={() => setPickerOpen(true)} />
        <DriverSecondaryKpis driver={driver} results={results} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-3">
        <PerformanceTrendChart analytics={analytics} isLoading={analyticsLoading} />
        <CircuitCapabilityRadar analytics={analytics} isLoading={analyticsLoading} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-3">
        <GridToFinishDelta results={results} />
        <SeasonComparisonTable
          seasons={seasonYears.map((year, index) => ({ year, stats: seasonQueries[index]?.data ?? null }))}
        />
      </div>

      {pickerOpen && (
        <EntityPickerModal
          title="Compare with..."
          options={allDrivers.map((d) => ({ id: d.driver_number, label: d.full_name, colour: d.team_colour }))}
          excludeId={driver.driver_number}
          onClose={() => setPickerOpen(false)}
          onSelect={(otherId) => {
            router.push(`/compare?type=driver&ids=${driver.driver_number},${otherId}`);
          }}
        />
      )}
    </div>
  );
}
