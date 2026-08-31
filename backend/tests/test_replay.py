import math
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from app.services import replay_cache, replay_service
from app.services.replay_transform import _circuit_outline, _dedupe_location, build_replay_payload


def test_dedupe_location_filters_placeholder_points_and_dedupes():
    rows = [
        {"date": "2025-01-01T00:00:00.000000+00:00", "driver_number": 1, "x": 0, "y": 0, "z": 0},
        {"date": "2025-01-01T00:00:01.000000+00:00", "driver_number": 1, "x": 100, "y": 200, "z": 0},
        # chunk overlap duplicate of the row above
        {"date": "2025-01-01T00:00:01.000000+00:00", "driver_number": 1, "x": 100, "y": 200, "z": 0},
    ]
    out = _dedupe_location(rows)
    assert len(out) == 1
    assert out.iloc[0]["x"] == 100


def test_build_replay_payload_unavailable_when_no_location():
    payload = build_replay_payload(
        session_key=1,
        meeting_name="Test GP",
        season=2099,
        date_from=pd.Timestamp("2099-01-01T00:00:00Z"),
        date_to=pd.Timestamp("2099-01-01T00:01:00Z"),
        location_rows=[],
        car_data_rows=[],
        laps_rows=[],
        positions_rows=[],
        entries=[],
    )
    assert payload["available"] is False
    assert "telemetry" in payload["reason"].lower()


def _iso(base: datetime, seconds: float) -> str:
    return (base + timedelta(seconds=seconds)).isoformat()


def test_build_replay_payload_has_no_nan_and_synchronizes_all_drivers():
    base = datetime(2099, 1, 1, tzinfo=timezone.utc)
    location_rows = []
    car_data_rows = []
    for driver_number in (1, 2):
        for i in range(20):
            t = i * 0.5
            location_rows.append(
                {"date": _iso(base, t), "driver_number": driver_number, "x": 100 + i * 5, "y": 200 + i * 3, "z": 0}
            )
            car_data_rows.append(
                {
                    "date": _iso(base, t),
                    "driver_number": driver_number,
                    "speed": 100 + i,
                    "throttle": 80,
                    "brake": 0,
                    "n_gear": 5,
                    "rpm": 10000,
                    "drs": 0,
                }
            )
    laps_rows = [
        {"driver_number": 1, "lap_number": 1, "date_start": base, "lap_duration": 9.5},
        {"driver_number": 2, "lap_number": 1, "date_start": base, "lap_duration": 9.6},
    ]
    positions_rows = [
        {"driver_number": 1, "date": base, "position": 1},
        {"driver_number": 2, "date": base, "position": 2},
    ]
    entries = [
        {"driver_number": 1, "full_name": "Driver One", "name_acronym": "ONE", "constructor_name": "Team A", "team_colour": "FF0000"},
        {"driver_number": 2, "full_name": "Driver Two", "name_acronym": "TWO", "constructor_name": "Team B", "team_colour": "0000FF"},
    ]

    payload = build_replay_payload(
        session_key=1,
        meeting_name="Test GP",
        season=2099,
        date_from=base,
        date_to=base + timedelta(seconds=9.5),
        location_rows=location_rows,
        car_data_rows=car_data_rows,
        laps_rows=laps_rows,
        positions_rows=positions_rows,
        entries=entries,
    )

    assert payload["available"] is True
    assert set(payload["drivers"].keys()) == {"1", "2"}
    assert len(payload["timestamps"]) == payload["frame_count"]

    for driver in payload["drivers"].values():
        assert len(driver["x"]) == payload["frame_count"]
        assert len(driver["speed"]) == payload["frame_count"]
        for field in ("x", "y", "speed", "throttle", "brake", "gear", "drs", "lap", "position"):
            for v in driver[field]:
                assert not (isinstance(v, float) and math.isnan(v)), f"NaN leaked into {field}"

    driver_one = payload["drivers"]["1"]
    assert driver_one["lap"][0] == 1
    assert driver_one["position"][0] == 1


def test_circuit_outline_falls_back_to_most_covered_driver_when_fastest_lap_too_sparse():
    base = datetime(2099, 1, 1, tzinfo=timezone.utc)
    # driver 1 has the fastest lap but almost no location points in it
    location_rows = [{"date": base, "driver_number": 1, "x": 0.0, "y": 0.0, "z": 0}]
    for i in range(30):
        location_rows.append(
            {"date": base + timedelta(seconds=i), "driver_number": 2, "x": float(i), "y": float(i * 2), "z": 0}
        )
    location = _dedupe_location(location_rows)
    laps = pd.DataFrame(
        [
            {"driver_number": 1, "lap_number": 1, "date_start": base, "lap_duration": 1.0},
            {"driver_number": 2, "lap_number": 1, "date_start": base, "lap_duration": 30.0},
        ]
    )
    bounds = {"min_x": 0.0, "max_x": 30.0, "min_y": 0.0, "max_y": 60.0, "span": 60.0}

    outline = _circuit_outline(location, laps, bounds)
    assert len(outline) >= 20


def test_cache_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(replay_cache, "CACHE_DIR", tmp_path)
    assert replay_cache.load(12345) is None

    payload = {"available": True, "session_key": 12345, "drivers": {}}
    replay_cache.save(12345, payload)

    loaded = replay_cache.load(12345)
    assert loaded == payload


def test_cache_returns_none_for_corrupt_file(tmp_path, monkeypatch):
    monkeypatch.setattr(replay_cache, "CACHE_DIR", tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    bad_file = tmp_path / f"999.v{replay_cache.SCHEMA_VERSION}.json.gz"
    bad_file.write_bytes(b"not a gzip file")

    assert replay_cache.load(999) is None


class _FakeOpenF1Client:
    def __init__(self, location_rows=None, car_data_rows=None):
        self.location_rows = location_rows or []
        self.car_data_rows = car_data_rows or []
        self.calls = 0

    def get_location(self, session_key, date_from, date_to):
        self.calls += 1
        return self.location_rows

    def get_car_data(self, session_key, date_from, date_to):
        return self.car_data_rows

    def close(self):
        pass


def test_get_replay_returns_unavailable_for_non_race_session(db_session):
    from app.models.circuit import Circuit
    from app.models.meeting import Meeting
    from app.models.season import Season
    from app.models.session import Session as SessionModel

    season = Season(year=2099)
    db_session.add(season)
    db_session.flush()
    circuit = Circuit(circuit_key=1, circuit_short_name="Test")
    db_session.add(circuit)
    db_session.flush()
    meeting = Meeting(meeting_key=1, meeting_name="Test GP", season_id=season.id, circuit_id=circuit.id)
    db_session.add(meeting)
    db_session.flush()
    quali = SessionModel(session_key=555, meeting_id=meeting.id, session_name="Qualifying", session_type="Qualifying")
    db_session.add(quali)
    db_session.commit()

    result = replay_service.get_replay(db_session, 555, openf1_client=_FakeOpenF1Client())
    assert result["available"] is False
    assert "Race" in result["reason"]


def test_get_replay_unknown_session_key(db_session):
    result = replay_service.get_replay(db_session, 999999, openf1_client=_FakeOpenF1Client())
    assert result["available"] is False


def test_get_replay_uses_cache_on_second_call(db_session, tmp_path, monkeypatch):
    from app.models.circuit import Circuit
    from app.models.driver import Driver
    from app.models.constructor import Constructor
    from app.models.lap import Lap
    from app.models.meeting import Meeting
    from app.models.season import Season
    from app.models.session import Session as SessionModel
    from app.models.session_entry import SessionEntry
    from app.models.session_result import SessionResult

    monkeypatch.setattr(replay_cache, "CACHE_DIR", tmp_path)

    season = Season(year=2099)
    db_session.add(season)
    db_session.flush()
    circuit = Circuit(circuit_key=1, circuit_short_name="Test")
    db_session.add(circuit)
    db_session.flush()
    meeting = Meeting(meeting_key=1, meeting_name="Test GP", season_id=season.id, circuit_id=circuit.id)
    db_session.add(meeting)
    db_session.flush()
    race = SessionModel(session_key=777, meeting_id=meeting.id, session_name="Race", session_type="Race")
    db_session.add(race)
    db_session.flush()

    driver = Driver(driver_number=1, full_name="Driver One")
    db_session.add(driver)
    db_session.flush()
    team = Constructor(name="Team A", team_colour="FF0000")
    db_session.add(team)
    db_session.flush()
    db_session.add(SessionEntry(session_id=race.id, driver_id=driver.id, constructor_id=team.id, team_colour="FF0000"))
    db_session.add(SessionResult(session_id=race.id, driver_id=driver.id, position=1, points=25.0, dnf=False, dns=False, dsq=False))

    base = datetime(2099, 1, 1, tzinfo=timezone.utc)
    db_session.add(Lap(session_id=race.id, driver_id=driver.id, lap_number=1, date_start=base, lap_duration=9.5))
    db_session.commit()

    location_rows = [{"date": base.isoformat(), "driver_number": 1, "x": 100, "y": 200, "z": 0}]
    car_data_rows = [{"date": base.isoformat(), "driver_number": 1, "speed": 300, "throttle": 100, "brake": 0, "n_gear": 8, "rpm": 11000, "drs": 0}]
    fake_client = _FakeOpenF1Client(location_rows, car_data_rows)

    first = replay_service.get_replay(db_session, 777, openf1_client=fake_client)
    assert first["available"] is True
    assert fake_client.calls >= 1

    calls_before = fake_client.calls
    second = replay_service.get_replay(db_session, 777, openf1_client=fake_client)
    assert second["available"] is True
    assert fake_client.calls == calls_before, "second call should be served from cache, not refetched"


def test_replay_races_endpoint_lists_completed_races(client, db_session):
    from app.models.circuit import Circuit
    from app.models.driver import Driver
    from app.models.constructor import Constructor
    from app.models.meeting import Meeting
    from app.models.season import Season
    from app.models.session import Session as SessionModel
    from app.models.session_entry import SessionEntry
    from app.models.session_result import SessionResult

    season = Season(year=2099)
    db_session.add(season)
    db_session.flush()
    circuit = Circuit(circuit_key=1, circuit_short_name="Test Circuit")
    db_session.add(circuit)
    db_session.flush()
    meeting = Meeting(meeting_key=1, meeting_name="Test GP", season_id=season.id, circuit_id=circuit.id)
    db_session.add(meeting)
    db_session.flush()
    race = SessionModel(session_key=888, meeting_id=meeting.id, session_name="Race", session_type="Race")
    quali = SessionModel(session_key=889, meeting_id=meeting.id, session_name="Qualifying", session_type="Qualifying")
    # OpenF1 tags a Sprint session's session_type as "Race" too (confirmed
    # against the real ingested 2025 Chinese GP) - session_name is the only
    # field that distinguishes it. Without filtering on session_name too,
    # this would show up in the picker as an indistinguishable duplicate of
    # the real Race entry for the same meeting.
    sprint = SessionModel(session_key=890, meeting_id=meeting.id, session_name="Sprint", session_type="Race")
    db_session.add_all([race, quali, sprint])
    db_session.flush()

    driver = Driver(driver_number=1, full_name="Driver One")
    db_session.add(driver)
    db_session.flush()
    team = Constructor(name="Team A", team_colour="FF0000")
    db_session.add(team)
    db_session.flush()
    db_session.add(SessionEntry(session_id=race.id, driver_id=driver.id, constructor_id=team.id))
    db_session.add(SessionResult(session_id=race.id, driver_id=driver.id, position=1, points=25.0, dnf=False, dns=False, dsq=False))
    db_session.commit()

    resp = client.get("/api/v1/replay/races")
    assert resp.status_code == 200
    body = resp.json()
    session_keys = [item["session_key"] for item in body["items"]]
    assert 888 in session_keys
    assert 889 not in session_keys, "Qualifying (non-Race) sessions must not be offered for replay"
    assert 890 not in session_keys, "Sprint sessions (session_type='Race' but session_name='Sprint') must be excluded"


def test_replay_endpoint_reports_unavailable_through_full_http_stack(client, db_session, monkeypatch, tmp_path):
    from app.services import replay_cache

    monkeypatch.setattr(replay_cache, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(replay_service, "OpenF1Client", lambda: _FakeOpenF1Client())

    resp = client.get("/api/v1/replay/424242")
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is False
    assert body["reason"]
