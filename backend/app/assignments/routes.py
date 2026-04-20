from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.auth.roles import require_role
from app.assignments.compute import (
    history_for_incident,
    history_for_subject,
    all_history
)

router = APIRouter(prefix="/assignments", tags=["Assignment History"])

@router.get("/")
def get_all_history(admin=Depends(require_role("ADMIN"))):
    return all_history()

@router.get("/incident/{incident_id}")
def get_incident_history(incident_id: int, user=Depends(get_current_user)):
    return history_for_incident(incident_id)

@router.get("/volunteer/{volunteer_id}")
def get_volunteer_history(volunteer_id: int, user=Depends(get_current_user)):
    return history_for_subject("VOLUNTEER", volunteer_id)

@router.get("/resource/{resource_id}")
def get_resource_history(resource_id: int, user=Depends(get_current_user)):
    return history_for_subject("RESOURCE", resource_id)
