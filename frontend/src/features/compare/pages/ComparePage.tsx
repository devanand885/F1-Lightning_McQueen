"use client";

import { useSearchParams } from "next/navigation";

import Panel from "@/features/shared/components/ui/Panel";
import AnalyticalComparisonTable from "../components/AnalyticalComparisonTable";
import ComparisonTable from "../components/ComparisonTable";
import { useCompare } from "../hooks/useCompare";
import { CompareEntityType } from "../types/compare.types";

export default function ComparePage() {
  const searchParams = useSearchParams();
  const type: CompareEntityType = searchParams.get("type") === "constructor" ? "constructor" : "driver";
  const ids = (searchParams.get("ids") ?? "")
    .split(",")
    .map(Number)
    .filter((n) => !Number.isNaN(n));

  const { data, isLoading, isError } = useCompare(type, ids);

  if (ids.length < 2) {
    return (
      <Panel className="text-xs uppercase tracking-widest text-text-muted">
        Select at least two {type === "driver" ? "drivers" : "constructors"} to compare.
      </Panel>
    );
  }

  if (isLoading) {
    return (
      <div className="text-xs uppercase tracking-widest text-text-muted py-8">Loading comparison...</div>
    );
  }

  if (isError || !data) {
    return (
      <Panel className="text-xs uppercase tracking-widest text-text-muted">
        Unable to load this comparison. Confirm the backend is running.
      </Panel>
    );
  }

  return (
    <div className="mx-auto max-w-[1000px] space-y-3">
      <div>
        <div className="text-[10px] uppercase tracking-[0.18em] text-primary font-semibold">
          {type === "driver" ? "Driver" : "Constructor"} Comparison
        </div>
        <h1 className="text-xl font-bold text-text-primary tracking-tight mt-0.5">
          {data.entities.map((entity) => entity.label).join(" vs ")}
        </h1>
      </div>

      <ComparisonTable comparison={data} />
      {data.entity_type === "driver" && data.analytics && data.analytics.length > 0 && (
        <AnalyticalComparisonTable entities={data.entities} analytics={data.analytics} />
      )}
    </div>
  );
}
