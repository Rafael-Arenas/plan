"""Módulo de operaciones de fechas para clientes.

Este módulo contiene la implementación de operaciones relacionadas con
la gestión de fechas para la entidad Cliente.
"""

from datetime import datetime

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.database.repositories.client.interfaces.date_interface import (
    IDateOperations,
)
from planificador.exceptions.repository import convert_sqlalchemy_error
from planificador.exceptions.repository.client_repository_exceptions import (
    ClientRepositoryError,
)
from planificador.models.client import Client


class DateOperations(IDateOperations):
    """Implementación de operaciones de fechas para clientes."""

    def __init__(self, session: AsyncSession) -> None:
        """Inicializa las operaciones de fechas.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        self.session = session
        self._logger = logger.bind(component="DateOperations")

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
            ClientRepositoryError: Si ocurre un error en la consulta.
        """
        self._logger.debug(
            f"Obteniendo clientes creados entre {start_date} y {end_date}"
        )
        try:
            stmt = select(Client).where(
                Client.created_at >= start_date, Client.created_at <= end_date
            )
            result = await self.session.execute(stmt)
            clients = result.scalars().all()
            self._logger.debug(
                f"Se encontraron {len(clients)} clientes creados en el rango"
            )
            return list(clients)
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD obteniendo clientes por fecha: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_created_in_date_range",
                entity_type="Client",
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo clientes por fecha: {e}")
            raise ClientRepositoryError(
                message="Error inesperado obteniendo clientes por fecha de creación.",
                operation="get_clients_created_in_date_range",
                original_error=e,
            )

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
            ClientRepositoryError: Si ocurre un error en la consulta.
        """
        self._logger.debug(
            f"Obteniendo clientes actualizados entre {start_date} y {end_date}"
        )
        try:
            stmt = select(Client).where(
                Client.updated_at >= start_date, Client.updated_at <= end_date
            )
            result = await self.session.execute(stmt)
            clients = result.scalars().all()
            self._logger.debug(
                f"Se encontraron {len(clients)} clientes actualizados en el rango"
            )
            return list(clients)
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de BD obteniendo clientes actualizados por fecha: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_updated_in_date_range",
                entity_type="Client",
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo clientes actualizados por fecha: {e}"
            )
            raise ClientRepositoryError(
                message="Error inesperado obteniendo clientes por fecha de actualización.",
                operation="get_clients_updated_in_date_range",
                original_error=e,
            )