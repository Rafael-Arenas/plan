"""Módulo de operaciones de relaciones para clientes.

Este módulo, ahora integrado con BaseRepository, gestiona las relaciones
entre clientes y proyectos, como la transferencia de proyectos y consultas
relacionadas.

Versión: 2.0.0
"""

from typing import Any, Optional, List

from sqlalchemy import func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from planificador.models.client import Client
from planificador.models.project import Project
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import convert_sqlalchemy_error
from ..interfaces.relationship_interface import IClientRelationshipOperations
from planificador.exceptions.repository.client_repository_exceptions import (
    ClientRepositoryError,
    ClientNotFoundError,
)


class RelationshipOperations(BaseRepository[Client], IClientRelationshipOperations):
    """Implementación de operaciones de relaciones para clientes.

    Hereda de BaseRepository para estandarizar el acceso a datos y se
    especializa en la gestión de relaciones entre clientes y proyectos.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Inicializa las operaciones de relaciones.

        Args:
            session: Sesión de base de datos asíncrona.
        """
        super().__init__(session, Client)

    async def transfer_projects_to_client(
        self, from_client_id: int, to_client_id: int
    ) -> int:
        """Transfiere proyectos de un cliente a otro y devuelve el conteo."""
        self._logger.info(
            f"Iniciando transferencia de proyectos de {from_client_id} a {to_client_id}"
        )
        try:
            from_client = await self.get_by_id(from_client_id)
            if not from_client:
                raise ClientNotFoundError(entity_id=from_client_id)

            to_client = await self.get_by_id(to_client_id)
            if not to_client:
                raise ClientNotFoundError(entity_id=to_client_id)

            stmt = (
                update(Project)
                .where(Project.client_id == from_client_id)
                .values(client_id=to_client_id)
            )
            result = await self.session.execute(stmt)
            await self.session.flush()
            
            count = result.rowcount
            self._logger.info(f"{count} proyectos transferidos.")
            return count

        except SQLAlchemyError as e:
            await self.session.rollback()
            self._logger.error(f"Error de BD transfiriendo proyectos: {e}")
            raise convert_sqlalchemy_error(
                error=e, operation="transfer_projects"
            )
        except Exception as e:
            await self.session.rollback()
            self._logger.error(f"Error inesperado transfiriendo proyectos: {e}")
            raise ClientRepositoryError(
                message="Error inesperado en la transferencia.",
                operation="transfer_projects",
                original_error=e,
            )

    async def get_client_projects(self, client_id: int) -> list[Project]:
        """Obtiene los proyectos de un cliente usando carga optimizada."""
        client = await self.find_by_id(
            client_id, options=[selectinload(Client.projects)]
        )
        if not client:
            raise ClientNotFoundError(entity_id=client_id)
        return client.projects

    async def get_client_project_count(self, client_id: int) -> int:
        """Obtiene el número de proyectos de un cliente."""
        if not await self.exists(client_id):
            raise ClientNotFoundError(entity_id=client_id)
        return await self.count(Project, criteria={"client_id": client_id})

    # Implementación de métodos abstractos de IClientRelationshipOperations
    async def get_projects_by_client(self, client_id: int) -> List[Project]:
        """
        Obtiene todos los proyectos asociados a un cliente.
        
        Args:
            client_id: ID del cliente.
            
        Returns:
            Lista de proyectos del cliente.
        """
        self._logger.debug(f"Obteniendo proyectos del cliente {client_id}")
        
        try:
            async with self.get_session() as session:
                query = select(Project).where(Project.client_id == client_id)
                result = await session.execute(query)
                projects = result.scalars().all()
                
                self._logger.debug(f"Encontrados {len(projects)} proyectos para cliente {client_id}")
                return list(projects)
                
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo proyectos del cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_projects_by_client",
                entity_type="Project",
                entity_id=client_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo proyectos: {e}")
            raise ClientRepositoryError(
                message=f"Error inesperado obteniendo proyectos del cliente {client_id}",
                operation="get_projects_by_client",
                entity_type="Project",
                entity_id=client_id,
                original_error=e
            )

    async def get_client_with_projects(self, client_id: int) -> Optional[Client]:
        """
        Obtiene un cliente con todos sus proyectos cargados.
        
        Args:
            client_id: ID del cliente.
            
        Returns:
            Cliente con sus proyectos o None si no se encuentra.
        """
        self._logger.debug(f"Obteniendo cliente {client_id} con proyectos")
        
        try:
            async with self.get_session() as session:
                query = (
                    select(Client)
                    .options(selectinload(Client.projects))
                    .where(Client.id == client_id)
                )
                result = await session.execute(query)
                client = result.scalar_one_or_none()
                
                if client:
                    self._logger.debug(f"Cliente {client_id} encontrado con {len(client.projects)} proyectos")
                else:
                    self._logger.debug(f"Cliente {client_id} no encontrado")
                
                return client
                
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo cliente {client_id} con proyectos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_with_projects",
                entity_type="Client",
                entity_id=client_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo cliente con proyectos: {e}")
            raise ClientRepositoryError(
                message=f"Error inesperado obteniendo cliente {client_id} con proyectos",
                operation="get_client_with_projects",
                entity_type="Client",
                entity_id=client_id,
                original_error=e
            )

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