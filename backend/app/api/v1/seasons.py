from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import seasons as repo
from app.schemas.common import ListResponse

router = APIRouter(prefix="/seasons", tags=["seasons"])


@router.get("", response_model=ListResponse[int])
def list_seasons(db: Session = Depends(get_db)):
    years = repo.list_seasons(db)
    return {"count": len(years), "items": years}
