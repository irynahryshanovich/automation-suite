import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.log import LogModel, Base as LogBase
from app.models.state import StateModel, Base as StateBase

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables and default data"""
    # Create tables
    LogBase.metadata.create_all(bind=engine)
    StateBase.metadata.create_all(bind=engine)

    # Add default states if they don't exist
    db = SessionLocal()
    try:
        # Check if states already exist
        existing_states = db.query(StateModel).count()
        if existing_states == 0:
            default_states = [
                StateModel(target="Twitter", status="active", last_updated=datetime.now()),
                StateModel(target="Facebook", status="active", last_updated=datetime.now()),
                StateModel(target="Instagram", status="active", last_updated=datetime.now()),
            ]
            db.add_all(default_states)
            db.commit()
    finally:
        db.close()

# Log functions
def add_log(source: str, data: Dict[str, Any], action_taken: str = "None") -> int:
    """Add a log entry to the database"""
    db = SessionLocal()
    try:
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
    finally:
        db.close()

def get_logs(limit: int = 50, source: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get logs from database with optional filtering"""
    db = SessionLocal()
    try:
        query = db.query(LogModel).order_by(LogModel.id.desc())

        if source:
            query = query.filter(LogModel.source == source)

        logs = query.limit(limit).all()
        # Convert SQLAlchemy models to dictionaries
        result = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "source": log.source,
                "data": log.data,  # This is already a JSON string
                "action_taken": log.action_taken
            }
            result.append(log_dict)

        return result
    finally:
        db.close()

# State functions
def get_states() -> List[Dict[str, Any]]:
    """Get current states of all targets"""
    db = SessionLocal()
    try:
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
    finally:
        db.close()

def update_state(target: str, status: str) -> bool:
    """Update the state of a target"""
    db = SessionLocal()
    try:
        state = db.query(StateModel).filter(StateModel.target == target).first()
        if not state:
            return False

        state.status = status
        state.last_updated = datetime.now()
        db.commit()
        return True
    finally:
        db.close()

def delete_all_logs():
    """Clear all logs from the database"""
    db = SessionLocal()
    try:
        # Delete all log entries using SQLAlchemy
        db.query(LogModel).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error clearing logs: {e}")
        return False
    finally:
        db.close()