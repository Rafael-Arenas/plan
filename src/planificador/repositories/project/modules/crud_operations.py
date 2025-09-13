from typing import Any, Dict, Optional

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from planificador.repositories.base_repository import BaseRepository
from planificador.models.project import Project
from planificador.utils.date_utils import get_current_time
from planificador.exceptions.base import NotFoundError, ValidationError
from planificador.exceptions.repository.project_repository_exceptions import (
    ProjectRepositoryError,
)
from planificador.exceptions.repository.base_repository_exceptions import (
    convert_sqlalchemy_error,
)


class CrudOperations(BaseRepository):
    def __init__(self, session, validator, query_builder, relationship_manager):
        super().__init__(session, Project)
        self.validator = validator
        self.query_builder = query_builder
        self.relationship_manager = relationship_manager
        self._logger = logger

    async def create_project(self, project_data: Dict[str, Any]) -> Project:
        """
        Crea un nuevo proyecto después de validar los datos de entrada.

        Args:
            project_data: Diccionario con los datos del proyecto

        Returns:
            El proyecto recién creado

        Raises:
            ValidationError: Si los datos del proyecto son inválidos
            ProjectRepositoryError: Si ocurre un error inesperado en el repositorio
        """
        try:
            await self.validator.validate_project_creation(project_data)

            new_project = Project(**project_data)
            self.session.add(new_project)
            await self.session.flush()
            await self.session.refresh(new_project)

            self._logger.info(f"Proyecto creado: {new_project.reference}")
            return new_project

        except (ValidationError, SQLAlchemyError) as e:
            await self.session.rollback()
            if isinstance(e, ValidationError):
                raise
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_project",
                entity_type="Project",
            )
        except Exception as e:
            await self.session.rollback()
            raise ProjectRepositoryError(
                message=f"Error inesperado creando proyecto: {e}",
                operation="create_project",
                entity_type="Project",
                original_error=e,
            )

    async def update_project(
        self, project_id: int, updated_data: Dict[str, Any]
    ) -> Optional[Project]:
        """
        Actualiza un proyecto existente después de validar los datos.

        Args:
            project_id: ID del proyecto a actualizar
            updated_data: Diccionario con los datos a actualizar

        Returns:
            Proyecto actualizado o None si no se encuentra

        Raises:
            ValidationError: Si los datos de actualización son inválidos
            NotFoundError: Si el proyecto no se encuentra
        """
        try:
            project = await self.get_by_id(project_id)
            if not project:
                raise NotFoundError(f"Proyecto con ID {project_id} no encontrado")

            await self.validator.validate_project_update(project_id, updated_data)

            for key, value in updated_data.items():
                setattr(project, key, value)

            await self.session.flush()
            await self.session.refresh(project)

            self._logger.info(f"Proyecto actualizado: {project.reference}")
            return project

        except (NotFoundError, ValidationError, SQLAlchemyError) as e:
            await self.session.rollback()
            if isinstance(e, (NotFoundError, ValidationError)):
                raise
            raise convert_sqlalchemy_error(
                error=e,
                operation="update_project",
                entity_type="Project",
                entity_id=project_id,
            )
        except Exception as e:
            await self.session.rollback()
            raise ProjectRepositoryError(
                message=f"Error inesperado actualizando proyecto {project_id}: {e}",
                operation="update_project",
                entity_type="Project",
                entity_id=project_id,
                original_error=e,
            )

    async def delete_project(self, project_id: int) -> bool:
        """
        Elimina un proyecto por su ID.

        Args:
            project_id: ID del proyecto a eliminar

        Returns:
            True si el proyecto fue eliminado, False en caso contrario

        Raises:
            ProjectNotFoundError: Si el proyecto no se encuentra
        """
        try:
            project = await self.get_by_id(project_id)
            if not project:
                raise NotFoundError(f"Proyecto con ID {project_id} no encontrado")

            await self.session.delete(project)
            await self.session.flush()

            self._logger.info(f"Proyecto eliminado: ID {project_id}")
            return True

        except (NotFoundError, SQLAlchemyError) as e:
            await self.session.rollback()
            if isinstance(e, NotFoundError):
                raise
            raise convert_sqlalchemy_error(
                error=e,
                operation="delete_project",
                entity_type="Project",
                entity_id=project_id,
            )
        except Exception as e:
            await self.session.rollback()
            raise ProjectRepositoryError(
                message=f"Error inesperado eliminando proyecto {project_id}: {e}",
                operation="delete_project",
                entity_type="Project",
                entity_id=project_id,
                original_error=e,
            )

    async def archive_project(self, project_id: int) -> Optional[Project]:
        """
        Archiva un proyecto después de validar que puede ser archivado.

        Args:
            project_id: ID del proyecto a archivar

        Returns:
            Proyecto archivado o None si no existe

        Raises:
            ProjectValidationError: Si el proyecto no puede ser archivado
        """
        try:
            project = await self.get_by_id(project_id)
            if not project:
                raise NotFoundError(f"Proyecto con ID {project_id} no encontrado")

            await self.validator.validate_project_archival(project_id)

            project.is_archived = True
            project.archived_at = get_current_time()

            await self.session.flush()

            self._logger.info(f"Proyecto archivado: {project.reference}")
            return project

        except (NotFoundError, ValidationError, SQLAlchemyError) as e:
            await self.session.rollback()
            if isinstance(e, (NotFoundError, ValidationError)):
                raise
            raise convert_sqlalchemy_error(
                error=e,
                operation="archive_project",
                entity_type="Project",
                entity_id=project_id,
            )
        except Exception as e:
            await self.session.rollback()
            raise ProjectRepositoryError(
                message=f"Error inesperado archivando proyecto {project_id}: {e}",
                operation="archive_project",
                entity_type="Project",
                entity_id=project_id,
                original_error=e,
            )