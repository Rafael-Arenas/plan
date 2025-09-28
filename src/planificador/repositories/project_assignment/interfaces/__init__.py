"""Interfaces para el repositorio de asignaciones de proyectos."""

from .crud_interface import ICrudOperations
from .query_interface import IQueryOperations
from .relationship_interface import IRelationshipOperations
from .statistics_interface import IStatisticsOperations
from .validation_interface import IValidationOperations

__all__ = [
    "ICrudOperations",
    "IQueryOperations", 
    "IRelationshipOperations",
    "IStatisticsOperations",
    "IValidationOperations",
]