"""
Interfaces para el servicio de dominio de proyectos.

Este módulo contiene todas las interfaces que definen los contratos
para las operaciones de gestión de proyectos, organizadas de manera
modular para facilitar el mantenimiento y la extensibilidad.

Interfaces disponibles:
- IProjectCrudOperations: Operaciones CRUD básicas
- IProjectQueryOperations: Consultas y búsquedas
- IProjectValidationOperations: Validaciones de datos y reglas de negocio
- IProjectAdvancedQueryOperations: Consultas complejas y análisis avanzados
- IProjectRelationshipOperations: Gestión de relaciones entre entidades
- IProjectStatisticsOperations: Estadísticas y métricas
- IProjectDatePlanningOperations: Planificación temporal y gestión de fechas
- IProjectDiagnosticOperations: Diagnósticos de salud y detección de anomalías
- IProjectDomainService: Interfaz principal que hereda de todas las anteriores
"""

from .crud_operations_interface import IProjectCrudOperations
from .query_operations_interface import IProjectQueryOperations
from .validation_operations_interface import IProjectValidationOperations
from .advanced_query_operations_interface import IProjectAdvancedQueryOperations
from .relationship_operations_interface import IProjectRelationshipOperations
from .statistics_operations_interface import IProjectStatisticsOperations
from .date_planning_operations_interface import IProjectDatePlanningOperations
from .diagnostic_operations_interface import IProjectDiagnosticOperations
from .project_domain_interface import IProjectDomainService

__all__ = [
    "IProjectCrudOperations",
    "IProjectQueryOperations", 
    "IProjectValidationOperations",
    "IProjectAdvancedQueryOperations",
    "IProjectRelationshipOperations",
    "IProjectStatisticsOperations",
    "IProjectDatePlanningOperations",
    "IProjectDiagnosticOperations",
    "IProjectDomainService",
]