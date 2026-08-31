"use client";

import Panel from "@/features/shared/components/ui/Panel";
import CircuitEntitiesCard from "../components/CircuitEntitiesCard";
import CircuitHero from "../components/CircuitHero";
import CircuitMeetingsTable from "../components/CircuitMeetingsTable";
import { useCircuit } from "../hooks/useCircuit";

interface Props {
  circuitId: string;
}

export default function CircuitDetailPage({ circuitId }: Props) {
  const { data: circuit, isLoading, isError } = useCircuit(circuitId);

  if (isLoading) {
    return (
      <div className="text-xs uppercase tracking-widest text-text-muted py-8">
        Loading circuit intelligence...
      </div>
    );
  }

  if (isError || !circuit) {
    return (
      <Panel className="text-xs uppercase tracking-widest text-text-muted">
        Circuit not found, or the backend is unreachable.
      </Panel>
    );
  }

  return (
    <div className="mx-auto max-w-[1600px] space-y-3">
      <CircuitHero circuit={circuit} />

      <div className="grid grid-cols-1 gap-3 xl:grid-cols-2">
        <CircuitEntitiesCard title="Drivers" items={circuit.drivers} />
        <CircuitEntitiesCard title="Constructors" items={circuit.constructors} />
      </div>

      <CircuitMeetingsTable meetings={circuit.meetings} />
    </div>
  );
}
