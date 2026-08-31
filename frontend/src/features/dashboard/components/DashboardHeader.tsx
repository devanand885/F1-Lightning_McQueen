import TelemetryBadge from "./TelemetryBadge";
import NextRaceCountdown from "./NextRaceCountdown";
import { CalendarEntry, SeasonOverview } from "../types/dashboard.types";

interface Props {
  overview: SeasonOverview;
  nextMeeting: CalendarEntry | null;
}

export default function DashboardHeader({ overview, nextMeeting }: Props) {
  return (
    <div className="space-y-3">
      {/* Top Row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <TelemetryBadge label={`Live : Season ${overview.season} Intelligence`} active />
        </div>

        {nextMeeting?.date_start && (
          <div className="hidden lg:flex items-center gap-6">
            <div className="text-[11px] uppercase tracking-[0.12em] text-text-primary font-medium">
              Next: {nextMeeting.meeting_name}
            </div>
            <NextRaceCountdown targetDate={nextMeeting.date_start} />
          </div>
        )}
      </div>

      {/* Bottom Row */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-text-primary">Data Overview Dashboard</h1>
      </div>
    </div>
  );
}
