import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import *  # noqa: F401,F403  (populate Base.metadata)

TEST_DATABASE_URL = "postgresql+psycopg://f1lm:f1lm@localhost:5433/f1lm_test"

_engine = create_engine(TEST_DATABASE_URL, future=True)
_TestSessionLocal = sessionmaker(bind=_engine, future=True)


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.create_all(_engine)
    yield
    Base.metadata.drop_all(_engine)


@pytest.fixture()
def db_session():
    """A real session against the test database. Ingestion code commits as
    it goes, so isolation between tests is done by truncating every table
    after the test rather than relying on a rolled-back transaction."""
    session = _TestSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        with _engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                conn.execute(table.delete())


@pytest.fixture()
def client(db_session):
    """A FastAPI TestClient whose `get_db` dependency is overridden to reuse
    the same test-database session as `db_session`, so a test can seed data
    with `db_session` and then hit the API and see it."""
    from fastapi.testclient import TestClient

    from app.db.session import get_db
    from app.main import app

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
