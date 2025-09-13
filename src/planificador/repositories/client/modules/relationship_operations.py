"""Módulo de operaciones de relaciones para clientes.

Este módulo, ahora integrado con BaseRepository, gestiona las relaciones
entre clientes y proyectos, como la transferencia de proyectos y consultas
relacionadas.

Versión: 2.0.0
"""

from typing import Any

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