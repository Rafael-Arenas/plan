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