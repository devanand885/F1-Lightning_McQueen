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
    team_b = Constructor(name="Team B", team_colour="0000FF")
    db_session.add_all([team_a, team_b])
    db_session.flush()

    db_session.add_all(
        [
            SessionEntry(session_id=race.id, driver_id=alpha.id, constructor_id=team_a.id),
            SessionEntry(session_id=race.id, driver_id=beta.id, constructor_id=team_b.id),
        ]
    )
    db_session.add_all(
        [
            SessionResult(session_id=race.id, driver_id=alpha.id, position=1, points=25.0, dnf=False, dns=False, dsq=False),
            SessionResult(session_id=race.id, driver_id=beta.id, position=2, points=18.0, dnf=False, dns=False, dsq=False),
        ]
    )
    db_session.add(Lap(session_id=race.id, driver_id=alpha.id, lap_number=1, lap_duration=90.5, date_start=datetime(2099, 5, 3)))
    db_session.add(
        PitStop(session_id=race.id, driver_id=alpha.id, lap_number=1, date=datetime(2099, 5, 3) + timedelta(minutes=10), pit_duration=2.3)
    )
    db_session.commit()

    return {"season": 2099, "session_key": race.session_key, "alpha": alpha.driver_number, "beta": beta.driver_number, "team_a": team_a.id, "team_b": team_b.id, "circuit_id": circuit.id}


def test_list_and_get_driver(client, seeded):
    resp = client.get("/api/v1/drivers", params={"season": seeded["season"]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 2
    assert body["items"][0]["position"] == 1
    assert body["items"][0]["points"] == 25.0

    resp = client.get(f"/api/v1/drivers/{seeded['alpha']}", params={"season": seeded["season"]})
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Driver Alpha"


def test_driver_sessions_results_laps_pit_stops(client, seeded):
    assert client.get(f"/api/v1/drivers/{seeded['alpha']}/sessions", params={"season": seeded["season"]}).json()["count"] == 1
    assert client.get(f"/api/v1/drivers/{seeded['alpha']}/results", params={"season": seeded["season"]}).json()["count"] == 1

    laps = client.get(f"/api/v1/drivers/{seeded['alpha']}/laps", params={"session_key": seeded["session_key"]}).json()
    assert laps["count"] == 1
    assert laps["items"][0]["lap_duration"] == 90.5

    pit_stops = client.get(f"/api/v1/drivers/{seeded['alpha']}/pit-stops", params={"season": seeded["season"]}).json()
    assert pit_stops["count"] == 1


def test_unknown_driver_number_is_404(client, seeded):
    resp = client.get("/api/v1/drivers/999999", params={"season": seeded["season"]})
    assert resp.status_code == 404


def test_list_and_get_constructor(client, seeded):
    resp = client.get("/api/v1/constructors", params={"season": seeded["season"]})
    assert resp.status_code == 200
    assert resp.json()["count"] == 2

    resp = client.get(f"/api/v1/constructors/{seeded['team_a']}", params={"season": seeded["season"]})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Team A"
    assert resp.json()["points"] == 25.0


def test_constructor_results_drivers_pit_stops(client, seeded):
    assert client.get(f"/api/v1/constructors/{seeded['team_a']}/results", params={"season": seeded["season"]}).json()["count"] == 1
    drivers = client.get(f"/api/v1/constructors/{seeded['team_a']}/drivers", params={"season": seeded["season"]}).json()
    assert drivers["count"] == 1
    assert drivers["items"][0]["full_name"] == "Driver Alpha"
    assert client.get(f"/api/v1/constructors/{seeded['team_a']}/pit-stops", params={"season": seeded["season"]}).json()["count"] == 1


def test_circuits_list_and_detail(client, seeded):
    resp = client.get("/api/v1/circuits", params={"season": seeded["season"]})
    assert resp.status_code == 200
    assert resp.json()["count"] == 1

    resp = client.get(f"/api/v1/circuits/{seeded['circuit_id']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["circuit_short_name"] == "Test Circuit"
    assert len(body["meetings"]) == 1
    assert "Driver Alpha" in body["drivers"]


def test_circuits_location_filter_matches_city_or_country(client, seeded):
    # location="Testville" (city) and country_name="Testland" - the filter
    # should match either, not just the city field.
    resp = client.get("/api/v1/circuits", params={"location": "Testville"})
    assert resp.json()["count"] == 1

    resp = client.get("/api/v1/circuits", params={"location": "Testland"})
    assert resp.json()["count"] == 1

    resp = client.get("/api/v1/circuits", params={"location": "Nowhereville"})
    assert resp.json()["count"] == 0


def test_dashboard_endpoints(client, seeded):
    assert client.get("/api/v1/dashboard/overview", params={"season": seeded["season"]}).status_code == 200
    assert client.get("/api/v1/dashboard/standings/drivers", params={"season": seeded["season"]}).json()["count"] == 2
    assert client.get("/api/v1/dashboard/standings/constructors", params={"season": seeded["season"]}).json()["count"] == 2
    assert client.get("/api/v1/dashboard/calendar", params={"season": seeded["season"]}).json()["count"] == 1


def test_search_finds_seeded_entities(client, seeded):
    resp = client.get("/api/v1/search", params={"q": "Driver Alpha"})
    assert resp.status_code == 200
    types = {r["type"] for r in resp.json()["items"]}
    assert "driver" in types


def test_compare_drivers_and_constructors(client, seeded):
    resp = client.get("/api/v1/compare/drivers", params={"ids": f"{seeded['alpha']},{seeded['beta']}", "season": seeded["season"]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["entity_type"] == "driver"
    assert len(body["entities"]) == 2
    points_metric = next(m for m in body["metrics"] if m["key"] == "points")
    assert points_metric["values"] == [25.0, 18.0]

    resp = client.get("/api/v1/compare/constructors", params={"ids": f"{seeded['team_a']},{seeded['team_b']}", "season": seeded["season"]})
    assert resp.status_code == 200
    assert resp.json()["entity_type"] == "constructor"


def test_compare_requires_at_least_two_ids(client, seeded):
    resp = client.get("/api/v1/compare/drivers", params={"ids": str(seeded["alpha"]), "season": seeded["season"]})
    assert resp.status_code == 400


def test_export_json_and_csv(client, seeded):
    resp = client.get("/api/v1/export/drivers", params={"season": seeded["season"], "format": "json"})
    assert resp.status_code == 200
    assert resp.json()["count"] == 2

    resp = client.get("/api/v1/export/race_results", params={"season": seeded["season"], "format": "csv"})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "driver_full_name" in resp.text
    assert "Driver Alpha" in resp.text


def test_export_unknown_dataset_is_400(client, seeded):
    resp = client.get("/api/v1/export/not_a_real_dataset", params={"season": seeded["season"]})
    assert resp.status_code == 400
