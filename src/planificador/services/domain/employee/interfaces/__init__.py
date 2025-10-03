# -*- coding: utf-8 -*-
"""
Employee Domain Service Interfaces

Este módulo contiene todas las interfaces que definen los contratos
para las operaciones del dominio de empleados.

Interfaces disponibles:
- IEmployeeDomainService: Interfaz principal del facade
- ICrudOperations: Operaciones CRUD especializadas
- IQueryOperations: Consultas básicas
- IAdvancedQueryOperations: Consultas avanzadas
- IDateOperations: Operaciones de fechas y tiempo
- IRelationshipOperations: Gestión de relaciones
- IStatisticsOperations: Estadísticas y métricas
- IValidationOperations: Validaciones de negocio
- IHealthOperations: Health checks del servicio
"""

from .employee_domain_interface import IEmployeeDomainService
from .crud_interface import ICrudOperations
from .query_interface import IQueryOperations
from .advanced_query_interface import IAdvancedQueryOperations
from .date_interface import IDateOperations
from .relationship_interface import IRelationshipOperations
from .statistics_interface import IStatisticsOperations
from .validation_interface import IValidationOperations
from .health_interface import IHealthOperations

__all__ = [
    "IEmployeeDomainService",
    "ICrudOperations",
    "IQueryOperations",
    "IAdvancedQueryOperations",
    "IDateOperations",
    "IRelationshipOperations",
    "IStatisticsOperations",
    "IValidationOperations",
    "IHealthOperations",
]