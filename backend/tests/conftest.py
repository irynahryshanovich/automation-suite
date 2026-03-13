import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.models.base import Base
from app.models.state import StateModel

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


@pytest.fixture(autouse=True)
def test_db():
    import app.database as db_module

    original_engine = db_module.engine
    original_session_local = db_module.SessionLocal

    db_module.engine = test_engine
    db_module.SessionLocal = TestSessionLocal

    Base.metadata.create_all(bind=test_engine)

    session = TestSessionLocal()
    default_states = [
        StateModel(target="Twitter", status="active"),
        StateModel(target="Facebook", status="active"),
        StateModel(target="Instagram", status="active"),
    ]
    session.add_all(default_states)
    session.commit()
    session.close()

    yield

    Base.metadata.drop_all(bind=test_engine)

    db_module.engine = original_engine
    db_module.SessionLocal = original_session_local


@pytest.fixture
def test_client():
    from app.main import app

    with TestClient(app) as client:
        yield client
