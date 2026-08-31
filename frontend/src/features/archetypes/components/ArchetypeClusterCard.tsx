import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { ArchetypeCluster } from "../types/archetype.types";
import { describeTraits } from "./traitLabels";

interface Props {
  cluster: ArchetypeCluster;
  colour: string;
}

export default function ArchetypeClusterCard({ cluster, colour }: Props) {
  const traits = describeTraits(cluster.centroid);

  return (
    <Panel>
      <PanelHeader
        title={cluster.name}
        subtitle={`${cluster.size} driver${cluster.size === 1 ? "" : "s"}`}
        action={<span className="h-3 w-3 rounded-full" style={{ background: colour }} />}
      />
      <ul className="mb-3 space-y-1">
        {traits.map((trait) => (
          <li key={trait} className="text-xs leading-relaxed text-text-secondary">
            · {trait}
          </li>
        ))}
      </ul>
      <div className="flex flex-wrap gap-1.5">
        {cluster.drivers.map((d) => (
          <span
            key={d.driver_id}
            className="rounded border border-border bg-bg-surface px-2 py-1 text-[11px] text-text-primary"
          >
            {d.full_name}
          </span>
        ))}
      </div>
    </Panel>
  );
}
