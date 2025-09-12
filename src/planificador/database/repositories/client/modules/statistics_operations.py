"""Módulo de operaciones de estadísticas para clientes.

Este módulo implementa la interfaz IStatisticsOperations y proporciona
funcionalidades para generar estadísticas, métricas y análisis de clientes.
"""

from typing import Any

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.client import Client
from planificador.exceptions.repository import convert_sqlalchemy_error
from planificador.exceptions.repository.client_repository_exceptions import (
    ClientRepositoryError,
)
from ..interfaces.statistics_interface import IStatisticsOperations


class StatisticsOperations(IStatisticsOperations):
    """Implementación de operaciones de estadísticas para clientes.
    
    Esta clase encapsula todas las operaciones relacionadas con estadísticas,
    métricas y análisis de datos de clientes.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Inicializa las operaciones de estadísticas.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        self.session = session
        self._logger = logger.bind(component="StatisticsOperations")

    async def get_client_statistics(self) -> dict[str, Any]:
        """Obtiene estadísticas generales de clientes.
        
        Returns:
            Diccionario con estadísticas básicas de clientes
            
        Raises:
            ClientRepositoryError: Si ocurre un error en el cálculo
        """
        try:
            self._logger.debug("Obteniendo estadísticas generales de clientes")
            return await self.get_client_counts_by_status()
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de BD obteniendo estadísticas de clientes: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_statistics",
                entity_type="Client",
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo estadísticas de clientes: {e}"
            )
            raise ClientRepositoryError(
                message=f"Error obteniendo estadísticas de clientes: {e}",
                operation="get_client_statistics",
                entity_type="Client",
                original_error=e,
            )

    async def get_client_counts_by_status(self) -> dict[str, int]:
        """Obtiene el conteo de clientes por estado (activo/inactivo).
        
        Returns:
            Diccionario con el número de clientes activos e inactivos.
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta.
        """
        try:
            self._logger.debug("Contando clientes por estado (activo/inactivo)")
            query = (
                select(Client.is_active, func.count(Client.id).label("count"))
                .group_by(Client.is_active)
            )
            result = await self.session.execute(query)
            rows = result.all()

            counts = {"active": 0, "inactive": 0}
            for row in rows:
                if row.is_active:
                    counts["active"] = row.count
                else:
                    counts["inactive"] = row.count

            self._logger.info(f"Clientes por estado: {counts}")
            return counts
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de BD contando clientes por estado: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_counts_by_status",
                entity_type="Client",
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado contando clientes por estado: {e}"
            )
            raise ClientRepositoryError(
                message=f"Error contando clientes por estado: {e}",
                operation="get_client_counts_by_status",
                entity_type="Client",
                original_error=e,
            )

    async def get_client_count(self) -> int:
        """Obtiene el número total de clientes.
        
        Returns:
            Número total de clientes registrados
            
        Raises:
            ClientRepositoryError: Si ocurre un error en el conteo
        """
        try:
            self._logger.debug("Obteniendo conteo total de clientes")
            query = select(func.count(Client.id))
            result = await self.session.execute(query)
            count = result.scalar_one()
            self._logger.info(f"Conteo total de clientes: {count}")
            return count
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo conteo de clientes: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_count",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo conteo de clientes: {e}")
            raise ClientRepositoryError(
                message=f"Error obteniendo conteo de clientes: {e}",
                operation="get_client_count",
                entity_type="Client",
                original_error=e
            )

    # Métodos adicionales de estadísticas específicas
    
    async def get_client_stats_by_id(self, client_id: int) -> dict[str, Any]:
        """Obtiene estadísticas de un cliente específico.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con estadísticas del cliente
            
        Raises:
            ClientRepositoryError: Si ocurre un error en el cálculo
        """
        try:
            self._logger.debug(f"Obteniendo estadísticas del cliente {client_id}")
            return await self.statistics.get_client_stats(client_id)
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo estadísticas del cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_stats_by_id",
                entity_type="Client",
                entity_id=client_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo estadísticas del cliente {client_id}: {e}")
            raise ClientRepositoryError(
                message=f"Error obteniendo estadísticas del cliente {client_id}: {e}",
                operation="get_client_stats_by_id",
                entity_type="Client",
                entity_id=client_id,
                original_error=e
            )

    async def get_client_creation_trends(self, days: int = 30, group_by: str = "day") -> list[dict[str, Any]]:
        """Obtiene tendencias de creación de clientes.
        
        Args:
            days: Número de días hacia atrás para el análisis
            group_by: Agrupación temporal ('day', 'week', 'month')
            
        Returns:
            Lista con tendencias de creación de clientes
            
        Raises:
            ClientRepositoryError: Si ocurre un error en el cálculo
        """
        try:
            self._logger.debug(f"Obteniendo tendencias de creación para {days} días agrupadas por {group_by}")
            return await self.statistics.get_client_creation_trends(days, group_by)
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo tendencias de creación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_creation_trends",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo tendencias de creación: {e}")
            raise ClientRepositoryError(
                message=f"Error obteniendo tendencias de creación: {e}",
                operation="get_client_creation_trends",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_by_project_count(self, limit: int = 10) -> list[dict[str, Any]]:
        """Obtiene clientes ordenados por número de proyectos.
        
        Args:
            limit: Número máximo de clientes a retornar
            
        Returns:
            Lista de clientes con conteo de proyectos
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo top {limit} clientes por número de proyectos")
            return await self.statistics.get_clients_by_project_count(limit)
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo clientes por proyectos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_by_project_count",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo clientes por proyectos: {e}")
            raise ClientRepositoryError(
                message=f"Error obteniendo clientes por proyectos: {e}",
                operation="get_clients_by_project_count",
                entity_type="Client",
                original_error=e
            )

    def get_comprehensive_dashboard_metrics(self) -> dict[str, Any]:
        """
        Recopila una serie de métricas clave sobre los clientes para un
        dashboard.

        Returns:
            Un diccionario con métricas completas.
        """
        try:
            total_clients = self.get_client_count()
            active_clients = self.get_client_count(is_active=True)
            inactive_clients = self.get_client_count(is_active=False)

            trends = self.get_client_creation_trends(days=30)

            return {
                "total_clients": total_clients,
                "clients_by_status": {
                    "active": active_clients,
                    "inactive": inactive_clients,
                },
                "creation_trends_last_30_days": trends,
            }
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                e, "Error al obtener métricas del dashboard."
            ) from e