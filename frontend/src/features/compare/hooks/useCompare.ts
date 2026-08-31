import { useQuery } from "@tanstack/react-query";

import { compareConstructors, compareDrivers } from "../api/compare.api";
import { CompareEntityType } from "../types/compare.types";

export function useCompare(type: CompareEntityType, ids: number[], season?: number) {
  return useQuery({
    queryKey: ["compare", type, ids, season],
    queryFn: () => (type === "driver" ? compareDrivers(ids, season) : compareConstructors(ids, season)),
    enabled: ids.length >= 2,
  });
}
