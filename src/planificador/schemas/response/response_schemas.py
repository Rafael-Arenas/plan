# src/planificador/schemas/response/response_schemas.py

from typing import List, Optional
from datetime import datetime, date, time
from decimal import Decimal
from pydantic import Field

from ..base.base import BaseSchema
from ...models.employee import EmployeeStatus
from ...models.project import ProjectStatus, ProjectPriority
from ...models.vacation import VacationType, VacationStatus


# ==========================================
# ESQUEMAS DE RESPUESTA PARA LISTADOS
# ==========================================

class EmployeeListResponse(BaseSchema):
    """Schema optimizado para listados de empleados."""
    
    id: int
    full_name: str
    employee_code: str
    email: str
    status: EmployeeStatus
    position: Optional[str] = None
    department: Optional[str] = None
    is_available: bool = True


class ProjectListResponse(BaseSchema):
    """Schema optimizado para listados de proyectos."""
    
    id: int
    name: str
    reference: str
    trigram: str
    status: ProjectStatus
    priority: ProjectPriority
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    client_name: str
    client_id: int


class ClientListResponse(BaseSchema):
    """Schema optimizado para listados de clientes."""
    
    id: int
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    projects_count: int = 0


class TeamListResponse(BaseSchema):
    """Schema optimizado para listados de equipos."""
    
    id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True
    members_count: int = 0


class ScheduleListResponse(BaseSchema):
    """Schema optimizado para listados de horarios."""
    
    id: int
    date: date
    start_time: time
    end_time: time
    hours_worked: Optional[Decimal] = None
    employee_name: str
    employee_id: int
    project_name: Optional[str] = None
    project_id: Optional[int] = None
    team_name: Optional[str] = None
    team_id: Optional[int] = None
    status_code: Optional[str] = None
    is_confirmed: bool = False
    location: Optional[str] = None


class VacationListResponse(BaseSchema):
    """Schema optimizado para listados de vacaciones."""
    
    id: int
    employee_name: str
    employee_id: int
    start_date: date
    end_date: date
    vacation_type: VacationType
    status: VacationStatus
    total_days: Optional[int] = None
    business_days: Optional[int] = None
    requested_date: datetime
    approved_date: Optional[datetime] = None


class WorkloadListResponse(BaseSchema):
    """Schema optimizado para listados de cargas de trabajo."""
    
    id: int
    employee_name: str
    employee_id: int
    project_name: str
    project_id: int
    date: date
    planned_hours: Decimal
    actual_hours: Optional[Decimal] = None
    utilization_percentage: Optional[Decimal] = None
    efficiency_score: Optional[Decimal] = None
    is_billable: bool = True


class ProjectAssignmentListResponse(BaseSchema):
    """Schema optimizado para listados de asignaciones de proyecto."""
    
    id: int
    employee_name: str
    employee_id: int
    project_name: str
    project_id: int
    start_date: date
    end_date: Optional[date] = None
    allocated_hours_per_day: Optional[Decimal] = None
    percentage_allocation: Optional[Decimal] = None
    role_in_project: Optional[str] = None
    is_active: bool = True


# ==========================================
# ESQUEMAS DE RESPUESTA PARA BÚSQUEDAS
# ==========================================

class EmployeeSearchResponse(BaseSchema):
    """Schema para resultados de búsqueda de empleados."""
    
    id: int
    full_name: str
    employee_code: str
    email: str
    phone: Optional[str] = None
    status: EmployeeStatus
    position: Optional[str] = None
    department: Optional[str] = None
    is_available: bool = True
    current_projects: List[str] = []
    current_teams: List[str] = []


class ProjectSearchResponse(BaseSchema):
    """Schema para resultados de búsqueda de proyectos."""
    
    id: int
    name: str
    reference: str
    trigram: str
    status: ProjectStatus
    priority: ProjectPriority
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    client_name: str
    client_id: int
    assigned_employees: List[str] = []
    total_assignments: int = 0


class ScheduleSearchResponse(BaseSchema):
    """Schema para resultados de búsqueda de horarios."""
    
    id: int
    date: date
    start_time: time
    end_time: time
    hours_worked: Optional[Decimal] = None
    employee_name: str
    employee_id: int
    project_name: Optional[str] = None
    project_id: Optional[int] = None
    team_name: Optional[str] = None
    team_id: Optional[int] = None
    status_code: Optional[str] = None
    is_confirmed: bool = False
    location: Optional[str] = None
    description: Optional[str] = None


# ==========================================
# ESQUEMAS DE RESPUESTA PARA RESÚMENES
# ==========================================

class EmployeeSummaryResponse(BaseSchema):
    """Schema para resumen de empleado."""
    
    id: int
    full_name: str
    employee_code: str
    status: EmployeeStatus
    position: Optional[str] = None
    department: Optional[str] = None
    total_projects: int = 0
    active_projects: int = 0
    total_teams: int = 0
    current_utilization: Optional[Decimal] = None
    avg_efficiency: Optional[Decimal] = None
    pending_vacations: int = 0


class ProjectSummaryResponse(BaseSchema):
    """Schema para resumen de proyecto."""
    
    id: int
    name: str
    reference: str
    status: ProjectStatus
    priority: ProjectPriority
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    client_name: str
    total_assignments: int = 0
    active_assignments: int = 0
    total_hours_planned: Optional[Decimal] = None
    total_hours_actual: Optional[Decimal] = None
    progress_percentage: Optional[Decimal] = None


class TeamSummaryResponse(BaseSchema):
    """Schema para resumen de equipo."""
    
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool = True
    total_members: int = 0
    active_members: int = 0
    current_projects: List[str] = []
    avg_utilization: Optional[Decimal] = None


class WorkloadSummaryResponse(BaseSchema):
    """Schema para resumen de carga de trabajo."""
    
    employee_id: int
    employee_name: str
    period_start: date
    period_end: date
    total_planned_hours: Decimal
    total_actual_hours: Optional[Decimal] = None
    avg_utilization: Optional[Decimal] = None
    avg_efficiency: Optional[Decimal] = None
    billable_hours: Optional[Decimal] = None
    billable_percentage: Optional[Decimal] = None
    projects_count: int = 0


# ==========================================
# ESQUEMAS DE RESPUESTA PAGINADOS
# ==========================================

class PaginatedResponse(BaseSchema):
    """Schema base para respuestas paginadas."""
    
    total: int = Field(..., description="Total de elementos")
    page: int = Field(..., description="Página actual")
    size: int = Field(..., description="Elementos por página")
    pages: int = Field(..., description="Total de páginas")
    has_next: bool = Field(..., description="Tiene página siguiente")
    has_prev: bool = Field(..., description="Tiene página anterior")


class PaginatedEmployeeResponse(PaginatedResponse):
    """Respuesta paginada de empleados."""
    
    items: List[EmployeeListResponse] = []


class PaginatedProjectResponse(PaginatedResponse):
    """Respuesta paginada de proyectos."""
    
    items: List[ProjectListResponse] = []


class PaginatedClientResponse(PaginatedResponse):
    """Respuesta paginada de clientes."""
    
    items: List[ClientListResponse] = []


class PaginatedScheduleResponse(PaginatedResponse):
    """Respuesta paginada de horarios."""
    
    items: List[ScheduleListResponse] = []


class PaginatedVacationResponse(PaginatedResponse):
    """Respuesta paginada de vacaciones."""
    
    items: List[VacationListResponse] = []


class PaginatedWorkloadResponse(PaginatedResponse):
    """Respuesta paginada de cargas de trabajo."""
    
    items: List[WorkloadListResponse] = []


# ==========================================
# ESQUEMAS DE RESPUESTA PARA DASHBOARDS
# ==========================================

class DashboardStatsResponse(BaseSchema):
    """Schema para estadísticas del dashboard."""
    
    total_employees: int = 0
    active_employees: int = 0
    total_projects: int = 0
    active_projects: int = 0
    total_clients: int = 0
    active_clients: int = 0
    pending_vacations: int = 0
    today_schedules: int = 0
    overdue_projects: int = 0
    high_priority_projects: int = 0


class EmployeeUtilizationResponse(BaseSchema):
    """Schema para utilización de empleados."""
    
    employee_id: int
    employee_name: str
    current_utilization: Decimal
    target_utilization: Decimal = Field(default=Decimal('80.0'))
    variance: Decimal
    status: str  # "Óptima", "Baja", "Alta", "Sobrecarga"


class ProjectProgressResponse(BaseSchema):
    """Schema para progreso de proyectos."""
    
    project_id: int
    project_name: str
    progress_percentage: Decimal
    days_remaining: Optional[int] = None
    status: ProjectStatus
    is_on_track: bool = True
    risk_level: str  # "Bajo", "Medio", "Alto"