"""API smoke tests for the DS/ML endpoints. The seeded fixture (from
test_api.py's pattern) is intentionally tiny - far below archetype/analytics
eligibility thresholds - so these tests mainly confirm the endpoints
respond correctly with an honest "not eligible / not available" shape
rather than crashing, plus the plain data-shape endpoints (circuit type,
strategy insights) which work regardless of sample size.
"""

from datetime import datetime, timedelta

import pytest

from app.models.circuit import Circuit
from app.models.constructor import Constructor
from app.models.driver import Driver
from app.models.lap import Lap
from app.models.meeting import Meeting
from app.models.pit_stop import PitStop
from app.models.season import Season
from app.models.session import Session as SessionModel
from app.models.session_entry import SessionEntry
from app.models.session_result import SessionResult
from app.models.stint import Stint


@pytest.fixture()
def seeded(db_session):
    season = Season(year=2099)
    db_session.add(season)
    db_session.flush()

    circuit = Circuit(circuit_key=555_001, circuit_short_name="Test Circuit", location="Testville", country_name="Testland")
    db_session.add(circuit)
    db_session.flush()

    meeting = Meeting(
        meeting_key=555_001, meeting_name="Test Grand Prix", season_id=season.id, circuit_id=circuit.id, date_start=datetime(2099, 5, 1)
    )
    db_session.add(meeting)
    db_session.flush()

    race = SessionModel(
        session_key=555_001,
        meeting_id=meeting.id,
        session_name="Race",
        session_type="Race",
        date_start=datetime(2099, 5, 3),
    )
    db_session.add(race)
    db_session.flush()

    alpha = Driver(driver_number=1, full_name="Driver Alpha", name_acronym="ALP")
    beta = Driver(driver_number=2, full_name="Driver Beta", name_acronym="BET")
    db_session.add_all([alpha, beta])
    db_session.flush()

    team_a = Constructor(name="Team A", team_colour="FF0000")
    db_session.add(team_a)
    db_session.flush()

    db_session.add_all(
        [
            SessionEntry(session_id=race.id, driver_id=alpha.id, constructor_id=team_a.id),
            SessionEntry(session_id=race.id, driver_id=beta.id, constructor_id=team_a.id),
        ]
    )
    db_session.add_all(
        [
            SessionResult(session_id=race.id, driver_id=alpha.id, position=1, points=25.0, dnf=False, dns=False, dsq=False),
            SessionResult(session_id=race.id, driver_id=beta.id, position=2, points=18.0, dnf=False, dns=False, dsq=False),
        ]
    )
    db_session.add(Lap(session_id=race.id, driver_id=alpha.id, lap_number=1, lap_duration=90.5, date_start=datetime(2099, 5, 3), st_speed=310.0))
    db_session.add(Stint(session_id=race.id, driver_id=alpha.id, stint_number=1, lap_start=1, lap_end=1, compound="MEDIUM"))
    db_session.add(
        PitStop(session_id=race.id, driver_id=alpha.id, lap_number=1, date=datetime(2099, 5, 3) + timedelta(minutes=10), pit_duration=2.3)
    )
    db_session.commit()

    return {"season": 2099, "alpha": alpha.driver_number, "beta": beta.driver_number, "circuit_id": circuit.id}


def test_archetypes_endpoint_responds(client, seeded):
    resp = client.get("/api/v1/archetypes")
    assert resp.status_code == 200
    body = resp.json()
    assert "clusters" in body
    assert "excluded_drivers" in body


def test_driver_analytics_reports_ineligible_with_reason(client, seeded):
    resp = client.get(f"/api/v1/drivers/{seeded['alpha']}/analytics")
    assert resp.status_code == 200
    body = resp.json()
    assert body["eligible"] is False
    assert body["eligibility_reason"] is not None
    assert body["race_sessions"] == 1


def test_driver_analytics_404_for_unknown_driver(client, seeded):
    resp = client.get("/api/v1/drivers/999999/analytics")
    assert resp.status_code == 404


def test_simulator_endpoint_responds(client, seeded):
    resp = client.get("/api/v1/simulator/championship", params={"season": seeded["season"], "n_simulations": 200})
    assert resp.status_code == 200
    body = resp.json()
    assert body["season"] == seeded["season"]
    assert "available" in body


def test_strategy_insights_endpoint_responds(client, seeded):
    resp = client.get("/api/v1/strategy/insights")
    assert resp.status_code == 200
    body = resp.json()
    assert "insights" in body
    for insight in body["insights"]:
        assert insight["sample_size"] >= 1


def test_circuit_detail_includes_circuit_type(client, seeded):
    resp = client.get(f"/api/v1/circuits/{seeded['circuit_id']}")
    assert resp.status_code == 200
    body = resp.json()
    assert "circuit_type" in body


def test_compare_drivers_includes_analytics_block(client, seeded):
    resp = client.get("/api/v1/compare/drivers", params={"ids": f"{seeded['alpha']},{seeded['beta']}", "season": seeded["season"]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["analytics"] is not None
    keys = {m["key"] for m in body["analytics"]}
    assert "archetype" in keys
