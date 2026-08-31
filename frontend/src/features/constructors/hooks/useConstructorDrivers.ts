import { useQuery } from "@tanstack/react-query";

import { getConstructorDrivers } from "../api/constructors.api";

export function useConstructorDrivers(constructorId: string, season?: number) {
  return useQuery({
    queryKey: ["constructor-drivers", constructorId, season],
    queryFn: () => getConstructorDrivers(constructorId, season),
    enabled: !!constructorId,
  });
}
