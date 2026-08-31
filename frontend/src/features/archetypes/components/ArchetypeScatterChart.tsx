"use client";

import { CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis } from "recharts";

import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { ArchetypeCluster } from "../types/archetype.types";

interface Props {
  clusters: ArchetypeCluster[];
  colours: string[];
  explainedVariance: number[] | null;
}

export default function ArchetypeScatterChart({ clusters, colours, explainedVariance }: Props) {
  const subtitle = explainedVariance
    ? `PCA projection - components explain ${(explainedVariance[0] * 100).toFixed(0)}% and ${(explainedVariance[1] * 100).toFixed(0)}% of feature variance`
    : "PCA projection of the clustering feature space";

  return (
    <Panel className="h-100">
      <PanelHeader title="Archetype Map" subtitle={subtitle} />
      <div className="h-75">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart>
            <CartesianGrid stroke="#221d1a" />
            <XAxis type="number" dataKey="pca_x" name="PC1" tick={{ fill: "#8d6f67", fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis type="number" dataKey="pca_y" name="PC2" tick={{ fill: "#8d6f67", fontSize: 10 }} axisLine={false} tickLine={false} />
            <ZAxis range={[80, 80]} />
            <Tooltip
              cursor={{ strokeDasharray: "3 3" }}
              contentStyle={{ background: "#141214", border: "1px solid #2a211e", color: "#f5e8e1" }}
              formatter={(_value, _name, entry) => {
                const payload = entry?.payload as { full_name: string } | undefined;
                return [payload?.full_name ?? "", ""];
              }}
            />
            {clusters.map((cluster, index) => (
              <Scatter key={cluster.cluster} name={cluster.name} data={cluster.drivers} fill={colours[index % colours.length]} />
            ))}
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  );
}
