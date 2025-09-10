# src/planificador/schemas/__init__.py

from .base.base import BaseSchema

from .client.client import (
    Client,
    ClientCreate,
    ClientUpdate,
    ClientWithProjects,
)

from .project.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectWithAssignments,
    ProjectWithDetails,
    ProjectWithSchedules,
    ProjectWithWorkloads,
    ProjectSearchFilter,
)

from .employee.employee import (
    Employee,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeWithDetails,
    EmployeeWithProjects,
    EmployeeWithSchedules,
    EmployeeWithTeams,
    EmployeeWithVacations,
    EmployeeWithWorkloads,
    EmployeeSearchFilter,
)

from .team.team import (
    Team,
    TeamCreate,
    TeamUpdate,
    TeamMembership,
    TeamMembershipCreate,
    TeamWithDetails,
    TeamWithMembers,
    TeamWithSchedules,
)

from .assignment.assignment import (
    ProjectAssignment,
    ProjectAssignmentCreate,
)

from .schedule.schedule import (
    Schedule,
    ScheduleCreate,
    ScheduleSearchFilter,
)

# Reconstruir modelos para resolver referencias anticipadas (ForwardRefs)
# Es crucial hacerlo aquí después de que todos los módulos de esquemas han sido importados
# para evitar errores de importación circular.

Client.model_rebuild()
ClientWithProjects.model_rebuild()

Project.model_rebuild()
ProjectWithAssignments.model_rebuild()
ProjectWithSchedules.model_rebuild()
ProjectWithWorkloads.model_rebuild()
ProjectWithDetails.model_rebuild()

Employee.model_rebuild()
EmployeeWithTeams.model_rebuild()
EmployeeWithProjects.model_rebuild()
EmployeeWithSchedules.model_rebuild()
EmployeeWithVacations.model_rebuild()
EmployeeWithWorkloads.model_rebuild()
EmployeeWithDetails.model_rebuild()

Team.model_rebuild()
TeamWithMembers.model_rebuild()
TeamWithSchedules.model_rebuild()
TeamWithDetails.model_rebuild()

from .workload.workload import (
    Workload,
    WorkloadCreate,
)

from .vacation.vacation import (
    Vacation,
    VacationCreate,
    VacationUpdate,
    VacationSearchFilter,
)

from .alert.alert import (
    Alert,
    AlertCreate,
    AlertUpdate,
    AlertSearchFilter,
)

from .alert.status_code import (
    StatusCode,
    StatusCodeCreate,
)

# Esquemas de report.py eliminados - funcionalidad consolidada en response_schemas.py

from .response.response_schemas import (
    # Esquemas de listados optimizados
    EmployeeListResponse,
    ProjectListResponse,
    ClientListResponse,
    TeamListResponse,
    ScheduleListResponse,
    VacationListResponse,
    WorkloadListResponse,
    ProjectAssignmentListResponse,
    
    # Esquemas de búsquedas optimizados
    EmployeeSearchResponse,
    ProjectSearchResponse,
    ScheduleSearchResponse,
    
    # Esquemas de resúmenes optimizados
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
    # Base
    "BaseSchema",
    # Client
    "Client",
    "ClientCreate",
    "ClientUpdate",
    "ClientWithProjects",
    # Project
    "Project",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectWithAssignments",
    "ProjectWithDetails",
    "ProjectWithSchedules",
    "ProjectWithWorkloads",
    "ProjectSearchFilter",
    # Employee
    "Employee",
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeWithDetails",
    "EmployeeWithProjects",
    "EmployeeWithSchedules",
    "EmployeeWithTeams",
    "EmployeeWithVacations",
    "EmployeeWithWorkloads",
    "EmployeeSearchFilter",
    # Team
    "Team",
    "TeamCreate",
    "TeamUpdate",
    "TeamMembership",
    "TeamMembershipCreate",
    "TeamWithDetails",
    "TeamWithMembers",
    "TeamWithSchedules",
    # Assignment
    "ProjectAssignment",
    "ProjectAssignmentCreate",
    # Schedule
    "Schedule",
    "ScheduleCreate",
    "ScheduleSearchFilter",
    # Workload
    "Workload",
    "WorkloadCreate",
    # Vacation
    "Vacation",
    "VacationCreate",
    "VacationSearchFilter",
    # Alert
    "Alert",
    "AlertCreate",
    "AlertUpdate",
    "AlertSearchFilter",
    "StatusCode",
    "StatusCodeCreate",
    # Report
    # Esquemas de report.py eliminados - funcionalidad consolidada en response_schemas.py
    
    # Response Schemas - Listados optimizados
    "EmployeeListResponse",
    "ProjectListResponse",
    "ClientListResponse",
    "TeamListResponse",
    "ScheduleListResponse",
    "VacationListResponse",
    "WorkloadListResponse",
    "ProjectAssignmentListResponse",
    
    # Response Schemas - Búsquedas optimizadas
    "EmployeeSearchResponse",
    "ProjectSearchResponse",
    "ScheduleSearchResponse",
    
    # Response Schemas - Resúmenes optimizados
    "EmployeeSummaryResponse",
    "ProjectSummaryResponse",
    "TeamSummaryResponse",
    "WorkloadSummaryResponse",
    
    # Response Schemas - Paginación
    "PaginatedResponse",
    "PaginatedEmployeeResponse",
    "PaginatedProjectResponse",
    "PaginatedClientResponse",
    "PaginatedScheduleResponse",
    "PaginatedVacationResponse",
    "PaginatedWorkloadResponse",
    
    # Response Schemas - Dashboard
    "DashboardStatsResponse",
    "EmployeeUtilizationResponse",
    "ProjectProgressResponse",
]