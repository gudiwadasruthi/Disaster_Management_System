from pydantic import BaseModel
from datetime import datetime
from app.incidents.models import IncidentStatus

class IncidentCreate(BaseModel):
    title: str
    description: str
    latitude: float
    longitude: float

class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    latitude: float
    longitude: float
    status: IncidentStatus
    created_at: datetime

    class Config:
        orm_mode = True
