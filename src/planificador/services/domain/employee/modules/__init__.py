# -*- coding: utf-8 -*-
"""
Employee Domain Service - Implementation Modules

Módulos de implementación concreta para el servicio de dominio Employee.
Cada módulo se especializa en un conjunto específico de operaciones.

Modules:
    - CrudOperations: Operaciones CRUD básicas
    - QueryOperations: Consultas y búsquedas básicas
    - AdvancedQueryOperations: Consultas avanzadas y filtros complejos
    - DateOperations: Operaciones relacionadas con fechas
    - RelationshipOperations: Gestión de relaciones jerárquicas
    - StatisticsOperations: Generación de estadísticas y reportes
    - ValidationOperations: Validaciones de reglas de negocio
    - HealthOperations: Monitoreo y métricas del servicio
"""

from .crud_operations import CrudOperations
from .query_operations import QueryOperations
from .advanced_query_operations import AdvancedQueryOperations
from .date_operations import DateOperations
from .relationship_operations import RelationshipOperations
from .statistics_operations import StatisticsOperations
from .validation_operations import ValidationOperations
from .health_operations import HealthOperations

__all__ = [
    "CrudOperations",
    "QueryOperations", 
    "AdvancedQueryOperations",
    "DateOperations",
    "RelationshipOperations",
    "StatisticsOperations",
    "ValidationOperations",
    "HealthOperations",
]