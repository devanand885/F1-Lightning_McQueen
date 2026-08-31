"use client";

import { useRouter } from "next/navigation";

import type { Constructor } from "../types/constructor.types";

interface Props {
  constructor: Constructor;
}

export default function ConstructorTableRow({ constructor }: Props) {
  const router = useRouter();
  const teamColor = constructor.team_colour ? `#${constructor.team_colour}` : "#666666";
  const finishRate = constructor.dnf_rate != null ? (1 - constructor.dnf_rate) * 100 : null;

  const navigate = () => router.push(`/constructors/${constructor.constructor_id}`);

  return (
    <tr
      tabIndex={0}
      onClick={navigate}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") navigate();
      }}
      className="group cursor-pointer border-b border-border bg-[#111111] outline-none transition-colors hover:bg-bg-hover focus-visible:bg-bg-hover"
    >
      <td className="px-3 py-3 font-mono text-sm text-text-secondary">
        {constructor.position ? String(constructor.position).padStart(2, "0") : "—"}
      </td>
      <td className="px-3 py-3">
        <div className="flex items-center gap-3">
          <div className="h-7 w-1 shrink-0" style={{ backgroundColor: teamColor }} />
          <div className="min-w-0 truncate text-sm font-semibold text-text-primary transition-colors group-hover:text-primary">
            {constructor.name}
          </div>
        </div>
      </td>
      <td className="px-3 py-3 text-right font-mono text-sm text-text-primary">{constructor.points}</td>
      <td className="px-3 py-3 text-right font-mono text-sm text-text-secondary">{constructor.wins}</td>
      <td className="px-3 py-3 text-right font-mono text-sm text-text-secondary">{constructor.podiums}</td>
      <td className="px-3 py-3 text-right font-mono text-sm text-text-secondary">
        {constructor.avg_finish != null ? constructor.avg_finish.toFixed(1) : "—"}
      </td>
      <td className="px-3 py-3 text-right">
        {finishRate != null ? (
          <div className="ml-auto flex w-[92px] items-center justify-end gap-2">
            <div className="h-1 w-9 overflow-hidden bg-bg-hover">
              <div className="h-full bg-success" style={{ width: `${finishRate}%` }} />
            </div>
            <span className="font-mono text-sm text-text-primary">{finishRate.toFixed(1)}%</span>
          </div>
        ) : (
          <span className="text-text-muted">—</span>
        )}
      </td>
    </tr>
  );
}
