from abc import ABC, abstractmethod
from typing import List, Optional

from planificador.models.client import Client
from planificador.models.project import Project


class IClientRelationshipOperations(ABC):
    """
    Interfaz para operaciones de relaciones de clientes.
    """

    @abstractmethod
    async def get_projects_by_client(self, client_id: int) -> List[Project]:
        """
        Obtiene todos los proyectos asociados a un cliente.
        
        Args:
            client_id: ID del cliente.
            
        Returns:
            Lista de proyectos del cliente.
        """
        pass

    @abstractmethod
    async def get_client_with_projects(self, client_id: int) -> Optional[Client]:
        """
        Obtiene un cliente con todos sus proyectos cargados.
        
        Args:
            client_id: ID del cliente.
            
        Returns:
            Cliente con sus proyectos o None si no se encuentra.
        """
        pass