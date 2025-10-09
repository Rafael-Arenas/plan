# src/planificador/schemas/project/project.py

from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING
from datetime import datetime, date
from pydantic import field_validator, Field, ConfigDict
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


# ============================================================================
# ESQUEMAS PARA OPERACIONES MASIVAS (BULK OPERATIONS)
# ============================================================================

class ProjectBulkUpdateSchema(BaseSchema):
    """Schema para actualizaciones masivas de proyectos."""
    
    project_id: int
    update_data: ProjectUpdate


class ProjectCloneSchema(BaseSchema):
    """Schema para clonar un proyecto."""
    
    name: str
    reference: str
    trigram: str
    client_id: Optional[int] = None
    copy_assignments: bool = False
    copy_schedules: bool = False
    copy_workloads: bool = False


# ============================================================================
# ESQUEMAS PARA BÚSQUEDAS Y FILTROS AVANZADOS
# ============================================================================

class ProjectAdvancedFilters(BaseSchema):
    """Filtros avanzados para búsqueda de proyectos."""
    
    search_term: Optional[str] = None
    statuses: Optional[List[ProjectStatus]] = None
    priorities: Optional[List[ProjectPriority]] = None
    client_ids: Optional[List[int]] = None
    employee_ids: Optional[List[int]] = None
    start_date_range: Optional[tuple[date, date]] = None
    end_date_range: Optional[tuple[date, date]] = None
    is_overdue: Optional[bool] = None
    is_active: Optional[bool] = None
    has_assignments: Optional[bool] = None
    min_duration_days: Optional[int] = None
    max_duration_days: Optional[int] = None


class ProjectFilterCriteria(BaseSchema):
    """Criterios específicos para filtrado de proyectos."""
    
    name_contains: Optional[str] = None
    reference_pattern: Optional[str] = None
    trigram_pattern: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None


class PaginationParams(BaseSchema):
    """Parámetros de paginación."""
    
    skip: int = 0
    limit: int = 100
    sort_by: str = "created_at"
    sort_order: str = "desc"  # "asc" o "desc"


class PaginatedProjectResponse(BaseSchema):
    """Respuesta paginada de proyectos."""
    
    items: List[Project]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


# ============================================================================
# ESQUEMAS PARA CRONOGRAMAS Y PLANIFICACIÓN TEMPORAL
# ============================================================================

class ProjectDurationSchema(BaseSchema):
    """Schema para duración y métricas temporales del proyecto."""
    
    project_id: int
    total_duration_days: int
    elapsed_duration_days: int
    remaining_duration_days: int
    progress_percentage: float
    is_overdue: bool
    days_overdue: Optional[int] = None
    estimated_completion_date: Optional[date] = None


class ProjectTimelineSchema(BaseSchema):
    """Schema para timeline del proyecto."""
    
    project_id: int
    project_name: str
    start_date: date
    end_date: date
    milestones: List[dict] = []  # Lista de hitos del proyecto
    critical_path: List[dict] = []  # Ruta crítica
    dependencies: List[dict] = []  # Dependencias
    risk_level: str  # "low", "medium", "high", "critical"


class ProjectDatesUpdateSchema(BaseSchema):
    """Schema para actualizar fechas del proyecto."""
    
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = None  # Razón del cambio
    notify_team: bool = True


# ============================================================================
# ESQUEMAS PARA ESTADÍSTICAS BÁSICAS
# ============================================================================

class ProjectStatusSummarySchema(BaseSchema):
    """Resumen de proyectos por estado."""
    
    total_projects: int
    planned_count: int
    in_progress_count: int
    completed_count: int
    cancelled_count: int
    on_hold_count: int


class ProjectCompletionRateSchema(BaseSchema):
    """Tasa de finalización de proyectos."""
    
    total_projects: int
    completed_projects: int
    completion_rate: float
    average_duration_days: float


# ============================================================================
# ESQUEMAS PARA ESTADÍSTICAS AVANZADAS
# ============================================================================

class ProjectPerformanceStatsSchema(BaseSchema):
    """Estadísticas de rendimiento de proyectos."""
    
    total_projects: int
    on_time_projects: int
    delayed_projects: int
    cancelled_projects: int
    average_delay_days: float
    on_time_percentage: float
    average_project_duration: float
    productivity_score: float


class MonthlyProjectStatsSchema(BaseSchema):
    """Estadísticas mensuales de proyectos."""
    
    year: int
    month: int
    projects_started: int
    projects_completed: int
    projects_cancelled: int
    total_active: int
    average_duration: float
    completion_rate: float


class ClientProjectStatsSchema(BaseSchema):
    """Estadísticas de proyectos por cliente."""
    
    client_id: int
    client_name: str
    total_projects: int
    active_projects: int
    completed_projects: int
    cancelled_projects: int
    average_project_duration: float
    total_revenue: Optional[float] = None
    success_rate: float


class OverdueProjectsSummarySchema(BaseSchema):
    """Resumen de proyectos atrasados."""
    
    total_overdue: int
    average_delay_days: float
    critical_overdue: int  # Más de 30 días
    high_priority_overdue: int
    affected_clients: int
    estimated_recovery_days: float


class ProjectDurationAnalysisSchema(BaseSchema):
    """Análisis de duración de proyectos."""
    
    average_duration: float
    median_duration: float
    shortest_duration: int
    longest_duration: int
    duration_variance: float
    projects_by_duration_range: dict  # Rangos de duración


class EmployeeWorkloadSchema(BaseSchema):
    """Carga de trabajo por empleado en proyectos."""
    
    employee_id: int
    employee_name: str
    active_projects: int
    total_assigned_hours: float
    utilization_percentage: float
    overloaded: bool
    projects_list: List[dict]


# ============================================================================
# ESQUEMAS PARA RELACIONES Y ASIGNACIONES
# ============================================================================

class ClientProjectsSummarySchema(BaseSchema):
    """Resumen de proyectos de un cliente."""
    
    client_id: int
    client_name: str
    total_projects: int
    active_projects: List[Project]
    completed_projects_count: int
    total_investment: Optional[float] = None
    success_rate: float
    average_project_duration: float


class ProjectFullDetailsSchema(BaseSchema):
    """Proyecto con todos los detalles completos."""
    
    project: Project
    assignments: List[ProjectAssignment]
    schedules: List[Schedule]
    workloads: List[Workload]
    statistics: ProjectDurationSchema
    team_summary: dict
    client_info: dict


# ============================================================================
# ESQUEMAS PARA VALIDACIÓN
# ============================================================================

class ValidationResultSchema(BaseSchema):
    """Resultado de validación."""
    
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []


class ProjectValidationSchema(BaseSchema):
    """Schema específico para validación de proyectos."""
    
    project_data: dict
    validation_rules: List[str] = []
    strict_mode: bool = False


# ============================================================================
# ESQUEMAS PARA DIAGNÓSTICO Y SALUD
# ============================================================================

class ServiceHealthSchema(BaseSchema):
    """Estado de salud del servicio."""
    
    service_name: str = "ProjectDomainService"
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    response_time_ms: float
    active_connections: int
    memory_usage_mb: float
    cpu_usage_percent: float


class DatabaseHealthSchema(BaseSchema):
    """Estado de salud de la base de datos."""
    
    database_name: str
    status: str  # "connected", "disconnected", "error"
    connection_time_ms: float
    active_connections: int
    query_performance_ms: float
    last_backup: Optional[datetime] = None


class HealthReportSchema(BaseSchema):
    """Reporte completo de salud del sistema."""
    
    overall_status: str
    service_health: ServiceHealthSchema
    database_health: DatabaseHealthSchema
    performance_metrics: dict
    recommendations: List[str] = []
    timestamp: datetime


# ============================================================================
# ESQUEMAS DE RESPUESTA ESPECIALIZADOS
# ============================================================================

class ProjectResponseSchema(Project):
    """Schema de respuesta estándar para proyectos."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class ProjectWithAssignmentsSchema(ProjectWithAssignments):
    """Schema de respuesta para proyectos con asignaciones."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)