import { useQuery } from "@tanstack/react-query";

import { getDriver } from "../api/drivers.api";

export function useDriver(driverNumber: string, season?: number) {
  return useQuery({
    queryKey: ["driver", driverNumber, season],
    queryFn: () => getDriver(driverNumber, season),
    enabled: !!driverNumber,
  });
}
