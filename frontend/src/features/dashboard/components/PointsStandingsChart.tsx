"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { Driver } from "@/features/drivers/types/driver.types";

interface Props {
  drivers: Driver[];
}

export default function PointsStandingsChart({ drivers }: Props) {
  const top = drivers.slice(0, 8).map((driver) => ({
    name: driver.name_acronym ?? driver.full_name,
    points: driver.points,
    fill: driver.team_colour ? `#${driver.team_colour}` : "#ff6548",
  }));

  return (
    <Panel className="h-85">
      <PanelHeader title="Championship Points" subtitle="Top drivers this season" />

      <div className="h-62.5">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={top}>
            <CartesianGrid stroke="#221d1a" vertical={false} />

            <XAxis dataKey="name" tick={{ fill: "#8d6f67", fontSize: 11 }} axisLine={false} tickLine={false} />

            <YAxis hide />

            <Tooltip contentStyle={{ background: "#141214", border: "1px solid #2a211e", color: "#f5e8e1" }} />

            <Bar dataKey="points" radius={[2, 2, 0, 0]}>
              {top.map((entry) => (
                <Cell key={entry.name} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  );
}
