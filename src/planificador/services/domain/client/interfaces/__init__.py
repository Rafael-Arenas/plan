# -*- coding: utf-8 -*-
"""
Client Domain Service Interfaces

Este módulo contiene todas las interfaces para las operaciones
del servicio de dominio de cliente.
"""

from .crud_interface import ICrudOperations
from .query_interface import IQueryOperations
from .advanced_query_interface import IAdvancedQueryOperations
from .statistics_interface import IStatisticsOperations
from .relationship_interface import IRelationshipOperations
from .date_interface import IDateOperations
from .validation_interface import IValidationOperations
from .health_interface import IHealthOperations

__all__ = [
    "ICrudOperations",
    "IQueryOperations", 
    "IAdvancedQueryOperations",
    "IStatisticsOperations",
    "IRelationshipOperations",
    "IDateOperations",
    "IValidationOperations",
    "IHealthOperations"
]