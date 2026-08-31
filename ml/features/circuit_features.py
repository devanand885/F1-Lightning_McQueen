"""Circuit-type classification from measurable race-session statistics.

Circuits have no stored length/type in the database - OpenF1 doesn't
provide one. Rather than inventing a type (or the old frontend mock's
5-axis "Aero/Top Speed/Traction/ERS/Low Speed" profile, which had no data
behind it at all), circuit character is derived from three things that are
directly measurable from ingested laps and stints:

  - mean top-speed-trap (`st_speed`)        -> how much of a power circuit it is
  - mean field lap-time coefficient of      -> how much the track itself spreads
    variation (CoV), across race sessions      the field out (technical/overtaking
                                                difficulty), independent of who's fast
  - mean stints-per-driver in races there   -> a degradation-severity proxy
                                                (more stops -> harsher on tyres,
                                                or a higher-than-usual safety-car rate)

Circuits are then quantile-bucketed into a small number of types by
top speed (the cleanest, most intuitive single axis - "how fast is this
track"). The exact number of buckets and their names are not decided in
advance; see `classify_circuit_types`.

Like driver_features.py, race laps are filtered to exclude
safety-car/VSC/red-flag/backmarker-affected laps (>107% of that session's
own median) before computing field CoV - profiling this dataset showed the
same confound found in tyre-degradation: without it, one chaotic session
(observed: Monaco) can inflate a circuit's spread by 5-40x relative to
every other circuit, which would make the "spread" feature mostly noise
from one incident-heavy race rather than a real property of the track.
"""

import numpy as np
import pandas as pd

OUTLIER_LAP_MEDIAN_RATIO = 1.07


def _to_df(rows: list[dict], columns: list[str]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(rows)


def circuit_speed_character(laps: pd.DataFrame) -> pd.DataFrame:
    """Per circuit: mean speed-trap reading across all race laps that
    recorded one. Not every lap has st_speed (e.g. red-flagged sessions);
    those rows are simply excluded rather than treated as zero."""
    columns = ["circuit_id", "mean_st_speed", "st_speed_laps"]
    if laps.empty:
        return pd.DataFrame(columns=columns)
    with_speed = laps.dropna(subset=["st_speed"])
    if with_speed.empty:
        return pd.DataFrame(columns=columns)
    out = with_speed.groupby("circuit_id")["st_speed"].agg(["mean", "count"]).reset_index()
    out.columns = columns
    return out


def circuit_field_spread(laps: pd.DataFrame) -> pd.DataFrame:
    """Per circuit: mean (across that circuit's race sessions) of the
    field's lap-time coefficient of variation (stdev/mean) within a
    session, after excluding SC/VSC/red-flag/traffic outlier laps. Higher =
    the track itself spreads the field's pace out more."""
    columns = ["circuit_id", "mean_field_cov", "cov_sessions"]
    if laps.empty:
        return pd.DataFrame(columns=columns)

    session_median = laps.groupby(["circuit_id", "session_id"])["lap_duration"].transform("median")
    clean = laps[laps["lap_duration"] <= session_median * OUTLIER_LAP_MEDIAN_RATIO]
    if clean.empty:
        return pd.DataFrame(columns=columns)

    per_session = clean.groupby(["circuit_id", "session_id"])["lap_duration"].agg(["mean", "std"])
    per_session = per_session[per_session["mean"] > 0]
    per_session["cov"] = per_session["std"] / per_session["mean"]
    per_session = per_session.dropna(subset=["cov"])
    if per_session.empty:
        return pd.DataFrame(columns=columns)

    out = per_session.groupby("circuit_id")["cov"].agg(["mean", "count"]).reset_index()
    out.columns = columns
    return out


def circuit_degradation_severity(stints: pd.DataFrame) -> pd.DataFrame:
    """Per circuit: mean number of race stints per driver per session -
    a rough proxy for how tyre/strategy-demanding a circuit is (more
    stints = more stops, whether from wear or from safety-car-driven
    strategy calls)."""
    columns = ["circuit_id", "mean_stints_per_driver", "stint_sessions"]
    if stints.empty:
        return pd.DataFrame(columns=columns)

    per_driver_session = stints.groupby(["circuit_id", "session_id", "driver_id"])["stint_number"].count()
    if per_driver_session.empty:
        return pd.DataFrame(columns=columns)
    per_driver_session = per_driver_session.rename("stint_count").reset_index()

    out = per_driver_session.groupby("circuit_id").agg(
        mean_stints_per_driver=("stint_count", "mean"),
        stint_sessions=("session_id", "nunique"),
    ).reset_index()
    return out


def classify_circuit_types(stats: pd.DataFrame, n_buckets: int = 3) -> pd.DataFrame:
    """Quantile-bucket circuits by mean_st_speed into `n_buckets` types.
    Bucket edges come from the real distribution of ingested circuits, not
    fixed thresholds - so this stays honest as more circuits are ingested.
    Falls back to fewer buckets if there aren't enough distinct circuits to
    fill them (quantile bucketing with too few points produces duplicate
    edges, which pandas.qcut rejects)."""
    columns = list(stats.columns) + ["circuit_type"]
    if stats.empty or "mean_st_speed" not in stats.columns:
        return pd.DataFrame(columns=columns)

    out = stats.copy()
    labels_by_bucket = {
        3: ["Low-Speed", "Medium-Speed", "High-Speed"],
        2: ["Low-Speed", "High-Speed"],
        1: ["All circuits (insufficient spread to classify)"],
    }
    k = min(n_buckets, out["mean_st_speed"].nunique())
    k = max(k, 1)
    while k > 1:
        try:
            out["circuit_type"] = pd.qcut(out["mean_st_speed"], q=k, labels=labels_by_bucket[k])
            break
        except ValueError:
            k -= 1
    else:
        out["circuit_type"] = labels_by_bucket[1][0]
    return out


def build_circuit_feature_table(*, race_laps: list[dict], race_stints: list[dict]) -> pd.DataFrame:
    laps_df = _to_df(race_laps, ["circuit_id", "session_id", "driver_id", "lap_duration", "st_speed"])
    stints_df = _to_df(race_stints, ["circuit_id", "session_id", "driver_id", "stint_number"])

    speed = circuit_speed_character(laps_df)
    spread = circuit_field_spread(laps_df)
    severity = circuit_degradation_severity(stints_df)

    table = speed
    for other in (spread, severity):
        table = table.merge(other, on="circuit_id", how="outer") if not table.empty else other

    if table.empty:
        return table

    table = classify_circuit_types(table)
    return table.sort_values("mean_st_speed").reset_index(drop=True)
