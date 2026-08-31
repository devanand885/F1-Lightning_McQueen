"use client";

import { PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer, Tooltip } from "recharts";

import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import InsufficientDataPanel from "@/features/shared/components/ui/InsufficientDataPanel";
import { DriverAnalytics } from "../types/driverAnalytics.types";

interface Props {
  analytics: DriverAnalytics | undefined;
  isLoading: boolean;
}

const MIN_CIRCUIT_TYPES = 2;
const MIN_SESSIONS_PER_TYPE = 2;

export default function CircuitCapabilityRadar({ analytics, isLoading }: Props) {
  if (isLoading || !analytics) {
    return (
      <Panel className="flex h-full min-h-55 flex-col">
        <PanelHeader title="Circuit Capability" subtitle="Pace vs. teammate, by circuit type" />
        <div className="flex flex-1 items-center justify-center text-xs text-text-muted">Loading...</div>
      </Panel>
    );
  }

  const usable = analytics.circuit_type_breakdown.filter((c) => c.n_sessions >= MIN_SESSIONS_PER_TYPE);

  if (usable.length < MIN_CIRCUIT_TYPES) {
    return (
      <InsufficientDataPanel
        title="Circuit Capability"
        subtitle="Pace vs. teammate, by circuit type"
        description={`Only ${usable.length} circuit type${usable.length === 1 ? "" : "s"} with ${MIN_SESSIONS_PER_TYPE}+ sessions of teammate-comparable data - need at least ${MIN_CIRCUIT_TYPES}.`}
      />
    );
  }

  // teammate_delta is negative when the driver is faster than their
  // teammate; flip the sign so the radar reads "further out = stronger",
  // the intuitive direction for this kind of chart.
  const data = usable.map((c) => ({
    circuitType: c.circuit_type,
    strength: -(c.race_pace_teammate_relative * 100),
    n_sessions: c.n_sessions,
  }));

  return (
    <Panel className="h-85">
      <PanelHeader title="Circuit Capability" subtitle="Pace vs. teammate, by circuit type (further out = stronger)" />
      <div className="h-62.5">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data}>
            <PolarGrid stroke="#221d1a" />
            <PolarAngleAxis dataKey="circuitType" tick={{ fill: "#8d6f67", fontSize: 11 }} />
            <Radar dataKey="strength" stroke="#ff6548" fill="#ff6548" fillOpacity={0.25} isAnimationActive={false} />
            <Tooltip
              contentStyle={{ background: "#141214", border: "1px solid #2a211e", color: "#f5e8e1" }}
              formatter={(value, _name, entry) => {
                const v = Number(value);
                const payload = entry?.payload as { n_sessions: number; circuitType: string } | undefined;
                return [
                  `${v > 0 ? "+" : ""}${v.toFixed(2)}% vs teammate (${payload?.n_sessions ?? "?"} sessions)`,
                  payload?.circuitType ?? "",
                ];
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  );
}
