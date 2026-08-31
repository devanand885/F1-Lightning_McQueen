"use client";

import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import InsufficientDataPanel from "@/features/shared/components/ui/InsufficientDataPanel";
import { DriverAnalytics } from "../types/driverAnalytics.types";

interface Props {
  analytics: DriverAnalytics | undefined;
  isLoading: boolean;
}

const MIN_TREND_POINTS = 5;

export default function PerformanceTrendChart({ analytics, isLoading }: Props) {
  if (isLoading || !analytics) {
    return (
      <Panel className="flex h-full min-h-55 flex-col">
        <PanelHeader title="Performance Trend" subtitle="Race pace vs. field average" />
        <div className="flex flex-1 items-center justify-center text-xs text-text-muted">Loading...</div>
      </Panel>
    );
  }

  const points = analytics.pace_trend
    .filter((p) => p.race_pace_field_relative !== null)
    .map((p) => ({
      label: p.meeting_name ?? "",
      date: p.date_start,
      // pace_ratio of 1.0 = exactly field-median pace; convert to a
      // "% off the field" delta so 0 reads as "at the field average" and
      // negative reads as "faster than the field", which is far more
      // legible on an axis than a ratio hovering near 1.0.
      pctOffField: p.race_pace_field_relative !== null ? (p.race_pace_field_relative - 1) * 100 : null,
    }));

  if (points.length < MIN_TREND_POINTS) {
    return (
      <InsufficientDataPanel
        title="Performance Trend"
        subtitle="Race pace vs. field average"
        description={`Only ${points.length} completed race session${points.length === 1 ? "" : "s"} with usable lap data - need at least ${MIN_TREND_POINTS} for a meaningful trend.`}
      />
    );
  }

  return (
    <Panel className="h-85">
      <PanelHeader title="Performance Trend" subtitle="Race pace vs. field average (median usable lap)" />
      <div className="h-62.5">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points}>
            <CartesianGrid stroke="#221d1a" vertical={false} />
            <XAxis dataKey="label" tick={{ fill: "#8d6f67", fontSize: 10 }} axisLine={false} tickLine={false} interval="preserveStartEnd" />
            <YAxis
              tick={{ fill: "#8d6f67", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => `${v > 0 ? "+" : ""}${v.toFixed(1)}%`}
            />
            <ReferenceLine y={0} stroke="#3a2f2a" strokeDasharray="3 3" />
            <Tooltip
              contentStyle={{ background: "#141214", border: "1px solid #2a211e", color: "#f5e8e1" }}
              formatter={(value) => {
                const v = Number(value);
                return [`${v > 0 ? "+" : ""}${v.toFixed(2)}%`, "vs. field"];
              }}
            />
            <Line type="monotone" dataKey="pctOffField" stroke="#ff6548" strokeWidth={2} dot={{ r: 2 }} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  );
}
