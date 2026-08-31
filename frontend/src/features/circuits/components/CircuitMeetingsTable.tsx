import Panel from "@/features/shared/components/ui/Panel";
import PanelHeader from "@/features/shared/components/ui/PanelHeader";
import { CircuitMeeting } from "../types/circuit.types";

interface Props {
  meetings: CircuitMeeting[];
}

export default function CircuitMeetingsTable({ meetings }: Props) {
  const sorted = [...meetings].sort((a, b) => {
    if (!a.date_start || !b.date_start) return b.season - a.season;
    return new Date(b.date_start).getTime() - new Date(a.date_start).getTime();
  });

  return (
    <Panel>
      <PanelHeader title="Historical Meetings" subtitle="Every recorded meeting at this circuit" />
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-border text-[9px] uppercase tracking-[0.14em] text-text-muted">
              <th className="py-2 text-left font-medium">Season</th>
              <th className="py-2 text-left font-medium">Meeting</th>
              <th className="py-2 text-right font-medium">Date</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((meeting) => (
              <tr key={meeting.meeting_key} className="border-b border-border/60">
                <td className="py-2.5 font-mono text-text-secondary">{meeting.season}</td>
                <td className="py-2.5 text-text-primary">{meeting.meeting_name}</td>
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
