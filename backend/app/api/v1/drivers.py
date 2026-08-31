from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import SeasonParam
from app.db.session import get_db
from app.repositories import drivers as repo
from app.schemas.common import ListResponse
from app.schemas.driver import DriverDetail, DriverLap, DriverPitStop, DriverResult, DriverSessionSummary, DriverSummary

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("", response_model=ListResponse[DriverSummary])
def list_drivers(season: SeasonParam = None, db: Session = Depends(get_db)):
    try:
        _, rows = repo.list_drivers(db, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"count": len(rows), "items": rows}


@router.get("/{driver_number}", response_model=DriverDetail)
def get_driver(driver_number: int, season: SeasonParam = None, db: Session = Depends(get_db)):
    try:
        driver = repo.get_driver(db, driver_number, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if driver is None:
        raise HTTPException(status_code=404, detail=f"No driver with number {driver_number}")
    return driver


@router.get("/{driver_number}/sessions", response_model=ListResponse[DriverSessionSummary])
def driver_sessions(driver_number: int, season: SeasonParam = None, db: Session = Depends(get_db)):
    try:
        rows = repo.driver_sessions(db, driver_number, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"count": len(rows), "items": rows}


@router.get("/{driver_number}/results", response_model=ListResponse[DriverResult])
def driver_results(driver_number: int, season: SeasonParam = None, db: Session = Depends(get_db)):
    try:
        rows = repo.driver_results(db, driver_number, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"count": len(rows), "items": rows}


@router.get("/{driver_number}/laps", response_model=ListResponse[DriverLap])
def driver_laps(driver_number: int, session_key: int = Query(..., description="OpenF1 session_key"), db: Session = Depends(get_db)):
    rows = repo.driver_laps(db, driver_number, session_key)
    return {"count": len(rows), "items": rows}


@router.get("/{driver_number}/pit-stops", response_model=ListResponse[DriverPitStop])
def driver_pit_stops(driver_number: int, season: SeasonParam = None, db: Session = Depends(get_db)):
    try:
        rows = repo.driver_pit_stops(db, driver_number, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"count": len(rows), "items": rows}
