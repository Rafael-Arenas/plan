"""Interface para construcción de consultas de cliente.

Esta interface define los métodos de construcción de consultas que deben ser
implementados por las clases de query builder, permitiendo la inyección de
dependencias y evitando referencias circulares.
"""

from abc import ABC, abstractmethod
from typing import Any

from planificador.models.client import Client


class IClientQueryBuilder(ABC):
    """Interface abstracta para construcción de consultas de cliente.

    Define los métodos que deben implementar las clases de construcción
    de consultas para operaciones con clientes.
    """

    @abstractmethod
    async def name_exists(
        self, name: str, exclude_id: int | None = None
    ) -> bool:
        """Verifica si existe un cliente con el nombre dado.

        Args:
            name: Nombre del cliente a verificar.
            exclude_id: ID del cliente a excluir de la búsqueda.

        Returns:
            True si existe un cliente con ese nombre, False en caso contrario.
        """
        pass

    @abstractmethod
    async def code_exists(
        self, code: str, exclude_id: int | None = None
    ) -> bool:
        """Verifica si existe un cliente con el código dado.

        Args:
            code: Código del cliente a verificar.
            exclude_id: ID del cliente a excluir de la búsqueda.

        Returns:
            True si existe un cliente con ese código, False en caso contrario.
        """
        pass

    @abstractmethod
    async def get_clients_by_filters(
        self,
        filters: dict[str, Any],
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Client]:
        """Obtiene clientes aplicando filtros específicos.

        Args:
            filters: Diccionario con los filtros a aplicar.
            limit: Número máximo de resultados.
            offset: Número de resultados a omitir.

        Returns:
            Lista de clientes que cumplen los filtros.
        """
        pass

    @abstractmethod
    async def search_clients_by_text(self, search_text: str) -> list[Client]:
        """Busca clientes por texto en nombre, código o email.

        Args:
            search_text: Texto a buscar.

        Returns:
            Lista de clientes que coinciden con la búsqueda.
        """
        pass

    @abstractmethod
    async def get_active_clients(self) -> list[Client]:
        """Obtiene todos los clientes activos.

        Returns:
            Lista de clientes activos.
        """
        pass
