from fastapi import APIRouter, Query, HTTPException, Request
from typing import List, Dict, Optional

from app.models.state import StateUpdate
from app.database import get_logs, get_states, update_state, delete_all_logs
from app.services.automation_service import perform_automation
from app.scheduler import modify_job_cadence
from app.config import settings

router = APIRouter(tags=["api"])

@router.get("/logs", response_model=List[Dict])
async def read_logs(
    limit: int = Query(50, ge=1, le=100),
    source: Optional[str] = None
):
    """Get logs with optional filtering"""
    return get_logs(limit=limit, source=source)

@router.get("/state", response_model=List[Dict])
async def read_state():
    """Get current state of all targets"""
    return get_states()

@router.put("/state/{target}", response_model=Dict)
async def update_target_state(target: str, state_update: StateUpdate):
    """Update state of a specific target"""
    if target not in settings.SOCIAL_TARGETS:
        raise HTTPException(status_code=404, detail="Target not found")

    success = update_state(target, state_update.status)
    if not success:
        raise HTTPException(status_code=404, detail="Target not found")

    return {"target": target, "status": state_update.status}

@router.post("/run", response_model=Dict)
async def run_automation(request: Request):
    """Manually trigger automation job with optional city"""
    try:
        data = await request.json()
        city = data.get("city")
        print(f"Received city parameter: {city}")  # Add logging
    except Exception as e:
        print(f"Error parsing request: {str(e)}")
        city = None

    result = perform_automation(city)
    return result

@router.put("/cadence", response_model=Dict)
async def update_cadence(minutes: int = Query(..., ge=5, le=1440)):
    """Update automation job cadence"""
    return modify_job_cadence(minutes)

@router.get("/settings", response_model=Dict)
async def get_settings():
    """Get current application settings"""
    return {
        "app_name": settings.APP_NAME,
        "cadence": settings.AUTOMATION_CADENCE,
        "city": settings.DEFAULT_CITY,
        "targets": settings.SOCIAL_TARGETS
    }

@router.delete("/logs", response_model=Dict)
async def clear_logs():
    """Clear all logs from the database"""
    success = delete_all_logs()
    if success:
        return {"message": "All logs cleared successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to clear logs")
