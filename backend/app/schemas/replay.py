from datetime import datetime

from pydantic import BaseModel


class RaceOption(BaseModel):
    session_key: int
    season: int
    meeting_name: str
    circuit_short_name: str | None
    date_start: datetime | None


class RaceListResponse(BaseModel):
    items: list[RaceOption]


class ReplayBounds(BaseModel):
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    span: float
    space: float


class DriverFrames(BaseModel):
    driver_number: int
    full_name: str
    name_acronym: str | None
    constructor_name: str
    team_colour: str | None
    x: list[float | None]
    y: list[float | None]
    speed: list[float | None]
    throttle: list[float | None]
    brake: list[float | None]
    gear: list[float | None]
    drs: list[float | None]
    lap: list[float | None]
    position: list[float | None]


class ReplayResponse(BaseModel):
    available: bool
    reason: str | None = None
    session_key: int | None = None
    meeting_name: str | None = None
    season: int | None = None
    date_from: str | None = None
    date_to: str | None = None
    grid_step_seconds: float | None = None
    frame_count: int | None = None
    timestamps: list[float] = []
    total_laps: int | None = None
    circuit_outline: list[list[float]] = []
    bounds: ReplayBounds | None = None
    has_car_data: bool = True
    drivers: dict[str, DriverFrames] = {}
