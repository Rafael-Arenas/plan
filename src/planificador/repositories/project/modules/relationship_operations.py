from typing import Any, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.repositories.base_repository import BaseRepository
from planificador.models.project import Project
from planificador.exceptions.repository.base_repository_exceptions import RepositoryError, convert_sqlalchemy_error


class RelationshipOperations(BaseRepository[Project]):
    """
    Módulo para gestionar las relaciones del modelo Project.
    """

    def __init__(self, query_builder):
        # Obtener la sesión del query_builder
        if hasattr(query_builder, 'session'):
            session = query_builder.session
        else:
            raise ValueError("query_builder debe tener una sesión válida")
        
        super().__init__(session, Project)
        self.query_builder = query_builder
        self._logger = logger.bind(module="project_relationship_operations")
    
    async def get_by_unique_field(self, field_name: str, field_value: Any) -> Optional[Project]:
        """
        Obtiene un proyecto por un campo único específico.
        
        Args:
            field_name: Nombre del campo único
            field_value: Valor del campo único
            
        Returns:
            Optional[Project]: El proyecto encontrado o None
            
        Raises:
            RepositoryError: Si ocurre un error durante la consulta
        """
        try:
            if not hasattr(Project, field_name):
                raise ValueError(f"El campo '{field_name}' no existe en el modelo Project")
            
            field_attr = getattr(Project, field_name)
            query = select(Project).where(field_attr == field_value)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al buscar proyecto por {field_name}={field_value}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_unique_field",
                entity_type="Project",
                entity_id=str(field_value)
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar proyecto por {field_name}={field_value}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al buscar proyecto por {field_name}={field_value}: {e}",
                operation="get_by_unique_field",
                entity_type="Project",
                entity_id=str(field_value),
                original_error=e
            )

    def with_client(self, query):
        """
        Añade la carga de la relación con el cliente.
        """
        return self.query_builder.with_client(query)

    def with_assignments(self, query):
        """
        Añade la carga de la relación con las asignaciones.
        """
        return self.query_builder.with_assignments(query)

    def with_full_details(self, query):
        """
        Añade la carga de todas las relaciones principales.
        """
        return self.query_builder.with_full_details(query)