from app.assignments.store import ASSIGNMENT_EVENTS

def history_for_incident(incident_id: int):
    return [e for e in ASSIGNMENT_EVENTS if e["incident_id"] == incident_id]

def history_for_subject(assignment_type: str, subject_id: int):
    return [
        e for e in ASSIGNMENT_EVENTS
        if e["assignment_type"] == assignment_type and e["subject_id"] == subject_id
    ]

def all_history():
    return ASSIGNMENT_EVENTS
