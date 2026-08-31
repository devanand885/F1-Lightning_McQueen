"use client";

import Panel from "@/features/shared/components/ui/Panel";
import PlaceholderPanel from "@/features/shared/components/ui/PlaceholderPanel";
import { useChampionshipSimulation } from "../hooks/useChampionshipSimulation";
import SimulationProbabilityChart from "../components/SimulationProbabilityChart";
import SimulationTable from "../components/SimulationTable";

export default function SimulatorPage() {
  const { data, isLoading, isError } = useChampionshipSimulation();

  if (isLoading) {
    return <div className="text-xs uppercase tracking-widest text-text-muted py-8">Running simulation...</div>;
  }

  if (isError || !data) {
    return (
      <Panel className="text-xs uppercase tracking-widest text-text-muted">
        Unable to reach the F1 Lightning McQueen API. Confirm the backend is running.
      </Panel>
    );
  }

  if (!data.available) {
    return (
      <PlaceholderPanel
        title="Championship Simulator"
        description={data.reason ?? "No simulation is available for this season yet."}
      />
    );
  }

  return (
    <div className="space-y-3">
      <div>
        <div className="text-[10px] uppercase tracking-[0.18em] text-primary font-semibold">Championship Simulator</div>
        <h1 className="text-xl font-bold text-text-primary tracking-tight mt-0.5">
          {data.n_remaining_races} races remaining, {(data.n_simulations ?? 0).toLocaleString()} simulations
        </h1>
      </div>

      <Panel className="border-warning/30 bg-warning/5">
        <p className="text-xs leading-relaxed text-text-secondary">
          <span className="font-semibold text-warning">This is a simulation, not a prediction.</span>{" "}
          {`Each driver's projection starts from their real, already-accumulated ${data.season} points and adds ${data.n_remaining_races} simulated remaining races, using a strength rating derived from their real field-relative race and qualifying pace, a noise term calibrated from their own session-to-session variance, and a Bayesian-shrunk DNF rate from their real reliability history. It assumes every driver who has raced this season keeps racing for the rest of it - mid-season driver changes aren't modeled. Run with a fixed random seed (${data.seed}) for reproducibility.`}
        </p>
      </Panel>

      <SimulationProbabilityChart drivers={data.drivers} />
      <SimulationTable drivers={data.drivers} />
    </div>
  );
}
