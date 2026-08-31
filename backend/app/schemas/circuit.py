from datetime import datetime

from pydantic import BaseModel


class CircuitSummary(BaseModel):
    circuit_id: int
    circuit_key: int
    circuit_short_name: str
    location: str | None
    country_name: str | None
    country_code: str | None
    seasons: list[int]


class CircuitMeeting(BaseModel):
    meeting_key: int
    meeting_name: str
    season: int
    date_start: datetime | None


class CircuitDetail(BaseModel):
    circuit_id: int
    circuit_key: int
    circuit_short_name: str
    location: str | None
    country_name: str | None
    country_code: str | None
    meetings: list[CircuitMeeting]
    drivers: list[str]
    constructors: list[str]
    circuit_type: str | None = None
    mean_st_speed: float | None = None
    mean_field_cov: float | None = None
    mean_stints_per_driver: float | None = None
