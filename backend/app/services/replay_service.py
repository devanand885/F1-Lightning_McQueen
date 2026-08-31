"""Router -> service -> (OpenF1 client + repository) -> DB/OpenF1.

Not a DS/ML feature, so it doesn't go through ml/ - this is data retrieval
and reshaping, not analysis. Orchestrates: resolve the session and its real
race-time window from Postgres, serve a cached transform if one exists,
otherwise fetch `/location` + `/car_data` from OpenF1 in bounded time
chunks (see OpenF1Client.get_location's docstring for why chunks overlap),
hand the raw rows to replay_transform.build_replay_payload, cache the
result, and return it. High-frequency telemetry is never written to
Postgres - only this on-demand, cached JSON transform exists anywhere.
"""

from __future__ import annotations

import logging
from datetime import timedelta

import pandas as pd
from sqlalchemy.orm import Session as DbSession

from app.integrations.openf1.client import OpenF1Client
from app.integrations.openf1.exceptions import OpenF1RequestError
from app.repositories import replay as repo
from app.services import replay_cache
from app.services.replay_transform import build_replay_payload

logger = logging.getLogger(__name__)

CHUNK_MINUTES = 10
CHUNK_OVERLAP_SECONDS = 2


def list_races(db: DbSession) -> list[dict]:
    return repo.list_completed_race_sessions(db)


def _time_chunks(date_from: pd.Timestamp, date_to: pd.Timestamp) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    # A real race always spans multiple lap timestamps, so date_from <
    # date_to holds in practice - but if lap data ever collapsed to a
    # single instant (e.g. a session with only one recorded lap), the loop
    # below would silently produce zero chunks and the fetch would return
    # nothing without any error. Guarantee at least one attempted fetch.
    if date_from >= date_to:
        return [(date_from, date_from + timedelta(seconds=CHUNK_OVERLAP_SECONDS))]

    chunks = []
    cursor = date_from
    step = timedelta(minutes=CHUNK_MINUTES)
    overlap = timedelta(seconds=CHUNK_OVERLAP_SECONDS)
    while cursor < date_to:
        chunk_end = min(cursor + step, date_to)
        chunks.append((cursor, chunk_end + overlap if chunk_end < date_to else chunk_end))
        cursor = chunk_end
    return chunks


def _fetch_chunked(fetch_fn, session_key: int, date_from: pd.Timestamp, date_to: pd.Timestamp) -> list[dict]:
    rows: list[dict] = []
    for chunk_start, chunk_end in _time_chunks(date_from, date_to):
        rows.extend(fetch_fn(session_key, chunk_start, chunk_end))
    return rows


def get_replay(db: DbSession, session_key: int, openf1_client: OpenF1Client | None = None) -> dict:
    session = repo.get_session_by_key(db, session_key)
    if session is None:
        return {"available": False, "reason": f"No session with session_key {session_key}."}
    if session.session_type != "Race" or session.session_name != "Race":
        return {"available": False, "reason": "Replay is only available for the main Race session, not Sprint/Qualifying/Practice."}

    bounds = repo.get_race_time_bounds(db, session.id)
    if bounds is None:
        return {"available": False, "reason": "No lap data available to determine this race's time window."}
    date_from, date_to = bounds

    cached = replay_cache.load(session_key)
    if cached is not None:
        logger.info("Replay cache hit for session_key=%s", session_key)
        return cached

    entries = repo.get_session_entries(db, session.id)
    if not entries:
        return {"available": False, "reason": "No driver entries recorded for this session."}

    laps_rows = repo.get_laps_for_replay(db, session.id)
    positions_rows = repo.get_positions_for_replay(db, session.id)

    date_from_ts = pd.Timestamp(date_from, tz="UTC") if date_from.tzinfo is None else pd.Timestamp(date_from)
    date_to_ts = pd.Timestamp(date_to, tz="UTC") if date_to.tzinfo is None else pd.Timestamp(date_to)

    client = openf1_client or OpenF1Client()
    try:
        logger.info("Fetching replay telemetry for session_key=%s (%s to %s)", session_key, date_from_ts, date_to_ts)
        location_rows = _fetch_chunked(client.get_location, session_key, date_from_ts, date_to_ts)
        car_data_rows = _fetch_chunked(client.get_car_data, session_key, date_from_ts, date_to_ts)
    except OpenF1RequestError as exc:
        logger.error("Replay telemetry fetch failed for session_key=%s: %s", session_key, exc)
        return {"available": False, "reason": "OpenF1 is currently unavailable. Try again shortly."}
    finally:
        if openf1_client is None:
            client.close()

    payload = build_replay_payload(
        session_key=session_key,
        meeting_name=session.meeting.meeting_name,
        season=session.meeting.season.year,
        date_from=date_from_ts,
        date_to=date_to_ts,
        location_rows=location_rows,
        car_data_rows=car_data_rows,
        laps_rows=laps_rows,
        positions_rows=positions_rows,
        entries=entries,
    )

    if payload.get("available"):
        replay_cache.save(session_key, payload)

    return payload
