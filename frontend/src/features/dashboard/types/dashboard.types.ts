export interface SeasonOverview {
  season: number;
  meeting_count: number;
  session_count: number;
  last_completed_meeting: string | null;
  next_meeting: string | null;
}

export interface CalendarEntry {
  meeting_key: number;
  meeting_name: string;
  circuit_short_name: string;
  location: string | null;
  date_start: string | null;
  status: "completed" | "upcoming";
}
