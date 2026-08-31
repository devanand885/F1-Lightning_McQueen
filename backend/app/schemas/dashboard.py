from datetime import datetime

from pydantic import BaseModel


class SeasonOverview(BaseModel):
    season: int
    meeting_count: int
    session_count: int
    last_completed_meeting: str | None
    next_meeting: str | None


class CalendarEntry(BaseModel):
    meeting_key: int
    meeting_name: str
    circuit_short_name: str
    location: str | None
    date_start: datetime | None
    status: str  # "completed" | "upcoming"
