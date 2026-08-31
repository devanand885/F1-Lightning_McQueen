from typing import Literal

from pydantic import BaseModel


class CompareEntity(BaseModel):
    id: int
    label: str
    colour: str | None


class CompareMetric(BaseModel):
    key: str
    label: str
    unit: str | None
    values: list[float | int | str | None]


class ComparisonResponse(BaseModel):
    entity_type: Literal["driver", "constructor"]
    season: int
    entities: list[CompareEntity]
    metrics: list[CompareMetric]
    analytics: list[CompareMetric] | None = None
