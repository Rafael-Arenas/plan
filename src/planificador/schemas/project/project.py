# src/planificador/schemas/project/project.py

from typing import List, Optional, TYPE_CHECKING
from datetime import datetime, date
from pydantic import field_validator
import pendulum

from ..base.base import BaseSchema
from ...models.project import ProjectStatus, ProjectPriority
if TYPE_CHECKING:
    from ..client.client import Client
from ..assignment.assignment import ProjectAssignment
from ..schedule.schedule import Schedule
from ..workload.workload import Workload


class ProjectBase(BaseSchema):
    name: str
    reference: str
    trigram: str
    details: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNED
    priority: ProjectPriority = ProjectPriority.MEDIUM
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    client_id: int

    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v: Optional[date]) -> Optional[date]:
        """Valida que la fecha de inicio del proyecto sea razonable."""
        if v is not None:
            if v < pendulum.now().subtract(years=5).date():
                raise ValueError("La fecha de inicio no puede ser anterior a 5 años")
            if v > pendulum.now().add(years=10).date():
                raise ValueError("La fecha de inicio no puede ser posterior a 10 años")
        return v

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: Optional[date]) -> Optional[date]:
        """Valida que la fecha de fin del proyecto sea razonable."""
        if v is not None:
            if v < pendulum.now().subtract(years=5).date():
                raise ValueError("La fecha de fin no puede ser anterior a 5 años")
            if v > pendulum.now().add(years=15).date():
                raise ValueError("La fecha de fin no puede ser posterior a 15 años")
        return v

    def validate_project_dates(self) -> 'ProjectBase':
        """Valida que las fechas del proyecto sean coherentes."""
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
            
            # Validar que la duración no sea excesiva (máximo 5 años)
            duration = pendulum.instance(self.end_date) - pendulum.instance(self.start_date)
            if duration.days > 365 * 5:
                raise ValueError("La duración del proyecto no puede exceder 5 años")
        return self


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseSchema):
    """Schema para actualizar un Proyecto."""

    name: Optional[str] = None
    reference: Optional[str] = None
    trigram: Optional[str] = None
    details: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    client_id: Optional[int] = None


class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    client: "Client"


class ProjectWithAssignments(Project):
    """Project con sus asignaciones de empleados."""

    assignments: List[ProjectAssignment] = []


class ProjectWithSchedules(Project):
    """Project con sus horarios."""

    schedules: List[Schedule] = []


class ProjectWithWorkloads(Project):
    """Project con sus cargas de trabajo."""

    workloads: List[Workload] = []


class ProjectWithDetails(Project):
    """Project con todas sus relaciones."""

    assignments: List[ProjectAssignment] = []
    schedules: List[Schedule] = []
    workloads: List[Workload] = []


class ProjectSearchFilter(BaseSchema):
    """Filtros para búsqueda de proyectos."""

    name: Optional[str] = None
    reference: Optional[str] = None
    trigram: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    client_id: Optional[int] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    end_date_from: Optional[date] = None
    end_date_to: Optional[date] = None