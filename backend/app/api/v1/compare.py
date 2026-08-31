from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import SeasonParam
from app.db.session import get_db
from app.repositories import compare as repo
from app.schemas.compare import ComparisonResponse
from app.services import compare_analytics_service

router = APIRouter(prefix="/compare", tags=["compare"])


def _parse_ids(raw: str) -> list[int]:
    try:
        ids = [int(part) for part in raw.split(",") if part.strip()]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="`ids` must be a comma-separated list of integers") from exc
    if len(ids) < 2:
        raise HTTPException(status_code=400, detail="Provide at least two ids to compare")
    return ids


@router.get("/drivers", response_model=ComparisonResponse)
def compare_drivers(
    ids: str = Query(..., description="Comma-separated driver numbers, e.g. 1,44"),
    season: SeasonParam = None,
    db: Session = Depends(get_db),
):
    driver_numbers = _parse_ids(ids)
    try:
        response = repo.compare_drivers(db, driver_numbers, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    response["analytics"] = compare_analytics_service.build_driver_analytics_block(db, driver_numbers)
    return response


@router.get("/constructors", response_model=ComparisonResponse)
def compare_constructors(
    ids: str = Query(..., description="Comma-separated constructor ids"),
    season: SeasonParam = None,
    db: Session = Depends(get_db),
):
    constructor_ids = _parse_ids(ids)
    try:
        return repo.compare_constructors(db, constructor_ids, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
