from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps import SeasonParam
from app.db.session import get_db
from app.repositories import constructors as repo
from app.schemas.common import ListResponse
from app.schemas.constructor import ConstructorDetail, ConstructorDriver, ConstructorPitStop, ConstructorResult, ConstructorSummary

router = APIRouter(prefix="/constructors", tags=["constructors"])


@router.get("", response_model=ListResponse[ConstructorSummary])
def list_constructors(season: SeasonParam = None, db: Session = Depends(get_db)):
    try:
        _, rows = repo.list_constructors(db, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"count": len(rows), "items": rows}


@router.get("/{constructor_id}", response_model=ConstructorDetail)
def get_constructor(constructor_id: int, season: SeasonParam = None, db: Session = Depends(get_db)):
    try:
        constructor = repo.get_constructor(db, constructor_id, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if constructor is None:
        raise HTTPException(status_code=404, detail=f"No constructor with id {constructor_id}")
    return constructor


@router.get("/{constructor_id}/results", response_model=ListResponse[ConstructorResult])
def constructor_results(constructor_id: int, season: SeasonParam = None, db: Session = Depends(get_db)):
    try:
        rows = repo.constructor_results(db, constructor_id, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"count": len(rows), "items": rows}


@router.get("/{constructor_id}/drivers", response_model=ListResponse[ConstructorDriver])
def constructor_drivers(constructor_id: int, season: SeasonParam = None, db: Session = Depends(get_db)):
    try:
        rows = repo.constructor_drivers(db, constructor_id, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"count": len(rows), "items": rows}


@router.get("/{constructor_id}/pit-stops", response_model=ListResponse[ConstructorPitStop])
def constructor_pit_stops(constructor_id: int, season: SeasonParam = None, db: Session = Depends(get_db)):
    try:
        rows = repo.constructor_pit_stops(db, constructor_id, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"count": len(rows), "items": rows}
