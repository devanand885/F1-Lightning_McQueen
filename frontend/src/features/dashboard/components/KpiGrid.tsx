import { CalendarClock, Flag, Trophy, Wrench } from "lucide-react";

import KpiCard from "@/features/shared/components/data-display/KpiCard";
import { Driver } from "@/features/drivers/types/driver.types";
import { Constructor } from "@/features/constructors/types/constructor.types";
import { CalendarEntry, SeasonOverview } from "../types/dashboard.types";

interface Props {
  overview: SeasonOverview;
  calendar: CalendarEntry[];
  drivers: Driver[];
  constructors: Constructor[];
}

export default function KpiGrid({ overview, calendar, drivers, constructors }: Props) {
  const completed = calendar.filter((m) => m.status === "completed").length;
  const total = calendar.length || overview.meeting_count;
  const progress = total > 0 ? (completed / total) * 100 : 0;

  const topDriver = drivers[0];
  const topConstructor = constructors[0];
  const secondConstructor = constructors[1];
  const constructorGap =
    topConstructor && secondConstructor ? topConstructor.points - secondConstructor.points : null;

  const nextMeeting = calendar.find((m) => m.status === "upcoming");

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      <KpiCard
        title="Meetings Completed"
        value={String(completed)}
        suffix={`/ ${total}`}
        icon={<Flag size={14} />}
        progress={progress}
      />
      <KpiCard
        title="Championship Leader"
        value={topDriver ? topDriver.full_name : "—"}
        footer={topDriver ? `${topDriver.team_name ?? "—"} · ${topDriver.points} PTS` : undefined}
        icon={<Trophy size={14} />}
      />
      <KpiCard
        title="Constructor Lead"
        value={topConstructor ? topConstructor.name : "—"}
        footer={constructorGap != null ? `GAP TO P2: +${constructorGap} PTS` : undefined}
        icon={<Wrench size={14} />}
      />
      <KpiCard
        title="Next Race"
        value={nextMeeting ? nextMeeting.meeting_name : "Season Complete"}
        footer={nextMeeting?.date_start ? new Date(nextMeeting.date_start).toLocaleDateString() : undefined}
        icon={<CalendarClock size={14} />}
      />
    </div>
  );
}
