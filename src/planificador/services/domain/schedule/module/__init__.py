"""
Paquete de Implementaciones del Servicio de Dominio Schedule.

Este paquete contiene todas las implementaciones concretas de las interfaces
del servicio de dominio Schedule, organizadas por categorías funcionales.
"""

from .crud_operations import ScheduleDomainCrudOperations
from .employee_operations import ScheduleDomainEmployeeOperations
from .project_operations import ScheduleDomainProjectOperations
from .team_operations import ScheduleDomainTeamOperations
from .search_operations import ScheduleDomainSearchOperations
from .confirmation_operations import ScheduleDomainConfirmationOperations
from .statistics_operations import ScheduleDomainStatisticsOperations
from .productivity_operations import ScheduleDomainProductivityOperations
from .validation_operations import ScheduleDomainValidationOperations
from .diagnostic_operations import ScheduleDomainDiagnosticOperations

__all__ = [
    # Operaciones CRUD
    "ScheduleDomainCrudOperations",
    
    # Operaciones por Empleado
    "ScheduleDomainEmployeeOperations",
    
    # Operaciones por Proyecto
    "ScheduleDomainProjectOperations",
    
    # Operaciones por Equipo
    "ScheduleDomainTeamOperations",
    
    # Operaciones de Búsqueda y Filtrado
    "ScheduleDomainSearchOperations",
    
    # Operaciones de Confirmación
    "ScheduleDomainConfirmationOperations",
    
    # Operaciones de Estadísticas
    "ScheduleDomainStatisticsOperations",
    
    # Operaciones de Productividad
    "ScheduleDomainProductivityOperations",
    
    # Operaciones de Validación
    "ScheduleDomainValidationOperations",
    
    # Operaciones de Diagnóstico
    "ScheduleDomainDiagnosticOperations",
]