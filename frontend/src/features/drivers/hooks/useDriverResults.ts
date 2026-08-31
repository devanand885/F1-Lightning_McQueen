import { useQuery } from "@tanstack/react-query";

import { getDriverResults } from "../api/drivers.api";

export function useDriverResults(driverNumber: string, season?: number) {
  return useQuery({
    queryKey: ["driver-results", driverNumber, season],
    queryFn: () => getDriverResults(driverNumber, season),
    enabled: !!driverNumber,
  });
}
