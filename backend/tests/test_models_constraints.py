import pytest
from sqlalchemy.exc import IntegrityError

from app.models.driver import Driver
from ingestion.services.seasons import upsert_season


def test_driver_full_name_unique_constraint_is_enforced(db_session):
    # full_name, not driver_number, is the identity key - see the comment on
    # the Driver model for why (pre-season testing reassigns car numbers).
    db_session.add(Driver(driver_number=1, full_name="Driver One"))
    db_session.commit()

    db_session.add(Driver(driver_number=2, full_name="Driver One"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_upsert_season_is_idempotent(db_session):
    first = upsert_season(db_session, 2025)
    db_session.commit()

    second = upsert_season(db_session, 2025)
    db_session.commit()

    assert first.id == second.id
    assert db_session.query(type(first)).filter(type(first).year == 2025).count() == 1
