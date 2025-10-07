"""
Módulo de servicios de dominio para proyectos.

Este módulo proporciona servicios de dominio especializados para la gestión
de proyectos, implementando patrones de arquitectura limpia y separación
de responsabilidades.

Exports:
    - ProjectDomainService: Servicio principal de dominio para proyectos
    - IProjectDomainService: Interfaz del servicio de dominio
    - Módulos especializados para operaciones específicas
"""

from .project_domain_service import ProjectDomainService
from .interfaces.project_domain_interface import IProjectDomainService

# Módulos especializados
from .modules.crud_operations import ProjectCrudOperations
from .modules.query_operations import ProjectQueryOperations
from .modules.advanced_query_operations import ProjectAdvancedQueryOperations
from .modules.date_planning_operations import ProjectDatePlanningOperations
from .modules.relationship_operations import ProjectRelationshipOperations
from .modules.statistics_operations import ProjectStatisticsOperations
from .modules.validation_operations import ProjectValidationOperations
from .modules.diagnostic_operations import ProjectDiagnosticOperations

__all__ = [
    # Servicio principal
    "ProjectDomainService",
    "IProjectDomainService",
    
    # Módulos especializados
    "ProjectCrudOperations",
    "ProjectQueryOperations", 
    "ProjectAdvancedQueryOperations",
    "ProjectDatePlanningOperations",
    "ProjectRelationshipOperations",
    "ProjectStatisticsOperations",
    "ProjectValidationOperations",
    "ProjectDiagnosticOperations",
]

# Información del módulo
__version__ = "1.0.0"
__author__ = "AkGroup Development Team"
__description__ = "Servicios de dominio para gestión de proyectos"