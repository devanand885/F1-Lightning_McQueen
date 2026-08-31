import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { CalendarEntry } from "../types/dashboard.types";

interface Props {
  calendar: CalendarEntry[];
}

export default function SeasonCalendarPanel({ calendar }: Props) {
  const sorted = [...calendar].sort((a, b) => {
    if (!a.date_start || !b.date_start) return 0;
    return new Date(a.date_start).getTime() - new Date(b.date_start).getTime();
  });

  return (
    <Panel>
      <PanelHeader title="Season Calendar" subtitle="Every meeting this season" />
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-border text-[9px] uppercase tracking-[0.14em] text-text-muted">
              <th className="py-2 text-left font-medium">Status</th>
              <th className="py-2 text-left font-medium">Meeting</th>
              <th className="py-2 text-left font-medium">Circuit</th>
              <th className="py-2 text-right font-medium">Date</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((meeting) => (
              <tr key={meeting.meeting_key} className="border-b border-border/60">
                <td className="py-2.5">
                  <span
                    className={`inline-block h-1.5 w-1.5 rounded-full ${
                      meeting.status === "completed" ? "bg-success" : "bg-text-muted"
                    }`}
                    title={meeting.status}
                  />
                </td>
                <td className="py-2.5 text-text-primary">{meeting.meeting_name}</td>
                <td className="py-2.5 text-text-secondary">
                  {[meeting.circuit_short_name, meeting.location].filter(Boolean).join(" · ")}
                </td>
                <td className="py-2.5 text-right font-mono text-text-muted">
                  {meeting.date_start ? new Date(meeting.date_start).toLocaleDateString() : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}
