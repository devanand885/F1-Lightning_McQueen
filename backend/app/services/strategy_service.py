from __future__ import annotations

from sqlalchemy.orm import Session as DbSession

from app.repositories import analytics as repo
from ml.inference.strategy import build_strategy_insights


def get_strategy_insights(db: DbSession) -> dict:
    insights = build_strategy_insights(
        race_stints=repo.race_stints(db, None),
        pit_stops=repo.race_pit_stops(db, None),
        positions=repo.race_positions_all(db, None),
    )
    return {"insights": insights}
