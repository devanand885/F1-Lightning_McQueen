"""Unit tests for the pure feature-engineering functions in ml/ - pandas in,
pandas out, no database. Focused on the specific confounds this project's
validation runs actually found and fixed (SC/VSC outlier laps dominating
tyre-degradation slope, mass pit-stop laps inflating undercut counts), not
just happy-path coverage.
"""

import pandas as pd
import pytest

from ml.features.circuit_features import classify_circuit_types
from ml.features.driver_features import eligibility, tyre_degradation
from ml.inference.strategy import undercut_analysis


def test_eligible_driver_clears_every_threshold():
    session_results = pd.DataFrame(
        {"driver_id": [1] * 15, "session_id": range(15), "session_type": ["Race"] * 15}
    )
    race_laps = pd.DataFrame({"driver_id": [1] * 500, "session_id": [0] * 500})
    race_stints = pd.DataFrame({"driver_id": [1] * 10, "session_id": [0] * 10})
    out = eligibility(session_results, race_laps, race_stints)
    row = out[out["driver_id"] == 1].iloc[0]
    assert row["eligible"]
    assert row["race_sessions"] == 15
    assert row["usable_race_laps"] == 500
    assert row["race_stints"] == 10


def test_ineligible_driver_below_lap_threshold():
    session_results = pd.DataFrame(
        {"driver_id": [1] * 15, "session_id": range(15), "session_type": ["Race"] * 15}
    )
    race_laps = pd.DataFrame({"driver_id": [1] * 400, "session_id": [0] * 400})
    race_stints = pd.DataFrame({"driver_id": [1] * 10, "session_id": [0] * 10})
    out = eligibility(session_results, race_laps, race_stints)
    row = out[out["driver_id"] == 1].iloc[0]
    assert not row["eligible"]


def test_tyre_degradation_excludes_safety_car_outlier_laps():
    """A stint with a real, mild positive wear trend, plus one lap that's a
    huge outlier (safety car). Without outlier filtering the single spike
    would dominate an OLS slope; with it, the slope should reflect the
    clean trend and land in a small, physically plausible range."""
    laps = []
    for lap_number in range(1, 11):
        duration = 90.0 + 0.05 * lap_number
        laps.append({"session_id": 1, "driver_id": 1, "lap_number": lap_number, "lap_duration": duration})
    laps.append({"session_id": 1, "driver_id": 1, "lap_number": 11, "lap_duration": 130.0})
    laps_df = pd.DataFrame(laps)
    stints_df = pd.DataFrame(
        [{"session_id": 1, "driver_id": 1, "stint_number": 1, "lap_start": 1, "lap_end": 11, "compound": "MEDIUM"}]
    )

    out = tyre_degradation(laps_df, stints_df, min_stint_laps=5)
    row = out[out["driver_id"] == 1].iloc[0]
    assert 0 < row["degradation_slope"] < 0.5


def test_classify_circuit_types_buckets_low_and_high_speed_correctly():
    stats = pd.DataFrame(
        {
            "circuit_id": range(9),
            "mean_st_speed": [270, 275, 280, 300, 302, 305, 320, 325, 330],
        }
    )
    out = classify_circuit_types(stats, n_buckets=3)
    low = out.sort_values("mean_st_speed").iloc[0]
    high = out.sort_values("mean_st_speed").iloc[-1]
    assert low["circuit_type"] == "Low-Speed"
    assert high["circuit_type"] == "High-Speed"


def test_undercut_analysis_excludes_mass_pit_lap():
    """6 drivers all pitting on the same lap (a safety-car mass-pit event)
    should be excluded entirely; a genuine 2-driver exchange on a different
    lap, with a real position swap, should still be counted and detected as
    a successful undercut."""
    base = pd.Timestamp("2026-01-01 12:00:00")
    mass_pit_stops = [
        {"session_id": 1, "driver_id": d, "lap_number": 20, "date": base + pd.Timedelta(seconds=d)}
        for d in range(1, 7)
    ]
    genuine_pair = [
        {"session_id": 1, "driver_id": 7, "lap_number": 30, "date": base + pd.Timedelta(minutes=20)},
        {"session_id": 1, "driver_id": 8, "lap_number": 31, "date": base + pd.Timedelta(minutes=20, seconds=25)},
    ]
    pit_stops = pd.DataFrame(mass_pit_stops + genuine_pair)

    positions = pd.DataFrame(
        [
            # driver 7 pits first while behind driver 8, then comes out ahead
            {"session_id": 1, "driver_id": 7, "date": base + pd.Timedelta(minutes=19), "position": 5},
            {"session_id": 1, "driver_id": 8, "date": base + pd.Timedelta(minutes=19), "position": 4},
            {"session_id": 1, "driver_id": 7, "date": base + pd.Timedelta(minutes=22), "position": 4},
            {"session_id": 1, "driver_id": 8, "date": base + pd.Timedelta(minutes=22), "position": 5},
        ]
    )

    result = undercut_analysis(pit_stops, positions)
    assert result["n_mass_pit_laps_excluded"] == 1
    assert result["n_adjacent_battles"] == 1
    assert result["n_successful_undercuts"] == 1
