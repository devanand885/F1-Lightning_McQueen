"""Builds the "Analytical" comparison block: teammate-relative pace,
consistency, tyre degradation, and archetype label for a set of compared
drivers - kept visually/structurally separate from the existing raw-results
comparison (points/wins/podiums/avg finish/DNF rate), which stays exactly
as it was. Driver-level only; constructor comparisons don't get this block
since the underlying features (teammate-relative pace, archetypes) are
defined per-driver.
"""

from __future__ import annotations

from sqlalchemy.orm import Session as DbSession

from app.services import driver_analytics_service

_METRICS: list[tuple[str, str, str | None]] = [
    ("race_pace_teammate_relative", "Race Pace vs Teammate", "ratio delta"),
    ("qualifying_pace_teammate_relative", "Qualifying Pace vs Teammate", "ratio delta"),
    ("degradation_slope", "Tyre Degradation", "s/lap"),
    ("consistency_cv", "Consistency (lower = steadier)", "CV"),
]


def build_driver_analytics_block(db: DbSession, driver_numbers: list[int]) -> list[dict]:
    per_driver = [driver_analytics_service.get_driver_analytics(db, number) for number in driver_numbers]

    metrics = []
    for key, label, unit in _METRICS:
        metrics.append(
            {
                "key": key,
                "label": label,
                "unit": unit,
                "values": [d.get(key) if d else None for d in per_driver],
            }
        )

    archetype_labels = []
    for d in per_driver:
        if not d or not d.get("archetype") or not d["archetype"].get("assigned"):
            archetype_labels.append(None)
        else:
            archetype_labels.append(d["archetype"]["archetype_name"])
    metrics.append({"key": "archetype", "label": "Archetype", "unit": None, "values": archetype_labels})

    return metrics
