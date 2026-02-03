from datetime import datetime
from typing import Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime
from pydantic import BaseModel

from app.models.base import Base

class LogModel(Base):
    """SQLAlchemy model for log entries"""
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    source = Column(String(50), nullable=False)
    data = Column(Text, nullable=False)
    action_taken = Column(String(255), default="None")

# Pydantic models for API
class LogBase(BaseModel):
    """Base model for log entries"""
    source: str
    data: Dict[str, Any]
    action_taken: str = "None"

class LogCreate(LogBase):
    """Model for creating log entries"""
    pass

class Log(LogBase):
    """Model for log entries from database"""
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True