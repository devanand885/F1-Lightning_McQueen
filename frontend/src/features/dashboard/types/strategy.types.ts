export interface StrategyInsight {
  statement: string;
  sample_size: number;
  metric: string;
}

export interface StrategyInsightsResponse {
  insights: StrategyInsight[];
}
