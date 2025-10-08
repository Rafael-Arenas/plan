"""
Interfaces del Servicio de Dominio Schedule.

Este módulo contiene todas las interfaces que definen los contratos
para las diferentes categorías de operaciones del servicio de dominio
de horarios.
"""

from .crud_operations import IScheduleDomainCrudOperations
from .employee_operations import IScheduleDomainEmployeeOperations
from .project_operations import IScheduleDomainProjectOperations
from .team_operations import IScheduleDomainTeamOperations
from .search_operations import IScheduleDomainSearchOperations
from .confirmation_operations import IScheduleDomainConfirmationOperations
from .statistics_operations import IScheduleDomainStatisticsOperations
from .productivity_operations import IScheduleDomainProductivityOperations
from .validation_operations import IScheduleDomainValidationOperations
from .diagnostic_operations import IScheduleDomainDiagnosticOperations

__all__ = [
    "IScheduleDomainCrudOperations",
    "IScheduleDomainEmployeeOperations", 
    "IScheduleDomainProjectOperations",
    "IScheduleDomainTeamOperations",
    "IScheduleDomainSearchOperations",
    "IScheduleDomainConfirmationOperations",
    "IScheduleDomainStatisticsOperations",
    "IScheduleDomainProductivityOperations",
    "IScheduleDomainValidationOperations",
    "IScheduleDomainDiagnosticOperations"
]