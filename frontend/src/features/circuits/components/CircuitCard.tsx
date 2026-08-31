"use client";

import Link from "next/link";
import { CircuitSummary } from "../types/circuit.types";

interface Props {
  circuit: CircuitSummary;
}

export default function CircuitCard({ circuit }: Props) {
  return (
    <Link
      href={`/circuits/${circuit.circuit_id}`}
      className="flex flex-col gap-3 border border-border bg-bg-card p-4 transition-colors hover:border-primary/50 hover:bg-bg-hover"
    >
      <div>
        <div className="text-sm font-semibold text-text-primary">{circuit.circuit_short_name}</div>
        <div className="mt-1 text-xs text-text-muted">
          {[circuit.location, circuit.country_name].filter(Boolean).join(", ") || "—"}
        </div>
      </div>
      <div className="mt-auto flex flex-wrap gap-1.5">
        {circuit.seasons.map((year) => (
          <span
            key={year}
            className="border border-border px-1.5 py-0.5 text-[9px] font-mono uppercase tracking-wider text-text-secondary"
          >
            {year}
          </span>
        ))}
      </div>
    </Link>
  );
}
