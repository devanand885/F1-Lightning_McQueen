import logging

from sqlalchemy.orm import Session as DbSession

from app.integrations.openf1.client import OpenF1Client
from app.models.weather import Weather
from ingestion.services.upsert import upsert

logger = logging.getLogger(__name__)


def ingest_weather(client: OpenF1Client, db: DbSession, session_key: int, session_id: int) -> int:
    records = client.get_weather(session_key)

    rows = [
        {
            "session_id": session_id,
            "date": record.date,
            "air_temperature": record.air_temperature,
            "track_temperature": record.track_temperature,
            "humidity": record.humidity,
            "pressure": record.pressure,
            "rainfall": record.rainfall,
            "wind_direction": record.wind_direction,
            "wind_speed": record.wind_speed,
        }
        for record, _raw in records
    ]

    count = upsert(db, Weather, rows, ["session_id", "date"])
    logger.info("Session %s: upserted %d weather samples", session_key, count)
    return count
