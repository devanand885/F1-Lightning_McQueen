import { useQuery } from "@tanstack/react-query";

import { getDrivers } from "../api/drivers.api";

export function useDrivers(season?: number) {
  return useQuery({
    queryKey: ["drivers", season],
    queryFn: () => getDrivers(season),
  });
}
