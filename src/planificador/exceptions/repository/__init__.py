# src/planificador/exceptions/repository/__init__.py
"""
Excepciones específicas para repositorios.

Este módulo contiene todas las excepciones relacionadas con operaciones
de repositorio y conversión de errores de SQLAlchemy a excepciones de dominio.
"""

from .base_repository_exceptions import (
    RepositoryError,
    RepositoryConnectionError,
    RepositoryIntegrityError,
    RepositoryTimeoutError,
    RepositoryTransactionError,
    RepositoryValidationError,
    convert_sqlalchemy_error
)

from .alert_repository_exceptions import (
    AlertRepositoryError,
    AlertStateTransitionError,
    AlertBulkOperationError,
    AlertQueryError,
    AlertStatisticsError,
    AlertValidationRepositoryError,
    AlertRelationshipError,
    AlertDateRangeError,
    create_alert_state_transition_error,
    create_alert_bulk_operation_error,
    create_alert_query_error,
    create_alert_statistics_error,
    create_alert_validation_repository_error,
    create_alert_relationship_error,
    create_alert_date_range_error
)

from .client_repository_exceptions import (
    ClientRepositoryError,
    ClientQueryError,
    ClientStatisticsError,
    ClientValidationRepositoryError,
    ClientRelationshipError,
    ClientBulkOperationError,
    ClientDateRangeError,
    create_client_query_error,
    create_client_statistics_error,
    create_client_validation_repository_error,
    create_client_relationship_error,
    create_client_bulk_operation_error,
    create_client_date_range_error
)

from .employee_repository_exceptions import (
    EmployeeRepositoryError,
    EmployeeQueryError,
    EmployeeStatisticsError,
    EmployeeValidationRepositoryError,
    EmployeeRelationshipError,
    EmployeeBulkOperationError,
    EmployeeDateRangeError,
    EmployeeSkillsError,
    EmployeeAvailabilityError,
    create_employee_query_error,
    create_employee_statistics_error,
    create_employee_validation_repository_error,
    create_employee_relationship_error,
    create_employee_bulk_operation_error,
    create_employee_date_range_error,
    create_employee_skills_error,
    create_employee_availability_error
)

from .project_repository_exceptions import (
    ProjectRepositoryError,
    ProjectQueryError,
    ProjectStatisticsError,
    ProjectValidationRepositoryError,
    ProjectRelationshipError,
    ProjectBulkOperationError,
    ProjectDateRangeError,
    ProjectReferenceError,
    ProjectTrigramError,
    ProjectWorkloadError,
    create_project_query_error,
    create_project_statistics_error,
    create_project_validation_repository_error,
    create_project_relationship_error,
    create_project_bulk_operation_error,
    create_project_date_range_error,
    create_project_reference_error,
    create_project_trigram_error,
    create_project_workload_error
)

from .schedule_repository_exceptions import (
    ScheduleRepositoryError,
    ScheduleQueryError,
    ScheduleStatisticsError,
    ScheduleValidationRepositoryError,
    ScheduleRelationshipError,
    ScheduleBulkOperationError,
    ScheduleDateRangeError,
    ScheduleOverlapError,
    create_schedule_query_error,
    create_schedule_statistics_error,
    create_schedule_validation_repository_error,
    create_schedule_relationship_error,
    create_schedule_bulk_operation_error,
    create_schedule_date_range_error,
    create_schedule_overlap_error,
)

from .workload_repository_exceptions import (
    WorkloadRepositoryError,
    WorkloadQueryError,
    WorkloadStatisticsError,
    WorkloadValidationRepositoryError,
    WorkloadRelationshipError,
    WorkloadBulkOperationError,
    WorkloadDateRangeError,
    WorkloadCapacityError,
    create_workload_query_error,
    create_workload_statistics_error,
    create_workload_validation_repository_error,
    create_workload_relationship_error,
    create_workload_bulk_operation_error,
    create_workload_date_range_error,
    create_workload_capacity_error,
)

from .team_repository_exceptions import (
    TeamRepositoryError,
    TeamQueryError,
    TeamStatisticsError,
    TeamValidationRepositoryError,
    TeamRelationshipError,
    TeamBulkOperationError,
    TeamMembershipError,
    TeamCapacityError,
    create_team_query_error,
    create_team_statistics_error,
    create_team_validation_repository_error,
    create_team_relationship_error,
    create_team_bulk_operation_error,
    create_team_membership_error,
    create_team_capacity_error,
)

from .vacation_repository_exceptions import (
    VacationRepositoryError,
    VacationQueryError,
    VacationStatisticsError,
    VacationValidationRepositoryError,
    VacationRelationshipError,
    VacationBulkOperationError,
    VacationDateRangeError,
    VacationBalanceError,
    VacationApprovalError,
    create_vacation_query_error,
    create_vacation_statistics_error,
    create_vacation_validation_repository_error,
    create_vacation_relationship_error,
    create_vacation_bulk_operation_error,
    create_vacation_date_range_error,
    create_vacation_balance_error,
    create_vacation_approval_error,
)

from .status_code_repository_exceptions import (
    StatusCodeRepositoryError,
    StatusCodeDuplicateError,
    StatusCodeNotFoundError,
    StatusCodeValidationError,
    StatusCodeOrderingError,
    StatusCodeFilterError,
    StatusCodeStatisticsError,
    create_status_code_duplicate_error,
    create_status_code_not_found_error,
    create_status_code_validation_error,
    create_status_code_ordering_error,
    create_status_code_filter_error,
    create_status_code_statistics_error
)

__all__ = [
    # Base repository exceptions
    "RepositoryError",
    "RepositoryConnectionError", 
    "RepositoryIntegrityError",
    "RepositoryTimeoutError",
    "RepositoryTransactionError",
    "RepositoryValidationError",
    "convert_sqlalchemy_error",
    
    # Alert repository exceptions
    "AlertRepositoryError",
    "AlertStateTransitionError",
    "AlertBulkOperationError",
    "AlertQueryError",
    "AlertStatisticsError",
    "AlertValidationRepositoryError",
    "AlertRelationshipError",
    "AlertDateRangeError",
    
    # Alert repository helper functions
    "create_alert_state_transition_error",
    "create_alert_bulk_operation_error",
    "create_alert_query_error",
    "create_alert_statistics_error",
    "create_alert_validation_repository_error",
    "create_alert_relationship_error",
    "create_alert_date_range_error",
    
    # Client repository exceptions
    "ClientRepositoryError",
    "ClientQueryError",
    "ClientStatisticsError",
    "ClientValidationRepositoryError",
    "ClientRelationshipError",
    "ClientBulkOperationError",
    "ClientDateRangeError",
    
    # Client repository exception factories
    "create_client_query_error",
    "create_client_statistics_error",
    "create_client_validation_repository_error",
    "create_client_relationship_error",
    "create_client_bulk_operation_error",
    "create_client_date_range_error",
    
    # Employee repository exceptions
    "EmployeeRepositoryError",
    "EmployeeQueryError",
    "EmployeeStatisticsError",
    "EmployeeValidationRepositoryError",
    "EmployeeRelationshipError",
    "EmployeeBulkOperationError",
    "EmployeeDateRangeError",
    "EmployeeSkillsError",
    "EmployeeAvailabilityError",
    
    # Employee factory functions
    "create_employee_query_error",
    "create_employee_statistics_error",
    "create_employee_validation_repository_error",
    "create_employee_relationship_error",
    "create_employee_bulk_operation_error",
    "create_employee_date_range_error",
    "create_employee_skills_error",
    "create_employee_availability_error",
    
    # Project repository exceptions
    "ProjectRepositoryError",
    "ProjectQueryError",
    "ProjectStatisticsError",
    "ProjectValidationRepositoryError",
    "ProjectRelationshipError",
    "ProjectBulkOperationError",
    "ProjectDateRangeError",
    "ProjectReferenceError",
    "ProjectTrigramError",
    "ProjectWorkloadError",
    
    # Project factory functions
    "create_project_query_error",
    "create_project_statistics_error",
    "create_project_validation_repository_error",
    "create_project_relationship_error",
    "create_project_bulk_operation_error",
    "create_project_date_range_error",
    "create_project_reference_error",
    "create_project_trigram_error",
    "create_project_workload_error",

    # Schedule repository exceptions
    "ScheduleRepositoryError",
    "ScheduleQueryError",
    "ScheduleStatisticsError",
    "ScheduleValidationRepositoryError",
    "ScheduleRelationshipError",
    "ScheduleBulkOperationError",
    "ScheduleDateRangeError",
    "ScheduleOverlapError",

    # Schedule factory functions
    "create_schedule_query_error",
    "create_schedule_statistics_error",
    "create_schedule_validation_repository_error",
    "create_schedule_relationship_error",
    "create_schedule_bulk_operation_error",
    "create_schedule_date_range_error",
    "create_schedule_overlap_error",

    # Workload repository exceptions
    "WorkloadRepositoryError",
    "WorkloadQueryError",
    "WorkloadStatisticsError",
    "WorkloadValidationRepositoryError",
    "WorkloadRelationshipError",
    "WorkloadBulkOperationError",
    "WorkloadDateRangeError",
    "WorkloadCapacityError",

    # Workload factory functions
    "create_workload_query_error",
    "create_workload_statistics_error",
    "create_workload_validation_repository_error",
    "create_workload_relationship_error",
    "create_workload_bulk_operation_error",
    "create_workload_date_range_error",
    "create_workload_capacity_error",

    # Team repository exceptions
    "TeamRepositoryError",
    "TeamQueryError",
    "TeamStatisticsError",
    "TeamValidationRepositoryError",
    "TeamRelationshipError",
    "TeamBulkOperationError",
    "TeamMembershipError",
    "TeamCapacityError",

    # Team factory functions
    "create_team_query_error",
    "create_team_statistics_error",
    "create_team_validation_repository_error",
    "create_team_relationship_error",
    "create_team_bulk_operation_error",
    "create_team_membership_error",
    "create_team_capacity_error",

    # Vacation repository exceptions
    "VacationRepositoryError",
    "VacationQueryError",
    "VacationStatisticsError",
    "VacationValidationRepositoryError",
    "VacationRelationshipError",
    "VacationBulkOperationError",
    "VacationDateRangeError",
    "VacationBalanceError",
    "VacationApprovalError",

    # Vacation factory functions
    "create_vacation_query_error",
    "create_vacation_statistics_error",
    "create_vacation_validation_repository_error",
    "create_vacation_relationship_error",
    "create_vacation_bulk_operation_error",
    "create_vacation_date_range_error",
    "create_vacation_balance_error",
    "create_vacation_approval_error",
    # StatusCode Repository Exceptions
    "StatusCodeRepositoryError",
    "StatusCodeDuplicateError",
    "StatusCodeNotFoundError",
    "StatusCodeValidationError",
    "StatusCodeOrderingError",
    "StatusCodeFilterError",
    "StatusCodeStatisticsError",
    # StatusCode Repository Exception Creators
    "create_status_code_duplicate_error",
    "create_status_code_not_found_error",
    "create_status_code_validation_error",
    "create_status_code_ordering_error",
    "create_status_code_filter_error",
    "create_status_code_statistics_error",
]