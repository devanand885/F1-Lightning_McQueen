from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import SeasonParam
from app.db.session import get_db
from app.repositories import seasons as seasons_repo
from app.schemas.simulator import SimulationResponse
from app.services import simulator_service
from ml.inference.simulator import DEFAULT_N_SIMULATIONS, DEFAULT_SEED

router = APIRouter(prefix="/simulator", tags=["simulator"])


@router.get("/championship", response_model=SimulationResponse)
def get_championship_simulation(
    season: SeasonParam = None,
    n_simulations: int = Query(DEFAULT_N_SIMULATIONS, ge=100, le=50_000),
    seed: int = Query(DEFAULT_SEED),
    db: Session = Depends(get_db),
):
    try:
        resolved = seasons_repo.resolve_season(db, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return simulator_service.get_championship_simulation(db, resolved.year, n_simulations=n_simulations, seed=seed)
