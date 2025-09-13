"""Módulo de operaciones de consulta para clientes.

Este módulo implementa la interfaz IQueryOperations y proporciona
funcionalidades especializadas para consultas básicas de clientes, ahora
optimizadas mediante la herencia de BaseRepository.

Versión: 2.1.0
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.client import Client
from planificador.repositories.base_repository import BaseRepository, ModelType
from ..interfaces.query_interface import IQueryOperations


class QueryOperations(BaseRepository[Client], IQueryOperations):
    """Implementación de operaciones de consulta para clientes.

    Hereda de BaseRepository para reutilizar la lógica de acceso a datos
    y se especializa en consultas comunes sobre la entidad Client.
    """

    def __init__(self, session: AsyncSession):
        """Inicializa las operaciones de consulta.

        Args:
            session: Sesión asíncrona de SQLAlchemy.
        """
        super().__init__(session, Client)

    async def _find_one_by_criteria(self, criteria: dict[str, Any]) -> Client | None:
        """Encuentra una entidad que coincida con los criterios."""
        results = await self.find_by_criteria(criteria, limit=1)
        return results[0] if results else None

    async def get_client_by_id(self, client_id: int) -> Client | None:
        """Obtiene un cliente por su ID."""
        return await self.get_by_id(client_id)

    async def get_client_by_name(self, name: str) -> Client | None:
        """Busca un cliente por nombre exacto (case-insensitive)."""
        return await self._find_one_by_criteria(
            {"name": {"operator": "iexact", "value": name}}
        )

    async def get_client_by_code(self, code: str) -> Client | None:
        """Busca un cliente por código único."""
        return await self._find_one_by_criteria({"code": code})

    async def get_client_by_email(self, email: str) -> Client | None:
        """Busca un cliente por email (case-insensitive)."""
        return await self._find_one_by_criteria(
            {"email": {"operator": "iexact", "value": email}}
        )

    async def search_clients_by_name(self, name_pattern: str) -> list[Client]:
        """Busca clientes por patrón de nombre (case-insensitive)."""
        return await self.find_by_criteria(
            criteria={"name": {"operator": "ilike", "value": name_pattern}}
        )

    async def get_all_clients(
        self, limit: int | None = None, offset: int = 0
    ) -> list[Client]:
        """Obtiene todos los clientes con paginación opcional."""
        return await self.get_all(limit=limit, offset=offset)

    async def get_by_unique_field(self, field_name: str, value: Any) -> ModelType | None:
        """Obtiene una entidad por un campo único específico."""
        return await self._find_one_by_criteria({field_name: value})