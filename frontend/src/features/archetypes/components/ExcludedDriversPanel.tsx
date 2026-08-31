import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { ExcludedDriver } from "../types/archetype.types";

interface Props {
  drivers: ExcludedDriver[];
}

export default function ExcludedDriversPanel({ drivers }: Props) {
  if (drivers.length === 0) return null;

  return (
    <Panel>
      <PanelHeader
        title="Excluded from classification"
        subtitle={`${drivers.length} driver${drivers.length === 1 ? "" : "s"} - insufficient completed race data (need 15+ race sessions, 500+ usable laps, 10+ stints)`}
      />
      <div className="grid grid-cols-1 gap-x-4 gap-y-1 sm:grid-cols-2 lg:grid-cols-3">
        {drivers.map((d) => (
          <div key={d.driver_id} className="flex items-center justify-between text-xs text-text-secondary">
            <span>{d.full_name}</span>
            <span className="font-mono text-text-muted">
              {d.race_sessions} races / {d.usable_race_laps} laps / {d.race_stints} stints
            </span>
          </div>
        ))}
      </div>
    </Panel>
  );
}
