"""Pure aggregation logic shared by the drivers and constructors repositories.

Kept dependency-free (no DB, no FastAPI) so it's directly unit-testable and
so it's obvious, by inspection, that the only things computed here are plain
sums/counts/averages over stored `session_results` rows - nothing invented.
"""

from collections.abc import Iterable


def aggregate_results(
    rows: Iterable[tuple[int, str, int | None, float | None, bool | None]],
) -> dict[int, dict[str, float | int | None]]:
    """rows: (entity_id, session_type, position, points, dnf) tuples, one per
    session_result row, where entity_id is a driver_id or constructor_id.

    Wins/podiums/avg_finish/dnf_rate are computed over session_type == "Race"
    only; points are summed across every session (OpenF1 only reports
    nonzero points on points-scoring sessions, so summing everything is
    correct for both race and sprint points).
    """
    buckets: dict[int, dict] = {}

    for entity_id, session_type, position, points, dnf in rows:
        bucket = buckets.setdefault(
            entity_id,
            {"points": 0.0, "wins": 0, "podiums": 0, "race_positions": [], "race_count": 0, "race_dnf": 0},
        )
        bucket["points"] += points or 0.0

        if session_type == "Race":
            bucket["race_count"] += 1
            if position == 1:
                bucket["wins"] += 1
            if position is not None and position <= 3:
                bucket["podiums"] += 1
            if position is not None:
                bucket["race_positions"].append(position)
            if dnf:
                bucket["race_dnf"] += 1

    result: dict[int, dict[str, float | int | None]] = {}
    for entity_id, bucket in buckets.items():
        race_positions = bucket["race_positions"]
        race_count = bucket["race_count"]
        result[entity_id] = {
            "points": bucket["points"],
            "wins": bucket["wins"],
            "podiums": bucket["podiums"],
            "avg_finish": (sum(race_positions) / len(race_positions)) if race_positions else None,
            "dnf_rate": (bucket["race_dnf"] / race_count) if race_count else None,
        }
    return result
