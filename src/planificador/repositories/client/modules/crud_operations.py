"""Módulo de operaciones CRUD para clientes.

Este módulo implementa la interfaz ICrudOperations y contiene todas las
operaciones básicas de creación, lectura, actualización y eliminación
de clientes, delegando la lógica al BaseRepository.
"""

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.client import Client
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import convert_sqlalchemy_error
from planificador.exceptions.repository.client_repository_exceptions import ClientRepositoryError
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