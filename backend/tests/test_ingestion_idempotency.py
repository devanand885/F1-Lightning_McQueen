from app.integrations.openf1.schemas import DriverEntryRecord, LapRecord
from app.models.circuit import Circuit
from app.models.driver import Driver
from app.models.lap import Lap
from app.models.meeting import Meeting
from app.models.season import Season
from app.models.session import Session as SessionModel
from app.models.session_entry import SessionEntry
from ingestion.services import entries, laps


class _FakeClient:
    """Stands in for OpenF1Client so ingestion services can be exercised
    without hitting the network."""

    def __init__(self, drivers, laps_):
        self._drivers = drivers
        self._laps = laps_

    def get_drivers(self, session_key):
        return self._drivers

    def get_laps(self, session_key):
        return self._laps


def _make_session(db_session) -> SessionModel:
    season = Season(year=2099)
    db_session.add(season)
    db_session.flush()

    circuit = Circuit(circuit_key=999_999, circuit_short_name="Test")
    db_session.add(circuit)
    db_session.flush()

    meeting = Meeting(meeting_key=999_999, meeting_name="Test GP", season_id=season.id, circuit_id=circuit.id)
    db_session.add(meeting)
    db_session.flush()

    session = SessionModel(session_key=999_999, meeting_id=meeting.id, session_name="Race", session_type="Race")
    db_session.add(session)
    db_session.flush()
    return session


def test_entries_and_laps_ingestion_is_idempotent(db_session):
    session = _make_session(db_session)

    driver_record = DriverEntryRecord(
        session_key=session.session_key,
        driver_number=44,
        full_name="Test Driver",
        team_name="Test Team",
        team_colour="00FF00",
    )
    lap_record = LapRecord(session_key=session.session_key, driver_number=44, lap_number=1, lap_duration=90.5)
    client = _FakeClient(drivers=[(driver_record, {})], laps_=[(lap_record, {"lap_number": 1})])

    driver_id_by_number = entries.ingest_entries(client, db_session, session.session_key, session.id)
    laps.ingest_laps(client, db_session, session.session_key, session.id, driver_id_by_number)
    db_session.commit()

    assert db_session.query(Driver).filter(Driver.driver_number == 44).count() == 1
    assert db_session.query(SessionEntry).count() == 1
    lap = db_session.query(Lap).one()
    assert lap.lap_duration == 90.5

    # Re-running with an updated lap_duration should update in place, not
    # create a second row for the same (session, driver, lap_number).
    updated_lap = LapRecord(session_key=session.session_key, driver_number=44, lap_number=1, lap_duration=91.0)
    client_rerun = _FakeClient(drivers=[(driver_record, {})], laps_=[(updated_lap, {"lap_number": 1})])

    driver_id_by_number = entries.ingest_entries(client_rerun, db_session, session.session_key, session.id)
    laps.ingest_laps(client_rerun, db_session, session.session_key, session.id, driver_id_by_number)
    db_session.commit()

    assert db_session.query(Driver).count() == 1
    assert db_session.query(SessionEntry).count() == 1
    laps_after = db_session.query(Lap).all()
    assert len(laps_after) == 1
    assert laps_after[0].lap_duration == 91.0
