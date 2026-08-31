"""Championship Monte Carlo simulator.

Unlike the archetype model, this has no persisted "model" - there's
nothing to fit offline. Every run recomputes each driver's calibration
inputs (a race-pace-and-qualifying-pace strength rating, a per-driver noise
sigma, and a Bayesian-shrunk DNF probability) from the current database,
then simulates the season's *remaining* races on top of each driver's real,
already-accumulated points. A calibration.json artifact is still written
per run (same ml/models/artifacts/<date>/ convention as the archetype
model) purely so a given run's inputs and result are reproducible and
auditable later - not because there's a trained model to version.

Methodology, and why it differs from the archetype model's teammate-
relative features: archetypes intentionally net out car performance (see
ml/features/driver_features.py) because they're describing driver skill in
isolation. The simulator is predicting actual finishing order, where car
performance is part of the real outcome - so it uses *field-relative* pace
(driver_value / field median or best that session), not teammate-relative.

  - strength rating: recency-weighted mean of field-relative race pace
    (median usable lap / field median) and qualifying pace (best lap /
    field best), blended 70/30 race:qualifying since race pace is what
    actually earns points. Recency weighting uses exponential decay with a
    120-day half-life - a documented, disclosed choice, not fitted.
  - sigma (per-race noise): the driver's own session-to-session standard
    deviation of race pace ratio, shrunk toward the field-average sigma
    using n/(n+k) weighting (k=8) so a driver with only a handful of
    sessions doesn't get an unrealistically tight or wide spread.
  - DNF probability: (dnf count) / (races entered), Bayesian-shrunk toward
    the field's overall DNF rate with a Beta prior worth 10 "races" of
    prior weight - the same reasoning as sigma: a driver with few races
    shouldn't get a 0% or 100% reliability figure off a tiny sample.

Each simulated race: draw iid Normal(0, sigma_i) noise per driver, rank by
(rating_i + noise_i) ascending, draw independent Bernoulli DNFs, award the
real F1 points table (P1..P10: 25/18/15/12/10/8/6/4/2/1, no fastest-lap
bonus - kept out per the plan's explicit "optional, not required" list) to
classified finishers. Only remaining (not-yet-completed) races for the
season are simulated; each driver's real current points are the starting
base for every run.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from ml.features.driver_features import driver_session_pace

RACE_PACE_WEIGHT = 0.7
QUALIFYING_PACE_WEIGHT = 0.3
RECENCY_HALF_LIFE_DAYS = 120
SIGMA_SHRINKAGE_K = 8
DNF_PRIOR_STRENGTH_RACES = 10
DEFAULT_N_SIMULATIONS = 10_000
DEFAULT_SEED = 42

POINTS_TABLE = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}

ARTIFACTS_ROOT = Path(__file__).resolve().parents[1] / "models" / "artifacts"


def _to_df(rows: list[dict], columns: list[str]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(rows)
    for col in ("date_start", "date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


def _recency_weighted_mean(values: pd.Series, dates: pd.Series, as_of: pd.Timestamp) -> float | None:
    if values.empty:
        return None
    age_days = (as_of - dates).dt.total_seconds() / 86400
    weights = 0.5 ** (age_days.clip(lower=0) / RECENCY_HALF_LIFE_DAYS)
    if weights.sum() == 0:
        return float(values.mean())
    return float((values * weights).sum() / weights.sum())


def build_calibration(
    *,
    race_laps: list[dict],
    qualifying_laps: list[dict],
    session_results: list[dict],
    current_grid: list[dict],
) -> pd.DataFrame:
    """Per current-grid driver: rating (lower = faster), sigma, dnf_prob,
    and the real points/race count already on the board this season. Grid
    drivers with no computable race pace (e.g. a reserve driver who's only
    done a single practice session) are dropped with a reason, mirroring
    the archetype model's eligibility-exclusion pattern.

    Assumption (disclosed, not modeled): every driver who has completed at
    least one race session in the ingested data is assumed to keep
    contesting the season's remaining races. There is no separate signal
    for "this driver has since been replaced" - a driver who has in fact
    been dropped mid-season simply keeps a rating from their historical
    sessions and, in practice, that rating is usually weak enough that
    their simulated win/podium probabilities come out negligible, but this
    is a simplification worth stating explicitly rather than assuming it
    away silently."""
    race_laps_df = _to_df(race_laps, ["session_id", "driver_id", "lap_number", "date_start", "lap_duration"])
    quali_laps_df = _to_df(qualifying_laps, ["session_id", "driver_id", "lap_number", "date_start", "lap_duration"])
    results_df = _to_df(
        session_results,
        ["session_id", "driver_id", "session_type", "date_start", "meeting_key", "position", "points", "dnf", "dns", "dsq"],
    )
    grid_df = pd.DataFrame(current_grid, columns=["driver_id", "constructor_id", "date_start"])

    race_pace = driver_session_pace(race_laps_df, agg="median", exclude_early_laps=2)
    quali_pace = driver_session_pace(quali_laps_df, agg="min")

    session_dates = results_df[["session_id", "date_start"]].drop_duplicates("session_id")
    race_pace = race_pace.merge(session_dates, on="session_id", how="left")
    quali_pace = quali_pace.merge(session_dates, on="session_id", how="left")

    as_of = pd.Timestamp.now(tz="UTC")
    if results_df["date_start"].notna().any():
        as_of = results_df["date_start"].max()
        if as_of.tzinfo is None:
            as_of = as_of.tz_localize("UTC")

    def localize(s: pd.Series) -> pd.Series:
        return pd.to_datetime(s, utc=True)

    field_sigma = None
    if not race_pace.empty:
        per_driver_sigma_all = race_pace.groupby("driver_id")["pace_ratio"].std()
        field_sigma = float(per_driver_sigma_all.dropna().mean()) if per_driver_sigma_all.notna().any() else 0.02

    race_results = results_df[results_df["session_type"] == "Race"]
    field_dnf_rate = float(race_results["dnf"].mean()) if not race_results.empty else 0.05

    rows = []
    excluded = []
    for _, grid_row in grid_df.iterrows():
        driver_id = grid_row["driver_id"]

        dr_race = race_pace[race_pace["driver_id"] == driver_id]
        dr_quali = quali_pace[quali_pace["driver_id"] == driver_id]

        if dr_race.empty:
            excluded.append({"driver_id": driver_id, "reason": "no completed race sessions"})
            continue

        race_rating = _recency_weighted_mean(dr_race["pace_ratio"], localize(dr_race["date_start"]), as_of)
        quali_rating = (
            _recency_weighted_mean(dr_quali["pace_ratio"], localize(dr_quali["date_start"]), as_of)
            if not dr_quali.empty
            else race_rating
        )
        rating = RACE_PACE_WEIGHT * race_rating + QUALIFYING_PACE_WEIGHT * quali_rating

        n_sessions = len(dr_race)
        raw_sigma = float(dr_race["pace_ratio"].std()) if n_sessions > 1 else None
        if raw_sigma is None or np.isnan(raw_sigma):
            sigma = field_sigma
        else:
            w = n_sessions / (n_sessions + SIGMA_SHRINKAGE_K)
            sigma = w * raw_sigma + (1 - w) * field_sigma

        driver_races = race_results[race_results["driver_id"] == driver_id]
        races_entered = len(driver_races)
        dnf_count = int(driver_races["dnf"].sum()) if races_entered else 0
        alpha = DNF_PRIOR_STRENGTH_RACES * field_dnf_rate
        beta = DNF_PRIOR_STRENGTH_RACES * (1 - field_dnf_rate)
        dnf_prob = (dnf_count + alpha) / (races_entered + alpha + beta)

        current_points = float(driver_races["points"].fillna(0).sum())

        rows.append(
            {
                "driver_id": driver_id,
                "constructor_id": grid_row["constructor_id"],
                "rating": rating,
                "sigma": sigma,
                "dnf_prob": dnf_prob,
                "races_entered": races_entered,
                "current_points": current_points,
            }
        )

    calibration = pd.DataFrame(rows)
    calibration.attrs["excluded"] = excluded
    return calibration


def simulate_remaining_season(
    calibration: pd.DataFrame,
    n_remaining_races: int,
    n_simulations: int = DEFAULT_N_SIMULATIONS,
    seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    """Returns one row per driver with championship + per-race probabilities.
    Deterministic for a given (calibration, n_remaining_races, seed)."""
    if calibration.empty or n_remaining_races <= 0:
        return pd.DataFrame(
            columns=[
                "driver_id",
                "expected_points",
                "expected_championship_position",
                "championship_win_probability",
                "championship_podium_probability",
                "race_win_probability",
                "race_podium_probability",
            ]
        )

    rng = np.random.default_rng(seed)
    drivers = calibration["driver_id"].to_numpy()
    n_drivers = len(drivers)
    ratings = calibration["rating"].to_numpy()
    sigmas = calibration["sigma"].to_numpy()
    dnf_probs = calibration["dnf_prob"].to_numpy()
    current_points = calibration["current_points"].to_numpy()

    total_points = np.tile(current_points, (n_simulations, 1))
    race_wins = np.zeros(n_drivers)
    race_podiums = np.zeros(n_drivers)
    n_race_draws = n_simulations * n_remaining_races

    for _race in range(n_remaining_races):
        noise = rng.normal(0.0, sigmas, size=(n_simulations, n_drivers))
        scores = ratings + noise
        dnf_draws = rng.random((n_simulations, n_drivers)) < dnf_probs

        order = np.argsort(scores, axis=1)
        for sim in range(n_simulations):
            finish_rank = 0
            for driver_idx in order[sim]:
                if dnf_draws[sim, driver_idx]:
                    continue
                finish_rank += 1
                if finish_rank == 1:
                    race_wins[driver_idx] += 1
                if finish_rank <= 3:
                    race_podiums[driver_idx] += 1
                points = POINTS_TABLE.get(finish_rank, 0)
                if points:
                    total_points[sim, driver_idx] += points
                if finish_rank >= 10:
                    break

    ranks = (-total_points).argsort(axis=1).argsort(axis=1) + 1  # 1 = championship leader
    champion_wins = (ranks == 1).sum(axis=0)
    champion_podiums = (ranks <= 3).sum(axis=0)

    out = pd.DataFrame(
        {
            "driver_id": drivers,
            "expected_points": total_points.mean(axis=0),
            "expected_championship_position": ranks.mean(axis=0),
            "championship_win_probability": champion_wins / n_simulations,
            "championship_podium_probability": champion_podiums / n_simulations,
            "race_win_probability": race_wins / n_race_draws,
            "race_podium_probability": race_podiums / n_race_draws,
        }
    )
    return out


def save_calibration_artifact(
    calibration: pd.DataFrame,
    *,
    n_remaining_races: int,
    n_simulations: int,
    seed: int,
    result: pd.DataFrame,
) -> Path:
    run_id = date.today().isoformat()
    out_dir = ARTIFACTS_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "n_simulations": n_simulations,
        "n_remaining_races": n_remaining_races,
        "race_pace_weight": RACE_PACE_WEIGHT,
        "qualifying_pace_weight": QUALIFYING_PACE_WEIGHT,
        "recency_half_life_days": RECENCY_HALF_LIFE_DAYS,
        "excluded_drivers": calibration.attrs.get("excluded", []),
        "calibration": calibration.drop(columns=[c for c in ["constructor_id"] if c in calibration.columns]).to_dict(
            orient="records"
        ),
        "result": result.to_dict(orient="records"),
    }
    (out_dir / "simulator_calibration.json").write_text(json.dumps(payload, indent=2, default=str))
    return out_dir
