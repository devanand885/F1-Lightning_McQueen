import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { CompareMetric, ComparisonResponse } from "../types/compare.types";

interface Props {
  comparison: ComparisonResponse;
}

function formatValue(metric: CompareMetric, value: number | string | null): string {
  if (value == null) return "—";
  if (typeof value === "string") return value;
  if (metric.unit === "%") return `${(value * 100).toFixed(1)}%`;
  if (metric.key === "avg_finish") return value.toFixed(1);
  return String(Math.round(value));
}

export default function ComparisonTable({ comparison }: Props) {
  return (
    <Panel className="overflow-hidden p-0">
      <div className="p-4 pb-0">
        <PanelHeader
          title={comparison.entity_type === "driver" ? "Driver Comparison" : "Constructor Comparison"}
          subtitle={`Season ${comparison.season} · real season aggregates only, no derived methodology`}
        />
      </div>

      <table className="w-full">
        <thead>
          <tr className="border-y border-border text-[10px] uppercase tracking-[0.14em] text-text-muted">
            <th className="py-3 px-4 text-left font-medium">Metric</th>
            {comparison.entities.map((entity) => (
              <th key={entity.id} className="py-3 px-4 text-right font-medium">
                <div className="flex items-center justify-end gap-2">
                  {entity.colour && <span className="h-3 w-1 shrink-0" style={{ background: `#${entity.colour}` }} />}
                  <span className="text-sm font-semibold normal-case tracking-normal text-text-primary">
                    {entity.label}
                  </span>
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {comparison.metrics.map((metric) => (
            <tr key={metric.key} className="border-b border-border/60">
              <td className="py-3 px-4 text-sm text-text-secondary">{metric.label}</td>
              {metric.values.map((value, index) => (
                <td key={index} className="py-3 px-4 text-right font-mono text-sm text-text-primary">
                  {formatValue(metric, value)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </Panel>
  );
}
