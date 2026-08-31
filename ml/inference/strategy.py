"""Historical, post-race strategy analysis. No ML - real counts and
statistics over completed race sessions, turned into numbered sentences
with the sample size attached to each one so the reader can judge
confidence. This is explicitly not live/real-time and not predictive - it
replaces the dashboard's old placeholder "Live Intelligence" panel with
real, sourced, historical statements instead of fabricated narrative text.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd

# Two pit stops (by different drivers, same session) within this many laps
# of each other are treated as a candidate undercut/exchange pair.
PIT_WINDOW_LAPS = 3
# Only counted as a genuine "battle" (not two cars in unrelated parts of the
# field) if the two drivers were within this many track positions of each
# other immediately before the exchange.
ADJACENCY_POSITIONS = 3
# A lap where this many or more drivers pit is almost certainly a
# safety-car/red-flag mass-pit window, not a discretionary strategy call by
# any one driver - profiling this dataset found laps with 9-15 simultaneous
# stops (and multi-minute gaps to the surrounding laps, consistent with a
# race stoppage). Those stops are excluded from the undercut comparison
# entirely, since "who pitted a lap earlier during a red flag" isn't a real
# strategic exchange.
MASS_PIT_LAP_THRESHOLD = 4


def _to_df(rows: list[dict], columns: list[str]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(rows)
    for col in ("date", "date_start"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


def stop_count_distribution(stints: pd.DataFrame) -> pd.DataFrame:
    """Per (session, driver): number of race stints (= number of stops + 1).
    Returns the season-wide distribution of stop counts."""
    columns = ["stops", "driver_race_count", "share"]
    if stints.empty:
        return pd.DataFrame(columns=columns)
    stint_counts = stints.groupby(["session_id", "driver_id"])["stint_number"].nunique()
    stops = (stint_counts - 1).clip(lower=0)
    dist = stops.value_counts().rename("driver_race_count").reset_index()
    dist.columns = ["stops", "driver_race_count"]
    dist["share"] = dist["driver_race_count"] / dist["driver_race_count"].sum()
    return dist.sort_values("stops").reset_index(drop=True)


def common_compound_transitions(stints: pd.DataFrame) -> pd.DataFrame:
    """Across every driver's consecutive stint pair all season, the
    frequency of each (from_compound -> to_compound) transition at a pit
    stop. Circuit-agnostic by design - this is "what do drivers switch to
    at a stop", not a per-circuit strategy call."""
    columns = ["from_compound", "to_compound", "count", "share"]
    if stints.empty:
        return pd.DataFrame(columns=columns)
    work = stints.dropna(subset=["compound"]).sort_values(["session_id", "driver_id", "stint_number"])
    work["next_compound"] = work.groupby(["session_id", "driver_id"])["compound"].shift(-1)
    transitions = work.dropna(subset=["next_compound"])
    if transitions.empty:
        return pd.DataFrame(columns=columns)
    counts = transitions.groupby(["compound", "next_compound"]).size().rename("count").reset_index()
    counts.columns = ["from_compound", "to_compound", "count"]
    counts["share"] = counts["count"] / counts["count"].sum()
    return counts.sort_values("count", ascending=False).reset_index(drop=True)


def pit_stop_timing(pit_stops: pd.DataFrame) -> dict:
    """Season-wide pit-stop duration stats (Race sessions only, already
    scoped by the repository layer)."""
    durations = pit_stops["pit_duration"].dropna() if not pit_stops.empty else pd.Series(dtype=float)
    if durations.empty:
        return {"n": 0, "median_seconds": None, "fastest_seconds": None}
    return {
        "n": int(len(durations)),
        "median_seconds": float(durations.median()),
        "fastest_seconds": float(durations.min()),
    }


def _position_before_after(
    positions: pd.DataFrame, session_id: int, driver_id: int, before_time, after_time
) -> tuple[float | None, float | None]:
    driver_positions = positions[(positions["session_id"] == session_id) & (positions["driver_id"] == driver_id)]
    if driver_positions.empty:
        return None, None
    before_rows = driver_positions[driver_positions["date"] <= before_time]
    after_rows = driver_positions[driver_positions["date"] <= after_time]
    before = float(before_rows.iloc[-1]["position"]) if not before_rows.empty else None
    after = float(after_rows.iloc[-1]["position"]) if not after_rows.empty else None
    return before, after


def undercut_analysis(pit_stops: pd.DataFrame, positions: pd.DataFrame) -> dict:
    """For pairs of drivers who pit within PIT_WINDOW_LAPS laps of each
    other and were within ADJACENCY_POSITIONS track positions of each other
    immediately beforehand, checks whether the driver who pitted first came
    out ahead of the one who pitted later (a successful "undercut") using
    the next recorded position sample after the exchange as the "settled"
    order. Reports real counts - no invented percentages if the sample is
    thin."""
    result = {
        "n_pairs_within_window": 0,
        "n_adjacent_battles": 0,
        "n_successful_undercuts": 0,
        "success_rate": None,
        "n_mass_pit_laps_excluded": 0,
    }
    if pit_stops.empty or positions.empty:
        return result

    positions = positions.sort_values("date")

    stops_per_lap = pit_stops.groupby(["session_id", "lap_number"]).size()
    mass_pit_laps = set(stops_per_lap[stops_per_lap >= MASS_PIT_LAP_THRESHOLD].index)
    clean_stops = pit_stops[
        ~pit_stops.apply(lambda r: (r["session_id"], r["lap_number"]) in mass_pit_laps, axis=1)
    ]

    pairs_checked = 0
    adjacent_battles = 0
    successes = 0

    for session_id, session_stops in clean_stops.groupby("session_id"):
        stops = session_stops.sort_values("lap_number").to_dict("records")
        for a, b in combinations(stops, 2):
            if a["driver_id"] == b["driver_id"]:
                continue
            if abs(a["lap_number"] - b["lap_number"]) > PIT_WINDOW_LAPS:
                continue
            pairs_checked += 1
            earlier, later = (a, b) if a["date"] <= b["date"] else (b, a)

            before_time = earlier["date"] - pd.Timedelta(seconds=1)
            after_time = later["date"] + pd.Timedelta(minutes=3)

            pos_before_earlier, pos_after_earlier = _position_before_after(
                positions, session_id, earlier["driver_id"], before_time, after_time
            )
            pos_before_later, pos_after_later = _position_before_after(
                positions, session_id, later["driver_id"], before_time, after_time
            )
            if None in (pos_before_earlier, pos_before_later, pos_after_earlier, pos_after_later):
                continue
            if abs(pos_before_earlier - pos_before_later) > ADJACENCY_POSITIONS:
                continue

            adjacent_battles += 1
            was_behind = pos_before_earlier > pos_before_later
            now_ahead = pos_after_earlier < pos_after_later
            if was_behind and now_ahead:
                successes += 1

    result["n_mass_pit_laps_excluded"] = len(mass_pit_laps)
    result["n_pairs_within_window"] = pairs_checked
    result["n_adjacent_battles"] = adjacent_battles
    result["n_successful_undercuts"] = successes
    if adjacent_battles > 0:
        result["success_rate"] = successes / adjacent_battles
    return result


def build_strategy_insights(*, race_stints: list[dict], pit_stops: list[dict], positions: list[dict]) -> list[dict]:
    """Returns a list of {statement, sample_size, ...supporting stats}
    dicts - real, sourced sentences replacing the dashboard's old
    LiveIntelligencePanel placeholder."""
    stints_df = _to_df(race_stints, ["session_id", "driver_id", "stint_number", "lap_start", "lap_end", "compound", "tyre_age_at_start"])
    pit_stops_df = _to_df(pit_stops, ["session_id", "driver_id", "lap_number", "date", "pit_duration"])
    positions_df = _to_df(positions, ["session_id", "driver_id", "date", "position"])

    insights = []

    stop_dist = stop_count_distribution(stints_df)
    if not stop_dist.empty:
        top = stop_dist.sort_values("share", ascending=False).iloc[0]
        insights.append(
            {
                "statement": (
                    f"The most common race strategy this season was a {int(top['stops'])}-stop race, "
                    f"used in {top['share']:.0%} of driver-races ({int(top['driver_race_count'])} of "
                    f"{int(stop_dist['driver_race_count'].sum())})."
                ),
                "sample_size": int(stop_dist["driver_race_count"].sum()),
                "metric": "stop_count_distribution",
            }
        )

    transitions = common_compound_transitions(stints_df)
    if not transitions.empty:
        top_t = transitions.iloc[0]
        insights.append(
            {
                "statement": (
                    f"The most common tyre change at a pit stop was {top_t['from_compound']} to "
                    f"{top_t['to_compound']}, seen in {top_t['share']:.0%} of stops "
                    f"({int(top_t['count'])} of {int(transitions['count'].sum())})."
                ),
                "sample_size": int(transitions["count"].sum()),
                "metric": "compound_transitions",
            }
        )

    pit_timing = pit_stop_timing(pit_stops_df)
    if pit_timing["n"] > 0:
        insights.append(
            {
                "statement": (
                    f"The median race pit stop this season took {pit_timing['median_seconds']:.1f}s "
                    f"(fastest recorded: {pit_timing['fastest_seconds']:.1f}s), across {pit_timing['n']} stops."
                ),
                "sample_size": pit_timing["n"],
                "metric": "pit_stop_timing",
            }
        )

    undercut = undercut_analysis(pit_stops_df, positions_df)
    if undercut["n_adjacent_battles"] > 0:
        insights.append(
            {
                "statement": (
                    f"In {undercut['n_adjacent_battles']} close pit-stop exchanges this season (drivers pitting "
                    f"within {PIT_WINDOW_LAPS} laps of each other while separated by {ADJACENCY_POSITIONS} track "
                    f"positions or fewer), the driver who pitted first came out ahead "
                    f"{undercut['success_rate']:.0%} of the time ({undercut['n_successful_undercuts']} of "
                    f"{undercut['n_adjacent_battles']})."
                ),
                "sample_size": undercut["n_adjacent_battles"],
                "metric": "undercut_analysis",
            }
        )
    elif undercut["n_pairs_within_window"] > 0:
        insights.append(
            {
                "statement": (
                    f"{undercut['n_pairs_within_window']} pit stops happened within {PIT_WINDOW_LAPS} laps of "
                    "another driver's stop this season, but none were close enough on track "
                    f"(within {ADJACENCY_POSITIONS} positions) to count as a real battle - insufficient sample "
                    "for an undercut success rate."
                ),
                "sample_size": undercut["n_pairs_within_window"],
                "metric": "undercut_analysis",
            }
        )

    return insights
