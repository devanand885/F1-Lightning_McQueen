import Panel from "./Panel";
import PanelHeader from "./PanelHeader";
import StatusBadge from "./StatusBadge";

interface Props {
  title: string;
  subtitle?: string;
  description: string;
  className?: string;
  fill?: boolean;
}

/** Sibling of PlaceholderPanel for the opposite case: the analysis exists
 * and is wired up, but *this particular driver/circuit* doesn't clear the
 * sample-size bar for it (e.g. too few completed race sessions). Distinct
 * copy and badge so it doesn't read as "not built yet". */
export default function InsufficientDataPanel({
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
        action={<StatusBadge label="Insufficient data" variant="neutral" />}
      />
      <div className="flex flex-1 items-center justify-center">
        <p className="max-w-[280px] text-center text-xs leading-relaxed text-text-muted">{description}</p>
      </div>
    </Panel>
  );
}
