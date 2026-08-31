import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { SimulatedDriver } from "../types/simulator.types";

interface Props {
  drivers: SimulatedDriver[];
}

function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export default function SimulationTable({ drivers }: Props) {
  const sorted = [...drivers].sort((a, b) => b.expected_points - a.expected_points);

  return (
    <Panel className="overflow-hidden p-0">
      <div className="p-4 pb-0">
        <PanelHeader title="Championship Simulation" subtitle="Real current points + Monte Carlo projection of remaining races" />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-y border-border text-[10px] uppercase tracking-[0.14em] text-text-muted">
              <th className="py-3 px-4 text-left font-medium">Driver</th>
              <th className="py-3 px-4 text-right font-medium">Current Pts</th>
              <th className="py-3 px-4 text-right font-medium">Expected Pts</th>
              <th className="py-3 px-4 text-right font-medium">Expected Pos</th>
              <th className="py-3 px-4 text-right font-medium">Title Win %</th>
              <th className="py-3 px-4 text-right font-medium">Title Podium %</th>
              <th className="py-3 px-4 text-right font-medium">Race Win %</th>
              <th className="py-3 px-4 text-right font-medium">Race Podium %</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((d) => (
              <tr key={d.driver_number} className="border-b border-border/60">
                <td className="py-3 px-4 text-sm text-text-primary">{d.full_name}</td>
                <td className="py-3 px-4 text-right font-mono text-sm text-text-secondary">{d.current_points}</td>
                <td className="py-3 px-4 text-right font-mono text-sm text-text-primary">{d.expected_points.toFixed(0)}</td>
                <td className="py-3 px-4 text-right font-mono text-sm text-text-secondary">{d.expected_championship_position.toFixed(1)}</td>
                <td className="py-3 px-4 text-right font-mono text-sm text-text-primary">{pct(d.championship_win_probability)}</td>
                <td className="py-3 px-4 text-right font-mono text-sm text-text-secondary">{pct(d.championship_podium_probability)}</td>
                <td className="py-3 px-4 text-right font-mono text-sm text-text-secondary">{pct(d.race_win_probability)}</td>
                <td className="py-3 px-4 text-right font-mono text-sm text-text-secondary">{pct(d.race_podium_probability)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}
