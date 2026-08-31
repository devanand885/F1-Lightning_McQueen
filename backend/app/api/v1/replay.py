from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.replay import RaceListResponse, ReplayResponse
from app.services import replay_service

router = APIRouter(prefix="/replay", tags=["replay"])


@router.get("/races", response_model=RaceListResponse)
def list_races(db: Session = Depends(get_db)):
    return {"items": replay_service.list_races(db)}


@router.get("/{session_key}", response_model=ReplayResponse)
def get_replay(session_key: int, db: Session = Depends(get_db)):
    return replay_service.get_replay(db, session_key)
