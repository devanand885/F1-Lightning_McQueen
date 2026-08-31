"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import Panel from "@/features/shared/components/ui/Panel";
import EntityPickerModal from "@/features/compare/components/EntityPickerModal";
import ConstructorHero from "../components/ConstructorHero";
import DevelopmentProgressCard from "../components/DevelopmentProgressCard";
import PerformanceComparisonMatrix from "../components/PerformanceComparisonMatrix";
import PerformanceEfficiencyScatter from "../components/PerformanceEfficiencyScatter";
import PerformanceProfileRadar from "../components/PerformanceProfileRadar";
import PitLaneEfficiencyCard from "../components/PitLaneEfficiencyCard";
import ReliabilityCard from "../components/ReliabilityCard";
import WindTunnelAvailabilityCard from "../components/WindTunnelAvailabilityCard";

import { useConstructor } from "../hooks/useConstructor";
import { useConstructorDrivers } from "../hooks/useConstructorDrivers";
import { useConstructorPitStops } from "../hooks/useConstructorPitStops";
import { useConstructorResults } from "../hooks/useConstructorResults";
import { useConstructors } from "../hooks/useConstructors";

interface Props {
  constructorId: string;
}

export default function ConstructorAnalyticsPage({ constructorId }: Props) {
  const router = useRouter();
  const [pickerOpen, setPickerOpen] = useState(false);

  const { data: constructor, isLoading, isError } = useConstructor(constructorId);
  const { data: driversResponse } = useConstructorDrivers(constructorId);
  const { data: pitStopsResponse } = useConstructorPitStops(constructorId);
  const { data: resultsResponse } = useConstructorResults(constructorId);
  const { data: allConstructorsResponse } = useConstructors();

  if (isLoading) {
    return (
      <div className="text-xs uppercase tracking-widest text-text-muted py-8">
        Loading constructor intelligence...
      </div>
    );
  }

  if (isError || !constructor) {
    return (
      <Panel className="text-xs uppercase tracking-widest text-text-muted">
        Constructor intelligence profile not found, or the backend is unreachable.
      </Panel>
    );
  }

  const drivers = driversResponse?.items ?? [];
  const pitStops = pitStopsResponse?.items ?? [];
  const results = resultsResponse?.items ?? [];
  const allConstructors = allConstructorsResponse?.items ?? [];
  const raceCount = results.filter((r) => r.session_type === "Race").length;

  return (
    <div className="mx-auto max-w-[1600px] space-y-3">
      <ConstructorHero constructor={constructor} drivers={drivers} onCompareClick={() => setPickerOpen(true)} />

      <section className="grid grid-cols-1 gap-3 xl:grid-cols-12">
        <div className="xl:col-span-3"><ReliabilityCard constructor={constructor} raceCount={raceCount} /></div>
        <div className="xl:col-span-6"><PerformanceEfficiencyScatter /></div>
        <div className="xl:col-span-3"><PitLaneEfficiencyCard pitStops={pitStops} /></div>
      </section>

      <section className="grid grid-cols-1 gap-3 xl:grid-cols-12">
        <div className="xl:col-span-7"><PerformanceProfileRadar /></div>
        <div className="space-y-3 xl:col-span-5">
          <DevelopmentProgressCard />
          <WindTunnelAvailabilityCard />
        </div>
      </section>

      <PerformanceComparisonMatrix constructors={allConstructors} activeConstructorId={constructorId} />

      {pickerOpen && (
        <EntityPickerModal
          title="Compare with..."
          options={allConstructors.map((c) => ({ id: c.constructor_id, label: c.name, colour: c.team_colour }))}
          excludeId={constructor.constructor_id}
          onClose={() => setPickerOpen(false)}
          onSelect={(otherId) => {
            router.push(`/compare?type=constructor&ids=${constructor.constructor_id},${otherId}`);
          }}
        />
      )}
    </div>
  );
}
