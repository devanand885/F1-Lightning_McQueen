from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import search as repo
from app.schemas.common import ListResponse
from app.schemas.search import SearchResult

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=ListResponse[SearchResult])
def search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    rows = repo.search(db, q)
    return {"count": len(rows), "items": rows}
