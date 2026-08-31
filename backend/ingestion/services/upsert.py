"""Generic idempotent bulk upsert used by every ingestion service.

Every ORM model this is used with declares a unique constraint matching
`index_elements`, so re-running ingestion updates existing rows in place
instead of duplicating them.
"""

from typing import Any

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session


# Postgres caps bound parameters at 65535 per statement; stay comfortably
# under that regardless of how many columns a row has.
_MAX_PARAMS_PER_STATEMENT = 60_000


def upsert(db: Session, model: type, rows: list[dict[str, Any]], index_elements: list[str]) -> int:
    if not rows:
        return 0

    # Postgres rejects ON CONFLICT DO UPDATE if the same statement proposes
    # two rows with the same conflict key (CardinalityViolation) - OpenF1
    # occasionally emits duplicate samples for the same (session, driver,
    # timestamp). Keep the last occurrence per key, matching upsert's own
    # "last write wins" semantics.
    deduped: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        deduped[tuple(row[col] for col in index_elements)] = row
    rows = list(deduped.values())

    excluded_columns = {"id", "created_at", "updated_at", *index_elements}
    update_columns_template = {
        col.name for col in model.__table__.columns if col.name not in excluded_columns
    }

    params_per_row = len(rows[0])
    batch_size = max(1, _MAX_PARAMS_PER_STATEMENT // params_per_row)

    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        stmt = insert(model).values(batch)
        update_columns = {name: getattr(stmt.excluded, name) for name in update_columns_template}
        if "updated_at" in model.__table__.columns:
            update_columns["updated_at"] = func.now()
        stmt = stmt.on_conflict_do_update(index_elements=index_elements, set_=update_columns)
        db.execute(stmt)

    return len(rows)
