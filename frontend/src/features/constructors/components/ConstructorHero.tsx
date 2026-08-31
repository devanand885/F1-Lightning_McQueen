"use client";

import { ArrowLeftRight, Radio } from "lucide-react";

import ExportMenu from "@/features/shared/components/export/ExportMenu";
import type { ConstructorDetail, ConstructorDriver } from "../types/constructor.types";

interface Props {
  constructor: ConstructorDetail;
  drivers: ConstructorDriver[];
  onCompareClick: () => void;
}

export default function ConstructorHero({ constructor, drivers, onCompareClick }: Props) {
  const teamColor = constructor.team_colour ? `#${constructor.team_colour}` : "#666666";

  return (
    <section className="relative overflow-hidden border border-border bg-[#0d0d0d]">
      <div
        className="pointer-events-none absolute inset-0 opacity-20"
        style={{ background: `linear-gradient(110deg, ${teamColor}66 0%, transparent 38%)` }}
      />
      <div className="relative flex min-h-[174px] flex-col justify-between gap-8 p-5 sm:p-7 lg:flex-row lg:items-center">
        <div className="flex min-w-0 items-center gap-5">
          <div
            className="grid h-24 w-24 shrink-0 place-items-center border bg-bg-surface font-mono text-2xl font-black tracking-[-0.08em] text-text-primary"
            style={{ borderColor: teamColor, boxShadow: `inset 0 -4px 0 ${teamColor}` }}
            aria-label={`${constructor.name} logo placeholder`}
          >
            {constructor.name_acronym ?? constructor.name.slice(0, 3).toUpperCase()}
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-[9px] font-semibold uppercase tracking-[0.18em] text-primary">
                Constructor Analytics
              </span>
              <span className="inline-flex items-center gap-1.5 font-mono text-[9px] uppercase tracking-[0.14em] text-success">
                <Radio size={10} /> Live data
              </span>
            </div>
            <h1 className="mt-2 truncate text-3xl font-black uppercase tracking-[-0.04em] text-text-primary sm:text-5xl">
              {constructor.name}
            </h1>
            <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-[10px] uppercase tracking-[0.14em] text-text-muted">
              <span>Season {constructor.season}</span>
              {constructor.position && (
                <span className="font-mono" style={{ color: teamColor }}>WCC P{constructor.position}</span>
              )}
              {drivers.length > 0 && <span>{drivers.map((d) => d.name_acronym ?? d.full_name).join(" · ")}</span>}
            </div>
          </div>
        </div>

        <div className="flex shrink-0 flex-wrap items-start gap-2">
          <button
            type="button"
            onClick={onCompareClick}
            className="inline-flex h-10 items-center gap-2 border border-border bg-bg-card px-4 text-[10px] font-semibold uppercase tracking-[0.12em] text-text-secondary transition-colors hover:border-primary/50 hover:text-text-primary"
          >
            <ArrowLeftRight size={13} /> Compare Team
          </button>
          <ExportMenu season={constructor.season} />
        </div>
      </div>
    </section>
  );
}
