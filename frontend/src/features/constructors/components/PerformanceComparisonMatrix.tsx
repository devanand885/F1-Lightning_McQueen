import Link from "next/link";

import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import type { Constructor } from "../types/constructor.types";

interface Props {
  constructors: Constructor[];
  activeConstructorId: string;
}

export default function PerformanceComparisonMatrix({ constructors, activeConstructorId }: Props) {
  return (
    <Panel className="rounded-none p-0">
      <div className="p-4 pb-0">
        <PanelHeader title="Performance Comparison Matrix" subtitle="Constructor field benchmark" />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px]">
          <thead>
            <tr className="border-y border-border bg-[#141214] text-[9px] uppercase tracking-[0.15em] text-primary">
              <th className="px-4 py-2.5 text-left font-semibold">Constructor</th>
              <th className="px-4 py-2.5 text-right font-semibold">Points</th>
              <th className="px-4 py-2.5 text-right font-semibold">Avg Finish</th>
              <th className="px-4 py-2.5 text-right font-semibold">Wins</th>
              <th className="px-4 py-2.5 text-right font-semibold">Podiums</th>
            </tr>
          </thead>
          <tbody>
            {constructors.map((constructor) => {
              const isActive = String(constructor.constructor_id) === activeConstructorId;
              const teamColor = constructor.team_colour ? `#${constructor.team_colour}` : "#666666";

              return (
                <tr
                  key={constructor.constructor_id}
                  className={`border-b border-border/70 transition-colors hover:bg-bg-hover ${isActive ? "bg-primary/[0.06]" : "bg-[#111111]"}`}
                >
                  <td className="px-4 py-3">
                    <Link href={`/constructors/${constructor.constructor_id}`} className="flex items-center gap-3">
                      <span className="h-5 w-1" style={{ backgroundColor: teamColor }} />
                      <span className="text-xs font-semibold uppercase tracking-[0.08em] text-text-primary">{constructor.name}</span>
                      {isActive && (
                        <span className="border border-primary/30 px-1.5 py-0.5 text-[7px] uppercase tracking-widest text-primary">
                          Active
                        </span>
                      )}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-sm text-text-primary">{constructor.points}</td>
                  <td className="px-4 py-3 text-right font-mono text-sm text-text-secondary">
                    {constructor.avg_finish != null ? constructor.avg_finish.toFixed(1) : "—"}
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-sm text-text-secondary">{constructor.wins}</td>
                  <td className="px-4 py-3 text-right font-mono text-sm text-text-secondary">{constructor.podiums}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}
