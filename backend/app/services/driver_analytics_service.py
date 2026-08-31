"""Router -> service -> ml/(features|inference) -> repository -> DB.

Builds the real driver-analytics payload that replaces the old mocked
values on /drivers/[driverNumber]: pace (field- and teammate-relative),
consistency, tyre degradation, start performance, wet/dry, a pace-over-time
trend, a circuit-type performance breakdown, and an archetype assignment
when the driver has enough data for one. Always pools every ingested
season (same convention as ml/features - these are career-to-date figures,
not a single-season snapshot), independent of any `season` filter used
elsewhere in the app.
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session as DbSession

from app.models.driver import Driver
from app.repositories import analytics as repo
from ml.features.circuit_features import build_circuit_feature_table
from ml.features.driver_features import (
    CLUSTERING_FEATURES,
    MIN_RACE_SESSIONS,
    MIN_RACE_STINTS,
    MIN_USABLE_RACE_LAPS,
    MIN_WET_LAPS_FOR_SAMPLE,
    build_driver_feature_table,
    driver_session_pace,
    teammate_relative_pace,
)
from ml.inference.archetypes import load_latest


def _to_df(rows: list[dict], columns: list[str]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(rows)
    for col in ("date_start", "date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


def _resolve_driver(db: DbSession, driver_number: int) -> Driver | None:
    return db.query(Driver).filter(Driver.driver_number == driver_number).order_by(Driver.id.asc()).first()


def _eligibility_reason(row: pd.Series) -> str:
    missing = []
    if row["race_sessions"] < MIN_RACE_SESSIONS:
        missing.append(f"{int(row['race_sessions'])} completed race sessions (minimum {MIN_RACE_SESSIONS})")
    if row["usable_race_laps"] < MIN_USABLE_RACE_LAPS:
        missing.append(f"{int(row['usable_race_laps'])} usable race laps (minimum {MIN_USABLE_RACE_LAPS})")
    if row["race_stints"] < MIN_RACE_STINTS:
        missing.append(f"{int(row['race_stints'])} race stints (minimum {MIN_RACE_STINTS})")
    return "Not enough race data yet: " + "; ".join(missing) + "."


def get_driver_analytics(db: DbSession, driver_number: int) -> dict | None:
    driver = _resolve_driver(db, driver_number)
    if driver is None:
        return None

    race_laps = repo.usable_laps(db, None, "Race")
    quali_laps = repo.usable_laps(db, None, "Qualifying")
    stints = repo.race_stints(db, None)
    race_pos = repo.race_positions_earliest(db, None)
    quali_pos = repo.qualifying_classified_positions(db, None)
    weather = repo.race_weather(db, None)
    entries = repo.race_weekend_entries(db, None)
    session_results = repo.session_results_all(db, None)
    session_ctx = _to_df(repo.session_context(db, None), ["session_id", "session_type", "date_start", "meeting_key", "meeting_name", "circuit_id"])

    table = build_driver_feature_table(
        race_laps=race_laps,
        qualifying_laps=quali_laps,
        stints=stints,
        race_positions_earliest=race_pos,
        qualifying_positions=quali_pos,
        weather=weather,
        entries=entries,
        session_results=session_results,
    )
    row = table[table["driver_id"] == driver.id]
    if row.empty:
        return {
            "driver_number": driver.driver_number,
            "full_name": driver.full_name,
            "eligible": False,
            "eligibility_reason": "No completed race or qualifying sessions yet.",
            "race_sessions": 0,
            "qualifying_sessions": 0,
            "usable_race_laps": 0,
            "race_stints": 0,
        }
    row = row.iloc[0]

    payload: dict = {
        "driver_number": driver.driver_number,
        "full_name": driver.full_name,
        "eligible": bool(row["eligible"]),
        "eligibility_reason": None if row["eligible"] else _eligibility_reason(row),
        "race_sessions": int(row["race_sessions"]),
        "qualifying_sessions": int(row["qualifying_sessions"]),
        "usable_race_laps": int(row["usable_race_laps"]),
        "race_stints": int(row["race_stints"]),
        "race_pace_field_relative": _none_if_nan(row.get("race_pace_field_relative")),
        "qualifying_pace_field_relative": _none_if_nan(row.get("qualifying_pace_field_relative")),
        "race_pace_teammate_relative": _none_if_nan(row.get("race_pace_teammate_relative")),
        "qualifying_pace_teammate_relative": _none_if_nan(row.get("qualifying_pace_teammate_relative")),
        "degradation_slope": _none_if_nan(row.get("degradation_slope")),
        "degradation_stints_used": _none_if_nan(row.get("stints_used")),
        "consistency_cv": _none_if_nan(row.get("consistency_cv")),
        "start_performance_delta": _none_if_nan(row.get("start_performance_delta")),
        "dry_laps": int(row["dry_laps"]) if pd.notna(row.get("dry_laps")) else 0,
        "wet_laps": int(row["wet_laps"]) if pd.notna(row.get("wet_laps")) else 0,
        "dry_pace_ratio": _none_if_nan(row.get("dry_pace_ratio")),
        "wet_pace_ratio": _none_if_nan(row.get("wet_pace_ratio")),
        "wet_sample_sufficient": bool(row.get("wet_sample_sufficient", False)),
        "wet_sample_threshold": MIN_WET_LAPS_FOR_SAMPLE,
    }

    payload["pace_trend"] = _pace_trend(driver.id, race_laps, quali_laps, session_ctx)
    payload["circuit_type_breakdown"] = _circuit_breakdown(db, driver.id, race_laps, entries, session_ctx)
    payload["archetype"] = _archetype(driver.id, row)

    return payload


def _none_if_nan(value) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def _pace_trend(driver_id: int, race_laps: list[dict], quali_laps: list[dict], session_ctx: pd.DataFrame) -> list[dict]:
    race_laps_df = _to_df(race_laps, ["session_id", "driver_id", "lap_number", "date_start", "lap_duration"])
    quali_laps_df = _to_df(quali_laps, ["session_id", "driver_id", "lap_number", "date_start", "lap_duration"])

    race_pace = driver_session_pace(race_laps_df, agg="median", exclude_early_laps=2)
    quali_pace = driver_session_pace(quali_laps_df, agg="min")

    race_pace = race_pace[race_pace["driver_id"] == driver_id][["session_id", "pace_ratio"]].rename(
        columns={"pace_ratio": "race_pace_field_relative"}
    )
    quali_pace = quali_pace[quali_pace["driver_id"] == driver_id][["session_id", "pace_ratio"]].rename(
        columns={"pace_ratio": "qualifying_pace_field_relative"}
    )

    merged = race_pace.merge(quali_pace, on="session_id", how="outer")
    if merged.empty:
        return []
    merged = merged.merge(session_ctx, on="session_id", how="left").sort_values("date_start")

    out = []
    for _, r in merged.iterrows():
        out.append(
            {
                "session_id": int(r["session_id"]),
                "meeting_name": r.get("meeting_name"),
                "date_start": r.get("date_start"),
                "race_pace_field_relative": _none_if_nan(r.get("race_pace_field_relative")),
                "qualifying_pace_field_relative": _none_if_nan(r.get("qualifying_pace_field_relative")),
            }
        )
    return out


def _circuit_breakdown(
    db: DbSession, driver_id: int, race_laps: list[dict], entries: list[dict], session_ctx: pd.DataFrame
) -> list[dict]:
    circuit_table = build_circuit_feature_table(
        race_laps=repo.circuit_race_laps(db, None), race_stints=repo.circuit_race_stints(db, None)
    )
    if circuit_table.empty:
        return []

    race_laps_df = _to_df(race_laps, ["session_id", "driver_id", "lap_number", "date_start", "lap_duration"])
    entries_df = _to_df(entries, ["session_id", "driver_id", "constructor_id"])
    race_pace = driver_session_pace(race_laps_df, agg="median", exclude_early_laps=2)
    teammate_pace = teammate_relative_pace(race_pace, entries_df)
    driver_pace = teammate_pace[teammate_pace["driver_id"] == driver_id]
    if driver_pace.empty:
        return []

    merged = driver_pace.merge(session_ctx[["session_id", "circuit_id"]], on="session_id", how="left")
    merged = merged.merge(circuit_table[["circuit_id", "circuit_type"]], on="circuit_id", how="inner")
    if merged.empty:
        return []

    grouped = merged.groupby("circuit_type", observed=True).agg(
        race_pace_teammate_relative=("teammate_delta", "mean"), n_sessions=("session_id", "nunique")
    ).reset_index()
    return [
        {
            "circuit_type": str(r["circuit_type"]),
            "race_pace_teammate_relative": float(r["race_pace_teammate_relative"]),
            "n_sessions": int(r["n_sessions"]),
        }
        for _, r in grouped.iterrows()
    ]


def _archetype(driver_id: int, row: pd.Series) -> dict:
    if not row["eligible"]:
        return {"assigned": False, "reason": "Driver does not meet the archetype eligibility thresholds."}

    model = load_latest()
    if model is None:
        return {"assigned": False, "reason": "No trained archetype model available."}

    features = row[CLUSTERING_FEATURES]
    if features.isna().any():
        return {"assigned": False, "reason": "Missing one or more clustering features for this driver."}

    single = pd.DataFrame([row])
    assigned = model.assign(single)
    return {
        "assigned": True,
        "cluster": int(assigned.iloc[0]["cluster"]),
        "archetype_name": assigned.iloc[0]["archetype_name"],
        "model_run_id": model.run_id,
    }
