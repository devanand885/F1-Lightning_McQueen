import { useQuery } from "@tanstack/react-query";

import { getCalendar, getOverview } from "../api/dashboard.api";

export function useOverview(season?: number) {
  return useQuery({
    queryKey: ["dashboard-overview", season],
    queryFn: () => getOverview(season),
  });
}

export function useCalendar(season?: number) {
  return useQuery({
    queryKey: ["dashboard-calendar", season],
    queryFn: () => getCalendar(season),
  });
}
