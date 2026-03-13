from typing import List, Optional

from fastapi import APIRouter, Query, HTTPException

from app.models.log import Log
from app.models.state import (
    AutomationRequest,
    AutomationResponse,
    CadenceResponse,
    MessageResponse,
    SettingsResponse,
    SocialTarget,
    State,
    StateBase,
    StateUpdate,
)
from app.database import add_log, get_logs, get_states, update_state, delete_all_logs
from app.services.automation_service import perform_automation
from app.scheduler import modify_job_cadence
from app.config import settings

router = APIRouter(tags=["api"])


@router.get("/logs", response_model=List[Log])
async def read_logs(
    limit: int = Query(50, ge=1, le=100),
    source: Optional[str] = None
):
    """Get logs with optional filtering"""
    return get_logs(limit=limit, source=source)


@router.get("/state", response_model=List[State])
async def read_state():
    """Get current state of all targets"""
    return get_states()


@router.put("/state/{target}", response_model=StateBase)
async def update_target_state(target: SocialTarget, state_update: StateUpdate):
    """Update state of a specific target"""
    success = update_state(target.value, state_update.status.value)
    if not success:
        raise HTTPException(status_code=404, detail="Target not found")

    action_message = f"Manually set {target.value} to {state_update.status.value}"
    add_log("manual", {"target": target.value, "status": state_update.status.value}, action_message)

    return {"target": target, "status": state_update.status}


@router.post("/run", response_model=AutomationResponse)
async def run_automation(automation_request: AutomationRequest = None):
    """Manually trigger automation job with optional city"""
    city = automation_request.city if automation_request else None
    city_warning = None

    if city and city not in settings.CITY_COORDINATES:
        city_warning = f"Unknown city '{city}', using {settings.DEFAULT_CITY}"

    result = perform_automation(city, source="manual")
    result["city_warning"] = city_warning
    return result


@router.put("/cadence", response_model=CadenceResponse)
async def update_cadence(minutes: int = Query(..., ge=5, le=1440)):
    """Update automation job cadence"""
    return modify_job_cadence(minutes)


@router.get("/settings", response_model=SettingsResponse)
async def get_settings():
    """Get current application settings"""
    return {
        "app_name": settings.APP_NAME,
        "cadence": settings.AUTOMATION_CADENCE,
        "city": settings.DEFAULT_CITY,
        "available_cities": settings.AVAILABLE_CITIES,
        "targets": settings.SOCIAL_TARGETS
    }


@router.delete("/logs", response_model=MessageResponse)
async def clear_logs():
    """Clear all logs from the database"""
    success = delete_all_logs()
    if success:
        return {"message": "All logs cleared successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to clear logs")
