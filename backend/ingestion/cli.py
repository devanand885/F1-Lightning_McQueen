"""Ingestion CLI.

Usage (from backend/):
    python -m ingestion.cli ingest-season --year 2025
    python -m ingestion.cli ingest-meeting --meeting-key 1234
    python -m ingestion.cli ingest-session --session-key 9876
"""

import logging

import typer

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.integrations.openf1.client import OpenF1Client
from ingestion.services import orchestrate

app = typer.Typer(help="OpenF1 -> PostgreSQL ingestion")
logger = logging.getLogger(__name__)


@app.callback()
def _setup() -> None:
    configure_logging(get_settings().log_level)


@app.command("ingest-season")
def ingest_season(year: int = typer.Option(..., help="Season year, e.g. 2025")) -> None:
    db = SessionLocal()
    try:
        with OpenF1Client() as client:
            results = orchestrate.ingest_season(client, db, year)
    finally:
        db.close()
    logger.info("Season %s: ingested %d meetings", year, len(results))


@app.command("ingest-meeting")
def ingest_meeting(meeting_key: int = typer.Option(..., help="OpenF1 meeting_key")) -> None:
    db = SessionLocal()
    try:
        with OpenF1Client() as client:
            results = orchestrate.ingest_meeting(client, db, meeting_key)
    finally:
        db.close()
    logger.info("Meeting %s: ingested %d sessions", meeting_key, len(results))


@app.command("ingest-session")
def ingest_session(session_key: int = typer.Option(..., help="OpenF1 session_key")) -> None:
    db = SessionLocal()
    try:
        with OpenF1Client() as client:
            counts = orchestrate.ingest_session(client, db, session_key)
    finally:
        db.close()
    logger.info("Session %s: %s", session_key, counts)


if __name__ == "__main__":
    app()
