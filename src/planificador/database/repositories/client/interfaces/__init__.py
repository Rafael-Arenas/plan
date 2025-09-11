"""Interfaces para romper dependencias circulares en repositorios de cliente.

Este módulo contiene las interfaces abstractas que permiten la inyección de
dependencias y evitan las referencias circulares entre las clases especializadas
del repositorio de cliente.

Interfaces disponibles:
    - IClientValidator: Interface para validación de datos de cliente
    - IClientQueryBuilder: Interface para construcción de consultas
    - IClientStatistics: Interface para operaciones estadísticas

Example:
    >>> from planificador.database.repositories.client.interfaces import IClientValidator
    >>> # Usar la interface para inyección de dependencias
"""

from .i_client_query_builder import IClientQueryBuilder
from .i_client_statistics import IClientStatistics
from .i_client_validator import IClientValidator


__all__ = ["IClientQueryBuilder", "IClientStatistics", "IClientValidator"]
