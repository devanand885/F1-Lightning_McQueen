"""Trains the driver-archetype KMeans model and writes a versioned artifact.

Standalone script - pulls raw rows via the backend's repository layer (the
same functions the live API uses), builds the feature table via
ml.features.driver_features, fits StandardScaler + KMeans on the eligible
population, and writes scaler.joblib / kmeans.joblib / pca.joblib /
metadata.json to ml/models/artifacts/<YYYY-MM-DD>/.

Run from the backend venv (ml/ is installed editable into it):

    backend/venv/Scripts/python.exe ml/models/train_archetypes.py

k is chosen by sweeping K_MIN..K_MAX and picking the highest silhouette
score - not fixed in advance. Cluster *names* are deliberately NOT decided
here: metadata.json records each cluster's centroid in standardized units
(z-scores) per feature, and ml/inference/archetypes.py's ARCHETYPE_NAMES
maps cluster index -> human name for a specific artifact version, assigned
by a human after inspecting the real centroids this script prints - not
guessed in advance and not auto-generated narrative text.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

import joblib
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import SessionLocal  # noqa: E402
from app.repositories import analytics as repo  # noqa: E402

from ml.features.driver_features import CLUSTERING_FEATURES, build_driver_feature_table  # noqa: E402

K_MIN = 2
K_MAX = 6
RANDOM_SEED = 42

# With a small eligible population (n in the low 20s), pure silhouette-max
# selection tends to carve off singleton clusters around outlier drivers
# (observed: k=6 beat k=3 by a small silhouette margin only by isolating
# three drivers into clusters of 1 each). A cluster of one driver isn't an
# archetype, it's an outlier flag - so k is chosen by silhouette *among the
# k values that keep every cluster at or above this size*, not by raw
# silhouette alone.
MIN_CLUSTER_SIZE = 2

ARTIFACTS_ROOT = Path(__file__).resolve().parent / "artifacts"


def pull_feature_table():
    db = SessionLocal()
    try:
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
        return table
    finally:
        db.close()


def sweep_k(x_scaled: np.ndarray, k_min: int, k_max: int, seed: int) -> list[dict]:
    n_samples = x_scaled.shape[0]
    results = []
    for k in range(k_min, min(k_max, n_samples - 1) + 1):
        model = KMeans(n_clusters=k, n_init=10, random_state=seed)
        labels = model.fit_predict(x_scaled)
        score = silhouette_score(x_scaled, labels)
        min_cluster_size = int(np.bincount(labels).min())
        results.append({"k": k, "silhouette": score, "inertia": model.inertia_, "min_cluster_size": min_cluster_size})
    return results


def main() -> None:
    table = pull_feature_table()
    eligible = table[table["eligible"]].reset_index(drop=True)

    missing = eligible[CLUSTERING_FEATURES].isna().any(axis=1)
    if missing.any():
        dropped = eligible.loc[missing, "full_name"].tolist()
        print(f"Dropping {missing.sum()} eligible driver(s) with missing clustering features: {dropped}")
        eligible = eligible.loc[~missing].reset_index(drop=True)

    n = len(eligible)
    print(f"Eligible drivers used for clustering: {n} of {len(table)} total in the population")
    if n < K_MIN + 1:
        raise SystemExit(f"Only {n} eligible drivers - need at least {K_MIN + 1} to fit >= {K_MIN} clusters")

    x = eligible[CLUSTERING_FEATURES].to_numpy(dtype=float)
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)

    sweep = sweep_k(x_scaled, K_MIN, K_MAX, RANDOM_SEED)
    for r in sweep:
        print(
            f"  k={r['k']}: silhouette={r['silhouette']:.4f} inertia={r['inertia']:.2f} "
            f"min_cluster_size={r['min_cluster_size']}"
        )
    candidates = [r for r in sweep if r["min_cluster_size"] >= MIN_CLUSTER_SIZE]
    if not candidates:
        print(f"No k in the sweep keeps every cluster >= {MIN_CLUSTER_SIZE}; falling back to raw silhouette-max")
        candidates = sweep
    best = max(candidates, key=lambda r: r["silhouette"])
    k = best["k"]
    print(f"Selected k={k} (silhouette={best['silhouette']:.4f}, min_cluster_size={best['min_cluster_size']})")

    kmeans = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_SEED)
    labels = kmeans.fit_predict(x_scaled)

    pca = PCA(n_components=2, random_state=RANDOM_SEED)
    coords = pca.fit_transform(x_scaled)

    print("\nCluster centroids (standardized units, i.e. z-scores vs the eligible population):")
    centroids_by_cluster = {}
    cluster_sizes = {}
    for cluster_id in range(k):
        mask = labels == cluster_id
        cluster_sizes[cluster_id] = int(mask.sum())
        centroid = {feat: round(float(v), 3) for feat, v in zip(CLUSTERING_FEATURES, kmeans.cluster_centers_[cluster_id])}
        centroids_by_cluster[cluster_id] = centroid
        members = eligible.loc[mask, "full_name"].tolist()
        print(f"  cluster {cluster_id} (n={mask.sum()}): {centroid}")
        print(f"    members: {members}")

    run_id = date.today().isoformat()
    out_dir = ARTIFACTS_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(scaler, out_dir / "scaler.joblib")
    joblib.dump(kmeans, out_dir / "kmeans.joblib")
    joblib.dump(pca, out_dir / "pca.joblib")

    metadata = {
        "run_id": run_id,
        "trained_at": datetime.now().isoformat(),
        "random_seed": RANDOM_SEED,
        "features": CLUSTERING_FEATURES,
        "k": k,
        "k_sweep": sweep,
        "min_cluster_size_constraint": MIN_CLUSTER_SIZE,
        "silhouette": best["silhouette"],
        "pca_explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "cluster_sizes": cluster_sizes,
        "cluster_centroids": centroids_by_cluster,
        "driver_ids_used": eligible["driver_id"].tolist(),
        "n_eligible": n,
        "n_population": len(table),
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print(f"\nArtifact written to {out_dir}")


if __name__ == "__main__":
    main()
