# src/planificador/database/repositories/client/__init__.py

"""  
Módulo de repositorio de clientes con patrón Facade.

Este módulo implementa el patrón Facade para organizar la funcionalidad
del repositorio de clientes en clases especializadas coordinadas.

Clases principales:
- ClientRepository: Alias del Facade para compatibilidad hacia atrás
- ClientRepositoryFacade: Implementación del patrón Facade
- ClientQueryBuilder: Constructor de consultas SQLAlchemy
- ClientStatistics: Generador de estadísticas y métricas
- ClientValidator: Validador de datos de clientes
- ClientRelationshipManager: Gestor de relaciones con proyectos

Uso recomendado:
    from planificador.database.repositories.client import ClientRepository

    # ClientRepository ahora es un Facade que coordina automáticamente
    # todas las funcionalidades especializadas
    client_repo = ClientRepository(session)

    # También se pueden usar las clases especializadas individualmente
    from planificador.database.repositories.client import ClientQueryBuilder
    query_builder = ClientQueryBuilder(session)
"""

from .client_repository_facade import ClientRepositoryFacade

# Nuevos módulos extraídos (arquitectura modular)
from .modules.crud_operations import CrudOperations
from .modules.query_operations import QueryOperations
from .modules.advanced_query_operations import AdvancedQueryOperations
from .modules.validation_operations import ValidationOperations
from .modules.statistics_operations import StatisticsOperations
from .modules.relationship_operations import RelationshipOperations
from .modules.date_operations import DateOperations
from .modules.health_operations import HealthOperations


# Alias para compatibilidad - ahora ClientRepository apunta al Facade
ClientRepository = ClientRepositoryFacade
ClientRepositoryRefactored = ClientRepositoryFacade

__all__ = [
    "ClientRepository",
    "ClientRepositoryFacade",
    "ClientRepositoryRefactored",
    # Nuevos módulos
    "CrudOperations",
    "QueryOperations",
    "AdvancedQueryOperations",
    "ValidationOperations",
    "StatisticsOperations",
    "RelationshipOperations",
    "DateOperations",
    "HealthOperations",
]
