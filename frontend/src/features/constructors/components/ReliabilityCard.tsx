import { Activity } from "lucide-react";

import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import StatusBadge from "@/features/shared/components/ui/StatusBadge";
import type { ConstructorDetail } from "../types/constructor.types";

interface Props {
  constructor: ConstructorDetail;
  raceCount: number;
}

export default function ReliabilityCard({ constructor, raceCount }: Props) {
  const finishRate = constructor.dnf_rate != null ? (1 - constructor.dnf_rate) * 100 : null;
  const dnfCount = constructor.dnf_rate != null ? Math.round(constructor.dnf_rate * raceCount) : null;

  return (
    <Panel className="flex h-full min-h-[300px] flex-col rounded-none">
      <PanelHeader title="Finish Rate" action={<Activity size={14} className="text-primary" />} />

      <div className="flex flex-1 flex-col justify-between">
        <div>
          <div className="flex items-end justify-between gap-3">
            <div className="font-mono text-5xl font-light tracking-[-0.06em] text-text-primary">
              {finishRate != null ? finishRate.toFixed(1) : "—"}
              <span className="text-2xl text-text-secondary">%</span>
            </div>
            {finishRate != null && (
              <StatusBadge label={finishRate >= 90 ? "Strong" : "Mixed"} variant={finishRate >= 90 ? "success" : "warning"} />
            )}
          </div>
          <p className="mt-5 max-w-[260px] text-xs leading-5 text-text-muted">
            {dnfCount != null && raceCount > 0
              ? `${raceCount - dnfCount} of ${raceCount} race finishes completed this season.`
              : "No completed races yet this season."}
          </p>
        </div>
      </div>
    </Panel>
  );
}
