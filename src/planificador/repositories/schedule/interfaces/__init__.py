# src/planificador/repositories/schedule/interfaces/__init__.py

"""
Interfaces del repositorio Schedule.

Este módulo contiene las interfaces abstractas que definen los contratos
para las operaciones del repositorio de horarios.
"""

from .crud_interface import IScheduleCrudOperations
from .query_interface import IScheduleQueryOperations
from .validation_interface import IScheduleValidationOperations
from .statistics_interface import IScheduleStatisticsOperations
from .relationship_interface import IScheduleRelationshipOperations

__all__ = [
    "IScheduleCrudOperations",
    "IScheduleQueryOperations",
    "IScheduleValidationOperations",
    "IScheduleStatisticsOperations",
    "IScheduleRelationshipOperations",
]