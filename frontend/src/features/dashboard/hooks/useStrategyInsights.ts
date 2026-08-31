import { useQuery } from "@tanstack/react-query";

import { getStrategyInsights } from "../api/strategy.api";

export function useStrategyInsights() {
  return useQuery({
    queryKey: ["strategy-insights"],
    queryFn: getStrategyInsights,
  });
}
