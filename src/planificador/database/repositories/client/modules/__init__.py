"""Módulos especializados del ClientRepositoryFacade.

Este paquete contiene los módulos que implementan las diferentes
responsabilidades del facade de repositorio de clientes.
"""

from .crud_operations import CrudOperations
from .query_operations import QueryOperations
from .advanced_query_operations import AdvancedQueryOperations
from .statistics_operations import StatisticsOperations
from .validation_operations import ValidationOperations
from .relationship_operations import RelationshipOperations
from .date_operations import DateOperations
from .health_operations import HealthOperations

__all__ = [
    "CrudOperations",
    "QueryOperations",
    "AdvancedQueryOperations",
    "StatisticsOperations",
    "ValidationOperations",
    "RelationshipOperations",
    "DateOperations",
    "HealthOperations",
]