"use client";

import { useEffect, useState } from "react";

interface Props {
  targetDate: string;
}

function formatRemaining(ms: number): string {
  if (ms <= 0) return "00:00:00:00";
  const totalSeconds = Math.floor(ms / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return [days, hours, minutes, seconds].map((n) => String(n).padStart(2, "0")).join(":");
}

export default function NextRaceCountdown({ targetDate }: Props) {
  const [remaining, setRemaining] = useState(() => new Date(targetDate).getTime() - Date.now());

  useEffect(() => {
    const target = new Date(targetDate).getTime();
    const interval = setInterval(() => setRemaining(target - Date.now()), 1000);
    return () => clearInterval(interval);
  }, [targetDate]);

  return <span className="text-[11px] font-mono text-text-secondary">{formatRemaining(remaining)}</span>;
}
