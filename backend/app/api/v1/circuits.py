from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import SeasonParam
from app.db.session import get_db
from app.repositories import circuits as repo
from app.schemas.circuit import CircuitDetail, CircuitSummary
from app.schemas.common import ListResponse
from app.services import circuit_capability_service

router = APIRouter(prefix="/circuits", tags=["circuits"])


@router.get("", response_model=ListResponse[CircuitSummary])
def list_circuits(season: SeasonParam = None, location: str | None = Query(None), db: Session = Depends(get_db)):
    rows = repo.list_circuits(db, season, location)
    return {"count": len(rows), "items": rows}


@router.get("/{circuit_id}", response_model=CircuitDetail)
def get_circuit(circuit_id: int, db: Session = Depends(get_db)):
    circuit = circuit_capability_service.get_circuit_with_capability(db, circuit_id)
    if circuit is None:
        raise HTTPException(status_code=404, detail=f"No circuit with id {circuit_id}")
    return circuit
