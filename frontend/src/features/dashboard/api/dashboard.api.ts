import { apiGet, ListResponse } from "@/lib/api/client";
import { CalendarEntry, SeasonOverview } from "../types/dashboard.types";

export function getOverview(season?: number) {
  return apiGet<SeasonOverview>("/dashboard/overview", { season });
}

export function getCalendar(season?: number) {
  return apiGet<ListResponse<CalendarEntry>>("/dashboard/calendar", { season });
}
