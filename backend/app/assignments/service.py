from app.assignments.store import ASSIGNMENT_EVENTS
from app.assignments.models import assignment_event

def log_assignment(**kwargs):
    ASSIGNMENT_EVENTS.append(assignment_event(**kwargs))
