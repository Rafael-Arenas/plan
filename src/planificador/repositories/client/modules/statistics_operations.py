"""Módulo de operaciones de estadísticas para clientes.

Este módulo implementa la interfaz IStatisticsOperations y proporciona
funcionalidades para generar estadísticas, métricas y análisis de clientes.
"""

from typing import Any, Coroutine

import pendulum
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from planificador.repositories.base_repository import BaseRepository
from planificador.models.client import Client
from planificador.models.project import Project
from planificador.repositories.client.interfaces.statistics_interface import (
    IClientStatistics as IStatisticsOperations,
)


class StatisticsOperations(BaseRepository[Client], IStatisticsOperations):
    """Implementación de operaciones de estadísticas para clientes.
    
    Esta clase encapsula todas las operaciones relacionadas con estadísticas,
    métricas y análisis de datos de clientes.
    """

    def __init__(self, session_factory: Coroutine) -> None:
        """Inicializa las operaciones de estadísticas.
        
        Args:
            session_factory: Factoría de sesiones de base de datos asíncrona
        """
        super().__init__(session_factory, Client)
        self._logger = logger.bind(component="StatisticsOperations")

    async def get_client_statistics(self) -> dict[str, Any]:
        """Obtiene estadísticas generales de clientes.
        
        Returns:
            Diccionario con estadísticas básicas de clientes
        """
        self._logger.debug("Obteniendo estadísticas generales de clientes")
        return await self.get_client_counts_by_status()

    async def get_client_counts_by_status(self) -> dict[str, int]:
        """Obtiene el conteo de clientes por estado (activo/inactivo).
        
        Returns:
            Diccionario con el número de clientes activos e inactivos.
        """
        self._logger.debug("Contando clientes por estado (activo/inactivo)")
        active_count = await self.count([self.model_class.is_active == True])
        inactive_count = await self.count([self.model_class.is_active == False])
        
        counts = {"active": active_count, "inactive": inactive_count}
        self._logger.info(f"Clientes por estado: {counts}")
        return counts

    async def get_client_count(self, is_active: bool | None = None) -> int:
        """Obtiene el número total de clientes.
        
        Args:
            is_active: Filtra por estado de actividad si se proporciona.
        
        Returns:
            Número total de clientes registrados
        """
        self._logger.debug("Obteniendo conteo total de clientes")
        criteria = []
        if is_active is not None:
            criteria.append(self.model_class.is_active == is_active)
        
        count = await self.count(criteria)
        self._logger.info(f"Conteo total de clientes: {count}")
        return count

    async def get_client_stats_by_id(self, client_id: int) -> dict[str, Any]:
        """Obtiene estadísticas de un cliente específico.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con estadísticas del cliente
        """
        self._logger.debug(f"Obteniendo estadísticas del cliente {client_id}")
        client = await self.get_by_id(client_id)
        if not client:
            return {}

        project_count = await self.count_related(
            Project, Project.client_id == client_id
        )
        
        return {
            "client_id": client.id,
            "name": client.name,
            "is_active": client.is_active,
            "project_count": project_count,
            "created_at": client.created_at,
            "updated_at": client.updated_at,
        }

    async def get_client_creation_trends(
        self, days: int = 30, group_by: str = "day"
    ) -> list[dict[str, Any]]:
        """Obtiene tendencias de creación de clientes.
        
        Args:
            days: Número de días hacia atrás para el análisis
            group_by: Agrupación temporal ('day', 'week', 'month')
            
        Returns:
            Lista con tendencias de creación de clientes
        """
        self._logger.debug(
            f"Obteniendo tendencias de creación para {days} días agrupadas por {group_by}"
        )
        end_date = pendulum.now()
        start_date = end_date.subtract(days=days)

        if group_by == "day":
            trunc_func = func.date
        elif group_by == "week":
            trunc_func = func.strftime("%Y-%W", self.model_class.created_at)
        elif group_by == "month":
            trunc_func = func.strftime("%Y-%m", self.model_class.created_at)
        else:
            raise ValueError("group_by debe ser 'day', 'week' o 'month'")

        async with self.get_session() as session:
            query = (
                select(
                    trunc_func(self.model_class.created_at).label("period"),
                    func.count(self.model_class.id).label("count"),
                )
                .where(self.model_class.created_at.between(start_date, end_date))
                .group_by("period")
                .order_by("period")
            )
            result = await session.execute(query)
            return [{"period": row.period, "count": row.count} for row in result]

    async def get_clients_by_project_count(
        self, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Obtiene clientes ordenados por número de proyectos.
        
        Args:
            limit: Número máximo de clientes a retornar
            
        Returns:
            Lista de clientes con conteo de proyectos
        """
        self._logger.debug(f"Obteniendo top {limit} clientes por número de proyectos")
        async with self.get_session() as session:
            query = (
                select(
                    self.model_class.id,
                    self.model_class.name,
                    func.count(Project.id).label("project_count"),
                )
                .join(Project, self.model_class.id == Project.client_id)
                .group_by(self.model_class.id)
                .order_by(func.count(Project.id).desc())
                .limit(limit)
            )
            result = await session.execute(query)
            return [
                {
                    "client_id": row.id,
                    "name": row.name,
                    "project_count": row.project_count,
                }
                for row in result
            ]

    async def get_comprehensive_dashboard_metrics(self) -> dict[str, Any]:
        """
        Recopila una serie de métricas clave sobre los clientes para un
        dashboard.

        Returns:
            Un diccionario con métricas completas.
        """
        total_clients = await self.get_client_count()
        clients_by_status = await self.get_client_counts_by_status()
        trends = await self.get_client_creation_trends(days=30)

        return {
            "total_clients": total_clients,
            "clients_by_status": clients_by_status,
            "creation_trends_last_30_days": trends,
        }