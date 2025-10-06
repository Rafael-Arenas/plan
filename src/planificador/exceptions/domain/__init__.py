# src/planificador/exceptions/domain/__init__.py

"""
Excepciones del dominio de la aplicación.

Este módulo centraliza todas las excepciones específicas de los dominios
de negocio de la aplicación, incluyendo clientes y proyectos.
"""

# Excepciones del dominio de clientes
from .client_domain_exceptions import (
    ClientDomainError,
    ClientBusinessRuleViolationError,
    ClientDependencyError,
    ClientProjectTransferError,
)

# Excepciones del dominio de proyectos
from .project_domain_exceptions import (
    # Excepciones base
    ProjectDomainError,
    
    # Excepciones de validación
    ProjectValidationError,
    ProjectDateValidationError,
    ProjectCodeDuplicateError,
    ProjectTrigramDuplicateError,
    
    # Excepciones de lógica de negocio
    ProjectBusinessRuleViolationError,
    ProjectStatusTransitionError,
    
    # Excepciones de asignaciones y relaciones
    ProjectAssignmentError,
    ProjectCapacityExceededError,
    ProjectClientRelationshipError,
    
    # Excepciones de operaciones masivas
    ProjectBulkOperationError,
    ProjectCloneError,
    
    # Excepciones de estadísticas y análisis
    ProjectStatisticsError,
    
    # Excepciones de planificación y cronogramas
    ProjectPlanningError,
    ProjectTimelineConflictError,
    
    # Funciones de utilidad
    create_project_not_found_error,
    create_project_validation_error,
    create_project_business_rule_error,
)

# Exportar todas las excepciones del dominio
__all__ = [
    # Excepciones del dominio de clientes
    "ClientDomainError",
    "ClientBusinessRuleViolationError", 
    "ClientDependencyError",
    "ClientProjectTransferError",
    
    # Excepciones del dominio de proyectos - Base
    "ProjectDomainError",
    
    # Excepciones del dominio de proyectos - Validación
    "ProjectValidationError",
    "ProjectDateValidationError",
    "ProjectCodeDuplicateError",
    "ProjectTrigramDuplicateError",
    
    # Excepciones del dominio de proyectos - Lógica de negocio
    "ProjectBusinessRuleViolationError",
    "ProjectStatusTransitionError",
    
    # Excepciones del dominio de proyectos - Asignaciones y relaciones
    "ProjectAssignmentError",
    "ProjectCapacityExceededError",
    "ProjectClientRelationshipError",
    
    # Excepciones del dominio de proyectos - Operaciones masivas
    "ProjectBulkOperationError",
    "ProjectCloneError",
    
    # Excepciones del dominio de proyectos - Estadísticas y análisis
    "ProjectStatisticsError",
    
    # Excepciones del dominio de proyectos - Planificación y cronogramas
    "ProjectPlanningError",
    "ProjectTimelineConflictError",
    
    # Funciones de utilidad para proyectos
    "create_project_not_found_error",
    "create_project_validation_error",
    "create_project_business_rule_error",
]