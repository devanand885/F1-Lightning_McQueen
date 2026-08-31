import { useQuery } from "@tanstack/react-query";

import { getConstructor } from "../api/constructors.api";

export function useConstructor(constructorId: string, season?: number) {
  return useQuery({
    queryKey: ["constructor", constructorId, season],
    queryFn: () => getConstructor(constructorId, season),
    enabled: !!constructorId,
  });
}
