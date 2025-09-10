# src/planificador/database/repositories/__init__.py
"""
Módulo de repositorios para operaciones de base de datos.

Este módulo proporciona la infraestructura base para todos los repositorios
del sistema, incluyendo operaciones CRUD estándar y manejo de errores.
"""

from .base_repository import BaseRepository
from .client import ClientRepository

__all__ = [
    "BaseRepository",
    "ClientRepository",
]

# Versión del módulo de repositorios
__version__ = "1.0.0"