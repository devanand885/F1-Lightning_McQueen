from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.strategy import StrategyInsightsResponse
from app.services import strategy_service

router = APIRouter(prefix="/strategy", tags=["strategy"])


@router.get("/insights", response_model=StrategyInsightsResponse)
def get_strategy_insights(db: Session = Depends(get_db)):
    return strategy_service.get_strategy_insights(db)
