"""
Interfaces del Servicio de Dominio Schedule.

Este módulo contiene todas las interfaces que definen los contratos
para las diferentes categorías de operaciones del servicio de dominio
de horarios, organizadas por categorías funcionales.

Categorías de Interfaces:
- IScheduleDomainService: Interfaz principal del Facade
- IScheduleDomainCrudOperations: Operaciones CRUD básicas y especializadas
- IScheduleDomainEmployeeOperations: Consultas y operaciones centradas en empleados
- IScheduleDomainProjectOperations: Consultas y operaciones centradas en proyectos
- IScheduleDomainTeamOperations: Consultas y operaciones centradas en equipos
- IScheduleDomainSearchOperations: Búsqueda y filtrado avanzado
- IScheduleDomainConfirmationOperations: Operaciones de confirmación de horarios
- IScheduleDomainStatisticsOperations: Estadísticas básicas y avanzadas
- IScheduleDomainProductivityOperations: Análisis de productividad y rendimiento
- IScheduleDomainValidationOperations: Validaciones y reglas de negocio
- IScheduleDomainDiagnosticOperations: Diagnóstico y salud del sistema

Estas interfaces garantizan la consistencia arquitectural y facilitan
el testing mediante dependency injection y mocking.
"""

from .schedule_domain_interface import IScheduleDomainService
from .crud_operations_interface import IScheduleDomainCrudOperations
from .employee_operations_interface import IScheduleDomainEmployeeOperations
from .project_operations_interface import IScheduleDomainProjectOperations
from .team_operations_interface import IScheduleDomainTeamOperations
from .search_operations_interface import IScheduleDomainSearchOperations
from .confirmation_operations_interface import IScheduleDomainConfirmationOperations
from .statistics_operations_interface import IScheduleDomainStatisticsOperations
from .productivity_operations_interface import IScheduleDomainProductivityOperations
from .validation_operations_interface import IScheduleDomainValidationOperations
from .diagnostic_operations_interface import IScheduleDomainDiagnosticOperations

__all__ = [
    # Interfaz principal del Facade
    "IScheduleDomainService",
    
    # Interfaces de operaciones por categoría
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