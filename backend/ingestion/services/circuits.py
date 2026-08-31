from sqlalchemy.orm import Session as DbSession

from app.integrations.openf1.schemas import MeetingRecord
from app.models.circuit import Circuit


def upsert_circuit(db: DbSession, record: MeetingRecord) -> Circuit:
    circuit = db.query(Circuit).filter(Circuit.circuit_key == record.circuit_key).one_or_none()
    if circuit is None:
        circuit = Circuit(circuit_key=record.circuit_key)
        db.add(circuit)

    circuit.circuit_short_name = record.circuit_short_name
    circuit.location = record.location
    circuit.country_name = record.country_name
    circuit.country_code = record.country_code
    db.flush()
    return circuit
