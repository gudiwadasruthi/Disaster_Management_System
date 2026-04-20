from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.roles import require_role
from app.users.models import User
from app.volunteers.models import Volunteer
from app.volunteers.schemas import VolunteerCreate, VolunteerResponse
from app.assignments.service import log_assignment
from app.analytics.store import VOLUNTEERS

router = APIRouter(prefix="/volunteers", tags=["Volunteers"])

# Volunteer registers
@router.post("/", response_model=VolunteerResponse)
def register_volunteer(
    data: VolunteerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.role != "VOLUNTEER":
        raise HTTPException(status_code=403, detail="Only volunteers allowed")

    volunteer = Volunteer(
        user_id=user.id,
        skill=data.skill
    )

    db.add(volunteer)
    db.commit()
    db.refresh(volunteer)

    # Analytics hook
    volunteer_dict = {
        "id": volunteer.id,
        "user_id": volunteer.user_id,
        "skill": volunteer.skill,
        "available": volunteer.is_available,
    }
    VOLUNTEERS.append(volunteer_dict)

    return volunteer

# Admin assigns volunteer
@router.put("/{volunteer_id}/assign/{incident_id}")
def assign_volunteer(
    volunteer_id: int,
    incident_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("ADMIN"))
):
    volunteer = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()

    if not volunteer or not volunteer.is_available:
        raise HTTPException(status_code=404, detail="Volunteer not available")

    volunteer.is_available = False
    
    from app.incidents.models import Incident
    from app.incidents.schemas import IncidentStatus
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if incident and incident.status in [IncidentStatus.REPORTED, IncidentStatus.VERIFIED]:
        incident.status = IncidentStatus.IN_PROGRESS

    db.commit()

    # Analytics hook
    for vol in VOLUNTEERS:
        if vol["id"] == volunteer_id:
            vol["available"] = False
            break

    log_assignment(
        assignment_type="VOLUNTEER",
        action="ASSIGNED",
        incident_id=incident_id,
        subject_id=volunteer_id,
        admin_id=admin.id,
        reason="Primary responder"
    )

    return {"message": "Volunteer assigned successfully"}

# Admin releases volunteer
@router.put("/{volunteer_id}/release/{incident_id}")
def release_volunteer(
    volunteer_id: int,
    incident_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("ADMIN"))
):
    volunteer = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()

    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")

    volunteer.is_available = True
    db.commit()

    # Analytics hook
    for vol in VOLUNTEERS:
        if vol["id"] == volunteer_id:
            vol["available"] = True
            break
    
    log_assignment(
        assignment_type="VOLUNTEER",
        action="RELEASED",
        incident_id=incident_id,
        subject_id=volunteer_id,
        admin_id=admin.id,
        reason="Task completed"
    )

    return {"message": "Volunteer released successfully"}


# View all volunteers
@router.get("/")
def list_volunteers(
    available: bool | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db)
):
    from app.users.models import User
    query = db.query(Volunteer, User).join(User, Volunteer.user_id == User.id)
    if available is not None:
        query = query.filter(Volunteer.is_available == available)
    
    results = query.offset((page - 1) * limit).limit(limit).all()
    
    response = []
    for vol, user in results:
        name_parts = user.full_name.split(" ", 1) if user.full_name else [""]
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        response.append({
            "id": vol.id,
            "user_id": vol.user_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "city": user.city,
            "skill": getattr(vol.skill, 'value', vol.skill) if hasattr(vol, 'skill') else None,
            "experience_years": vol.experience_years,
            "availability": getattr(vol.availability, 'value', vol.availability) if hasattr(vol, 'availability') else None,
            "vehicle": vol.vehicle_availability,
            "vehicle_type": getattr(vol.vehicle_type, 'value', vol.vehicle_type) if hasattr(vol, 'vehicle_type') else None,
            "organization": vol.organization,
            "is_available": vol.is_available,
            "assignments_completed": 0, 
            "rating": None,
            "joined_at": "2024-01-01T00:00:00Z"
        })
    return response
