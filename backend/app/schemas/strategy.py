from pydantic import BaseModel


class StrategyInsight(BaseModel):
    statement: str
    sample_size: int
    metric: str


class StrategyInsightsResponse(BaseModel):
    insights: list[StrategyInsight]
