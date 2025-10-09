# src/planificador/schemas/assignment/advanced_schemas.py

from typing import List, Optional, Dict, Any
from pydantic import Field, BaseModel, ConfigDict
from datetime import date, datetime
from decimal import Decimal

from ..base.base import BaseSchema
from .assignment import ProjectAssignment


class ProjectTeamSummarySchema(BaseSchema):
    """Esquema para resumen del equipo de un proyecto."""
    
    project_id: int
    project_name: str
    total_team_members: int
    active_assignments: int
    total_allocation_percentage: Decimal
    average_allocation_per_member: Decimal
    roles_distribution: Dict[str, int]
    team_capacity_status: str  # "underutilized", "optimal", "overallocated"
    team_members: List[Dict[str, Any]]
    project_timeline: Dict[str, Any]


class ProjectResourceAllocationSchema(BaseSchema):
    """Esquema para distribución de recursos de un proyecto."""
    
    project_id: int
    project_name: str
    total_allocated_hours_per_day: Decimal
    total_allocation_percentage: Decimal
    resource_distribution_by_role: Dict[str, Dict[str, Any]]
    resource_distribution_by_time: List[Dict[str, Any]]
    capacity_analysis: Dict[str, Any]
    cost_estimation: Optional[Dict[str, Any]] = None
    efficiency_metrics: Dict[str, Any]


class ProjectTimelineSchema(BaseSchema):
    """Esquema para línea de tiempo de asignaciones de un proyecto."""
    
    project_id: int
    project_name: str
    project_start_date: Optional[date]
    project_end_date: Optional[date]
    timeline_events: List[Dict[str, Any]]
    phases: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    resource_timeline: List[Dict[str, Any]]
    critical_path: List[Dict[str, Any]]


class AssignmentAdvancedFilters(BaseSchema):
    """Esquema para filtros avanzados de búsqueda de asignaciones."""
    
    employee_ids: Optional[List[int]] = None
    project_ids: Optional[List[int]] = None
    roles: Optional[List[str]] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    end_date_from: Optional[date] = None
    end_date_to: Optional[date] = None
    min_allocation_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    max_allocation_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    min_hours_per_day: Optional[Decimal] = Field(None, ge=0, le=24)
    max_hours_per_day: Optional[Decimal] = Field(None, ge=0, le=24)
    is_active: Optional[bool] = None
    has_end_date: Optional[bool] = None
    overlapping_with_date_range: Optional[Dict[str, date]] = None
    exclude_assignment_ids: Optional[List[int]] = None
    include_notes_search: Optional[str] = None


class EmployeeWorkloadSummarySchema(BaseSchema):
    """Esquema para resumen de carga de trabajo de un empleado."""
    
    employee_id: int
    employee_name: str
    total_assignments: int
    active_assignments: int
    total_allocation_percentage: Decimal
    total_hours_per_day: Decimal
    capacity_status: str  # "available", "optimal", "overloaded"
    current_projects: List[Dict[str, Any]]
    workload_distribution: Dict[str, Any]
    availability_forecast: List[Dict[str, Any]]


class EmployeeAllocationSummarySchema(BaseSchema):
    """Esquema para resumen de asignación actual de un empleado."""
    
    employee_id: int
    employee_name: str
    current_total_percentage: Decimal
    current_total_hours_per_day: Decimal
    available_percentage: Decimal
    available_hours_per_day: Decimal
    capacity_status: str
    projects_breakdown: List[Dict[str, Any]]
    recommendations: List[str]


class TransferResultSchema(BaseSchema):
    """Esquema para resultado de transferencia de asignaciones."""
    
    success: bool
    transferred_assignments: int
    failed_transfers: int
    from_employee_id: int
    to_employee_id: int
    project_id: Optional[int]
    transfer_details: List[Dict[str, Any]]
    validation_errors: List[str]
    warnings: List[str]


class ReassignmentResultSchema(BaseSchema):
    """Esquema para resultado de reasignación de proyectos."""
    
    success: bool
    reassigned_assignments: int
    failed_reassignments: int
    from_project_id: int
    to_project_id: int
    employee_id: Optional[int]
    reassignment_details: List[Dict[str, Any]]
    validation_errors: List[str]
    warnings: List[str]


class WorkloadBalanceResultSchema(BaseSchema):
    """Esquema para resultado de balanceo de carga de trabajo."""
    
    success: bool
    project_id: int
    target_allocation: Decimal
    original_distribution: Dict[str, Any]
    balanced_distribution: Dict[str, Any]
    adjustments_made: List[Dict[str, Any]]
    balance_score: Decimal  # 0-100, donde 100 es perfectamente balanceado
    recommendations: List[str]


class AssignmentDurationAnalyticsSchema(BaseSchema):
    """Esquema para análisis de duración de asignaciones."""
    
    total_assignments_analyzed: int
    average_duration_days: Decimal
    median_duration_days: Decimal
    min_duration_days: int
    max_duration_days: int
    duration_distribution: Dict[str, int]  # rangos de duración
    duration_by_role: Dict[str, Dict[str, Any]]
    trends: List[Dict[str, Any]]
    insights: List[str]


class WorkloadDistributionAnalyticsSchema(BaseSchema):
    """Esquema para análisis de distribución de carga de trabajo."""
    
    total_employees_analyzed: int
    average_workload_percentage: Decimal
    workload_distribution: Dict[str, int]  # rangos de carga
    overloaded_employees: List[Dict[str, Any]]
    underutilized_employees: List[Dict[str, Any]]
    optimal_employees: List[Dict[str, Any]]
    department_analysis: Dict[str, Any]
    recommendations: List[str]


class AssignmentTrendDataSchema(BaseSchema):
    """Esquema para datos de tendencias de asignaciones."""
    
    date: date
    new_assignments: int
    completed_assignments: int
    active_assignments: int
    total_allocation_percentage: Decimal
    average_allocation_per_assignment: Decimal
    unique_employees: int
    unique_projects: int


class AssignmentDashboardMetricsSchema(BaseSchema):
    """Esquema para métricas completas del dashboard de asignaciones."""
    
    overview: Dict[str, Any]
    employee_metrics: Dict[str, Any]
    project_metrics: Dict[str, Any]
    workload_metrics: Dict[str, Any]
    trend_metrics: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    recommendations: List[str]
    last_updated: datetime


class ValidationResultSchema(BaseSchema):
    """Esquema para resultado de validación de reglas de negocio."""
    
    is_valid: bool
    validation_errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    business_rules_checked: List[str]
    validation_summary: Dict[str, Any]


class DeletionValidationSchema(BaseSchema):
    """Esquema para validación de eliminación de asignaciones."""
    
    can_delete: bool
    blocking_factors: List[Dict[str, Any]]
    warnings: List[str]
    impact_analysis: Dict[str, Any]
    recommended_actions: List[str]


class EmployeeAvailabilitySchema(BaseSchema):
    """Esquema para disponibilidad de empleado."""
    
    employee_id: int
    employee_name: str
    is_available: bool
    availability_percentage: Decimal
    availability_hours_per_day: Decimal
    conflicting_assignments: List[Dict[str, Any]]
    availability_periods: List[Dict[str, Any]]
    recommendations: List[str]


class ProjectAssignmentDuplicateSchema(BaseSchema):
    """Esquema para duplicar una asignación con nuevos parámetros."""
    
    new_employee_id: Optional[int] = None
    new_project_id: Optional[int] = None
    new_start_date: Optional[date] = None
    new_end_date: Optional[date] = None
    new_allocated_hours_per_day: Optional[Decimal] = Field(None, ge=0, le=24)
    new_percentage_allocation: Optional[Decimal] = Field(None, ge=0, le=100)
    new_role_in_project: Optional[str] = Field(None, max_length=100)
    copy_notes: bool = False
    additional_notes: Optional[str] = None


class ProjectAssignmentResponseSchema(ProjectAssignment):
    """Esquema de respuesta enriquecido para asignaciones de proyecto."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    employee_name: Optional[str] = None
    project_name: Optional[str] = None
    project_reference: Optional[str] = None
    duration_days: Optional[int] = None
    is_current: Optional[bool] = None
    workload_status: Optional[str] = None