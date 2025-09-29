# src/planificador/schemas/team_membership.py

import enum

class MembershipStatus(str, enum.Enum):
    """Estado de una membresía de equipo."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FUTURE = "future"
    PAST = "past"
    PENDING = "pending"