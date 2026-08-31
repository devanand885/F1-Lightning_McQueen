"use client";

import Link from "next/link";
import Image from "next/image";
import { Driver } from "../types/driver.types";

interface Props {
  driver: Driver;
}

export default function DriverTableRow({ driver }: Props) {
  const teamColor = driver.team_colour ? `#${driver.team_colour}` : "#666666";

  return (
    <tr className="border-b border-border bg-[#111111] hover:bg-bg-hover transition-colors duration-150">
      <td className="px-3 py-2 font-mono text-sm text-text-secondary">
        {driver.position ? String(driver.position).padStart(2, "0") : "—"}
      </td>

      <td className="px-3 py-2 font-mono text-sm text-text-muted">
        {String(driver.driver_number).padStart(2, "0")}
      </td>

      <td className="px-3 py-2">
        <Link
          href={`/drivers/${driver.driver_number}`}
          className="flex items-center gap-2.5 group"
        >
          {driver.headshot_url ? (
            <Image
              src={driver.headshot_url}
              alt={driver.full_name}
              width={32}
              height={32}
              className="rounded-full bg-bg-surface shrink-0 outline outline-1 outline-offset-1"
              style={{ outlineColor: teamColor }}
            />
          ) : (
            <div
              className="w-8 h-8 rounded-full bg-bg-surface shrink-0 outline outline-1 outline-offset-1"
              style={{ outlineColor: teamColor }}
            />
          )}
          <div className="min-w-0">
            <div className="text-sm font-semibold text-text-primary leading-tight group-hover:text-primary transition-colors truncate">
              {driver.full_name}
            </div>
            <div className="text-[10px] font-medium tracking-widest uppercase text-text-muted">
              {driver.name_acronym}
            </div>
          </div>
        </Link>
      </td>

      <td className="px-3 py-2">
        <div className="flex items-center gap-2">
          <div className="w-1 h-4 shrink-0" style={{ background: teamColor }} />
          <span className="text-xs font-semibold uppercase tracking-wide" style={{ color: teamColor }}>
            {driver.team_name ?? "—"}
          </span>
        </div>
      </td>

      <td className="px-3 py-2 text-right font-mono text-sm text-text-primary">
        {driver.points}
      </td>

      <td className="px-3 py-2 text-right font-mono text-sm text-text-secondary">
        {driver.wins}
      </td>

      <td className="px-3 py-2 text-right font-mono text-sm text-text-secondary">
        {driver.podiums}
      </td>

      <td className="px-3 py-2 text-right font-mono text-sm text-text-secondary">
        {driver.avg_finish != null ? driver.avg_finish.toFixed(1) : "—"}
      </td>
    </tr>
  );
}
