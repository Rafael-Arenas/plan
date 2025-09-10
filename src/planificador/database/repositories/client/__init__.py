# src/planificador/database/repositories/client/__init__.py

"""
Módulo de repositorio de clientes refactorizado.

Este módulo organiza la funcionalidad del repositorio de clientes
en clases especializadas para mejorar la mantenibilidad y legibilidad.

Clases principales:
- ClientRepository: Repositorio principal refactorizado
- ClientQueryBuilder: Constructor de consultas SQLAlchemy
- ClientStatistics: Generador de estadísticas y métricas
- ClientValidator: Validador de datos de clientes
- ClientRelationshipManager: Gestor de relaciones con proyectos

Uso recomendado:
    from planificador.database.repositories.client import ClientRepository
    
    # El ClientRepository refactorizado incluye automáticamente
    # todas las funcionalidades especializadas
    client_repo = ClientRepository(session)
    
    # También se pueden usar las clases especializadas individualmente
    from planificador.database.repositories.client import ClientQueryBuilder
    query_builder = ClientQueryBuilder(session)
"""

from .client_repository import ClientRepository
from .client_query_builder import ClientQueryBuilder
from .client_statistics import ClientStatistics
from .client_validator import ClientValidator
from .client_relationship_manager import ClientRelationshipManager

# Alias para compatibilidad
ClientRepositoryRefactored = ClientRepository

__all__ = [
    'ClientRepository',
    'ClientRepositoryRefactored',
    'ClientQueryBuilder',
    'ClientStatistics',
    'ClientValidator',
    'ClientRelationshipManager'
]