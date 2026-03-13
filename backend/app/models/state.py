from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Integer, String, DateTime
from pydantic import BaseModel, ConfigDict, Field

from app.models.base import Base


class SocialTarget(str, Enum):
    TWITTER = "Twitter"
    FACEBOOK = "Facebook"
    INSTAGRAM = "Instagram"


class TargetStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"


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
    target: SocialTarget
    status: TargetStatus

class StateCreate(StateBase):
    """Model for creating state entries"""
    pass

class State(StateBase):
    """Model for state entries from database"""
    id: int
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)

class StateUpdate(BaseModel):
    """Model for updating state entries"""
    status: TargetStatus


class AutomationRequest(BaseModel):
    city: Optional[str] = Field(default=None, strict=True)


class AutomationResponse(BaseModel):
    timestamp: str
    weather: Dict[str, Any]
    sports: Dict[str, Any]
    actions: List[str]
    states: List[Dict[str, Any]]
    city_warning: Optional[str] = None


class SettingsResponse(BaseModel):
    app_name: str
    cadence: int
    city: str
    available_cities: List[str]
    targets: List[str]


class CadenceResponse(BaseModel):
    message: str


class MessageResponse(BaseModel):
    message: str