# src/planificador/repositories/alert/modules/__init__.py

"""
Módulo de implementaciones especializadas para el repositorio de alertas.

Este módulo contiene todas las implementaciones especializadas que
proporcionan funcionalidades específicas para el manejo de alertas.
"""

from .crud_operations import CrudOperations
from .query_operations import QueryOperations
from .statistics_operations import StatisticsOperations
from .state_manager import StateManager
from .validation_operations import ValidationOperations

__all__ = [
    "CrudOperations",
    "QueryOperations", 
    "StatisticsOperations",
    "StateManager",
    "ValidationOperations",
]

__version__ = "1.0.0"
__author__ = "Planificador Team"