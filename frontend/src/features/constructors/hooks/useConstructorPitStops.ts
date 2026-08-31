import { useQuery } from "@tanstack/react-query";

import { getConstructorPitStops } from "../api/constructors.api";

export function useConstructorPitStops(constructorId: string, season?: number) {
  return useQuery({
    queryKey: ["constructor-pit-stops", constructorId, season],
    queryFn: () => getConstructorPitStops(constructorId, season),
    enabled: !!constructorId,
  });
}
