# -*- coding: utf-8 -*-
"""
Paquete de Servicios de Dominio Cliente

Este paquete contiene todos los servicios relacionados con la lógica de negocio
del dominio cliente, incluyendo operaciones CRUD, consultas avanzadas, 
validaciones, estadísticas y más.

Estructura:
- interfaces/: Interfaces que definen contratos para operaciones especializadas
- modules/: Implementaciones concretas de las interfaces
- client_domain_service.py: Facade principal que unifica todos los módulos

Características principales:
- Separación clara de responsabilidades
- Interfaces bien definidas para cada tipo de operación
- Implementaciones modulares y reutilizables
- Integración con el sistema de repositorios
- Logging estructurado y manejo robusto de errores
"""

# Exportar el facade principal
from .client_domain_service import ClientDomainService

# Exportar la interfaz principal del dominio
from .interfaces.client_domain_interface import IClientDomainService

# Exportar las interfaces principales
from .interfaces.crud_interface import ICrudOperations
from .interfaces.query_interface import IQueryOperations
from .interfaces.advanced_query_interface import IAdvancedQueryOperations
from .interfaces.statistics_interface import IStatisticsOperations
from .interfaces.relationship_interface import IRelationshipOperations
from .interfaces.date_interface import IDateOperations
from .interfaces.validation_interface import IValidationOperations
from .interfaces.health_interface import IHealthOperations

# Exportar las implementaciones de módulos
from .modules.crud_operations import CrudOperations
from .modules.query_operations import QueryOperations
from .modules.advanced_query_operations import AdvancedQueryOperations
from .modules.statistics_operations import StatisticsOperations
from .modules.relationship_operations import RelationshipOperations
from .modules.date_operations import DateOperations
from .modules.validation_operations import ValidationOperations
from .modules.health_operations import HealthOperations

__all__ = [
    # Facade principal
    "ClientDomainService",
    
    # Interfaz principal del dominio
    "IClientDomainService",
    
    # Interfaces
    "ICrudOperations",
    "IQueryOperations", 
    "IAdvancedQueryOperations",
    "IStatisticsOperations",
    "IRelationshipOperations",
    "IDateOperations",
    "IValidationOperations",
    "IHealthOperations",
    
    # Implementaciones
    "CrudOperations",
    "QueryOperations",
    "AdvancedQueryOperations", 
    "StatisticsOperations",
    "RelationshipOperations",
    "DateOperations",
    "ValidationOperations",
    "HealthOperations",
]