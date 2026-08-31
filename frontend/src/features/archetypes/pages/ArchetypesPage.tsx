"use client";

import Panel from "@/features/shared/components/ui/Panel";
import PlaceholderPanel from "@/features/shared/components/ui/PlaceholderPanel";
import { useArchetypes } from "../hooks/useArchetypes";
import ArchetypeClusterCard from "../components/ArchetypeClusterCard";
import ArchetypeScatterChart from "../components/ArchetypeScatterChart";
import ExcludedDriversPanel from "../components/ExcludedDriversPanel";

const CLUSTER_COLOURS = ["#ff6548", "#4fb0ff", "#8bd450", "#e0c341", "#c785ff", "#ff8fb1"];

export default function ArchetypesPage() {
  const { data, isLoading, isError } = useArchetypes();

  if (isLoading) {
    return <div className="text-xs uppercase tracking-widest text-text-muted py-8">Loading archetypes...</div>;
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
        title="Driver Archetypes"
        description={data.reason ?? "No trained archetype model is available yet."}
      />
    );
  }

  return (
    <div className="space-y-3">
      <div>
        <div className="text-[10px] uppercase tracking-[0.18em] text-primary font-semibold">Driver Archetypes</div>
        <h1 className="text-xl font-bold text-text-primary tracking-tight mt-0.5">
          {data.n_eligible} of {data.n_population} drivers classified into {data.clusters.length} archetypes
        </h1>
        <p className="text-xs text-text-muted mt-1">
          K-means clustering on teammate-relative pace, tyre degradation, consistency and start performance -
          controls for car performance by comparing each driver only against their own teammate. Silhouette score:{" "}
          {data.silhouette?.toFixed(3)}.
        </p>
      </div>

      <ArchetypeScatterChart clusters={data.clusters} colours={CLUSTER_COLOURS} explainedVariance={data.pca_explained_variance_ratio} />

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
        {data.clusters.map((cluster, index) => (
          <ArchetypeClusterCard key={cluster.cluster} cluster={cluster} colour={CLUSTER_COLOURS[index % CLUSTER_COLOURS.length]} />
        ))}
      </div>

      <ExcludedDriversPanel drivers={data.excluded_drivers} />
    </div>
  );
}
