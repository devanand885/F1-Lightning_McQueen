from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps import SeasonParam
from app.db.session import get_db
from app.repositories import constructors as constructors_repo
from app.repositories import dashboard as repo
from app.repositories import drivers as drivers_repo
from app.schemas.common import ListResponse
from app.schemas.constructor import ConstructorSummary
from app.schemas.dashboard import CalendarEntry, SeasonOverview
from app.schemas.driver import DriverSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=SeasonOverview)
def overview(season: SeasonParam = None, db: Session = Depends(get_db)):
    try:
        return repo.season_overview(db, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/standings/drivers", response_model=ListResponse[DriverSummary])
def driver_standings(season: SeasonParam = None, db: Session = Depends(get_db)):
    try:
        _, rows = drivers_repo.list_drivers(db, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"count": len(rows), "items": rows}


@router.get("/standings/constructors", response_model=ListResponse[ConstructorSummary])
def constructor_standings(season: SeasonParam = None, db: Session = Depends(get_db)):
    try:
        _, rows = constructors_repo.list_constructors(db, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"count": len(rows), "items": rows}


@router.get("/calendar", response_model=ListResponse[CalendarEntry])
def calendar(season: SeasonParam = None, db: Session = Depends(get_db)):
    try:
        rows = repo.calendar(db, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"count": len(rows), "items": rows}
