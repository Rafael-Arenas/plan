# src/planificador/repositories/base_repository.py
from typing import Generic, TypeVar, Type, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.base import BaseModel
from planificador.exceptions.repository import (
    convert_sqlalchemy_error,
    RepositoryError,
)

Model = TypeVar("Model", bound=BaseModel)


class BaseRepository(Generic[Model]):
    """
    Repositorio base con operaciones CRUD genéricas.
    """

    def __init__(self, session: AsyncSession, model_class: Type[Model]):
        """
        Inicializa el repositorio base.

        Args:
            session: La sesión de base de datos asíncrona.
            model_class: La clase del modelo SQLAlchemy.
        """
        self.session = session
        self.model_class = model_class
        self._logger = logger

    async def get_by_id(self, entity_id: Any) -> Optional[Model]:
        """
        Obtiene una entidad por su ID.

        Args:
            entity_id: El ID de la entidad.

        Returns:
            La entidad si se encuentra, de lo contrario None.
        """
        try:
            result = await self.session.get(self.model_class, entity_id)
            return result
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener {self.model_class.__name__} por ID: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_id",
                entity_type=self.model_class.__name__,
                entity_id=entity_id,
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener {self.model_class.__name__} por ID: {e}")
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_by_id",
                entity_type=self.model_class.__name__,
                entity_id=entity_id,
                original_error=e,
            )

    async def get_all(self) -> List[Model]:
        """
        Obtiene todas las entidades de un tipo.

        Returns:
            Una lista de todas las entidades.
        """
        try:
            result = await self.session.execute(select(self.model_class))
            return result.scalars().all()
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener todos los {self.model_class.__name__}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_all",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener todos los {self.model_class.__name__}: {e}")
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_all",
                entity_type=self.model_class.__name__,
                original_error=e,
            )