# src/planificador/services/domain/project_assignment/modules/__init__.py

"""
Módulos de operaciones para el servicio de dominio de asignaciones de proyecto.

Este paquete contiene las implementaciones concretas de todas las interfaces
de operaciones definidas para el manejo de asignaciones de proyecto.
"""

from .crud_operations import CrudOperations
from .employee_queries import EmployeeQueries
from .project_queries import ProjectQueries
from .search_operations import SearchOperations
from .resource_management import ResourceManagement
from .statistics_operations import StatisticsOperations
from .validation_operations import ValidationOperations
from .diagnostic_operations import DiagnosticOperations

__all__ = [
    "CrudOperations",
    "EmployeeQueries", 
    "ProjectQueries",
    "SearchOperations",
    "ResourceManagement",
    "StatisticsOperations",
    "ValidationOperations",
    "DiagnosticOperations"
]