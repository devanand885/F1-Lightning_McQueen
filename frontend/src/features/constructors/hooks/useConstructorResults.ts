import { useQuery } from "@tanstack/react-query";

import { getConstructorResults } from "../api/constructors.api";

export function useConstructorResults(constructorId: string, season?: number) {
  return useQuery({
    queryKey: ["constructor-results", constructorId, season],
    queryFn: () => getConstructorResults(constructorId, season),
    enabled: !!constructorId,
  });
}
