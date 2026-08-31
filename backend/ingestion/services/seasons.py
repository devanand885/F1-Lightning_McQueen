from sqlalchemy.orm import Session as DbSession

from app.models.season import Season


def upsert_season(db: DbSession, year: int) -> Season:
    season = db.query(Season).filter(Season.year == year).one_or_none()
    if season is None:
        season = Season(year=year)
        db.add(season)
        db.flush()
    return season
