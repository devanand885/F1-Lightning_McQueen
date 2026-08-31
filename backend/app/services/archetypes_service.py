from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session as DbSession

from app.repositories import analytics as repo
from ml.features.driver_features import CLUSTERING_FEATURES, build_driver_feature_table
from ml.inference.archetypes import load_latest


def get_archetypes(db: DbSession) -> dict:
    model = load_latest()
    if model is None:
        return {
            "available": False,
            "reason": "No trained archetype model available. Run ml/models/train_archetypes.py.",
            "clusters": [],
            "excluded_drivers": [],
        }

    drivers = {d["driver_id"]: d["full_name"] for d in repo.drivers_all(db)}
    table = build_driver_feature_table(
        race_laps=repo.usable_laps(db, None, "Race"),
        qualifying_laps=repo.usable_laps(db, None, "Qualifying"),
        stints=repo.race_stints(db, None),
        race_positions_earliest=repo.race_positions_earliest(db, None),
        qualifying_positions=repo.qualifying_classified_positions(db, None),
        weather=repo.race_weather(db, None),
        entries=repo.race_weekend_entries(db, None),
        session_results=repo.session_results_all(db, None),
    )
    table["full_name"] = table["driver_id"].map(drivers)

    eligible = table[table["driver_id"].isin(model.metadata["driver_ids_used"])].copy()
    # Defensive, not just a test nicety: if the live data for a driver the
    # artifact was trained on has since changed shape (or, as this project's
    # own test found, an id coincidentally matches in an unrelated
    # database), any row missing a clustering feature must not reach
    # model.assign() - StandardScaler/KMeans/PCA propagate NaN silently,
    # which would surface as a non-JSON-serializable NaN in the response.
    eligible = eligible.dropna(subset=CLUSTERING_FEATURES)
    assigned = model.assign(eligible) if not eligible.empty else eligible

    clusters = []
    for cluster_id in sorted(assigned["cluster"].unique()) if not assigned.empty else []:
        members = assigned[assigned["cluster"] == cluster_id]
        centroid = model.metadata["cluster_centroids"].get(str(cluster_id), model.metadata["cluster_centroids"].get(cluster_id, {}))
        clusters.append(
            {
                "cluster": int(cluster_id),
                "name": model.cluster_name(cluster_id),
                "size": int(len(members)),
                "centroid": centroid,
                "drivers": [
                    {
                        "driver_id": int(r["driver_id"]),
                        "full_name": r["full_name"],
                        "pca_x": float(r["pca_x"]),
                        "pca_y": float(r["pca_y"]),
                    }
                    for _, r in members.iterrows()
                ],
            }
        )

    ineligible = table[~table["driver_id"].isin(model.metadata["driver_ids_used"])]
    excluded = [
        {
            "driver_id": int(r["driver_id"]),
            "full_name": r["full_name"],
            "race_sessions": int(r["race_sessions"]),
            "usable_race_laps": int(r["usable_race_laps"]),
            "race_stints": int(r["race_stints"]),
        }
        for _, r in ineligible.iterrows()
    ]

    return {
        "available": True,
        "reason": None,
        "run_id": model.run_id,
        "features": model.features,
        "silhouette": model.metadata["silhouette"],
        "pca_explained_variance_ratio": model.metadata["pca_explained_variance_ratio"],
        "n_eligible": model.metadata["n_eligible"],
        "n_population": model.metadata["n_population"],
        "clusters": clusters,
        "excluded_drivers": excluded,
    }
