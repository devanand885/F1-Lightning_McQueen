import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import StatusBadge from "@/features/shared/components/ui/StatusBadge";
import { CompareEntity, CompareMetric } from "../types/compare.types";

interface Props {
  entities: CompareEntity[];
  analytics: CompareMetric[];
}

function formatValue(metric: CompareMetric, value: number | string | null): string {
  if (value == null) return "—";
  if (typeof value === "string") return value;
  if (metric.unit === "ratio delta") return `${value > 0 ? "+" : ""}${(value * 100).toFixed(2)}%`;
  if (metric.unit === "s/lap") return `${value > 0 ? "+" : ""}${value.toFixed(3)}s`;
  if (metric.unit === "CV") return value.toFixed(3);
  return String(value);
}

/** Deliberately separate from ComparisonTable: those are raw season
 * aggregates (points, wins, finishing position); this is the derived,
 * teammate-relative analytical layer (pace vs. teammate, tyre degradation,
 * consistency, archetype). Keeping them visually distinct is the point -
 * a driver "ahead" here isn't a claim that they're objectively better,
 * only that they beat their own teammate on that specific dimension. */
export default function AnalyticalComparisonTable({ entities, analytics }: Props) {
  return (
    <Panel className="overflow-hidden p-0">
      <div className="p-4 pb-0">
        <PanelHeader
          title="Analytical Comparison"
          subtitle="Teammate-relative pace and race craft - not a claim of overall superiority"
          action={<StatusBadge label="Derived" variant="warning" />}
        />
      </div>

      <table className="w-full">
        <thead>
          <tr className="border-y border-border text-[10px] uppercase tracking-[0.14em] text-text-muted">
            <th className="py-3 px-4 text-left font-medium">Metric</th>
            {entities.map((entity) => (
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
          {analytics.map((metric) => (
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
      <p className="px-4 py-3 text-[11px] leading-relaxed text-text-muted border-t border-border">
        &quot;vs. teammate&quot; figures compare same-session, same-constructor teammates only - they control for car
        performance but require both drivers to have shared a teammate this season. A driver with no eligible
        session data shows as &quot;—&quot;.
      </p>
    </Panel>
  );
}
