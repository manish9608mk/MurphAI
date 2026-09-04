OPEN = "open"
ASSIGNED = "assigned"
IN_PROGRESS = "in_progress"
COMPLETED = "completed"
CANCELLED = "cancelled"


ALLOWED_TRANSITIONS = {
    OPEN: {
        ASSIGNED,
        CANCELLED,
    },
    ASSIGNED: {
        IN_PROGRESS,
        CANCELLED,
    },
    IN_PROGRESS: {
        COMPLETED,
        CANCELLED,
    },
    COMPLETED: set(),
    CANCELLED: set(),
}


def is_valid_transition(
    current_status: str,
    new_status: str,
) -> bool:
    return new_status in ALLOWED_TRANSITIONS.get(
        current_status,
        set(),
    )