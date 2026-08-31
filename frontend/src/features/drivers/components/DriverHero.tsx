"use client";

import Image from "next/image";
import { ArrowLeftRight } from "lucide-react";
import { DriverDetail } from "../types/driver.types";

interface Props {
  driver: DriverDetail;
  onCompareClick: () => void;
}

export default function DriverHero({ driver, onCompareClick }: Props) {
  const teamColor = driver.team_colour ? `#${driver.team_colour}` : "#666666";
  const driverNumber = String(driver.driver_number).padStart(2, "0");
  const summary = driver.position
    ? `P${driver.position} in the ${driver.season} championship with ${driver.points} points, ${driver.wins} win${driver.wins === 1 ? "" : "s"} and ${driver.podiums} podium${driver.podiums === 1 ? "" : "s"}.`
    : `No championship points recorded yet for the ${driver.season} season.`;

  return (
    <div className="flex overflow-hidden border border-[#222] bg-[#0d0d0d] min-h-[200px]">
      {/* Left — image panel with driver number */}
      <div className="relative w-[260px] flex-shrink-0 overflow-hidden max-sm:hidden border-r border-[#222] bg-[#111]">
        {/* Team colour glow */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background: `radial-gradient(ellipse 120% 80% at 60% 40%, ${teamColor}22 0%, transparent 65%)`,
          }}
        />

        <Image
          src={"/waves.jpg"}
          alt={driver.full_name}
          fill
          className="object-cover object-top"
          sizes="260px"
        />

        {/* Gradient overlay so number is always readable */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />

        {/* Driver number */}
        <span
          className="absolute bottom-3.5 left-4 text-[52px] font-black leading-none tracking-[-2px]"
          style={{ color: teamColor }}
        >
          {driverNumber}
        </span>
      </div>

      {/* Centre — name + info */}
      <div className="flex flex-1 max-sm:px-2 sm:pr-8 justify-center gap-2.5 border-r border-[#222]">
        <div className="flex flex-1 flex-col justify-center gap-2.5 border-[#222] sm:px-8 px-2 sm:py-7 py-5">
          {/* Badges */}
          <div className="flex flex-wrap items-center gap-2.5">
            {driver.team_name && (
              <span
                className="px-2 py-1 text-[9px] font-extrabold uppercase tracking-[0.10em] text-white"
                style={{ background: teamColor }}
              >
                {driver.team_name}
              </span>
            )}
            {driver.position && (
              <span className="font-mono text-[9px] font-bold uppercase tracking-[0.12em] text-text-muted">
                WDC P{driver.position}
              </span>
            )}
          </div>

          {/* Name */}
          <h1 className="text-[42px] font-black uppercase leading-none tracking-[-1.5px] text-white">
            {driver.full_name}
          </h1>

          {/* Summary */}
          <p className="max-w-[380px] text-xs leading-relaxed text-[#888]">
            {summary}
          </p>

          <button
            type="button"
            onClick={onCompareClick}
            className="inline-flex h-9 w-fit items-center gap-2 border border-[#333] bg-[#151515] px-3 text-[10px] font-semibold uppercase tracking-[0.12em] text-[#aaa] transition-colors hover:border-primary/50 hover:text-white"
          >
            <ArrowLeftRight size={12} /> Compare Driver
          </button>
        </div>

        {driver.headshot_url && (
          <Image
            src={driver.headshot_url}
            alt={driver.full_name}
            width={100}
            height={100}
            style={{ outlineColor: teamColor }}
            className="object-cover outline-2 outline-offset-1 rounded-full self-center object-top sm:w-20 w-12 sm:h-20 h-12"
          />
        )}
      </div>
    </div>
  );
}
