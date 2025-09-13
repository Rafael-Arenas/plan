"""Interface para operaciones de fechas de clientes.

Define el contrato que deben cumplir las implementaciones de operaciones
relacionadas con fechas para la entidad Cliente.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from planificador.models.client import Client


class IDateOperations(ABC):
    """Interface para operaciones de fechas de clientes."""

    @abstractmethod
    async def get_clients_created_in_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[Client]:
        """Obtiene clientes creados en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            
        Returns:
            Lista de clientes creados en el rango
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def get_clients_updated_in_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[Client]:
        """Obtiene clientes actualizados en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            
        Returns:
            Lista de clientes actualizados en el rango
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass