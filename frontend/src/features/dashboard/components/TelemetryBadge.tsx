interface Props {
  label: string;
  active?: boolean;
}

export default function TelemetryBadge({
  label,
  active = false,
}: Props) {
  return (
    <div className="flex items-center gap-2">
      {active && (
        <div className="w-1.5 h-1.5 rounded-full bg-primary" />
      )}

      <span
        className="
          text-[10px]
          uppercase
          tracking-[0.18em]
          text-primary
          font-medium
        "
      >
        {label}
      </span>
    </div>
  );
}