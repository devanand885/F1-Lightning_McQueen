from datetime import datetime

from pydantic import BaseModel


class PaceTrendPoint(BaseModel):
    session_id: int
    meeting_name: str | None
    date_start: datetime | None
    race_pace_field_relative: float | None
    qualifying_pace_field_relative: float | None


class CircuitTypeBreakdownEntry(BaseModel):
    circuit_type: str
    race_pace_teammate_relative: float
    n_sessions: int


class ArchetypeAssignment(BaseModel):
    assigned: bool
    reason: str | None = None
    cluster: int | None = None
    archetype_name: str | None = None
    model_run_id: str | None = None


class DriverAnalytics(BaseModel):
    driver_number: int
    full_name: str
    eligible: bool
    eligibility_reason: str | None

    race_sessions: int
    qualifying_sessions: int
    usable_race_laps: int
    race_stints: int

    race_pace_field_relative: float | None = None
    qualifying_pace_field_relative: float | None = None
    race_pace_teammate_relative: float | None = None
    qualifying_pace_teammate_relative: float | None = None

    degradation_slope: float | None = None
    degradation_stints_used: float | None = None

    consistency_cv: float | None = None
    start_performance_delta: float | None = None

    dry_laps: int = 0
    wet_laps: int = 0
    dry_pace_ratio: float | None = None
    wet_pace_ratio: float | None = None
    wet_sample_sufficient: bool = False
    wet_sample_threshold: int | None = None

    pace_trend: list[PaceTrendPoint] = []
    circuit_type_breakdown: list[CircuitTypeBreakdownEntry] = []
    archetype: ArchetypeAssignment | None = None
