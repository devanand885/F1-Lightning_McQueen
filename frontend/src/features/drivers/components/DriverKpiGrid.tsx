"use client";

import { BarChart3, Target, TrendingUp, Trophy } from "lucide-react";
import DriverKpiCard from "./DriverKpiCard";
import { Driver, DriverResult } from "../types/driver.types";

interface Props {
  driver: Driver;
  results: DriverResult[];
}

export function DriverSecondaryKpis({ driver, results }: Props) {
  const races = results.filter((r) => r.session_type === "Race").length;
  const poles = results.filter((r) => r.session_type === "Qualifying" && r.position === 1).length;
  const podiumRatio = races > 0 ? (driver.podiums / races) * 100 : 0;
  const pointsPerRace = races > 0 ? driver.points / races : 0;

  return (
    <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
      <DriverKpiCard
        title="Grand Prix Wins"
        value={String(driver.wins)}
        icon={<Trophy size={13} />}
        compact
      />
      <DriverKpiCard
        title="Pole Positions"
        value={String(poles)}
        icon={<Target size={13} />}
        compact
      />
      <DriverKpiCard
        title="Podium Ratio"
        value={`${podiumRatio.toFixed(1)}%`}
        icon={<TrendingUp size={13} />}
        compact
      />
      <DriverKpiCard
        title="Points / Race"
        value={pointsPerRace.toFixed(1)}
        icon={<BarChart3 size={13} />}
        compact
      />
    </div>
  );
}
