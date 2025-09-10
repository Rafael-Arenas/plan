# src/planificador/schemas/response/__init__.py

"""Esquemas de respuesta optimizados para listados, búsquedas y dashboards."""

from .response_schemas import (
    # Esquemas de listados
    EmployeeListResponse,
    ProjectListResponse,
    ClientListResponse,
    TeamListResponse,
    ScheduleListResponse,
    VacationListResponse,
    WorkloadListResponse,
    ProjectAssignmentListResponse,
    
    # Esquemas de búsquedas
    EmployeeSearchResponse,
    ProjectSearchResponse,
    ScheduleSearchResponse,
    
    # Esquemas de resúmenes
    EmployeeSummaryResponse,
    ProjectSummaryResponse,
    TeamSummaryResponse,
    WorkloadSummaryResponse,
    
    # Esquemas paginados
    PaginatedResponse,
    PaginatedEmployeeResponse,
    PaginatedProjectResponse,
    PaginatedClientResponse,
    PaginatedScheduleResponse,
    PaginatedVacationResponse,
    PaginatedWorkloadResponse,
    
    # Esquemas de dashboard
    DashboardStatsResponse,
    EmployeeUtilizationResponse,
    ProjectProgressResponse,
)

__all__ = [
    # Esquemas de listados
    "EmployeeListResponse",
    "ProjectListResponse",
    "ClientListResponse",
    "TeamListResponse",
    "ScheduleListResponse",
    "VacationListResponse",
    "WorkloadListResponse",
    "ProjectAssignmentListResponse",
    
    # Esquemas de búsquedas
    "EmployeeSearchResponse",
    "ProjectSearchResponse",
    "ScheduleSearchResponse",
    
    # Esquemas de resúmenes
    "EmployeeSummaryResponse",
    "ProjectSummaryResponse",
    "TeamSummaryResponse",
    "WorkloadSummaryResponse",
    
    # Esquemas paginados
    "PaginatedResponse",
    "PaginatedEmployeeResponse",
    "PaginatedProjectResponse",
    "PaginatedClientResponse",
    "PaginatedScheduleResponse",
    "PaginatedVacationResponse",
    "PaginatedWorkloadResponse",
    
    # Esquemas de dashboard
    "DashboardStatsResponse",
    "EmployeeUtilizationResponse",
    "ProjectProgressResponse",
]