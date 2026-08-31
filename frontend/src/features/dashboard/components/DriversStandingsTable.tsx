import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { Driver } from "@/features/drivers/types/driver.types";

interface Props {
  drivers: Driver[];
}

export default function DriverStandingsTable({ drivers }: Props) {
  return (
    <Panel className="overflow-hidden p-0">
      <div className="p-4 pb-0">
        <PanelHeader title="Driver Standings" />
      </div>

      <table className="w-full">
        <thead>
          <tr className="border-y border-border text-[12px] bg-[#242324]">
            <th className="py-3 px-4 text-left font-semibold uppercase tracking-[0.16em] text-primary w-14">
              Pos
            </th>
            <th className="text-left font-semibold uppercase tracking-[0.16em] text-primary">Driver</th>
            <th className="text-left font-semibold uppercase tracking-[0.16em] text-primary">Team</th>
            <th className="text-right pr-4 font-semibold uppercase tracking-[0.16em] text-primary w-20">
              Points
            </th>
          </tr>
        </thead>

        <tbody>
          {drivers.map((driver) => (
            <tr
              key={driver.driver_number}
              className="border-b border-border bg-[#1c1b1c] hover:bg-bg-hover transition-colors"
            >
              <td className="px-4 py-4 font-mono text-[20px] text-text-secondary">
                {driver.position ? String(driver.position).padStart(2, "0") : "—"}
              </td>

              <td className="py-4">
                <div className="flex items-center gap-3">
                  <div
                    className="w-[6px] h-[22px] flex-shrink-0"
                    style={{ background: driver.team_colour ? `#${driver.team_colour}` : "#666666" }}
                  />
                  <span className="text-text-primary text-[18px] font-mono">{driver.full_name}</span>
                </div>
              </td>

              <td className="text-text-secondary text-sm">{driver.team_name ?? "—"}</td>

              <td className="text-right pr-4 text-text-primary text-[20px] font-mono">{driver.points}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Panel>
  );
}
