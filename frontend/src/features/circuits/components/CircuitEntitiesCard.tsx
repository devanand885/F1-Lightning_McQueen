import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";

interface Props {
  title: string;
  items: string[];
}

export default function CircuitEntitiesCard({ title, items }: Props) {
  return (
    <Panel>
      <PanelHeader title={title} subtitle={`${items.length} on record`} />
      {items.length > 0 ? (
        <div className="flex flex-wrap gap-1.5">
          {items.map((item) => (
            <span key={item} className="border border-border bg-bg-hover px-2 py-1 text-xs text-text-secondary">
              {item}
            </span>
          ))}
        </div>
      ) : (
        <p className="text-xs text-text-muted">No records yet.</p>
      )}
    </Panel>
  );
}
