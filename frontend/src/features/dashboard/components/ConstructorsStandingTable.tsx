import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { Constructor } from "@/features/constructors/types/constructor.types";

interface Props {
  constructors: Constructor[];
}

export default function ConstructorStandingsTable({ constructors }: Props) {
  const leaderPoints = constructors[0]?.points ?? 0;

  return (
    <Panel className="overflow-hidden p-0">
      <div className="p-4 pb-0">
        <PanelHeader title="Constructor Standings" />
      </div>

      <table className="w-full">
        <thead>
          <tr className="border-y border-border text-[12px] bg-[#242324]">
            <th className="py-3 px-4 text-left font-semibold uppercase tracking-[0.16em] text-primary w-14">
              Pos
            </th>
            <th className="text-left font-semibold uppercase tracking-[0.16em] text-primary">Team</th>
            <th className="text-left font-semibold uppercase tracking-[0.16em] text-primary w-20">Points</th>
            <th className="text-left font-semibold uppercase tracking-[0.16em] text-primary w-16">Gap</th>
          </tr>
        </thead>

        <tbody>
          {constructors.map((constructor) => {
            const gap = constructor.points - leaderPoints;
            return (
              <tr
                key={constructor.constructor_id}
                className="border-b border-border bg-[#1c1b1c] hover:bg-bg-hover transition-colors"
              >
                <td className="px-4 py-4 font-mono text-[20px] text-text-secondary">
                  {constructor.position ? String(constructor.position).padStart(2, "0") : "—"}
                </td>

                <td className="py-4">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-[6px] h-[22px] flex-shrink-0"
                      style={{ background: constructor.team_colour ? `#${constructor.team_colour}` : "#666666" }}
                    />
                    <span className="text-text-primary text-[18px] font-mono">{constructor.name}</span>
                  </div>
                </td>

                <td className="text-text-primary text-[20px] font-mono">{constructor.points}</td>

                <td className={`text-[18px] font-mono ${gap === 0 ? "text-text-secondary" : "text-[#ff8c8c]"}`}>
                  {gap === 0 ? "—" : gap}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </Panel>
  );
}
