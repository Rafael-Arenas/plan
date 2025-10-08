# src/planificador/schemas/schedule/__init__.py

from .schedule import (
    ScheduleBase,
    ScheduleCreate,
    ScheduleUpdate,
    Schedule,
    ScheduleSearchFilter,
    ProductivityMetricsSchema,
    UtilizationReportSchema,
    ScheduleDistributionSchema,
    ValidationResultSchema,
    ConflictValidationSchema,
    TeamCoordinationValidationSchema,
    WorkloadValidationSchema,
)

from .confirmation_schemas import (
    ScheduleConfirmationSchema,
    BulkConfirmationSchema,
    ConfirmationResponseSchema,
    PendingConfirmationSchema,
    ConfirmationFilterSchema,
)

# Statistics schemas
from .statistics_schemas import (
    EmployeeHoursSummarySchema,
    ProjectHoursSummarySchema,
    TeamHoursSummarySchema,
    OvertimeAnalysisSchema,
    ScheduleStatisticsSummarySchema,
    ProductivityTrendsSchema,
)

__all__ = [
    # Esquemas básicos de Schedule
    "ScheduleBase",
    "ScheduleCreate", 
    "ScheduleUpdate",
    "Schedule",
    "ScheduleSearchFilter",
    
    # Esquemas de análisis de productividad
    "ProductivityMetricsSchema",
    "UtilizationReportSchema",
    "ScheduleDistributionSchema",
    
    # Esquemas de validación
    "ValidationResultSchema",
    "ConflictValidationSchema",
    "TeamCoordinationValidationSchema",
    "WorkloadValidationSchema",
    
    # Esquemas de confirmación
    "ScheduleConfirmationSchema",
    "BulkConfirmationSchema",
    "ConfirmationResponseSchema",
    "PendingConfirmationSchema",
    "ConfirmationFilterSchema",
    
    # Statistics schemas
    "EmployeeHoursSummarySchema",
    "ProjectHoursSummarySchema",
    "TeamHoursSummarySchema",
    "OvertimeAnalysisSchema",
    "ScheduleStatisticsSummarySchema",
    "ProductivityTrendsSchema",
]