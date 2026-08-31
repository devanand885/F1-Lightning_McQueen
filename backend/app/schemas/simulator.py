from pydantic import BaseModel


class SimulatedDriver(BaseModel):
    driver_number: int
    full_name: str
    current_points: float
    expected_points: float
    expected_championship_position: float
    championship_win_probability: float
    championship_podium_probability: float
    race_win_probability: float
    race_podium_probability: float


class SimulationResponse(BaseModel):
    available: bool
    reason: str | None = None
    season: int
    n_remaining_races: int | None = None
    n_completed_races: int | None = None
    n_simulations: int | None = None
    seed: int | None = None
    drivers: list[SimulatedDriver] = []
