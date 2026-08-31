"use client";

import { useState } from "react";
import { X } from "lucide-react";

interface Option {
  id: number;
  label: string;
  colour?: string | null;
}

interface Props {
  title: string;
  options: Option[];
  excludeId: number;
  onSelect: (id: number) => void;
  onClose: () => void;
}

export default function EntityPickerModal({ title, options, excludeId, onSelect, onClose }: Props) {
  const [query, setQuery] = useState("");
  const filtered = options
    .filter((option) => option.id !== excludeId)
    .filter((option) => option.label.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/70 px-4 pt-24" onClick={onClose}>
      <div
        className="w-full max-w-md border border-border bg-bg-card shadow-xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <span className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">{title}</span>
          <button type="button" onClick={onClose} className="text-text-muted hover:text-text-primary">
            <X size={16} />
          </button>
        </div>

        <div className="border-b border-border px-4 py-2">
          <input
            autoFocus
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Filter..."
            className="w-full bg-transparent text-sm text-text-primary outline-none placeholder:text-text-muted"
          />
        </div>

        <div className="max-h-[320px] overflow-y-auto">
          {filtered.length === 0 && <p className="px-4 py-6 text-center text-xs text-text-muted">No matches.</p>}
          {filtered.map((option) => (
            <button
              key={option.id}
              type="button"
              onClick={() => onSelect(option.id)}
              className="flex w-full items-center gap-2.5 px-4 py-2.5 text-left text-sm text-text-primary hover:bg-bg-hover"
            >
              {option.colour && <span className="h-3 w-1 shrink-0" style={{ background: `#${option.colour}` }} />}
              {option.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
