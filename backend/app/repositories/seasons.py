from sqlalchemy.orm import Session as DbSession

from app.models.season import Season


def resolve_season(db: DbSession, year: int | None) -> Season:
    """Returns the requested season, or the latest ingested season if `year`
    is omitted. Raises ValueError if no matching data exists."""
    if year is not None:
        season = db.query(Season).filter(Season.year == year).one_or_none()
        if season is None:
            raise ValueError(f"No data for season {year}")
        return season

    season = db.query(Season).order_by(Season.year.desc()).first()
    if season is None:
        raise ValueError("No seasons ingested yet")
    return season


def list_seasons(db: DbSession) -> list[int]:
    rows = db.query(Season.year).order_by(Season.year.desc()).all()
    return [row[0] for row in rows]
