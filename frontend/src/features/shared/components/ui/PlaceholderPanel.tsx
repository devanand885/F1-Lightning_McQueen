import Panel from "./Panel";
import PanelHeader from "./PanelHeader";
import StatusBadge from "./StatusBadge";

interface Props {
  title: string;
  subtitle?: string;
  description?: string;
  className?: string;
  /** Stretch to fill the parent's height - appropriate when this is the
   * sole occupant of a grid cell, wrong when stacked with sibling panels
   * in a plain block container (each `h-full` would then demand the full
   * cell height, overflowing past it). Default true. */
  fill?: boolean;
}

export default function PlaceholderPanel({
  title,
  subtitle,
  description,
  className = "",
  fill = true,
}: Props) {
  return (
    <Panel className={`flex ${fill ? "h-full" : ""} min-h-[220px] flex-col ${className}`}>
      <PanelHeader
        title={title}
        subtitle={subtitle}
        action={<StatusBadge label="Not yet available" variant="neutral" />}
      />
      <div className="flex flex-1 items-center justify-center">
        <p className="max-w-[280px] text-center text-xs leading-relaxed text-text-muted">
          {description ??
            "This needs a defined analytical methodology before F1 Lightning McQueen can show it honestly."}
        </p>
      </div>
    </Panel>
  );
}
