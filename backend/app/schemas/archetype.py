from pydantic import BaseModel


class ArchetypeDriver(BaseModel):
    driver_id: int
    full_name: str
    pca_x: float
    pca_y: float


class ArchetypeCluster(BaseModel):
    cluster: int
    name: str
    size: int
    centroid: dict[str, float]
    drivers: list[ArchetypeDriver]


class ExcludedDriver(BaseModel):
    driver_id: int
    full_name: str
    race_sessions: int
    usable_race_laps: int
    race_stints: int


class ArchetypesResponse(BaseModel):
    available: bool
    reason: str | None = None
    run_id: str | None = None
    features: list[str] | None = None
    silhouette: float | None = None
    pca_explained_variance_ratio: list[float] | None = None
    n_eligible: int | None = None
    n_population: int | None = None
    clusters: list[ArchetypeCluster] = []
    excluded_drivers: list[ExcludedDriver] = []
