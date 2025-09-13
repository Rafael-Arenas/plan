"""Módulo de operaciones de fechas para clientes.

Este módulo contiene la implementación de operaciones relacionadas con
la gestión de fechas para la entidad Cliente, delegando la lógica
de consulta al BaseRepository.
"""

import pendulum
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.client import Client
from planificador.repositories.base_repository import BaseRepository
from ..interfaces.date_interface import IDateOperations


class DateOperations(BaseRepository[Client], IDateOperations):
    """Implementación de operaciones de fechas para clientes.
    
    Hereda de BaseRepository para reutilizar la lógica de consulta y se
    especializa para la entidad Client.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Inicializa las operaciones de fechas.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Client)
        self._logger = self._logger.bind(component="DateOperations")
        self._logger.debug("DateOperations inicializado")

    async def get_clients_created_in_date_range(
        self, start_date: pendulum.DateTime, end_date: pendulum.DateTime
    ) -> list[Client]:
        """Obtiene clientes creados en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango (Pendulum)
            end_date: Fecha de fin del rango (Pendulum)
            
        Returns:
            Lista de clientes creados en el rango
        """
        self._logger.debug(
            f"Obteniendo clientes creados entre {start_date} y {end_date}"
        )
        criteria = {
            "created_at": {
                "operator": "gte", "value": start_date
            },
            "and": {
                "created_at": {
                    "operator": "lte", "value": end_date
                }
            }
        }
        return await self.find_by_criteria(criteria)

    async def get_clients_updated_in_date_range(
        self, start_date: pendulum.DateTime, end_date: pendulum.DateTime
    ) -> list[Client]:
        """Obtiene clientes actualizados en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango (Pendulum)
            end_date: Fecha de fin del rango (Pendulum)
            
        Returns:
            Lista de clientes actualizados en el rango
        """
        self._logger.debug(
            f"Obteniendo clientes actualizados entre {start_date} y {end_date}"
        )
        criteria = {
            "updated_at": {
                "operator": "gte", "value": start_date
            },
            "and": {
                "updated_at": {
                    "operator": "lte", "value": end_date
                }
            }
        }
        return await self.find_by_criteria(criteria)