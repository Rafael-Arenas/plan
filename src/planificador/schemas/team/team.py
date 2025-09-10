# src/planificador/schemas/team/team.py

from typing import List, Optional, TYPE_CHECKING
from pydantic import Field, field_validator, model_validator
from datetime import datetime, date
import pendulum

from ..base.base import BaseSchema
from ...models.team_membership import MembershipRole

if TYPE_CHECKING:
    from ..schedule.schedule import Schedule
    from ..employee.employee import Employee
else:
    Schedule = "Schedule"
    Employee = "Employee"


class TeamBase(BaseSchema):
    """Schema base para Team."""

    name: str = Field(..., min_length=1, max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    color_hex: str = Field(default="#3498db", pattern=r"^#[0-9A-Fa-f]{6}$")
    max_members: int = Field(default=10, ge=1, le=100)
    is_active: bool = True
    notes: Optional[str] = None


class TeamCreate(TeamBase):
    """Schema para crear un Team."""

    pass


class TeamUpdate(BaseSchema):
    """Schema para actualizar un Team."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    color_hex: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    max_members: Optional[int] = Field(None, ge=1, le=100)
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class Team(TeamBase):
    """Schema de salida para Team."""

    id: int
    created_at: datetime
    updated_at: datetime


class TeamMembershipBase(BaseSchema):
    """Schema base para TeamMembership."""

    employee_id: int
    team_id: int
    role: MembershipRole = MembershipRole.MEMBER
    start_date: date
    end_date: Optional[date] = None
    is_active: bool = True

    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v: date) -> date:
        """Valida que la fecha de inicio no sea muy antigua ni muy futura."""
        if v < pendulum.now().subtract(years=10).date():
            raise ValueError("La fecha de inicio no puede ser anterior a 10 años")
        if v > pendulum.now().add(years=5).date():
            raise ValueError("La fecha de inicio no puede ser posterior a 5 años")
        return v

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: Optional[date]) -> Optional[date]:
        """Valida que la fecha de fin no sea muy futura."""
        if v is not None:
            if v > pendulum.now().add(years=10).date():
                raise ValueError("La fecha de fin no puede ser posterior a 10 años")
        return v

    @model_validator(mode='after')
    def validate_date_range(self) -> 'TeamMembershipBase':
        """Valida que el rango de fechas sea coherente."""
        if self.end_date and self.start_date >= self.end_date:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
        return self


class TeamMembershipCreate(TeamMembershipBase):
    """Schema para crear una TeamMembership."""

    pass


class TeamMembership(TeamMembershipBase):
    """Schema de salida para TeamMembership."""

    id: int
    created_at: datetime
    updated_at: datetime


class TeamWithMembers(Team):
    """Team con sus miembros."""

    memberships: List[TeamMembership] = []


class TeamWithSchedules(Team):
    """Team con sus horarios."""

    schedules: List["Schedule"] = []


class TeamWithDetails(Team):
    """Team con todas sus relaciones."""

    memberships: List[TeamMembership] = []
    schedules: List["Schedule"] = []