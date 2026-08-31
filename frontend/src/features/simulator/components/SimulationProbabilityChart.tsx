"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { SimulatedDriver } from "../types/simulator.types";

interface Props {
  drivers: SimulatedDriver[];
}

export default function SimulationProbabilityChart({ drivers }: Props) {
  const data = drivers
    .filter((d) => d.championship_win_probability > 0.001)
    .sort((a, b) => b.championship_win_probability - a.championship_win_probability)
    .slice(0, 8)
    .map((d) => ({
      name: d.full_name.split(" ").slice(-1)[0],
      probability: d.championship_win_probability * 100,
    }));

  return (
    <Panel className="h-85">
      <PanelHeader title="Championship Win Probability" subtitle="Share of simulated seasons won, by driver" />
      <div className="h-62.5">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid stroke="#221d1a" vertical={false} />
            <XAxis dataKey="name" tick={{ fill: "#8d6f67", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis hide />
            <Tooltip
              contentStyle={{ background: "#141214", border: "1px solid #2a211e", color: "#f5e8e1" }}
              formatter={(value) => [`${Number(value).toFixed(1)}%`, "win probability"]}
            />
            <Bar dataKey="probability" radius={[2, 2, 0, 0]} fill="#ff6548">
              {data.map((entry) => (
                <Cell key={entry.name} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  );
}
