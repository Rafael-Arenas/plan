"""Módulo de operaciones CRUD para clientes.

Este módulo implementa la interfaz ICrudOperations y contiene todas las
operaciones básicas de creación, lectura, actualización y eliminación
de clientes, delegando la lógica al BaseRepository.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.client import Client
from planificador.repositories.base_repository import BaseRepository
from ..interfaces.crud_interface import ICrudOperations


class CrudOperations(BaseRepository[Client], ICrudOperations):
    """Implementación de operaciones CRUD para clientes.
    
    Hereda de BaseRepository para reutilizar la lógica CRUD y se
    especializa para la entidad Client.
    """

    def __init__(self, session: AsyncSession):
        """Inicializa las operaciones CRUD.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        super().__init__(session, Client)
        self._logger = self._logger.bind(component="CrudOperations")
        self._logger.debug("CrudOperations inicializado")

    async def create_client(self, client_data: dict[str, Any]) -> Client:
        """Crea un nuevo cliente delegando en el repositorio base.
        
        Args:
            client_data: Datos del cliente a crear
            
        Returns:
            Cliente creado
        """
        self._logger.debug(f"Creando cliente con datos: {client_data}")
        return await self.create(client_data)

    async def update_client(
        self, client_id: int, client_data: dict[str, Any]
    ) -> Client | None:
        """Actualiza un cliente existente delegando en el repositorio base.
        
        Args:
            client_id: ID del cliente a actualizar
            client_data: Datos actualizados del cliente
            
        Returns:
            Cliente actualizado o None si no existe
        """
        self._logger.debug(
            f"Actualizando cliente ID {client_id} con datos: {client_data}"
        )
        return await self.update(client_id, client_data)

    async def delete_client(self, client_id: int) -> bool:
        """Elimina un cliente delegando en el repositorio base.
        
        Args:
            client_id: ID del cliente a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        self._logger.debug(f"Eliminando cliente ID {client_id}")
        return await self.delete(client_id)