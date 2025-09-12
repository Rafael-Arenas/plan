"""Módulo de operaciones de relaciones para clientes.

Este módulo contiene la implementación de operaciones relacionadas con
la gestión de relaciones entre clientes y proyectos.
"""

from typing import Any

from loguru import logger
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from planificador.models.client import Client
from planificador.models.project import Project
from planificador.exceptions.repository import convert_sqlalchemy_error
from planificador.database.repositories.client.interfaces.relationship_interface import (
    IRelationshipOperations,
)
from planificador.exceptions.repository.client_repository_exceptions import (
    ClientRepositoryError,
    ClientNotFoundError,
)


class RelationshipOperations(IRelationshipOperations):
    """Implementación de operaciones de relaciones para clientes.
    
    Esta clase maneja todas las operaciones relacionadas con la gestión
    de relaciones entre clientes y proyectos.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Inicializa las operaciones de relaciones.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        self.session = session
        self._logger = logger.bind(component="RelationshipOperations")

    async def transfer_projects_to_client(
        self, from_client_id: int, to_client_id: int
    ) -> bool:
        """Transfiere proyectos de un cliente a otro.
        
        Args:
            from_client_id: ID del cliente origen
            to_client_id: ID del cliente destino
            
        Returns:
            True si la transferencia fue exitosa
            
        Raises:
            ClientNotFoundError: Si uno de los clientes no existe.
            ClientRepositoryError: Si ocurre un error en la transferencia.
        """
        self._logger.info(
            f"Iniciando transferencia de proyectos del cliente {from_client_id} "
            f"al cliente {to_client_id}"
        )
        try:
            from_client = await self.session.get(Client, from_client_id)
            if not from_client:
                raise ClientNotFoundError(entity_id=from_client_id)

            to_client = await self.session.get(Client, to_client_id)
            if not to_client:
                raise ClientNotFoundError(entity_id=to_client_id)

            stmt = (
                update(Project)
                .where(Project.client_id == from_client_id)
                .values(client_id=to_client_id)
            )
            result = await self.session.execute(stmt)
            await self.session.flush()

            self._logger.info(
                f"{result.rowcount} proyectos transferidos de {from_client.name} "
                f"a {to_client.name}"
            )
            return True
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD transfiriendo proyectos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="transfer_projects_to_client",
                entity_type="Project",
            )
        except Exception as e:
            self._logger.error(f"Error inesperado transfiriendo proyectos: {e}")
            raise ClientRepositoryError(
                message="Error inesperado en la transferencia de proyectos.",
                operation="transfer_projects_to_client",
                original_error=e,
            )

    async def get_client_projects(self, client_id: int) -> list[Any]:
        """Obtiene los proyectos asociados a un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Lista de proyectos del cliente
            
        Raises:
            ClientNotFoundError: Si el cliente no existe.
            ClientRepositoryError: Si ocurre un error en la consulta.
        """
        self._logger.debug(f"Obteniendo proyectos del cliente {client_id}")
        try:
            query = (
                select(Client)
                .where(Client.id == client_id)
                .options(selectinload(Client.projects))
            )
            result = await self.session.execute(query)
            client = result.scalar_one_or_none()

            if not client:
                raise ClientNotFoundError(entity_id=client_id)

            self._logger.debug(
                f"Se encontraron {len(client.projects)} proyectos para el cliente {client_id}"
            )
            return client.projects
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD obteniendo proyectos: {e}")
            raise convert_sqlalchemy_error(
                error=e, operation="get_client_projects", entity_type="Project"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo proyectos: {e}")
            raise ClientRepositoryError(
                message="Error inesperado obteniendo proyectos.",
                operation="get_client_projects",
                original_error=e,
            )

    async def get_client_project_count(self, client_id: int) -> int:
        """Obtiene el número de proyectos de un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Número de proyectos del cliente
            
        Raises:
            ClientRepositoryError: Si ocurre un error en el conteo.
        """
        self._logger.debug(f"Contando proyectos del cliente {client_id}")
        try:
            query = select(func.count(Project.id)).where(
                Project.client_id == client_id
            )
            result = await self.session.execute(query)
            count = result.scalar_one()

            self._logger.debug(f"Cliente {client_id} tiene {count} proyectos")
            return count
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD contando proyectos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_project_count",
                entity_type="Project",
            )
        except Exception as e:
            self._logger.error(f"Error inesperado contando proyectos: {e}")
            raise ClientRepositoryError(
                message="Error inesperado contando proyectos.",
                operation="get_client_project_count",
                original_error=e,
            )