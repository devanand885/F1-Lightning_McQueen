from __future__ import annotations

from sqlalchemy.orm import Session as DbSession

from app.models.driver import Driver
from app.repositories import analytics as repo
from ml.inference import simulator as sim


def get_championship_simulation(
    db: DbSession, year: int, n_simulations: int = sim.DEFAULT_N_SIMULATIONS, seed: int = sim.DEFAULT_SEED
) -> dict:
    all_races = repo.all_race_sessions(db, year)
    completed_ids = {r["session_id"] for r in repo.session_results_all(db, [year]) if r["session_type"] == "Race"}
    remaining = [r for r in all_races if r["session_id"] not in completed_ids]
    n_remaining = len(remaining)

    if n_remaining == 0:
        return {
            "available": False,
            "reason": f"Season {year} has no remaining races to simulate - all {len(all_races)} are complete.",
            "season": year,
            "drivers": [],
        }

    current_grid = repo.current_driver_constructors(db)
    calibration = sim.build_calibration(
        race_laps=repo.usable_laps(db, None, "Race"),
        qualifying_laps=repo.usable_laps(db, None, "Qualifying"),
        session_results=repo.session_results_all(db, None),
        current_grid=current_grid,
    )
    if calibration.empty:
        return {
            "available": False,
            "reason": "No drivers on the current grid have enough completed race data to calibrate a simulation.",
            "season": year,
            "drivers": [],
        }

    result = sim.simulate_remaining_season(calibration, n_remaining, n_simulations=n_simulations, seed=seed)
    sim.save_calibration_artifact(
        calibration, n_remaining_races=n_remaining, n_simulations=n_simulations, seed=seed, result=result
    )

    driver_ids = result["driver_id"].tolist()
    driver_rows = db.query(Driver).filter(Driver.id.in_(driver_ids)).all()
    names = {d.id: d.full_name for d in driver_rows}
    numbers = {d.id: d.driver_number for d in driver_rows}
    result = result.merge(calibration[["driver_id", "current_points"]], on="driver_id")
    result["full_name"] = result["driver_id"].map(names)
    result["driver_number"] = result["driver_id"].map(numbers)
    result = result.sort_values("expected_points", ascending=False)

    return {
        "available": True,
        "reason": None,
        "season": year,
        "n_remaining_races": n_remaining,
        "n_completed_races": len(all_races) - n_remaining,
        "n_simulations": n_simulations,
        "seed": seed,
        "drivers": [
            {
                "driver_number": int(r["driver_number"]),
                "full_name": r["full_name"],
                "current_points": float(r["current_points"]),
                "expected_points": float(r["expected_points"]),
                "expected_championship_position": float(r["expected_championship_position"]),
                "championship_win_probability": float(r["championship_win_probability"]),
                "championship_podium_probability": float(r["championship_podium_probability"]),
                "race_win_probability": float(r["race_win_probability"]),
                "race_podium_probability": float(r["race_podium_probability"]),
            }
            for _, r in result.iterrows()
        ],
    }
