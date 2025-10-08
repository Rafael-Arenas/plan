# src/planificador/services/domain/project_assignment/interfaces/__init__.py

"""
Interfaces del Dominio de Asignaciones de Proyecto

Este módulo define los contratos (interfaces) para todas las operaciones
del dominio de asignaciones de proyecto, organizadas por categorías funcionales.

Categorías de Interfaces:
- IProjectAssignmentDomainService: Interfaz principal del Facade
- ICrudOperations: Operaciones CRUD básicas y especializadas
- IEmployeeQueries: Consultas centradas en empleados
- IProjectQueries: Consultas centradas en proyectos
- ISearchOperations: Búsqueda y filtrado avanzado
- IResourceManagement: Gestión de recursos y capacidades
- IStatisticsOperations: Estadísticas básicas y avanzadas
- IValidationOperations: Validaciones y reglas de negocio
- IDiagnosticOperations: Diagnóstico y salud del sistema

Estas interfaces garantizan la consistencia arquitectural y facilitan
el testing mediante dependency injection y mocking.
"""

from .project_assignment_domain_interface import IProjectAssignmentDomainService
from .crud_operations_interface import ICrudOperations
from .employee_queries_interface import IEmployeeQueries
from .project_queries_interface import IProjectQueries
from .search_operations_interface import ISearchOperations
from .resource_management_interface import IResourceManagement
from .statistics_operations_interface import IStatisticsOperations
from .validation_operations_interface import IValidationOperations
from .diagnostic_operations_interface import IDiagnosticOperations

__all__ = [
    # Interfaz principal del Facade
    "IProjectAssignmentDomainService",
    
    # Interfaces de operaciones por categoría
    "ICrudOperations",
    "IEmployeeQueries", 
    "IProjectQueries",
    "ISearchOperations",
    "IResourceManagement",
    "IStatisticsOperations",
    "IValidationOperations",
    "IDiagnosticOperations",
]