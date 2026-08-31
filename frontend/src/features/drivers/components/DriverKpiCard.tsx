import { ReactNode } from "react";

interface Props {
  title: string;
  value: string;
  suffix?: string;
  tag?: string;
  tagPositive?: boolean;
  accent?: "primary" | "teal";
  icon?: ReactNode;
  compact?: boolean;
}

export default function DriverKpiCard({
  title,
  value,
  suffix,
  tag,
  tagPositive,
  accent = "primary",
  icon,
  compact = false,
}: Props) {
  const valueColor = accent === "teal" ? "text-tertiary" : "text-primary";

  return (
    <div
      className={`
        border border-border bg-bg-card flex flex-col justify-between
        ${compact ? "p-3 min-h-[88px]" : "p-4 min-h-[100px]"}
      `}
    >
      <div className="flex items-center justify-between">
        <div className="text-[9px] uppercase tracking-[0.16em] text-primary font-medium">
          {title}
        </div>
        {icon && <div className="text-primary opacity-70 shrink-0">{icon}</div>}
      </div>

      <div>
        <div className="flex items-end gap-1 mt-2">
          <span
            className={`
              font-light leading-none tracking-tight
              ${valueColor}
              ${compact ? "text-3xl" : "text-4xl xl:text-5xl"}
            `}
          >
            {value}
          </span>
          {suffix && (
            <span className="text-sm text-text-secondary pb-1">{suffix}</span>
          )}
        </div>

        {tag && (
          <div
            className={`
              mt-2 text-[9px] uppercase tracking-wide font-medium
              ${tagPositive ? "text-success" : "text-text-muted"}
            `}
          >
            {tag}
          </div>
        )}
      </div>
    </div>
  );
}
