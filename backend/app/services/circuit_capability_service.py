from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session as DbSession

from app.repositories import analytics as repo
from app.repositories import circuits as circuits_repo
from ml.features.circuit_features import build_circuit_feature_table


def _none_if_nan(value) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def get_circuit_with_capability(db: DbSession, circuit_id: int) -> dict | None:
    circuit = circuits_repo.get_circuit(db, circuit_id)
    if circuit is None:
        return None

    table = build_circuit_feature_table(
        race_laps=repo.circuit_race_laps(db, None), race_stints=repo.circuit_race_stints(db, None)
    )
    row = table[table["circuit_id"] == circuit_id] if not table.empty else table
    if row.empty:
        circuit["circuit_type"] = None
        circuit["mean_st_speed"] = None
        circuit["mean_field_cov"] = None
        circuit["mean_stints_per_driver"] = None
    else:
        r = row.iloc[0]
        # mean_field_cov in particular can be NaN for a circuit with only a
        # single usable lap in every session so far (stdev of one value is
        # undefined) - a real, if rare, early-data-coverage case, not just a
        # test artifact.
        circuit["circuit_type"] = str(r["circuit_type"]) if pd.notna(r["circuit_type"]) else None
        circuit["mean_st_speed"] = _none_if_nan(r["mean_st_speed"])
        circuit["mean_field_cov"] = _none_if_nan(r["mean_field_cov"])
        circuit["mean_stints_per_driver"] = _none_if_nan(r["mean_stints_per_driver"])

    return circuit
