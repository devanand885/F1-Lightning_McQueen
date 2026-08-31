from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.archetype import ArchetypesResponse
from app.services import archetypes_service

router = APIRouter(prefix="/archetypes", tags=["archetypes"])


@router.get("", response_model=ArchetypesResponse)
def get_archetypes(db: Session = Depends(get_db)):
    return archetypes_service.get_archetypes(db)
