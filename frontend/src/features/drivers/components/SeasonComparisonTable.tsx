"use client";

import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { Driver } from "../types/driver.types";

interface SeasonRow {
  year: number;
  stats: Driver | null;
}

interface Props {
  seasons: SeasonRow[];
}

const METRICS: {
  key: "points" | "wins" | "podiums" | "avg_finish";
  label: string;
  format: (value: number) => string;
}[] = [
  { key: "points", label: "Points", format: (v) => v.toFixed(0) },
  { key: "wins", label: "Wins", format: (v) => v.toFixed(0) },
  { key: "podiums", label: "Podiums", format: (v) => v.toFixed(0) },
  { key: "avg_finish", label: "Avg Finish", format: (v) => v.toFixed(1) },
];

export default function SeasonComparisonTable({ seasons }: Props) {
  return (
    <Panel className="h-full">
      <PanelHeader title="Season Comparison" subtitle="Real season totals" />

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-border text-[9px] uppercase tracking-[0.14em] text-text-muted">
              <th className="py-2 text-left font-medium">Metric</th>
              {seasons.map((season) => (
                <th key={season.year} className="py-2 text-right font-medium">
                  {season.year}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {METRICS.map((metric) => (
              <tr key={metric.key} className="border-b border-border/60">
                <td className="py-2.5 text-text-secondary">{metric.label}</td>
                {seasons.map((season) => {
                  const value = season.stats?.[metric.key];
                  return (
                    <td key={season.year} className="py-2.5 text-right font-mono text-text-primary">
                      {value == null ? "—" : metric.format(value)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}
