"""Pydantic models validating raw OpenF1 API responses.

Every OpenF1 endpoint returns a JSON array of loosely-typed objects with no
formal schema of its own. These models pin down the fields the ingestion
layer relies on; unrecognized fields are ignored rather than rejected, so
the OpenF1 API can add fields without breaking ingestion.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OpenF1BaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class MeetingRecord(OpenF1BaseModel):
    meeting_key: int
    meeting_name: str
    meeting_official_name: str | None = None
    location: str | None = None
    country_code: str | None = None
    country_name: str | None = None
    circuit_key: int
    circuit_short_name: str
    date_start: datetime
    gmt_offset: str | None = None
    year: int


class SessionRecord(OpenF1BaseModel):
    session_key: int
    meeting_key: int
    session_name: str
    session_type: str
    date_start: datetime
    date_end: datetime | None = None
    gmt_offset: str | None = None


class DriverEntryRecord(OpenF1BaseModel):
    """A row from /drivers - a driver's entry in one specific session."""

    session_key: int
    driver_number: int
    broadcast_name: str | None = None
    full_name: str
    first_name: str | None = None
    last_name: str | None = None
    name_acronym: str | None = None
    team_name: str
    team_colour: str | None = None
    headshot_url: str | None = None
    country_code: str | None = None


class LapRecord(OpenF1BaseModel):
    session_key: int
    driver_number: int
    lap_number: int
    date_start: datetime | None = None
    lap_duration: float | None = None
    duration_sector_1: float | None = None
    duration_sector_2: float | None = None
    duration_sector_3: float | None = None
    is_pit_out_lap: bool | None = None
    i1_speed: float | None = None
    i2_speed: float | None = None
    st_speed: float | None = None


class PositionRecord(OpenF1BaseModel):
    session_key: int
    driver_number: int
    date: datetime
    position: int


class PitRecord(OpenF1BaseModel):
    session_key: int
    driver_number: int
    lap_number: int
    date: datetime | None = None
    pit_duration: float | None = None


class IntervalRecord(OpenF1BaseModel):
    session_key: int
    driver_number: int
    date: datetime
    # Usually numeric (seconds); text like "+4 LAPS" for a lapped car.
    gap_to_leader: float | str | None = None
    interval: float | str | None = None


class StintRecord(OpenF1BaseModel):
    session_key: int
    driver_number: int
    stint_number: int
    lap_start: int | None = None
    lap_end: int | None = None
    compound: str | None = None
    tyre_age_at_start: int | None = None


class WeatherRecord(OpenF1BaseModel):
    session_key: int
    date: datetime
    air_temperature: float | None = None
    track_temperature: float | None = None
    humidity: float | None = None
    pressure: float | None = None
    rainfall: float | None = None
    wind_direction: float | None = None
    wind_speed: float | None = None


class RaceControlRecord(OpenF1BaseModel):
    session_key: int
    date: datetime
    driver_number: int | None = None
    lap_number: int | None = None
    category: str | None = None
    flag: str | None = None
    scope: str | None = None
    sector: int | None = None
    message: str | None = None


class SessionResultRecord(OpenF1BaseModel):
    session_key: int
    driver_number: int
    position: int | None = None
    number_of_laps: int | None = None
    points: float | None = None
    dnf: bool | None = None
    dns: bool | None = None
    dsq: bool | None = None
    # Numeric for race sessions; a list of per-segment values (Q1/Q2/Q3) for
    # qualifying. Kept loose here and resolved by the ingestion mapper, which
    # also stores the untouched record in `session_results.raw`.
    duration: float | list | None = None
    gap_to_leader: str | float | list | None = None
