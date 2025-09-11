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

from .client_query_builder import ClientQueryBuilder
from .client_relationship_manager import ClientRelationshipManager
from .client_repository_facade import ClientRepositoryFacade
from .client_statistics import ClientStatistics
from .client_validator import ClientValidator


# Alias para compatibilidad - ahora ClientRepository apunta al Facade
ClientRepository = ClientRepositoryFacade
ClientRepositoryRefactored = ClientRepositoryFacade

__all__ = [
    "ClientQueryBuilder",
    "ClientRelationshipManager",
    "ClientRepository",
    "ClientRepositoryFacade",
    "ClientRepositoryRefactored",
    "ClientStatistics",
    "ClientValidator",
]
