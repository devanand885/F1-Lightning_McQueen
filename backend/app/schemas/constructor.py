from datetime import datetime

from pydantic import BaseModel


class ConstructorSummary(BaseModel):
    season: int
    position: int | None
    constructor_id: int
    name: str
    team_colour: str | None
    points: float
    wins: int
    podiums: int
    avg_finish: float | None
    dnf_rate: float | None


class ConstructorDetail(ConstructorSummary):
    name_acronym: str | None


class ConstructorResult(BaseModel):
    session_key: int
    session_name: str
    session_type: str
    meeting_name: str
    date_start: datetime | None
    driver_number: int
    driver_full_name: str
    position: int | None
    points: float | None
    dnf: bool | None
    dns: bool | None
    dsq: bool | None


class ConstructorDriver(BaseModel):
    driver_number: int
    full_name: str
    name_acronym: str | None
    headshot_url: str | None


class ConstructorPitStop(BaseModel):
    session_key: int
    session_type: str
    driver_number: int
    lap_number: int
    date: datetime | None
    pit_duration: float | None
