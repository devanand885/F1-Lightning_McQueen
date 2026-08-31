import { apiGet } from "@/lib/api/client";
import { StrategyInsightsResponse } from "../types/strategy.types";

export function getStrategyInsights() {
  return apiGet<StrategyInsightsResponse>("/strategy/insights");
}
