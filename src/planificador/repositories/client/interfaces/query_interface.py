"""Interfaz para operaciones de consulta de clientes.

Este módulo define las interfaces para operaciones de consulta básicas y
avanzadas sobre la entidad Client.

Autor: Sistema de Repositorios
Versión: 2.0.0
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from planificador.models.client import Client


class IQueryOperations(ABC):
    """Interfaz para operaciones de consulta básicas de clientes."""

    @abstractmethod
    async def get_client_by_id(self, client_id: int) -> Client | None:
        """Obtiene un cliente por su ID."""
        pass

    @abstractmethod
    async def get_client_by_name(self, name: str) -> Client | None:
        """Busca un cliente por nombre exacto (case-insensitive)."""
        pass

    @abstractmethod
    async def get_client_by_code(self, code: str) -> Client | None:
        """Busca un cliente por código único."""
        pass

    @abstractmethod
    async def get_client_by_email(self, email: str) -> Client | None:
        """Busca un cliente por email (case-insensitive)."""
        pass

    @abstractmethod
    async def search_clients_by_name(self, name_pattern: str) -> list[Client]:
        """Busca clientes por patrón de nombre (case-insensitive)."""
        pass

    @abstractmethod
    async def get_all_clients(
        self, limit: int | None = None, offset: int = 0
    ) -> list[Client]:
        """Obtiene todos los clientes con paginación opcional."""
        pass


class IAdvancedQueryOperations(ABC):
    """Interfaz para operaciones de consulta avanzadas de clientes."""

    @abstractmethod
    async def search_clients_by_text(
        self,
        search_text: str,
        fields: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Client]:
        """Busca clientes por texto en múltiples campos."""
        pass

    @abstractmethod
    async def get_clients_by_filters(
        self,
        filters: Dict[str, Any],
        limit: int = 50,
        offset: int = 0,
        order_by: Optional[str] = None,
    ) -> List[Client]:
        """Obtiene clientes aplicando múltiples filtros."""
        pass

    @abstractmethod
    async def get_clients_with_relationships(
        self,
        include_projects: bool = False,
        include_contacts: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Client]:
        """Obtiene clientes con sus relaciones cargadas."""
        pass

    @abstractmethod
    async def count_clients_by_filters(self, filters: Dict[str, Any]) -> int:
        """Cuenta clientes que cumplen los filtros especificados."""
        pass

    @abstractmethod
    async def search_clients_fuzzy(
        self, search_term: str, similarity_threshold: float = 0.3
    ) -> List[Client]:
        """Realiza búsqueda difusa de clientes."""
        pass