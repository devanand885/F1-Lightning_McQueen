from app.models.circuit import Circuit
from ingestion.services import upsert as upsert_module
from ingestion.services.upsert import upsert


def test_upsert_is_idempotent_and_updates_existing_rows(db_session):
    rows = [
        {
            "circuit_key": 999,
            "circuit_short_name": "Test Circuit",
            "location": "Nowhere",
            "country_name": "Testland",
            "country_code": "TST",
        }
    ]

    upsert(db_session, Circuit, rows, ["circuit_key"])
    db_session.commit()
    assert db_session.query(Circuit).filter(Circuit.circuit_key == 999).count() == 1

    # Re-running with the same key updates the row rather than duplicating it.
    rows[0]["location"] = "Updated Location"
    upsert(db_session, Circuit, rows, ["circuit_key"])
    db_session.commit()

    circuits = db_session.query(Circuit).filter(Circuit.circuit_key == 999).all()
    assert len(circuits) == 1
    assert circuits[0].location == "Updated Location"


def test_upsert_batches_rows_exceeding_the_per_statement_param_cap(db_session, monkeypatch):
    # Force a tiny per-statement cap so a handful of rows already needs
    # several batches - exercises the same chunking path that broke on a
    # real 19k-row /intervals response during manual testing.
    monkeypatch.setattr(upsert_module, "_MAX_PARAMS_PER_STATEMENT", 10)

    rows = [
        {
            "circuit_key": 2000 + i,
            "circuit_short_name": f"C{i}",
            "location": None,
            "country_name": None,
            "country_code": None,
        }
        for i in range(7)
    ]

    count = upsert(db_session, Circuit, rows, ["circuit_key"])
    db_session.commit()

    assert count == 7
    assert db_session.query(Circuit).filter(Circuit.circuit_key >= 2000).count() == 7


def test_upsert_with_no_rows_is_a_noop(db_session):
    assert upsert(db_session, Circuit, [], ["circuit_key"]) == 0


def test_upsert_dedupes_same_batch_conflicts(db_session):
    # Postgres raises CardinalityViolation if a single ON CONFLICT DO UPDATE
    # statement proposes two rows with the same conflict key - OpenF1 does
    # this in practice (duplicate samples at the same timestamp). The last
    # occurrence should win rather than the statement failing outright.
    rows = [
        {
            "circuit_key": 3000,
            "circuit_short_name": "First",
            "location": None,
            "country_name": None,
            "country_code": None,
        },
        {
            "circuit_key": 3000,
            "circuit_short_name": "Second",
            "location": None,
            "country_name": None,
            "country_code": None,
        },
    ]

    upsert(db_session, Circuit, rows, ["circuit_key"])
    db_session.commit()

    circuits = db_session.query(Circuit).filter(Circuit.circuit_key == 3000).all()
    assert len(circuits) == 1
    assert circuits[0].circuit_short_name == "Second"
