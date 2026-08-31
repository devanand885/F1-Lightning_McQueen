"""Thin, resilient HTTP client for the OpenF1 API.

This is the only module in the whole system allowed to know OpenF1's base
URL. Callers get back validated pydantic records (extra fields ignored) and,
alongside each, the original raw dict in case downstream storage wants to
keep it verbatim.
"""

import logging
import time
from collections import deque
from datetime import datetime
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError
from tenacity import before_sleep_log, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings, get_settings
from app.integrations.openf1.exceptions import OpenF1RequestError, OpenF1ValidationError
from app.integrations.openf1.schemas import (
    DriverEntryRecord,
    IntervalRecord,
    LapRecord,
    MeetingRecord,
    PitRecord,
    PositionRecord,
    RaceControlRecord,
    SessionRecord,
    SessionResultRecord,
    StintRecord,
    WeatherRecord,
)

logger = logging.getLogger(__name__)

TModel = TypeVar("TModel", bound=BaseModel)


class _RetriableStatus(Exception):
    """Internal signal for a 5xx or 429 response, so tenacity retries those
    but leaves other 4xx responses alone."""

    def __init__(self, status_code: int):
        self.status_code = status_code
        super().__init__(f"OpenF1 returned a retriable status {status_code}")


class _RateLimiter:
    """Sleeps as needed to stay under OpenF1's published per-second and
    per-minute request caps. Not thread-safe - ingestion runs sequentially."""

    def __init__(self, max_per_second: float, max_per_minute: float):
        self._max_per_second = max_per_second
        self._max_per_minute = max_per_minute
        self._timestamps: deque[float] = deque()

    def acquire(self) -> None:
        now = time.monotonic()
        self._timestamps.append(now)
        while self._timestamps and now - self._timestamps[0] > 60:
            self._timestamps.popleft()

        if len(self._timestamps) > self._max_per_minute:
            time.sleep(max(0.0, 60 - (now - self._timestamps[0])))

        recent_second = [t for t in self._timestamps if now - t <= 1]
        if len(recent_second) > self._max_per_second:
            time.sleep(max(0.0, 1 - (now - recent_second[0])))


class OpenF1Client:
    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._http = httpx.Client(
            base_url=self._settings.openf1_base_url,
            timeout=self._settings.openf1_timeout_seconds,
        )
        self._limiter = _RateLimiter(
            self._settings.openf1_max_requests_per_second,
            self._settings.openf1_max_requests_per_minute,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "OpenF1Client":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def _get(self, path: str, params: dict[str, Any]) -> list[dict]:
        retryer = retry(
            reraise=True,
            stop=stop_after_attempt(self._settings.openf1_max_retries),
            wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
            retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError, _RetriableStatus)),
            before_sleep=before_sleep_log(logger, logging.WARNING),
        )

        @retryer
        def _do_request() -> list[dict]:
            self._limiter.acquire()
            logger.debug("GET %s params=%s", path, params)
            response = self._http.get(path, params=params)
            if response.status_code >= 500 or response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                if retry_after is not None:
                    try:
                        time.sleep(max(0.0, float(retry_after)))
                    except ValueError:
                        pass
                raise _RetriableStatus(response.status_code)
            if response.status_code == 404:
                # OpenF1 returns 404 (rather than an empty array) when a
                # filtered query has no matching data, e.g. /intervals for a
                # practice session. That's a legitimate empty result, not a
                # failure.
                logger.debug("OpenF1 returned 404 (no data) for %s params=%s", path, params)
                return []
            response.raise_for_status()
            return response.json()

        try:
            return _do_request()
        except httpx.HTTPStatusError as exc:
            logger.error("OpenF1 request failed (%s %s): %s", path, params, exc)
            raise OpenF1RequestError(f"OpenF1 request failed for {path}: {exc}") from exc
        except (httpx.TimeoutException, httpx.TransportError, _RetriableStatus) as exc:
            logger.error("OpenF1 request failed after retries (%s %s): %s", path, params, exc)
            raise OpenF1RequestError(f"OpenF1 request failed for {path} after retries: {exc}") from exc

    def _get_and_parse(self, path: str, params: dict[str, Any], model: type[TModel]) -> list[tuple[TModel, dict]]:
        raw_items = self._get(path, params)
        try:
            return [(model.model_validate(item), item) for item in raw_items]
        except ValidationError as exc:
            raise OpenF1ValidationError(f"OpenF1 response failed validation for {model.__name__}: {exc}") from exc

    def get_meetings(
        self, year: int | None = None, meeting_key: int | None = None
    ) -> list[tuple[MeetingRecord, dict]]:
        params: dict[str, Any] = {}
        if year is not None:
            params["year"] = year
        if meeting_key is not None:
            params["meeting_key"] = meeting_key
        return self._get_and_parse("/meetings", params, MeetingRecord)

    def get_sessions(
        self, meeting_key: int | None = None, session_key: int | None = None
    ) -> list[tuple[SessionRecord, dict]]:
        params: dict[str, Any] = {}
        if meeting_key is not None:
            params["meeting_key"] = meeting_key
        if session_key is not None:
            params["session_key"] = session_key
        return self._get_and_parse("/sessions", params, SessionRecord)

    def get_drivers(self, session_key: int) -> list[tuple[DriverEntryRecord, dict]]:
        return self._get_and_parse("/drivers", {"session_key": session_key}, DriverEntryRecord)

    def get_laps(self, session_key: int) -> list[tuple[LapRecord, dict]]:
        return self._get_and_parse("/laps", {"session_key": session_key}, LapRecord)

    def get_positions(self, session_key: int) -> list[tuple[PositionRecord, dict]]:
        return self._get_and_parse("/position", {"session_key": session_key}, PositionRecord)

    def get_pit_stops(self, session_key: int) -> list[tuple[PitRecord, dict]]:
        return self._get_and_parse("/pit", {"session_key": session_key}, PitRecord)

    def get_intervals(self, session_key: int) -> list[tuple[IntervalRecord, dict]]:
        return self._get_and_parse("/intervals", {"session_key": session_key}, IntervalRecord)

    def get_stints(self, session_key: int) -> list[tuple[StintRecord, dict]]:
        return self._get_and_parse("/stints", {"session_key": session_key}, StintRecord)

    def get_weather(self, session_key: int) -> list[tuple[WeatherRecord, dict]]:
        return self._get_and_parse("/weather", {"session_key": session_key}, WeatherRecord)

    def get_race_control(self, session_key: int) -> list[tuple[RaceControlRecord, dict]]:
        return self._get_and_parse("/race_control", {"session_key": session_key}, RaceControlRecord)

    def get_session_result(self, session_key: int) -> list[tuple[SessionResultRecord, dict]]:
        return self._get_and_parse("/session_result", {"session_key": session_key}, SessionResultRecord)

    def get_location(self, session_key: int, date_from: datetime, date_to: datetime) -> list[dict]:
        """Raw car-position telemetry for every driver in the given time
        window, all drivers in one call (no driver_number filter). Returned
        as plain dicts, not validated pydantic ingestion records - this is
        never persisted, only transformed for on-demand replay (see
        app/services/replay_service.py), so the ingestion schema module
        doesn't need to know about it.

        OpenF1's range filters are strict inequalities appended to the field
        name (`date>`, `date<` - `date>=` is not a recognized filter and
        silently matches nothing, confirmed against the live API), so
        callers should pass slightly overlapping chunk boundaries and
        de-duplicate by (driver_number, date) rather than relying on an
        inclusive bound."""
        return self._get(
            "/location",
            {"session_key": session_key, "date>": date_from.isoformat(), "date<": date_to.isoformat()},
        )

    def get_car_data(self, session_key: int, date_from: datetime, date_to: datetime) -> list[dict]:
        """Raw car telemetry (speed/throttle/brake/gear/RPM/DRS) for every
        driver in the given time window. Same on-demand, not-persisted,
        strict-inequality contract as get_location."""
        return self._get(
            "/car_data",
            {"session_key": session_key, "date>": date_from.isoformat(), "date<": date_to.isoformat()},
        )
