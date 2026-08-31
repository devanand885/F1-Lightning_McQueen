from sqlalchemy.orm import Session as DbSession

from app.repositories import constructors as constructors_repo
from app.repositories import drivers as drivers_repo
from app.repositories.seasons import resolve_season

# The only metrics with a legitimate, unambiguous source in stored data.
_METRICS: list[tuple[str, str, str | None]] = [
    ("points", "Points", None),
    ("wins", "Wins", None),
    ("podiums", "Podiums", None),
    ("avg_finish", "Average Finish", "position"),
    ("dnf_rate", "DNF Rate", "%"),
]


def compare_drivers(db: DbSession, driver_numbers: list[int], year: int | None) -> dict:
    season = resolve_season(db, year)
    entities = []
    values_by_metric: dict[str, list] = {key: [] for key, _, _ in _METRICS}

    for number in driver_numbers:
        detail = drivers_repo.get_driver(db, number, season.year)
        if detail is None:
            raise ValueError(f"No driver with number {number}")
        entities.append({"id": number, "label": detail["full_name"], "colour": detail["team_colour"]})
        for key, _, _ in _METRICS:
            values_by_metric[key].append(detail[key])

    return {
        "entity_type": "driver",
        "season": season.year,
        "entities": entities,
        "metrics": [{"key": key, "label": label, "unit": unit, "values": values_by_metric[key]} for key, label, unit in _METRICS],
    }


def compare_constructors(db: DbSession, constructor_ids: list[int], year: int | None) -> dict:
    season = resolve_season(db, year)
    entities = []
    values_by_metric: dict[str, list] = {key: [] for key, _, _ in _METRICS}

    for constructor_id in constructor_ids:
        detail = constructors_repo.get_constructor(db, constructor_id, season.year)
        if detail is None:
            raise ValueError(f"No constructor with id {constructor_id}")
        entities.append({"id": constructor_id, "label": detail["name"], "colour": detail["team_colour"]})
        for key, _, _ in _METRICS:
            values_by_metric[key].append(detail[key])

    return {
        "entity_type": "constructor",
        "season": season.year,
        "entities": entities,
        "metrics": [{"key": key, "label": label, "unit": unit, "values": values_by_metric[key]} for key, label, unit in _METRICS],
    }
