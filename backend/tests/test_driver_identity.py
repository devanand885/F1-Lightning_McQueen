"""Regression test for a real bug found during manual verification: OpenF1
reports non-standard car numbers during pre-season testing (a driver's real
season number gets swapped for a promotional one), and keying the `drivers`
table's identity by driver_number let a testing session silently overwrite
a different driver's name/team/headshot. See ingestion/services/entries.py.
"""

from app.integrations.openf1.schemas import DriverEntryRecord
from app.models.circuit import Circuit
from app.models.driver import Driver
from app.models.meeting import Meeting
from app.models.season import Season
from app.models.session import Session as SessionModel
from ingestion.services import entries


class _FakeClient:
    def __init__(self, drivers):
        self._drivers = drivers

    def get_drivers(self, session_key):
        return self._drivers


def _make_session(db_session, meeting_name: str, meeting_key: int, session_key: int) -> SessionModel:
    season = db_session.query(Season).filter(Season.year == 2099).one_or_none()
    if season is None:
        season = Season(year=2099)
        db_session.add(season)
        db_session.flush()

    circuit = Circuit(circuit_key=888_000 + meeting_key, circuit_short_name="Test")
    db_session.add(circuit)
    db_session.flush()

    meeting = Meeting(meeting_key=meeting_key, meeting_name=meeting_name, season_id=season.id, circuit_id=circuit.id)
    db_session.add(meeting)
    db_session.flush()

    session = SessionModel(session_key=session_key, meeting_id=meeting.id, session_name="Day 1", session_type="Practice")
    db_session.add(session)
    db_session.flush()
    return session


def test_testing_session_does_not_overwrite_an_existing_drivers_identity(db_session):
    race_session = _make_session(db_session, "Australian Grand Prix", meeting_key=777_001, session_key=888_001)
    verstappen = DriverEntryRecord(
        session_key=race_session.session_key,
        driver_number=1,
        full_name="Max VERSTAPPEN",
        team_name="Red Bull Racing",
        team_colour="3671C6",
    )
    entries.ingest_entries(_FakeClient([(verstappen, {})]), db_session, race_session.session_key, race_session.id)
    db_session.commit()

    testing_session = _make_session(db_session, "Pre-Season Testing", meeting_key=777_002, session_key=888_002)
    norris_wearing_number_1 = DriverEntryRecord(
        session_key=testing_session.session_key,
        driver_number=1,
        full_name="Lando NORRIS",
        team_name="McLaren",
        team_colour="F47600",
    )
    entries.ingest_entries(_FakeClient([(norris_wearing_number_1, {})]), db_session, testing_session.session_key, testing_session.id)
    db_session.commit()

    verstappen_row = db_session.query(Driver).filter(Driver.full_name == "Max VERSTAPPEN").one()
    assert verstappen_row.driver_number == 1
    assert verstappen_row.full_name == "Max VERSTAPPEN"

    norris_row = db_session.query(Driver).filter(Driver.full_name == "Lando NORRIS").one_or_none()
    assert norris_row is not None
    assert norris_row.id != verstappen_row.id

    assert db_session.query(Driver).count() == 2
