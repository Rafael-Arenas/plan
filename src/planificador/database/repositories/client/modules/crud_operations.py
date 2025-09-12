"""Módulo de operaciones CRUD para clientes.

Este módulo implementa la interfaz ICrudOperations y contiene todas las
operaciones básicas de creación, lectura, actualización y eliminación
de clientes.
"""

from typing import Any

import pendulum
from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.database.repositories.client.interfaces.crud_interface import (
    ICrudOperations,
)
from planificador.exceptions.repository.base_repository_exceptions import (
    RepositoryError,
    convert_sqlalchemy_error,
)
from planificador.exceptions.repository.client_repository_exceptions import (
    ClientNotFoundError,
    ClientRepositoryError,
    ClientValidationError,
)
from planificador.models.client import Client
from planificador.utils.date_utils import get_current_time


class CrudOperations(ICrudOperations):
    """Implementación de operaciones CRUD para clientes."""

    def __init__(self, session: AsyncSession):
        """Inicializa las operaciones CRUD.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        self.session = session
        self._logger = logger.bind(component="CrudOperations")

    async def create_client(self, client_data: dict[str, Any]) -> Client:
        """Crea un nuevo cliente.
        
        Args:
            client_data: Datos del cliente a crear
            
        Returns:
            Cliente creado
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la creación
        """
        try:
            # Agregar timestamp de creación
            current_time = get_current_time()
            client_data["created_at"] = current_time
            client_data["updated_at"] = current_time

            # Crear instancia del cliente
            client = Client(**client_data)

            # Persistir en base de datos
            self.session.add(client)
            await self.session.commit()
            await self.session.refresh(client)

            self._logger.info(
                f"Cliente creado exitosamente",
                client_id=client.id,
                client_name=client.name
            )
            return client

        except SQLAlchemyError as e:
            await self.session.rollback()
            self._logger.error(f"Error de base de datos creando cliente: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_client",
                entity_type="Client"
            )
        except Exception as e:
            await self.session.rollback()
            self._logger.error(f"Error inesperado creando cliente: {e}")
            raise RepositoryError(
                message=f"Error inesperado creando cliente: {e}",
                operation="create_client",
                entity_type="Client",
                original_error=e
            )

    async def update_client(
        self, client_id: int, client_data: dict[str, Any]
    ) -> Client | None:
        """Actualiza un cliente existente.
        
        Args:
            client_id: ID del cliente a actualizar
            client_data: Datos actualizados del cliente
            
        Returns:
            Cliente actualizado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la actualización
        """
        try:
            # Buscar cliente existente
            stmt = select(Client).where(Client.id == client_id)
            result = await self.session.execute(stmt)
            client = result.scalar_one_or_none()

            if not client:
                self._logger.warning(
                    f"Cliente no encontrado para actualización",
                    client_id=client_id
                )
                return None

            # Actualizar campos
            for field, value in client_data.items():
                if hasattr(client, field):
                    setattr(client, field, value)

            # Actualizar timestamp
            client.updated_at = get_current_time()

            await self.session.commit()
            await self.session.refresh(client)

            self._logger.info(
                f"Cliente actualizado exitosamente",
                client_id=client.id,
                client_name=client.name
            )
            return client

        except SQLAlchemyError as e:
            await self.session.rollback()
            self._logger.error(f"Error de base de datos actualizando cliente: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="update_client",
                entity_type="Client",
                entity_id=client_id
            )
        except Exception as e:
            await self.session.rollback()
            self._logger.error(f"Error inesperado actualizando cliente: {e}")
            raise RepositoryError(
                message=f"Error inesperado actualizando cliente: {e}",
                operation="update_client",
                entity_type="Client",
                entity_id=client_id,
                original_error=e
            )

    async def delete_client(self, client_id: int) -> bool:
        """Elimina un cliente.
        
        Args:
            client_id: ID del cliente a eliminar
            
        Returns:
            True si se eliminó correctamente
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la eliminación
        """
        try:
            # Buscar cliente existente
            stmt = select(Client).where(Client.id == client_id)
            result = await self.session.execute(stmt)
            client = result.scalar_one_or_none()

            if not client:
                self._logger.warning(
                    f"Cliente no encontrado para eliminación",
                    client_id=client_id
                )
                return False

            # Eliminar cliente
            await self.session.delete(client)
            await self.session.commit()

            self._logger.info(
                f"Cliente eliminado exitosamente",
                client_id=client_id,
                client_name=client.name
            )
            return True

        except SQLAlchemyError as e:
            await self.session.rollback()
            self._logger.error(f"Error de base de datos eliminando cliente: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="delete_client",
                entity_type="Client",
                entity_id=client_id
            )
        except Exception as e:
            await self.session.rollback()
            self._logger.error(f"Error inesperado eliminando cliente: {e}")
            raise RepositoryError(
                message=f"Error inesperado eliminando cliente: {e}",
                operation="delete_client",
                entity_type="Client",
                entity_id=client_id,
                original_error=e
            )

    async def get_client_by_id(self, client_id: int) -> Client | None:
        """Obtiene un cliente por su ID.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            stmt = select(Client).where(Client.id == client_id)
            result = await self.session.execute(stmt)
            client = result.scalar_one_or_none()

            if client:
                self._logger.debug(
                    f"Cliente encontrado",
                    client_id=client_id,
                    client_name=client.name
                )
            else:
                self._logger.debug(
                    f"Cliente no encontrado",
                    client_id=client_id
                )

            return client

        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo cliente: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_by_id",
                entity_type="Client",
                entity_id=client_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo cliente: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo cliente: {e}",
                operation="get_client_by_id",
                entity_type="Client",
                entity_id=client_id,
                original_error=e
            )

    async def get_all_clients(self) -> list[Client]:
        """Obtiene todos los clientes.
        
        Returns:
            Lista de todos los clientes
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            stmt = select(Client).order_by(Client.name)
            result = await self.session.execute(stmt)
            clients = result.scalars().all()

            self._logger.debug(
                f"Obtenidos {len(clients)} clientes"
            )
            return list(clients)

        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo clientes: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_all_clients",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo clientes: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo clientes: {e}",
                operation="get_all_clients",
                entity_type="Client",
                original_error=e
            )

    async def get_client_by_name(self, name: str) -> Client | None:
        """Obtiene un cliente por su nombre.
        
        Args:
            name: Nombre del cliente
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            stmt = select(Client).where(Client.name == name)
            result = await self.session.execute(stmt)
            client = result.scalar_one_or_none()

            if client:
                self._logger.debug(
                    f"Cliente encontrado por nombre",
                    client_name=name,
                    client_id=client.id
                )
            else:
                self._logger.debug(
                    f"Cliente no encontrado por nombre",
                    client_name=name
                )

            return client

        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo cliente por nombre: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_by_name",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo cliente por nombre: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo cliente por nombre: {e}",
                operation="get_client_by_name",
                entity_type="Client",
                original_error=e
            )

    async def get_client_by_email(self, email: str) -> Client | None:
        """Obtiene un cliente por su email.
        
        Args:
            email: Email del cliente
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            stmt = select(Client).where(Client.email == email)
            result = await self.session.execute(stmt)
            client = result.scalar_one_or_none()

            if client:
                self._logger.debug(
                    f"Cliente encontrado por email",
                    client_email=email,
                    client_id=client.id
                )
            else:
                self._logger.debug(
                    f"Cliente no encontrado por email",
                    client_email=email
                )

            return client

        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo cliente por email: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_by_email",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo cliente por email: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo cliente por email: {e}",
                operation="get_client_by_email",
                entity_type="Client",
                original_error=e
            )