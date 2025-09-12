"""Interface para operaciones de relaciones de clientes.

Define el contrato que deben cumplir las implementaciones de operaciones
de gestión de relaciones para la entidad Cliente.
"""

from abc import ABC, abstractmethod
from typing import Any

from planificador.models.client import Client


class IRelationshipOperations(ABC):
    """Interface para operaciones de relaciones de clientes."""

    @abstractmethod
    async def transfer_projects_to_client(
        self, from_client_id: int, to_client_id: int
    ) -> bool:
        """Transfiere proyectos de un cliente a otro.
        
        Args:
            from_client_id: ID del cliente origen
            to_client_id: ID del cliente destino
            
        Returns:
            True si la transferencia fue exitosa
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la transferencia
        """
        pass

    @abstractmethod
    async def get_client_projects(self, client_id: int) -> list[Any]:
        """Obtiene los proyectos asociados a un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Lista de proyectos del cliente
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def get_client_project_count(self, client_id: int) -> int:
        """Obtiene el número de proyectos de un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Número de proyectos del cliente
            
        Raises:
            ClientRepositoryError: Si ocurre un error en el conteo
        """
        pass