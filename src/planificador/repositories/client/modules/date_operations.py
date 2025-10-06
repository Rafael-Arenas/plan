"""Módulo de operaciones de fechas para clientes.

Este módulo contiene la implementación de operaciones relacionadas con
la gestión de fechas para la entidad Cliente, delegando la lógica
de consulta al BaseRepository.
"""

from typing import Any, Optional
import pendulum
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.client import Client
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import convert_sqlalchemy_error
from planificador.exceptions.repository.client_repository_exceptions import ClientRepositoryError
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

    # Implementación del método abstracto de BaseRepository
    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[Client]:
        """
        Obtiene un cliente por un campo único específico.
        
        Args:
            field_name: Nombre del campo único (email, code, etc.)
            value: Valor a buscar
            
        Returns:
            Cliente encontrado o None si no existe
        """
        self._logger.debug(f"Buscando cliente por {field_name} = {value}")
        
        try:
            async with self.get_session() as session:
                # Obtener el atributo del modelo dinámicamente
                if not hasattr(self.model_class, field_name):
                    raise ValueError(f"El campo '{field_name}' no existe en el modelo Client")
                
                field_attr = getattr(self.model_class, field_name)
                query = select(self.model_class).where(field_attr == value)
                result = await session.execute(query)
                client = result.scalar_one_or_none()
                
                if client:
                    self._logger.debug(f"Cliente encontrado: {client.id}")
                else:
                    self._logger.debug(f"No se encontró cliente con {field_name} = {value}")
                
                return client
                
        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando cliente por {field_name}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_unique_field",
                entity_type="Client",
                entity_id=value
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando cliente: {e}")
            raise ClientRepositoryError(
                message=f"Error inesperado buscando cliente por {field_name}",
                operation="get_by_unique_field",
                entity_type="Client",
                entity_id=value,
                original_error=e
            )

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