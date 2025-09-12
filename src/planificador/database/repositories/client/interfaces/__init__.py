"""Interfaces para los módulos del ClientRepositoryFacade.

Este paquete define los contratos que deben cumplir cada uno de los
módulos especializados del facade.
"""

from .crud_interface import ICrudOperations
from .query_interface import IQueryOperations
from .advanced_query_interface import IAdvancedQueryOperations
from .search_interface import ISearchOperations
from .statistics_interface import IStatisticsOperations
from .validation_interface import IValidationOperations
from .relationship_interface import IRelationshipOperations
from .date_interface import IDateOperations
from .health_interface import IHealthOperations

__all__ = [
    "ICrudOperations",
    "IQueryOperations",
    "IAdvancedQueryOperations",
    "ISearchOperations",
    "IStatisticsOperations", 
    "IValidationOperations",
    "IRelationshipOperations",
    "IDateOperations",
    "IHealthOperations",
]
