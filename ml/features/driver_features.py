"""Driver-level feature engineering.

Pure functions: raw rows (as returned by backend/app/repositories/analytics.py)
in, pandas/numpy out. Nothing here talks to a database or an HTTP framework.

Every "pace" figure is a *ratio* against a same-session baseline (field
median, or teammate) rather than an absolute lap time, so it's comparable
across circuits without needing lap-length data. Values below 1.0 mean
faster than the baseline (a shorter lap time), above 1.0 mean slower.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

MIN_RACE_SESSIONS = 15
MIN_USABLE_RACE_LAPS = 500
MIN_RACE_STINTS = 10

MIN_STINT_LAPS_FOR_DEGRADATION = 5
MIN_WET_LAPS_FOR_SAMPLE = 20
MIN_SESSION_LAPS_FOR_CONSISTENCY = 5
FUEL_LOAD_EXCLUDE_LAPS = 2


def _to_df(rows: list[dict], columns: list[str]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(rows)
    for col in ("date_start", "date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------


def eligibility(session_results: pd.DataFrame, race_laps: pd.DataFrame, race_stints: pd.DataFrame) -> pd.DataFrame:
    """Per driver: how much completed race data they have, and whether that
    clears the archetype-eligibility bar. Reserve/test drivers with no race
    participation naturally get zero counts and `eligible=False`."""
    race_sessions = (
        session_results[session_results["session_type"] == "Race"]
        .groupby("driver_id")["session_id"]
        .nunique()
        .rename("race_sessions")
    )
    qualifying_sessions = (
        session_results[session_results["session_type"] == "Qualifying"]
        .groupby("driver_id")["session_id"]
        .nunique()
        .rename("qualifying_sessions")
    )
    laps_count = race_laps.groupby("driver_id").size().rename("usable_race_laps")
    stints_count = race_stints.groupby("driver_id").size().rename("race_stints")

    out = pd.concat([race_sessions, qualifying_sessions, laps_count, stints_count], axis=1).fillna(0)
    out.index.name = "driver_id"
    out = out.reset_index()
    for col in ["race_sessions", "qualifying_sessions", "usable_race_laps", "race_stints"]:
        out[col] = out[col].astype(int)

    out["eligible"] = (
        (out["race_sessions"] >= MIN_RACE_SESSIONS)
        & (out["usable_race_laps"] >= MIN_USABLE_RACE_LAPS)
        & (out["race_stints"] >= MIN_RACE_STINTS)
    )
    return out


# ---------------------------------------------------------------------------
# Pace (field-relative and teammate-relative)
# ---------------------------------------------------------------------------


def driver_session_pace(laps: pd.DataFrame, agg: str, exclude_early_laps: int = 0) -> pd.DataFrame:
    """Per (session_id, driver_id): the driver's aggregate lap time
    (`agg='median'` for race pace, `agg='min'` for qualifying best lap) and
    its ratio to the field's same aggregate in that session."""
    columns = ["session_id", "driver_id", "driver_value", "field_value", "pace_ratio"]
    if laps.empty:
        return pd.DataFrame(columns=columns)

    work = laps
    if exclude_early_laps:
        min_lap = work.groupby("session_id")["lap_number"].transform("min")
        work = work[work["lap_number"] > min_lap + exclude_early_laps - 1]
    if work.empty:
        return pd.DataFrame(columns=columns)

    per_driver = work.groupby(["session_id", "driver_id"])["lap_duration"].agg(agg).rename("driver_value")
    field = work.groupby("session_id")["lap_duration"].agg(agg).rename("field_value")
    out = per_driver.reset_index().merge(field.reset_index(), on="session_id")
    out["pace_ratio"] = out["driver_value"] / out["field_value"]
    return out


def teammate_relative_pace(pace: pd.DataFrame, entries: pd.DataFrame) -> pd.DataFrame:
    """Per (session_id, driver_id): pace_ratio minus the same-session,
    same-constructor teammate's pace_ratio, averaged over every teammate
    present that session. Rows with no teammate that session are dropped -
    there's nothing to compute a teammate delta against."""
    if pace.empty or entries.empty:
        return pd.DataFrame(columns=["session_id", "driver_id", "teammate_delta"])

    merged = pace.merge(entries, on=["session_id", "driver_id"], how="inner")
    pairs = merged.merge(merged, on=["session_id", "constructor_id"], suffixes=("", "_mate"))
    pairs = pairs[pairs["driver_id"] != pairs["driver_id_mate"]]
    if pairs.empty:
        return pd.DataFrame(columns=["session_id", "driver_id", "teammate_delta"])

    pairs["delta"] = pairs["pace_ratio"] - pairs["pace_ratio_mate"]
    out = pairs.groupby(["session_id", "driver_id"])["delta"].mean().rename("teammate_delta").reset_index()
    return out


# ---------------------------------------------------------------------------
# Tyre degradation
# ---------------------------------------------------------------------------


# Fuel burn-off makes a car faster as a stint progresses (lighter car). This
# is a fixed, disclosed correction (not a fitted one) using a commonly-cited
# F1 fuel-effect figure of roughly 0.03-0.045s gained per lap of fuel
# burned; the corrected series adds that back so the residual trend is
# attributable to tyre age rather than fuel.
FUEL_EFFECT_SECONDS_PER_LAP = 0.035

# A stint's raw lap times are also dominated by events that have nothing to
# do with tyre wear: safety cars, VSCs, red flags, and being stuck behind
# backmarkers can all make a single lap several seconds slower than the
# green-flag pace around it. Profiling the real data confirmed this is the
# dominant confound here (far larger than fuel burn): ~10% of in-stint laps
# sit above 107% of their own stint's median, and 63% of stints contain at
# least one such lap. Left in, a handful of these outliers routinely swing
# an OLS slope by more than a full second/lap. They're excluded before
# fitting using the stint's own median as the reference (same style of
# threshold as F1's real 107% qualifying cutoff), which is a standard,
# disclosed way to approximate "green flag laps only" without a race-control
# feed. The stint's first lap is also excluded - it is adjacent to the
# out-lap from the pit stop (cold tyres) and is not representative of the
# green-flag degradation trend the slope is meant to capture.
OUTLIER_LAP_MEDIAN_RATIO = 1.07


def tyre_degradation(
    laps: pd.DataFrame, stints: pd.DataFrame, min_stint_laps: int = MIN_STINT_LAPS_FOR_DEGRADATION
) -> pd.DataFrame:
    """Per driver: mean linear-regression slope (seconds/lap) of
    fuel-corrected lap time against laps-since-stint-start, across every
    stint with enough green-flag laps. Safety-car/VSC/red-flag/traffic
    outlier laps and each stint's first lap are excluded before fitting (see
    OUTLIER_LAP_MEDIAN_RATIO above). A simple linear approximation with a
    fixed fuel correction, not a compound-specific physical model -
    documented as such. Positive = pace getting worse as the tyre ages."""
    columns = ["driver_id", "degradation_slope", "stints_used"]
    if laps.empty or stints.empty:
        return pd.DataFrame(columns=columns)

    merged = laps.merge(stints, on=["session_id", "driver_id"], how="inner")
    lap_end = merged["lap_end"].fillna(np.inf)
    in_stint = merged[(merged["lap_number"] >= merged["lap_start"]) & (merged["lap_number"] <= lap_end)].copy()
    if in_stint.empty:
        return pd.DataFrame(columns=columns)
    in_stint["laps_into_stint"] = in_stint["lap_number"] - in_stint["lap_start"]
    in_stint = in_stint[in_stint["laps_into_stint"] > 0]
    if in_stint.empty:
        return pd.DataFrame(columns=columns)

    stint_median = in_stint.groupby(["session_id", "driver_id", "stint_number"])["lap_duration"].transform("median")
    in_stint = in_stint[in_stint["lap_duration"] <= stint_median * OUTLIER_LAP_MEDIAN_RATIO]
    if in_stint.empty:
        return pd.DataFrame(columns=columns)

    in_stint["fuel_corrected_duration"] = in_stint["lap_duration"] + in_stint["laps_into_stint"] * FUEL_EFFECT_SECONDS_PER_LAP

    slopes = []
    for (session_id, driver_id, stint_number), group in in_stint.groupby(["session_id", "driver_id", "stint_number"]):
        if len(group) < min_stint_laps:
            continue
        x = group["laps_into_stint"].to_numpy(dtype=float)
        y = group["fuel_corrected_duration"].to_numpy(dtype=float)
        if np.std(x) == 0:
            continue
        slope, _intercept = np.polyfit(x, y, 1)
        slopes.append({"driver_id": driver_id, "slope": slope})

    if not slopes:
        return pd.DataFrame(columns=columns)

    slopes_df = pd.DataFrame(slopes)
    out = slopes_df.groupby("driver_id")["slope"].agg(["mean", "count"]).reset_index()
    out.columns = columns
    return out


# ---------------------------------------------------------------------------
# Consistency
# ---------------------------------------------------------------------------


def consistency(laps: pd.DataFrame, exclude_early_laps: int = FUEL_LOAD_EXCLUDE_LAPS) -> pd.DataFrame:
    """Per driver: mean coefficient of variation (stdev/mean) of usable race
    lap times within each session, averaged across sessions. Sessions with
    too few laps to compute a meaningful spread are skipped."""
    columns = ["driver_id", "consistency_cv"]
    if laps.empty:
        return pd.DataFrame(columns=columns)

    work = laps
    if exclude_early_laps:
        min_lap = work.groupby("session_id")["lap_number"].transform("min")
        work = work[work["lap_number"] > min_lap + exclude_early_laps - 1]
    if work.empty:
        return pd.DataFrame(columns=columns)

    per_session = work.groupby(["session_id", "driver_id"])["lap_duration"].agg(["mean", "std", "count"])
    per_session = per_session[per_session["count"] >= MIN_SESSION_LAPS_FOR_CONSISTENCY]
    if per_session.empty:
        return pd.DataFrame(columns=columns)
    per_session["cv"] = per_session["std"] / per_session["mean"]

    out = per_session.reset_index().groupby("driver_id")["cv"].mean().reset_index()
    out.columns = columns
    return out


# ---------------------------------------------------------------------------
# Start performance
# ---------------------------------------------------------------------------


def start_performance(
    qualifying_positions: pd.DataFrame, race_positions_earliest: pd.DataFrame, session_meeting_map: pd.DataFrame
) -> pd.DataFrame:
    """Per driver: mean (qualifying classified position - earliest recorded
    race position), across meetings where both exist. Positive = gained
    places early. Qualifying position stands in for grid position since the
    real starting grid isn't ingested - documented limitation, not silently
    assumed to be exact (penalties etc. can move the real grid)."""
    columns = ["driver_id", "start_performance_delta", "meetings_used"]
    if qualifying_positions.empty or race_positions_earliest.empty or session_meeting_map.empty:
        return pd.DataFrame(columns=columns)

    quali_map = session_meeting_map[session_meeting_map["session_type"] == "Qualifying"][["session_id", "meeting_key"]]
    race_map = session_meeting_map[session_meeting_map["session_type"] == "Race"][["session_id", "meeting_key"]]

    quali = qualifying_positions.merge(quali_map, on="session_id").rename(columns={"position": "grid_proxy"})
    race = race_positions_earliest.merge(race_map, on="session_id").rename(columns={"position": "early_position"})

    paired = quali.merge(race, on=["meeting_key", "driver_id"], suffixes=("_q", "_r"))
    if paired.empty:
        return pd.DataFrame(columns=columns)
    paired["places_gained"] = paired["grid_proxy"] - paired["early_position"]

    out = paired.groupby("driver_id")["places_gained"].agg(["mean", "count"]).reset_index()
    out.columns = columns
    return out


# ---------------------------------------------------------------------------
# Wet / dry
# ---------------------------------------------------------------------------


def classify_dry_wet(laps: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    """Adds a `rainfall` column (0.0/1.0/NaN) to `laps` via a per-session
    nearest-timestamp join against `weather`. `rainfall` is a clean binary
    flag in this dataset (verified against real values, not assumed)."""
    out_columns = list(laps.columns) + ["rainfall"]
    if laps.empty or weather.empty:
        out = laps.copy()
        out["rainfall"] = np.nan
        return out

    results = []
    for session_id, lap_group in laps.groupby("session_id"):
        w = weather[weather["session_id"] == session_id].sort_values("date")
        undated = lap_group[lap_group["date_start"].isna()].copy()
        if not undated.empty:
            undated["rainfall"] = np.nan
            results.append(undated)

        dated = lap_group[lap_group["date_start"].notna()].sort_values("date_start")
        if dated.empty:
            continue
        if w.empty:
            dated = dated.copy()
            dated["rainfall"] = np.nan
            results.append(dated)
            continue
        merged = pd.merge_asof(dated, w[["date", "rainfall"]], left_on="date_start", right_on="date", direction="nearest")
        merged.index = dated.index
        results.append(merged)

    result = pd.concat(results) if results else pd.DataFrame(columns=out_columns)
    return result


def wet_dry_pace(laps_with_rainfall: pd.DataFrame, min_wet_laps: int = MIN_WET_LAPS_FOR_SAMPLE) -> pd.DataFrame:
    """Per driver: dry/wet usable-lap counts, and wet-pace-ratio only when
    the sample clears `min_wet_laps` - otherwise `insufficient_sample=True`
    and the ratio is left null rather than computed from a handful of laps."""
    columns = ["driver_id", "dry_laps", "wet_laps", "dry_pace_ratio", "wet_pace_ratio", "wet_sample_sufficient"]
    if laps_with_rainfall.empty:
        return pd.DataFrame(columns=columns)

    counts = laps_with_rainfall.groupby(["driver_id", "rainfall"]).size().unstack(fill_value=0)
    counts = counts.rename(columns={0.0: "dry_laps", 1.0: "wet_laps"})
    for col in ("dry_laps", "wet_laps"):
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[["dry_laps", "wet_laps"]].reset_index()

    dry_pace = driver_session_pace(laps_with_rainfall[laps_with_rainfall["rainfall"] == 0], agg="median")
    wet_pace = driver_session_pace(laps_with_rainfall[laps_with_rainfall["rainfall"] == 1], agg="median")
    dry_avg = dry_pace.groupby("driver_id")["pace_ratio"].mean().rename("dry_pace_ratio").reset_index()
    wet_avg = wet_pace.groupby("driver_id")["pace_ratio"].mean().rename("wet_pace_ratio").reset_index()

    out = counts.merge(dry_avg, on="driver_id", how="left").merge(wet_avg, on="driver_id", how="left")
    out["wet_sample_sufficient"] = out["wet_laps"] >= min_wet_laps
    out.loc[~out["wet_sample_sufficient"], "wet_pace_ratio"] = np.nan
    return out


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

CLUSTERING_FEATURES = [
    "race_pace_teammate_relative",
    "qualifying_pace_teammate_relative",
    "quali_race_delta_teammate_relative",
    "degradation_slope",
    "consistency_cv",
    "start_performance_delta",
]


def build_driver_feature_table(
    *,
    race_laps: list[dict],
    qualifying_laps: list[dict],
    stints: list[dict],
    race_positions_earliest: list[dict],
    qualifying_positions: list[dict],
    weather: list[dict],
    entries: list[dict],
    session_results: list[dict],
) -> pd.DataFrame:
    """Builds the full per-driver feature table (one row per driver seen in
    `session_results`, eligible or not - callers filter on `eligible`)."""
    race_laps_df = _to_df(race_laps, ["session_id", "driver_id", "lap_number", "date_start", "lap_duration"])
    qualifying_laps_df = _to_df(qualifying_laps, ["session_id", "driver_id", "lap_number", "date_start", "lap_duration"])
    stints_df = _to_df(stints, ["session_id", "driver_id", "stint_number", "lap_start", "lap_end", "compound", "tyre_age_at_start"])
    race_positions_df = _to_df(race_positions_earliest, ["session_id", "driver_id", "date", "position"])
    qualifying_positions_df = _to_df(qualifying_positions, ["session_id", "driver_id", "position"])
    weather_df = _to_df(weather, ["session_id", "date", "rainfall"])
    entries_df = _to_df(entries, ["session_id", "driver_id", "constructor_id"])
    session_results_df = _to_df(
        session_results,
        ["session_id", "driver_id", "session_type", "date_start", "meeting_key", "position", "points", "dnf", "dns", "dsq"],
    )

    elig = eligibility(session_results_df, race_laps_df, stints_df)

    race_pace = driver_session_pace(race_laps_df, agg="median", exclude_early_laps=FUEL_LOAD_EXCLUDE_LAPS)
    quali_pace = driver_session_pace(qualifying_laps_df, agg="min")

    race_pace_field = race_pace.groupby("driver_id")["pace_ratio"].mean().rename("race_pace_field_relative").reset_index()
    quali_pace_field = quali_pace.groupby("driver_id")["pace_ratio"].mean().rename("qualifying_pace_field_relative").reset_index()

    race_pace_tm = teammate_relative_pace(race_pace, entries_df)
    quali_pace_tm = teammate_relative_pace(quali_pace, entries_df)
    race_pace_tm_avg = race_pace_tm.groupby("driver_id")["teammate_delta"].mean().rename("race_pace_teammate_relative").reset_index()
    quali_pace_tm_avg = quali_pace_tm.groupby("driver_id")["teammate_delta"].mean().rename("qualifying_pace_teammate_relative").reset_index()

    degradation_df = tyre_degradation(race_laps_df, stints_df)
    consistency_df = consistency(race_laps_df)

    session_meeting_map = session_results_df[["session_id", "meeting_key", "session_type"]].drop_duplicates("session_id")
    start_perf_df = start_performance(qualifying_positions_df, race_positions_df, session_meeting_map)

    laps_with_rain = classify_dry_wet(race_laps_df, weather_df)
    wet_dry_df = wet_dry_pace(laps_with_rain)

    table = elig
    for other in [
        race_pace_field,
        quali_pace_field,
        race_pace_tm_avg,
        quali_pace_tm_avg,
        degradation_df,
        consistency_df,
        start_perf_df,
        wet_dry_df,
    ]:
        table = table.merge(other, on="driver_id", how="left")

    table["quali_race_delta_field_relative"] = table["qualifying_pace_field_relative"] - table["race_pace_field_relative"]
    table["quali_race_delta_teammate_relative"] = (
        table["qualifying_pace_teammate_relative"] - table["race_pace_teammate_relative"]
    )

    return table
