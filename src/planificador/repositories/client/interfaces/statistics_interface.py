"""Interface para operaciones estadísticas de cliente.

Esta interface define los métodos de estadísticas que deben ser implementados
por las clases de estadísticas de cliente, permitiendo la inyección de
dependencias y evitando referencias circulares.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class IClientStatistics(ABC):
    """Interface abstracta para operaciones estadísticas de cliente.

    Define los métodos que deben implementar las clases de estadísticas
    para generar reportes y métricas de clientes.
    """

    @abstractmethod
    async def get_client_count(self) -> int:
        """Obtiene el número total de clientes.

        Returns:
            Número total de clientes en el sistema.
        """
        pass

    @abstractmethod
    async def get_active_client_count(self) -> int:
        """Obtiene el número de clientes activos.

        Returns:
            Número de clientes activos.
        """
        pass

    @abstractmethod
    async def get_clients_by_creation_date(
        self, start_date: datetime, end_date: datetime
    ) -> list[dict[str, Any]]:
        """Obtiene estadísticas de clientes por fecha de creación.

        Args:
            start_date: Fecha de inicio del período.
            end_date: Fecha de fin del período.

        Returns:
            Lista con estadísticas agrupadas por fecha.
        """
        pass

    @abstractmethod
    async def get_client_distribution_by_status(self) -> dict[str, int]:
        """Obtiene la distribución de clientes por estado.

        Returns:
            Diccionario con el conteo de clientes por estado.
        """
        pass

    @abstractmethod
    async def get_top_clients_by_projects(
        self, limit: int | None = 10
    ) -> list[dict[str, Any]]:
        """Obtiene los clientes con más proyectos.

        Args:
            limit: Número máximo de clientes a retornar.

        Returns:
            Lista de clientes ordenados por número de proyectos.
        """
        pass

    @abstractmethod
    async def calculate_client_metrics(self, client_id: int) -> dict[str, Any]:
        """Calcula métricas específicas para un cliente.

        Args:
            client_id: ID del cliente.

        Returns:
            Diccionario con las métricas del cliente.
        """
        pass

    @abstractmethod
    async def get_monthly_client_growth(
        self, year: int
    ) -> list[dict[str, Any]]:
        """Obtiene el crecimiento mensual de clientes para un año.

        Args:
            year: Año para el cual calcular el crecimiento.

        Returns:
            Lista con el crecimiento mensual de clientes.
        """
        pass
