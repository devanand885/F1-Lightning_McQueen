"use client";

import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import StatusBadge from "@/features/shared/components/ui/StatusBadge";
import PlaceholderPanel from "@/features/shared/components/ui/PlaceholderPanel";
import { useStrategyInsights } from "../hooks/useStrategyInsights";

/** Replaces the old "Live Intelligence" placeholder. Deliberately not
 * called that here - these are historical, post-race statistics computed
 * from completed sessions, not a live or predictive feed, and the copy
 * says so explicitly rather than implying otherwise. */
export default function StrategyInsightsPanel() {
  const { data, isLoading, isError } = useStrategyInsights();

  if (isLoading) {
    return (
      <Panel className="flex h-full min-h-85 flex-col">
        <PanelHeader title="Strategy Insights" subtitle="Historical, post-race analysis" />
        <div className="flex flex-1 items-center justify-center text-xs text-text-muted">Loading...</div>
      </Panel>
    );
  }

  if (isError || !data || data.insights.length === 0) {
    return (
      <PlaceholderPanel
        title="Strategy Insights"
        subtitle="Historical, post-race analysis"
        description="Not enough completed race data yet to compute season-wide strategy statistics."
        className="min-h-85"
      />
    );
  }

  return (
    <Panel className="flex h-full min-h-85 flex-col">
      <PanelHeader
        title="Strategy Insights"
        subtitle="Historical, post-race analysis"
        action={<StatusBadge label="Not live" variant="neutral" />}
      />
      <ul className="flex-1 space-y-3 pt-1">
        {data.insights.map((insight) => (
          <li key={insight.metric} className="border-l-2 border-primary/40 pl-3">
            <p className="text-sm leading-relaxed text-text-primary">{insight.statement}</p>
            <p className="mt-1 text-[10px] uppercase tracking-[0.14em] text-text-muted">
              sample size: {insight.sample_size}
            </p>
          </li>
        ))}
      </ul>
    </Panel>
  );
}
