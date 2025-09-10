# src/planificador/schemas/employee/employee.py

from typing import List, Optional
from pydantic import EmailStr, Field
from datetime import datetime

from ..base.base import BaseSchema
from ...models.employee import EmployeeStatus
from ..team.team import TeamMembership
from ..assignment.assignment import ProjectAssignment
from ..schedule.schedule import Schedule
from ..vacation.vacation import Vacation
from ..workload.workload import Workload


class EmployeeBase(BaseSchema):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    employee_code: str = Field(..., min_length=1, max_length=20)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    position: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)


class EmployeeCreate(BaseSchema):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    employee_code: str = Field(..., min_length=1, max_length=20)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    position: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)


class EmployeeUpdate(BaseSchema):
    """Schema para actualizar un Empleado."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    employee_code: Optional[str] = Field(None, min_length=1, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    status: Optional[EmployeeStatus] = None
    position: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)


class Employee(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime


class EmployeeWithTeams(Employee):
    """Employee con sus membresías de equipos."""

    team_memberships: List[TeamMembership] = []


class EmployeeWithProjects(Employee):
    """Employee con sus asignaciones de proyectos."""

    project_assignments: List[ProjectAssignment] = []


class EmployeeWithSchedules(Employee):
    """Employee con sus horarios."""

    schedules: List[Schedule] = []


class EmployeeWithVacations(Employee):
    """Employee con sus vacaciones."""

    vacations: List[Vacation] = []


class EmployeeWithWorkloads(Employee):
    """Employee con sus cargas de trabajo."""

    workloads: List[Workload] = []


class EmployeeWithDetails(Employee):
    """Employee con todas sus relaciones."""

    team_memberships: List[TeamMembership] = []
    project_assignments: List[ProjectAssignment] = []
    schedules: List[Schedule] = []
    vacations: List[Vacation] = []
    workloads: List[Workload] = []


class EmployeeSearchFilter(BaseSchema):
    """Filtros para búsqueda de empleados."""

    name: Optional[str] = None
    code: Optional[str] = None
    email: Optional[str] = None
    status: Optional[EmployeeStatus] = None
    department: Optional[str] = None
    position: Optional[str] = None
    team_id: Optional[int] = None
    project_id: Optional[int] = None