import json
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.base import Base
from app.models.log import LogModel
from app.models.state import StateModel

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_context():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def with_db_session(func):
    """Decorator for database sessions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with get_db_context() as db:
            return func(db, *args, **kwargs)
    return wrapper


def init_db():
    """Initialize database tables and default data"""
    Base.metadata.create_all(bind=engine)

    with get_db_context() as db:
        existing_states = db.query(StateModel).count()
        if existing_states == 0:
            default_states = [
                StateModel(target="Twitter", status="active", last_updated=datetime.now()),
                StateModel(target="Facebook", status="active", last_updated=datetime.now()),
                StateModel(target="Instagram", status="active", last_updated=datetime.now()),
            ]
            db.add_all(default_states)
            db.commit()


@with_db_session
def add_log(db, source: str, data: Dict[str, Any], action_taken: str = "None") -> int:
    """Add a log entry to the database"""
    log = LogModel(
        source=source,
        data=json.dumps(data),
        action_taken=action_taken,
        timestamp=datetime.now()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log.id


@with_db_session
def get_logs(db, limit: int = 50, source: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get logs from database with optional filtering"""
    query = db.query(LogModel).order_by(LogModel.id.desc())

    if source:
        query = query.filter(LogModel.source == source)

    logs = query.limit(limit).all()
    # Convert SQLAlchemy models to dictionaries
    result = []
    for log in logs:
        try:
            data = json.loads(log.data)
        except json.JSONDecodeError:
            data = log.data

        log_dict = {
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "source": log.source,
            "data": data,
            "action_taken": log.action_taken
        }
        result.append(log_dict)

    return result


@with_db_session
def get_states(db) -> List[Dict[str, Any]]:
    """Get current states of all targets"""
    states = db.query(StateModel).order_by(StateModel.target).all()

    # Convert SQLAlchemy models to dictionaries
    result = []
    for state in states:
        state_dict = {
            "id": state.id,
            "target": state.target,
            "status": state.status,
            "last_updated": state.last_updated.isoformat()
        }
        result.append(state_dict)

    return result


@with_db_session
def update_state(db, target: str, status: str) -> bool:
    """Update the state of a target"""
    state = db.query(StateModel).filter(StateModel.target == target).first()
    if not state:
        return False

    state.status = status
    state.last_updated = datetime.now()
    db.commit()
    return True


@with_db_session
def delete_all_logs(db):
    """Clear all logs from the database"""
    try:
        db.query(LogModel).delete()
        db.commit()
        return True
    except SQLAlchemyError as error:
        db.rollback()
        print(f"Error clearing logs: {error}")
        return False
