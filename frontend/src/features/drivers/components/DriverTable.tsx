"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

import { Driver } from "../types/driver.types";
import DriverTableRow from "./DriverTableRow";

type SortKey = "position" | "points" | "wins" | "podiums" | "avg_finish";

export default function DriverTable({ drivers }: { drivers: Driver[] }) {
  const [sortKey, setSortKey] = useState<SortKey>("position");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const sorted = [...drivers].sort((a, b) => {
    const fallback = sortDir === "asc" ? Number.MAX_SAFE_INTEGER : -Infinity;
    const av = a[sortKey] ?? fallback;
    const bv = b[sortKey] ?? fallback;
    return sortDir === "asc" ? av - bv : bv - av;
  });

  function toggleSort(key: SortKey) {
    if (key === sortKey) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir(key === "position" ? "asc" : "desc");
    }
  }

  function sortIcon(key: SortKey) {
    if (key !== sortKey) return null;
    return sortDir === "asc" ? (
      <ChevronUp size={11} className="inline ml-1" />
    ) : (
      <ChevronDown size={11} className="inline ml-1" />
    );
  }

  function headerButton(key: SortKey, label: string, align: "left" | "right") {
    return (
      <button
        type="button"
        onClick={() => toggleSort(key)}
        className={`flex items-center hover:text-white ${align === "right" ? "ml-auto" : ""}`}
      >
        {label}
        {sortIcon(key)}
      </button>
    );
  }

  return (
    <div className="border border-border bg-bg-card overflow-x-auto">
      <table className="w-full min-w-[720px]">
        <thead>
          <tr className="border-b border-border bg-[#141214] text-[10px] uppercase tracking-[0.16em] text-primary">
            <th className="py-2 px-3 text-left font-semibold w-12">{headerButton("position", "Pos", "left")}</th>
            <th className="py-2 px-3 text-left font-semibold w-14">No</th>
            <th className="py-2 px-3 text-left font-semibold">Driver</th>
            <th className="py-2 px-3 text-left font-semibold">Team</th>
            <th className="py-2 px-3 text-right font-semibold w-16">{headerButton("points", "Pts", "right")}</th>
            <th className="py-2 px-3 text-right font-semibold w-14">{headerButton("wins", "Wins", "right")}</th>
            <th className="py-2 px-3 text-right font-semibold w-16">
              {headerButton("podiums", "Podiums", "right")}
            </th>
            <th className="py-2 px-3 text-right font-semibold w-20">
              {headerButton("avg_finish", "Avg Fin", "right")}
            </th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((driver) => (
            <DriverTableRow key={driver.driver_number} driver={driver} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
