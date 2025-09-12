"""Interface para operaciones de estadísticas de clientes.

Define el contrato que deben cumplir las implementaciones de operaciones
estadísticas para la entidad Cliente.
"""

from abc import ABC, abstractmethod
from typing import Any


class IStatisticsOperations(ABC):
    """Interface para operaciones de estadísticas de clientes."""

    @abstractmethod
    async def get_client_statistics(self) -> dict[str, Any]:
        """Obtiene estadísticas generales de clientes.
        
        Returns:
            Diccionario con estadísticas de clientes
            
        Raises:
            ClientRepositoryError: Si ocurre un error en el cálculo
        """
        pass

    @abstractmethod
    async def get_comprehensive_dashboard_metrics(self) -> dict[str, Any]:
        """Obtiene métricas completas para el dashboard.
        
        Returns:
            Diccionario con métricas del dashboard
            
        Raises:
            ClientRepositoryError: Si ocurre un error en el cálculo
        """
        pass

    @abstractmethod
    async def get_client_count(self) -> int:
        """Obtiene el número total de clientes.
        
        Returns:
            Número total de clientes
            
        Raises:
            ClientRepositoryError: Si ocurre un error en el conteo
        """
        pass