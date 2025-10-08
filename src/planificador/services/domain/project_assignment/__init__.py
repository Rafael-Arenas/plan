"""
Paquete de Servicios de Dominio para Asignaciones de Proyecto.

Este paquete implementa el patrón Facade para proporcionar una interfaz
unificada y simplificada para todas las operaciones del dominio de
asignaciones de proyecto.
"""

from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from .interfaces import *
from .modules import *
from .project_assignment_domain_service import ProjectAssignmentDomainService

__all__ = [
    # Domain Service (Main Facade)
    "ProjectAssignmentDomainService",
    
    # Repository Facade
    "ProjectAssignmentRepositoryFacade",
    
    # Interfaces
    "ICrudOperations",
    "IEmployeeQueries", 
    "IProjectQueries",
    "ISearchOperations",
    "IResourceManagement",
    "IStatisticsOperations",
    "IValidationOperations",
    "IDiagnosticOperations",
    
    # Modules
    "CrudOperations",
    "EmployeeQueries",
    "ProjectQueries", 
    "SearchOperations",
    "ResourceManagement",
    "StatisticsOperations",
    "ValidationOperations",
    "DiagnosticOperations"
]