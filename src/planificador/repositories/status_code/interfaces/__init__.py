# src/planificador/repositories/status_code/interfaces/__init__.py

"""
Interfaces del repositorio de códigos de estado.

Este módulo exporta todas las interfaces abstractas que definen las operaciones
disponibles para el repositorio de códigos de estado, organizadas por
responsabilidad funcional.
"""

from .status_code_repository_interface import IStatusCodeRepository
from .crud_interface import IStatusCodeCrudOperations
from .query_interface import IStatusCodeQueryOperations
from .validation_interface import IStatusCodeValidationOperations
from .statistics_interface import IStatusCodeStatisticsOperations

__all__ = [
    # Interfaz principal del repositorio
    "IStatusCodeRepository",
    
    # Interfaces especializadas por operación
    "IStatusCodeCrudOperations",
    "IStatusCodeQueryOperations", 
    "IStatusCodeValidationOperations",
    "IStatusCodeStatisticsOperations",
]