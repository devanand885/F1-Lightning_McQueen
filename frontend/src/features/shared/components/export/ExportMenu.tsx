"use client";

import { useState } from "react";
import { Download } from "lucide-react";

import { downloadExport, ExportFormat } from "@/lib/downloadExport";

interface Props {
  season: number;
  datasets?: { key: string; label: string }[];
  label?: string;
}

const DEFAULT_DATASETS = [
  { key: "drivers", label: "Driver Standings" },
  { key: "constructors", label: "Constructor Standings" },
  { key: "race_results", label: "Race Results" },
  { key: "laps", label: "Laps" },
  { key: "pit_stops", label: "Pit Stops" },
  { key: "stints", label: "Stints" },
  { key: "weather", label: "Weather" },
  { key: "positions", label: "Positions" },
];

export default function ExportMenu({ season, datasets = DEFAULT_DATASETS, label = "Export Intelligence" }: Props) {
  const [open, setOpen] = useState(false);
  const [pending, setPending] = useState<string | null>(null);

  async function handleExport(dataset: string, format: ExportFormat) {
    const key = `${dataset}-${format}`;
    setPending(key);
    try {
      await downloadExport(dataset, format, season);
    } catch {
      // Network/backend failure - the menu stays open so the user can retry.
    } finally {
      setPending(null);
    }
  }

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="inline-flex h-10 items-center gap-2 bg-primary px-4 text-[10px] font-semibold uppercase tracking-[0.12em] text-white transition-[filter] hover:brightness-110"
      >
        <Download size={13} /> {label}
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 z-50 mt-1 w-72 border border-border bg-bg-card shadow-xl">
            <div className="border-b border-border px-3 py-2 text-[9px] uppercase tracking-[0.14em] text-text-muted">
              Season {season} datasets
            </div>
            <div className="max-h-[280px] overflow-y-auto">
              {datasets.map((dataset) => (
                <div key={dataset.key} className="flex items-center justify-between gap-2 px-3 py-2 hover:bg-bg-hover">
                  <span className="text-xs text-text-primary">{dataset.label}</span>
                  <div className="flex gap-1.5">
                    <button
                      type="button"
                      disabled={pending !== null}
                      onClick={() => handleExport(dataset.key, "csv")}
                      className="border border-border px-2 py-0.5 text-[9px] uppercase tracking-wider text-text-secondary hover:border-primary/50 hover:text-text-primary disabled:opacity-50"
                    >
                      {pending === `${dataset.key}-csv` ? "…" : "CSV"}
                    </button>
                    <button
                      type="button"
                      disabled={pending !== null}
                      onClick={() => handleExport(dataset.key, "json")}
                      className="border border-border px-2 py-0.5 text-[9px] uppercase tracking-wider text-text-secondary hover:border-primary/50 hover:text-text-primary disabled:opacity-50"
                    >
                      {pending === `${dataset.key}-json` ? "…" : "JSON"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
