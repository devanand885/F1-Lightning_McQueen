"""Pure transformation of raw OpenF1 `/location` + `/car_data` telemetry
into a compact, frontend-ready replay payload. No DB, no HTTP - plain rows
in (already fetched by replay_service.py, already queried from Postgres by
app/repositories/replay.py), a dict out. Nothing here is persisted.

Output is columnar per driver (parallel arrays over a shared time grid)
rather than one object per car per frame, so field names aren't repeated
tens of thousands of times in the JSON response.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

GRID_STEP_SECONDS = 0.5
COORDINATE_SPACE = 1000.0
MIN_REFERENCE_LAP_POINTS = 20


def _to_df(rows: list[dict], columns: list[str]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(rows)
    # OpenF1 timestamps aren't uniformly formatted - a sample landing on an
    # exact second (no fractional part) is a real, observed case, not
    # hypothetical (confirmed against session_key=9693). A fixed strptime
    # format inferred from the first row breaks on the first row that
    # differs, so this needs ISO8601's per-element parsing.
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], format="ISO8601", utc=True)
    if "date_start" in df.columns:
        df["date_start"] = pd.to_datetime(df["date_start"], format="ISO8601", utc=True)
    return df


def _dedupe_location(rows: list[dict]) -> pd.DataFrame:
    """Drops (0,0) placeholder points (car not yet on track) and
    de-duplicates by (driver_number, date) - chunked OpenF1 fetches
    deliberately overlap slightly at their boundaries (see
    OpenF1Client.get_location) to avoid gaps from the API's strict `date>`/
    `date<` filters, which this collapses back down."""
    df = _to_df(rows, ["date", "driver_number", "x", "y", "z"])
    if df.empty:
        return df
    df = df[~((df["x"] == 0) & (df["y"] == 0))]
    df = df.drop_duplicates(subset=["driver_number", "date"]).sort_values(["driver_number", "date"])
    return df


def _dedupe_car_data(rows: list[dict]) -> pd.DataFrame:
    df = _to_df(rows, ["date", "driver_number", "speed", "throttle", "brake", "n_gear", "rpm", "drs"])
    if df.empty:
        return df
    df = df.drop_duplicates(subset=["driver_number", "date"]).sort_values(["driver_number", "date"])
    return df


# Strict min/max is not robust here: a car's location while deep in the
# pit lane (garage approach, pit box) can sit far from the racing line -
# profiling a real cached session found ALL cars' actual range spanning the
# full 0..1000 normalized box while the visible track outline (one clean
# lap) only used the middle ~55% of it. One rare pit-lane excursion was
# dictating the scale for the entire replay. Percentile-based bounds trim
# that small tail while keeping the racing line intact - a pit-laned car
# may render just outside the (SVG-clipped) view for a few seconds, which
# is an acceptable, disclosed trade for the track actually being visible
# at a usable size for the other ~99% of the race.
_BOUNDS_LOWER_PERCENTILE = 2.0
_BOUNDS_UPPER_PERCENTILE = 98.0


def _compute_bounds(location: pd.DataFrame) -> dict:
    min_x, max_x = float(np.percentile(location["x"], _BOUNDS_LOWER_PERCENTILE)), float(
        np.percentile(location["x"], _BOUNDS_UPPER_PERCENTILE)
    )
    min_y, max_y = float(np.percentile(location["y"], _BOUNDS_LOWER_PERCENTILE)), float(
        np.percentile(location["y"], _BOUNDS_UPPER_PERCENTILE)
    )
    span = max(max_x - min_x, max_y - min_y, 1.0)
    return {"min_x": min_x, "max_x": max_x, "min_y": min_y, "max_y": max_y, "span": span}


def _normalize(x: pd.Series, y: pd.Series, bounds: dict) -> tuple[pd.Series, pd.Series]:
    scale = COORDINATE_SPACE / bounds["span"]
    return (x - bounds["min_x"]) * scale, (y - bounds["min_y"]) * scale


def _circuit_outline(location: pd.DataFrame, laps: pd.DataFrame, bounds: dict) -> list[list[float]]:
    """A single clean lap trace, not an overlay of every car's full-race
    telemetry (which would show pit-lane excursions, overtakes, and
    lapping as a scribble rather than a track shape). Prefers the fastest
    recorded lap; falls back to whichever driver has the most usable
    location points if that lap's own telemetry is too sparse."""
    if location.empty:
        return []

    candidates: list[tuple[int, pd.Timestamp, pd.Timestamp]] = []
    if not laps.empty:
        valid_laps = laps.dropna(subset=["lap_duration", "date_start"]).sort_values("lap_duration")
        by_driver_next_start = laps.sort_values(["driver_number", "date_start"])
        for _, lap_row in valid_laps.iterrows():
            driver_number = lap_row["driver_number"]
            start = lap_row["date_start"]
            later = by_driver_next_start[
                (by_driver_next_start["driver_number"] == driver_number)
                & (by_driver_next_start["date_start"] > start)
            ]
            end = later["date_start"].min() if not later.empty else location["date"].max()
            candidates.append((driver_number, start, end))

    for driver_number, start, end in candidates:
        points = location[
            (location["driver_number"] == driver_number) & (location["date"] >= start) & (location["date"] < end)
        ]
        if len(points) >= MIN_REFERENCE_LAP_POINTS:
            x, y = _normalize(points["x"], points["y"], bounds)
            return [[round(px, 1), round(py, 1)] for px, py in zip(x, y)]

    fallback_driver = location["driver_number"].value_counts().idxmax()
    points = location[location["driver_number"] == fallback_driver]
    x, y = _normalize(points["x"], points["y"], bounds)
    return [[round(px, 1), round(py, 1)] for px, py in zip(x, y)]


def build_replay_payload(
    *,
    session_key: int,
    meeting_name: str,
    season: int,
    date_from: pd.Timestamp,
    date_to: pd.Timestamp,
    location_rows: list[dict],
    car_data_rows: list[dict],
    laps_rows: list[dict],
    positions_rows: list[dict],
    entries: list[dict],
) -> dict:
    location = _dedupe_location(location_rows)
    car_data = _dedupe_car_data(car_data_rows)
    laps = _to_df(laps_rows, ["driver_number", "lap_number", "date_start", "lap_duration"])
    positions = _to_df(positions_rows, ["driver_number", "date", "position"])

    if location.empty:
        return {"available": False, "reason": "OpenF1 has no usable car-position telemetry for this session."}

    bounds = _compute_bounds(location)
    circuit_outline = _circuit_outline(location, laps, bounds)

    date_from = pd.Timestamp(date_from, tz="UTC") if pd.Timestamp(date_from).tzinfo is None else date_from
    date_to = pd.Timestamp(date_to, tz="UTC") if pd.Timestamp(date_to).tzinfo is None else date_to
    n_steps = max(int((date_to - date_from).total_seconds() / GRID_STEP_SECONDS), 1)
    grid = pd.DataFrame(
        {"date": [date_from + pd.Timedelta(seconds=i * GRID_STEP_SECONDS) for i in range(n_steps + 1)]}
    )
    timestamps = [round(i * GRID_STEP_SECONDS, 2) for i in range(n_steps + 1)]

    total_laps = int(laps["lap_number"].max()) if not laps.empty else None

    entries_by_number = {e["driver_number"]: e for e in entries}
    driver_numbers = sorted(set(location["driver_number"].unique()) & set(entries_by_number.keys()))

    drivers_payload: dict[str, dict] = {}
    for driver_number in driver_numbers:
        entry = entries_by_number[driver_number]

        driver_location = location[location["driver_number"] == driver_number].sort_values("date")
        merged = pd.merge_asof(grid, driver_location, on="date", direction="backward")
        x_norm, y_norm = _normalize(merged["x"], merged["y"], bounds)

        driver_car_data = car_data[car_data["driver_number"] == driver_number].sort_values("date") if not car_data.empty else car_data
        car_merged = pd.merge_asof(grid, driver_car_data, on="date", direction="backward") if not driver_car_data.empty else None

        driver_laps = laps[laps["driver_number"] == driver_number].sort_values("date_start") if not laps.empty else laps
        lap_merged = (
            pd.merge_asof(grid, driver_laps[["date_start", "lap_number"]].rename(columns={"date_start": "date"}), on="date", direction="backward")
            if not driver_laps.empty
            else None
        )

        driver_positions = positions[positions["driver_number"] == driver_number].sort_values("date") if not positions.empty else positions
        pos_merged = pd.merge_asof(grid, driver_positions, on="date", direction="backward") if not driver_positions.empty else None

        def col(series: pd.Series | None, round_to: int | None = None) -> list:
            # Explicit NaN -> None conversion, element by element - pandas'
            # own None-filling (e.g. Series.where) doesn't reliably survive
            # on a float64 column (it stays np.nan, not Python None), and a
            # raw NaN blows up FastAPI's JSON encoder ("Out of range float
            # values are not JSON compliant") rather than serializing as
            # `null`. This is the same failure mode already found and fixed
            # in the circuit-capability and archetype services.
            if series is None:
                return [None] * len(grid)
            out = []
            for v in series.tolist():
                if v is None or pd.isna(v):
                    out.append(None)
                elif round_to is not None:
                    out.append(round(float(v), round_to))
                else:
                    out.append(v)
            return out

        drivers_payload[str(driver_number)] = {
            "driver_number": driver_number,
            "full_name": entry["full_name"],
            "name_acronym": entry["name_acronym"],
            "constructor_name": entry["constructor_name"],
            "team_colour": entry["team_colour"],
            "x": col(x_norm, round_to=1),
            "y": col(y_norm, round_to=1),
            "speed": col(car_merged["speed"]) if car_merged is not None else [None] * len(grid),
            "throttle": col(car_merged["throttle"]) if car_merged is not None else [None] * len(grid),
            "brake": col(car_merged["brake"]) if car_merged is not None else [None] * len(grid),
            "gear": col(car_merged["n_gear"]) if car_merged is not None else [None] * len(grid),
            "drs": col(car_merged["drs"]) if car_merged is not None else [None] * len(grid),
            "lap": col(lap_merged["lap_number"]) if lap_merged is not None else [None] * len(grid),
            "position": col(pos_merged["position"]) if pos_merged is not None else [None] * len(grid),
        }

    return {
        "available": True,
        "reason": None,
        "session_key": session_key,
        "meeting_name": meeting_name,
        "season": season,
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "grid_step_seconds": GRID_STEP_SECONDS,
        "frame_count": len(grid),
        "timestamps": timestamps,
        "total_laps": total_laps,
        "circuit_outline": circuit_outline,
        "bounds": {**bounds, "space": COORDINATE_SPACE},
        "has_car_data": not car_data.empty,
        "drivers": drivers_payload,
    }
