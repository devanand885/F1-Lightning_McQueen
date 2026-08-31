import { useQuery } from "@tanstack/react-query";

import { getDriverAnalytics } from "../api/driverAnalytics.api";

export function useDriverAnalytics(driverNumber: number | string) {
  return useQuery({
    queryKey: ["driver-analytics", driverNumber],
    queryFn: () => getDriverAnalytics(driverNumber),
    enabled: Boolean(driverNumber),
  });
}
