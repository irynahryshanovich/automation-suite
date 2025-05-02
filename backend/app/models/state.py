from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class StateModel(Base):
    """SQLAlchemy model for state entries"""
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    target = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), nullable=False)
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# Pydantic models for API
class StateBase(BaseModel):
    """Base model for state entries"""
    target: str
    status: str

class StateCreate(StateBase):
    """Model for creating state entries"""
    pass

class State(StateBase):
    """Model for state entries from database"""
    id: int
    last_updated: datetime

    class Config:
        orm_mode = True

class StateUpdate(BaseModel):
    """Model for updating state entries"""
    status: str