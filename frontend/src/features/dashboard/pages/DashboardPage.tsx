"use client";

import Panel from "@/features/shared/components/ui/Panel";
import { useDrivers } from "@/features/drivers/hooks/useDrivers";
import { useConstructors } from "@/features/constructors/hooks/useConstructors";
import DashboardHeader from "../components/DashboardHeader";
import KpiGrid from "../components/KpiGrid";
import PointsStandingsChart from "../components/PointsStandingsChart";
import StrategyInsightsPanel from "../components/StrategyInsightsPanel";
import StandingsSection from "../components/StandingsSection";
import SeasonCalendarPanel from "../components/SeasonCalendarPanel";
import { useCalendar, useOverview } from "../hooks/useDashboard";

export default function DashboardPage() {
  const overviewQuery = useOverview();
  const calendarQuery = useCalendar();
  const driversQuery = useDrivers();
  const constructorsQuery = useConstructors();

  const isLoading =
    overviewQuery.isLoading || calendarQuery.isLoading || driversQuery.isLoading || constructorsQuery.isLoading;
  const isError =
    overviewQuery.isError || calendarQuery.isError || driversQuery.isError || constructorsQuery.isError;

  if (isLoading) {
    return (
      <div className="text-xs uppercase tracking-widest text-text-muted py-8">
        Loading season intelligence...
      </div>
    );
  }

  if (isError || !overviewQuery.data || !calendarQuery.data || !driversQuery.data || !constructorsQuery.data) {
    return (
      <Panel className="text-xs uppercase tracking-widest text-text-muted">
        Unable to reach the F1 Lightning McQueen API. Confirm the backend is running.
      </Panel>
    );
  }

  const overview = overviewQuery.data;
  const calendar = calendarQuery.data.items;
  const drivers = driversQuery.data.items;
  const constructors = constructorsQuery.data.items;
  const nextMeeting = calendar.find((m) => m.status === "upcoming") ?? null;

  return (
    <div className="space-y-4">
      <DashboardHeader overview={overview} nextMeeting={nextMeeting} />

      <KpiGrid overview={overview} calendar={calendar} drivers={drivers} constructors={constructors} />

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
        <div className="xl:col-span-8">
          <PointsStandingsChart drivers={drivers} />
        </div>

        <div className="xl:col-span-4">
          <StrategyInsightsPanel />
        </div>
      </div>

      <StandingsSection drivers={drivers} constructors={constructors} />

      <SeasonCalendarPanel calendar={calendar} />
    </div>
  );
}
