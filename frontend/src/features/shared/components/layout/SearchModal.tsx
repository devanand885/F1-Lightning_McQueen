"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Search, X } from "lucide-react";

import { useDebouncedValue } from "@/lib/useDebouncedValue";
import { useSearch } from "../../hooks/useSearch";
import { SearchResult, SearchResultType } from "../../types/search.types";

interface Props {
  onClose: () => void;
}

const ROUTES: Partial<Record<SearchResultType, (id: number) => string>> = {
  driver: (id) => `/drivers/${id}`,
  constructor: (id) => `/constructors/${id}`,
  circuit: (id) => `/circuits/${id}`,
};

const TYPE_LABELS: Record<SearchResultType, string> = {
  driver: "Driver",
  constructor: "Constructor",
  circuit: "Circuit",
  meeting: "Meeting",
  session: "Session",
};

// Mounted only while open (see Navbar) - so every open starts with fresh
// state instead of needing an effect to reset it.
export default function SearchModal({ onClose }: Props) {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);
  const debouncedQuery = useDebouncedValue(query, 250);
  const { data, isLoading } = useSearch(debouncedQuery);
  const results = data?.items ?? [];
  const trimmed = debouncedQuery.trim();

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const navigateTo = (result: SearchResult) => {
    const buildPath = ROUTES[result.type];
    if (!buildPath) return;
    router.push(buildPath(result.id));
    onClose();
  };

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      } else if (event.key === "ArrowDown") {
        event.preventDefault();
        setActiveIndex((i) => Math.min(i + 1, results.length - 1));
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        setActiveIndex((i) => Math.max(i - 1, 0));
      } else if (event.key === "Enter") {
        setActiveIndex((current) => {
          const result = results[current];
          if (result) navigateTo(result);
          return current;
        });
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [results]);

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/70 px-4 pt-24" onClick={onClose}>
      <div
        className="w-full max-w-xl border border-border bg-bg-card shadow-xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-center gap-2 border-b border-border px-4 py-3">
          <Search size={16} className="shrink-0 text-text-muted" />
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setActiveIndex(0);
            }}
            placeholder="Search drivers, teams, circuits..."
            className="flex-1 bg-transparent text-sm text-text-primary outline-none placeholder:text-text-muted"
          />
          <button type="button" onClick={onClose} className="text-text-muted hover:text-text-primary">
            <X size={16} />
          </button>
        </div>

        <div className="max-h-[360px] overflow-y-auto">
          {trimmed.length === 0 && (
            <p className="px-4 py-6 text-center text-xs text-text-muted">
              Start typing to search drivers, constructors, and circuits.
            </p>
          )}

          {trimmed.length > 0 && isLoading && (
            <p className="px-4 py-6 text-center text-xs text-text-muted">Searching...</p>
          )}

          {trimmed.length > 0 && !isLoading && results.length === 0 && (
            <p className="px-4 py-6 text-center text-xs text-text-muted">No results for &quot;{trimmed}&quot;.</p>
          )}

          {results.map((result, index) => {
            const linkable = Boolean(ROUTES[result.type]);
            return (
              <button
                key={`${result.type}-${result.id}`}
                type="button"
                disabled={!linkable}
                onClick={() => navigateTo(result)}
                onMouseEnter={() => setActiveIndex(index)}
                className={`
                  flex w-full items-center justify-between gap-3 px-4 py-2.5 text-left text-sm transition-colors
                  ${linkable ? "cursor-pointer" : "cursor-default opacity-50"}
                  ${index === activeIndex && linkable ? "bg-bg-hover" : ""}
                `}
              >
                <span className="min-w-0 truncate text-text-primary">
                  {result.title}
                  {result.subtitle && <span className="ml-2 text-xs text-text-muted">{result.subtitle}</span>}
                </span>
                <span className="shrink-0 text-[9px] uppercase tracking-wider text-text-muted">
                  {TYPE_LABELS[result.type]}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
