import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.v1.deps import SeasonParam
from app.db.session import get_db
from app.repositories import export as repo

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/{dataset}")
def export_dataset(
    dataset: str,
    season: SeasonParam = None,
    session_key: int | None = Query(None, description="Narrows laps/pit_stops/stints/weather/positions to one session"),
    export_format: str = Query("json", alias="format", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
):
    if dataset not in repo.DATASETS:
        raise HTTPException(status_code=400, detail=f"Unknown dataset '{dataset}'. Valid options: {', '.join(repo.DATASETS)}")

    try:
        fieldnames, rows = repo.export_dataset(db, dataset, season, session_key)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if export_format == "json":
        return {"count": len(rows), "items": rows}

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

    filename = f"{dataset}_{season or 'latest'}.csv"
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
