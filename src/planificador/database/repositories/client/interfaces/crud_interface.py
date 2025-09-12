"""Interface para operaciones CRUD de clientes.

Define el contrato que deben cumplir las implementaciones de operaciones
CRUD (Create, Read, Update, Delete) para la entidad Cliente.
"""

from abc import ABC, abstractmethod
from typing import Any

from planificador.models.client import Client


class ICrudOperations(ABC):
    """Interface para operaciones CRUD de clientes."""

    @abstractmethod
    async def create_client(self, client_data: dict[str, Any]) -> Client:
        """Crea un nuevo cliente.
        
        Args:
            client_data: Datos del cliente a crear
            
        Returns:
            Cliente creado
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la creación
        """
        pass

    @abstractmethod
    async def update_client(
        self, client_id: int, client_data: dict[str, Any]
    ) -> Client | None:
        """Actualiza un cliente existente.
        
        Args:
            client_id: ID del cliente a actualizar
            client_data: Datos actualizados del cliente
            
        Returns:
            Cliente actualizado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la actualización
        """
        pass

    @abstractmethod
    async def delete_client(self, client_id: int) -> bool:
        """Elimina un cliente.
        
        Args:
            client_id: ID del cliente a eliminar
            
        Returns:
            True si se eliminó correctamente
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la eliminación
        """
        pass

    @abstractmethod
    async def get_client_by_id(self, client_id: int) -> Client | None:
        """Obtiene un cliente por su ID.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def get_all_clients(self) -> list[Client]:
        """Obtiene todos los clientes.
        
        Returns:
            Lista de todos los clientes
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def get_client_by_name(self, name: str) -> Client | None:
        """Obtiene un cliente por su nombre.
        
        Args:
            name: Nombre del cliente
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def get_client_by_email(self, email: str) -> Client | None:
        """Obtiene un cliente por su email.
        
        Args:
            email: Email del cliente
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass