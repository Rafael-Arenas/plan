"""Interface para operaciones de búsqueda de clientes.

Define el contrato que deben cumplir las implementaciones de operaciones
de búsqueda y filtrado para la entidad Cliente.
"""

from abc import ABC, abstractmethod
from typing import Any

from planificador.models.client import Client


class ISearchOperations(ABC):
    """Interface para operaciones de búsqueda de clientes."""

    @abstractmethod
    async def search_clients_by_text(self, search_text: str) -> list[Client]:
        """Busca clientes por texto libre.
        
        Args:
            search_text: Texto a buscar en nombre, email, etc.
            
        Returns:
            Lista de clientes que coinciden con la búsqueda
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la búsqueda
        """
        pass

    @abstractmethod
    async def get_clients_by_filters(
        self, filters: dict[str, Any]
    ) -> list[Client]:
        """Obtiene clientes aplicando filtros específicos.
        
        Args:
            filters: Diccionario con filtros a aplicar
            
        Returns:
            Lista de clientes que cumplen los filtros
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def get_clients_with_contact_info(self) -> list[Client]:
        """Obtiene clientes que tienen información de contacto.
        
        Returns:
            Lista de clientes con información de contacto
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def get_clients_without_contact_info(self) -> list[Client]:
        """Obtiene clientes que no tienen información de contacto.
        
        Returns:
            Lista de clientes sin información de contacto
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def get_client_complete_profile(self, client_id: int) -> Client | None:
        """Obtiene el perfil completo de un cliente con todas sus relaciones.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Cliente con perfil completo o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def get_client_by_id_advanced(self, client_id: int) -> Client | None:
        """Obtiene un cliente por ID con información avanzada.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Cliente con información avanzada o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def get_client_by_name_advanced(self, name: str) -> Client | None:
        """Obtiene un cliente por nombre con información avanzada.
        
        Args:
            name: Nombre del cliente
            
        Returns:
            Cliente con información avanzada o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass