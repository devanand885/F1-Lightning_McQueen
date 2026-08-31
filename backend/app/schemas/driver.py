from datetime import datetime

from pydantic import BaseModel


class DriverSummary(BaseModel):
    season: int
    position: int | None
    driver_number: int
    full_name: str
    name_acronym: str | None
    headshot_url: str | None
    country_code: str | None
    team_id: int | None
    team_name: str | None
    team_colour: str | None
    points: float
    wins: int
    podiums: int
    avg_finish: float | None
    dnf_rate: float | None


class DriverDetail(DriverSummary):
    first_name: str | None
    last_name: str | None
    broadcast_name: str | None


class DriverSessionSummary(BaseModel):
    session_key: int
    session_name: str
    session_type: str
    meeting_name: str
    date_start: datetime | None


class DriverResult(DriverSessionSummary):
    position: int | None
    points: float | None
    dnf: bool | None
    dns: bool | None
    dsq: bool | None


class DriverLap(BaseModel):
    lap_number: int
    date_start: datetime | None
    lap_duration: float | None
    duration_sector_1: float | None
    duration_sector_2: float | None
    duration_sector_3: float | None
    is_pit_out_lap: bool | None


class DriverPitStop(BaseModel):
    session_key: int
    session_type: str
    lap_number: int
    date: datetime | None
    pit_duration: float | None
