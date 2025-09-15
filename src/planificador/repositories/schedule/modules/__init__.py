# src/planificador/repositories/schedule/modules/__init__.py

"""
Módulos operacionales del repositorio Schedule.

Este paquete contiene los módulos que implementan las operaciones
específicas del repositorio de horarios, organizados por responsabilidad:

- crud_module: Operaciones CRUD (Create, Read, Update, Delete)
- query_module: Operaciones de consulta y recuperación
- validation_module: Validaciones de datos y reglas de negocio
- statistics_module: Operaciones de estadísticas y métricas
- relationship_module: Gestión de relaciones y asignaciones
"""

from .crud_module import ScheduleCrudModule
from .query_module import ScheduleQueryModule
from .validation_module import ScheduleValidationModule
from .statistics_module import ScheduleStatisticsModule
from .relationship_module import ScheduleRelationshipModule

__all__ = [
    "ScheduleCrudModule",
    "ScheduleQueryModule",
    "ScheduleValidationModule",
    "ScheduleStatisticsModule",
    "ScheduleRelationshipModule",
]