"""A small disk-backed cache for transformed replay payloads.

Nothing in this project needed a caching layer before this feature - the
DS/ML endpoints are cheap enough to recompute per request. Full-race
telemetry is not: a single race's `/location` + `/car_data` fetch from
OpenF1 is tens of megabytes and takes real time even after chunking and
rate-limiting, so re-fetching it on every page load would make the feature
unusable. This is intentionally the simplest thing that works at portfolio
scale - one gzip-JSON file per session, keyed by session_key, no eviction
policy (a handful of browsed races is a few MB total) and no new
infrastructure dependency (no Redis).

Disk-backed rather than an in-memory dict specifically because the backend
runs under `uvicorn --reload` in dev, which restarts the process on every
code change - an in-memory cache would be pointless while iterating on
anything else in the app.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parents[2] / ".cache" / "replay"

# Bumped whenever build_replay_payload's output shape changes, so a stale
# cache file from a previous version of the transform is treated as a miss
# instead of being served (or crashing the response model) as-is.
SCHEMA_VERSION = 2


def _path(session_key: int) -> Path:
    return CACHE_DIR / f"{session_key}.v{SCHEMA_VERSION}.json.gz"


def load(session_key: int) -> dict | None:
    path = _path(session_key)
    if not path.exists():
        return None
    try:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError, gzip.BadGzipFile):
        return None


def save(session_key: int, payload: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _path(session_key)
    tmp_path = path.with_suffix(".tmp")
    with gzip.open(tmp_path, "wt", encoding="utf-8") as f:
        json.dump(payload, f)
    tmp_path.replace(path)
