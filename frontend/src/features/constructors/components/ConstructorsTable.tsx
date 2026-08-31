"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

import ConstructorTableRow from "./ConstructorTableRow";
import type { Constructor } from "../types/constructor.types";

interface Props {
  constructors: Constructor[];
}

type SortKey = "position" | "points" | "wins" | "podiums" | "avg_finish" | "finish_rate";

function sortValue(constructor: Constructor, key: SortKey): number {
  if (key === "finish_rate") {
    return constructor.dnf_rate != null ? 1 - constructor.dnf_rate : -Infinity;
  }
  return constructor[key] ?? -Infinity;
}

const COLUMNS: { key: SortKey; label: string; align: "text-left" | "text-right"; width: string }[] = [
  { key: "position", label: "Position", align: "text-left", width: "w-20" },
  { key: "points", label: "Points", align: "text-right", width: "w-20" },
  { key: "wins", label: "Wins", align: "text-right", width: "w-16" },
  { key: "podiums", label: "Podiums", align: "text-right", width: "w-20" },
  { key: "avg_finish", label: "Avg Finish", align: "text-right", width: "w-24" },
  { key: "finish_rate", label: "Finish Rate", align: "text-right", width: "w-32" },
];

export default function ConstructorsTable({ constructors }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>("position");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const sorted = [...constructors].sort((a, b) => {
    const av = sortValue(a, sortKey);
    const bv = sortValue(b, sortKey);
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

  return (
    <div className="overflow-x-auto border border-border bg-bg-card">
      <table className="w-full min-w-[860px]">
        <thead>
          <tr className="border-b border-border bg-[#141214] text-[9px] uppercase tracking-[0.16em] text-primary">
            {COLUMNS.map((column) => (
              <th key={column.key} className={`px-3 py-2.5 font-semibold ${column.align} ${column.width}`}>
                <button
                  type="button"
                  onClick={() => toggleSort(column.key)}
                  className={`flex items-center hover:text-white ${column.align === "text-right" ? "ml-auto" : ""}`}
                >
                  {column.label}
                  {sortKey === column.key &&
                    (sortDir === "asc" ? (
                      <ChevronUp size={11} className="inline ml-1" />
                    ) : (
                      <ChevronDown size={11} className="inline ml-1" />
                    ))}
                </button>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((constructor) => (
            <ConstructorTableRow key={constructor.constructor_id} constructor={constructor} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
