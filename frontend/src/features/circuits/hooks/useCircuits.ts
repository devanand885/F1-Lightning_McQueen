import { useQuery } from "@tanstack/react-query";

import { getCircuits } from "../api/circuits.api";

export function useCircuits(season?: number, location?: string) {
  return useQuery({
    queryKey: ["circuits", season, location],
    queryFn: () => getCircuits(season, location),
  });
}
