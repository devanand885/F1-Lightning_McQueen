"""Loads a trained archetype artifact and assigns clusters to current data.

Cluster *names* are assigned by a human after inspecting a specific
artifact run's real centroids (printed by ml/models/train_archetypes.py and
cross-checked against a constructor cross-tab to confirm the clusters
aren't just rediscovering which team is fastest - see the training run
notes below) - not decided in advance and not auto-generated narrative
text. ARCHETYPE_NAMES is keyed by run_id so a retrain that produces a
materially different clustering doesn't silently inherit stale names; an
unrecognized run_id falls back to "Cluster N" rather than guessing.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

ARTIFACTS_ROOT = Path(__file__).resolve().parents[1] / "models" / "artifacts"

# Assigned 2026-08-25 after inspecting that run's real centroids (k=3,
# n=22 eligible drivers, silhouette=0.1808) and confirming via a
# cluster x constructor cross-tab that no cluster exceeds 20% share from
# any single constructor (well under the 70% confounding-concern threshold
# from the plan) - i.e. these groups reflect teammate-relative performance
# patterns, not "which car is fastest".
#   cluster 0 (n=10): race pace clearly beats teammate (z=-0.49), below-
#     average tyre degradation (z=-0.77), above-average consistency
#     (z=-0.35), and *relatively* stronger in the race than in qualifying
#     versus their teammate.
#   cluster 1 (n=10): the mirror image - race pace behind teammate
#     (z=+0.77), above-average tyre degradation (z=+0.75), and relatively
#     stronger in qualifying than in the race versus their teammate.
#   cluster 2 (n=2): race pace far ahead of teammate (z=-1.40) but far less
#     consistent than the field (z=+2.60) - a small, distinct group of
#     drivers who win the race-pace comparison against their teammate but
#     with much higher lap-to-lap variance.
ARCHETYPE_NAMES: dict[str, dict[int, str]] = {
    "2026-08-25": {
        0: "Consistent Race Pace",
        1: "Qualifying-Leaning, Higher Degradation",
        2: "Fast but Inconsistent",
    },
}


def latest_artifact_dir() -> Path | None:
    if not ARTIFACTS_ROOT.exists():
        return None
    candidates = sorted((p for p in ARTIFACTS_ROOT.iterdir() if p.is_dir() and (p / "metadata.json").exists()))
    return candidates[-1] if candidates else None


class ArchetypeModel:
    def __init__(self, artifact_dir: Path):
        self.artifact_dir = artifact_dir
        self.metadata = json.loads((artifact_dir / "metadata.json").read_text())
        self.scaler = joblib.load(artifact_dir / "scaler.joblib")
        self.kmeans = joblib.load(artifact_dir / "kmeans.joblib")
        self.pca = joblib.load(artifact_dir / "pca.joblib")
        self.features: list[str] = self.metadata["features"]
        self.run_id: str = self.metadata["run_id"]

    def cluster_name(self, cluster_id: int) -> str:
        names = ARCHETYPE_NAMES.get(self.run_id, {})
        return names.get(cluster_id, f"Cluster {cluster_id}")

    def assign(self, eligible: pd.DataFrame) -> pd.DataFrame:
        """`eligible` must contain `driver_id` and every column in
        self.features. Returns a copy with `cluster`, `archetype_name`,
        `pca_x`, `pca_y` columns added."""
        out = eligible.copy()
        x = out[self.features].to_numpy(dtype=float)
        x_scaled = self.scaler.transform(x)
        out["cluster"] = self.kmeans.predict(x_scaled)
        out["archetype_name"] = out["cluster"].map(self.cluster_name)
        coords = self.pca.transform(x_scaled)
        out["pca_x"] = coords[:, 0]
        out["pca_y"] = coords[:, 1]
        return out


def load_latest() -> ArchetypeModel | None:
    artifact_dir = latest_artifact_dir()
    if artifact_dir is None:
        return None
    return ArchetypeModel(artifact_dir)
