from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.driver_analytics import DriverAnalytics
from app.services import driver_analytics_service

router = APIRouter(prefix="/drivers", tags=["driver-analytics"])


@router.get("/{driver_number}/analytics", response_model=DriverAnalytics)
def get_driver_analytics(driver_number: int, db: Session = Depends(get_db)):
    result = driver_analytics_service.get_driver_analytics(db, driver_number)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No driver with number {driver_number}")
    return result
