# src/planificador/database/repositories/base_repository.py
"""
Repositorio base para operaciones CRUD asíncronas.

Este módulo define la clase BaseRepository que proporciona operaciones
CRUD estándar y manejo de errores para todos los repositorios del sistema.
Implementa las mejores prácticas de SQLAlchemy asíncrono y manejo de excepciones.
"""

from typing import (
    TypeVar, 
    Generic, 
    Type, 
    Optional, 
    List, 
    Dict, 
    Any, 
    Union,
    Sequence
)
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
from loguru import logger

from ..models.base import BaseModel
from ..exceptions import (
    RepositoryError,
    convert_sqlalchemy_error,
    NotFoundError
)
from ..config.config import settings

# Type variable para el modelo genérico
ModelType = TypeVar('ModelType', bound=BaseModel)


class BaseRepository(Generic[ModelType], ABC):
    """
    Repositorio base genérico para operaciones CRUD asíncronas.
    
    Proporciona operaciones estándar de base de datos con manejo robusto
    de errores, logging estructurado y optimizaciones de performance.
    
    Attributes:
        model_class: Clase del modelo SQLAlchemy
        session: Sesión asíncrona de SQLAlchemy
        _logger: Logger configurado para el repositorio
    """
    
    def __init__(self, session: AsyncSession, model_class: Type[ModelType]):
        """
        Inicializa el repositorio base.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
            model_class: Clase del modelo a gestionar
        """
        self.session = session
        self.model_class = model_class
        self._logger = logger.bind(
            repository=self.__class__.__name__,
            model=model_class.__name__
        )
        
        # Configuración de logging según el entorno
        if settings.debug_mode:
            self._logger.debug(f"Repositorio {self.__class__.__name__} inicializado para modelo {model_class.__name__}")
    
    # ========================================================================
    # OPERACIONES CRUD BÁSICAS
    # ========================================================================
    
    async def create(self, entity: ModelType) -> ModelType:
        """
        Crea una nueva entidad en la base de datos.
        
        Args:
            entity: Instancia del modelo a crear
            
        Returns:
            Entidad creada con ID asignado
            
        Raises:
            RepositoryError: Si ocurre un error durante la creación
        """
        try:
            self.session.add(entity)
            await self.session.flush()  # Obtiene el ID sin hacer commit
            await self.session.refresh(entity)  # Refresca para obtener valores calculados
            
            self._logger.info(
                f"Entidad {self.model_class.__name__} creada exitosamente",
                entity_id=entity.id
            )
            
            return entity
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error al crear {self.model_class.__name__}: {e}",
                error_type=type(e).__name__
            )
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="create",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado al crear {self.model_class.__name__}: {e}",
                error_type=type(e).__name__
            )
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado al crear {self.model_class.__name__}: {e}",
                operation="create",
                entity_type=self.model_class.__name__,
                original_error=e
            )
    
    async def get_by_id(self, entity_id: Union[int, str]) -> Optional[ModelType]:
        """
        Obtiene una entidad por su ID.
        
        Args:
            entity_id: ID de la entidad a buscar
            
        Returns:
            Entidad encontrada o None si no existe
            
        Raises:
            RepositoryError: Si ocurre un error durante la consulta
        """
        try:
            stmt = select(self.model_class).where(self.model_class.id == entity_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            
            if entity:
                self._logger.debug(
                    f"{self.model_class.__name__} encontrado",
                    entity_id=entity_id
                )
            else:
                self._logger.debug(
                    f"{self.model_class.__name__} no encontrado",
                    entity_id=entity_id
                )
            
            return entity
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error al buscar {self.model_class.__name__} por ID {entity_id}: {e}",
                entity_id=entity_id,
                error_type=type(e).__name__
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_id",
                entity_type=self.model_class.__name__,
                entity_id=entity_id
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado al buscar {self.model_class.__name__} por ID {entity_id}: {e}",
                entity_id=entity_id,
                error_type=type(e).__name__
            )
            raise RepositoryError(
                message=f"Error inesperado al buscar {self.model_class.__name__}: {e}",
                operation="get_by_id",
                entity_type=self.model_class.__name__,
                entity_id=entity_id,
                original_error=e
            )
    
    async def get_all(
        self, 
        limit: Optional[int] = None, 
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Obtiene todas las entidades con paginación opcional.
        
        Args:
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            order_by: Campo por el cual ordenar (por defecto 'id')
            
        Returns:
            Lista de entidades
            
        Raises:
            RepositoryError: Si ocurre un error durante la consulta
        """
        try:
            stmt = select(self.model_class)
            
            # Aplicar ordenamiento
            if order_by:
                if hasattr(self.model_class, order_by):
                    stmt = stmt.order_by(getattr(self.model_class, order_by))
                else:
                    self._logger.warning(
                        f"Campo de ordenamiento '{order_by}' no existe en {self.model_class.__name__}, usando 'id'"
                    )
                    stmt = stmt.order_by(self.model_class.id)
            else:
                stmt = stmt.order_by(self.model_class.id)
            
            # Aplicar paginación
            if offset is not None:
                stmt = stmt.offset(offset)
            if limit is not None:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            entities = result.scalars().all()
            
            self._logger.debug(
                f"Obtenidas {len(entities)} entidades de {self.model_class.__name__}",
                count=len(entities),
                limit=limit,
                offset=offset
            )
            
            return list(entities)
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error al obtener todas las entidades de {self.model_class.__name__}: {e}",
                error_type=type(e).__name__
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_all",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado al obtener todas las entidades de {self.model_class.__name__}: {e}",
                error_type=type(e).__name__
            )
            raise RepositoryError(
                message=f"Error inesperado al obtener entidades: {e}",
                operation="get_all",
                entity_type=self.model_class.__name__,
                original_error=e
            )
    
    async def update(self, entity: ModelType) -> ModelType:
        """
        Actualiza una entidad existente.
        
        Args:
            entity: Entidad con los datos actualizados
            
        Returns:
            Entidad actualizada
            
        Raises:
            RepositoryError: Si ocurre un error durante la actualización
        """
        try:
            # Verificar que la entidad existe
            if not entity.id:
                raise RepositoryError(
                    message="No se puede actualizar una entidad sin ID",
                    operation="update",
                    entity_type=self.model_class.__name__
                )
            
            await self.session.merge(entity)
            await self.session.flush()
            await self.session.refresh(entity)
            
            self._logger.info(
                f"Entidad {self.model_class.__name__} actualizada exitosamente",
                entity_id=entity.id
            )
            
            return entity
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error al actualizar {self.model_class.__name__} ID {entity.id}: {e}",
                entity_id=entity.id,
                error_type=type(e).__name__
            )
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="update",
                entity_type=self.model_class.__name__,
                entity_id=entity.id
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado al actualizar {self.model_class.__name__} ID {entity.id}: {e}",
                entity_id=entity.id,
                error_type=type(e).__name__
            )
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado al actualizar {self.model_class.__name__}: {e}",
                operation="update",
                entity_type=self.model_class.__name__,
                entity_id=entity.id,
                original_error=e
            )
    
    async def delete(self, entity_id: Union[int, str]) -> bool:
        """
        Elimina una entidad por su ID.
        
        Args:
            entity_id: ID de la entidad a eliminar
            
        Returns:
            True si se eliminó exitosamente, False si no se encontró
            
        Raises:
            RepositoryError: Si ocurre un error durante la eliminación
        """
        try:
            # Verificar que la entidad existe
            entity = await self.get_by_id(entity_id)
            if not entity:
                self._logger.warning(
                    f"Intento de eliminar {self.model_class.__name__} inexistente",
                    entity_id=entity_id
                )
                return False
            
            await self.session.delete(entity)
            await self.session.flush()
            
            self._logger.info(
                f"Entidad {self.model_class.__name__} eliminada exitosamente",
                entity_id=entity_id
            )
            
            return True
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error al eliminar {self.model_class.__name__} ID {entity_id}: {e}",
                entity_id=entity_id,
                error_type=type(e).__name__
            )
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="delete",
                entity_type=self.model_class.__name__,
                entity_id=entity_id
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado al eliminar {self.model_class.__name__} ID {entity_id}: {e}",
                entity_id=entity_id,
                error_type=type(e).__name__
            )
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado al eliminar {self.model_class.__name__}: {e}",
                operation="delete",
                entity_type=self.model_class.__name__,
                entity_id=entity_id,
                original_error=e
            )
    
    # ========================================================================
    # OPERACIONES DE CONSULTA AVANZADAS
    # ========================================================================
    
    async def exists(self, entity_id: Union[int, str]) -> bool:
        """
        Verifica si una entidad existe por su ID.
        
        Args:
            entity_id: ID de la entidad a verificar
            
        Returns:
            True si existe, False en caso contrario
            
        Raises:
            RepositoryError: Si ocurre un error durante la consulta
        """
        try:
            stmt = select(func.count(self.model_class.id)).where(
                self.model_class.id == entity_id
            )
            result = await self.session.execute(stmt)
            count = result.scalar()
            
            exists = count > 0
            self._logger.debug(
                f"Verificación de existencia de {self.model_class.__name__}",
                entity_id=entity_id,
                exists=exists
            )
            
            return exists
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error al verificar existencia de {self.model_class.__name__} ID {entity_id}: {e}",
                entity_id=entity_id,
                error_type=type(e).__name__
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="exists",
                entity_type=self.model_class.__name__,
                entity_id=entity_id
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado al verificar existencia de {self.model_class.__name__} ID {entity_id}: {e}",
                entity_id=entity_id,
                error_type=type(e).__name__
            )
            raise RepositoryError(
                message=f"Error inesperado al verificar existencia: {e}",
                operation="exists",
                entity_type=self.model_class.__name__,
                entity_id=entity_id,
                original_error=e
            )
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta el número total de entidades con filtros opcionales.
        
        Args:
            filters: Diccionario de filtros a aplicar
            
        Returns:
            Número total de entidades
            
        Raises:
            RepositoryError: Si ocurre un error durante el conteo
        """
        try:
            stmt = select(func.count(self.model_class.id))
            
            # Aplicar filtros si se proporcionan
            if filters:
                conditions = []
                for field, value in filters.items():
                    if hasattr(self.model_class, field):
                        conditions.append(getattr(self.model_class, field) == value)
                    else:
                        self._logger.warning(
                            f"Campo de filtro '{field}' no existe en {self.model_class.__name__}"
                        )
                
                if conditions:
                    stmt = stmt.where(and_(*conditions))
            
            result = await self.session.execute(stmt)
            count = result.scalar()
            
            self._logger.debug(
                f"Conteo de {self.model_class.__name__} completado",
                count=count,
                filters=filters
            )
            
            return count
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error al contar entidades de {self.model_class.__name__}: {e}",
                filters=filters,
                error_type=type(e).__name__
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="count",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado al contar entidades de {self.model_class.__name__}: {e}",
                filters=filters,
                error_type=type(e).__name__
            )
            raise RepositoryError(
                message=f"Error inesperado al contar entidades: {e}",
                operation="count",
                entity_type=self.model_class.__name__,
                original_error=e
            )
    
    async def find_by_criteria(
        self, 
        criteria: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Busca entidades que cumplan con criterios específicos.
        
        Args:
            criteria: Diccionario de criterios de búsqueda
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            order_by: Campo por el cual ordenar
            
        Returns:
            Lista de entidades que cumplen los criterios
            
        Raises:
            RepositoryError: Si ocurre un error durante la búsqueda
        """
        try:
            stmt = select(self.model_class)
            
            # Aplicar criterios de búsqueda
            conditions = []
            for field, value in criteria.items():
                if hasattr(self.model_class, field):
                    if isinstance(value, list):
                        # Para listas, usar IN
                        conditions.append(getattr(self.model_class, field).in_(value))
                    elif isinstance(value, dict) and 'operator' in value:
                        # Para operadores especiales
                        field_attr = getattr(self.model_class, field)
                        operator = value['operator']
                        val = value['value']
                        
                        if operator == 'like':
                            conditions.append(field_attr.like(f"%{val}%"))
                        elif operator == 'ilike':
                            conditions.append(field_attr.ilike(f"%{val}%"))
                        elif operator == 'iexact':
                            conditions.append(field_attr.ilike(val))
                        elif operator == 'gt':
                            conditions.append(field_attr > val)
                        elif operator == 'gte':
                            conditions.append(field_attr >= val)
                        elif operator == 'lt':
                            conditions.append(field_attr < val)
                        elif operator == 'lte':
                            conditions.append(field_attr <= val)
                        elif operator == 'ne':
                            conditions.append(field_attr != val)
                        else:
                            conditions.append(field_attr == val)
                    else:
                        # Igualdad simple
                        conditions.append(getattr(self.model_class, field) == value)
                else:
                    self._logger.warning(
                        f"Campo de criterio '{field}' no existe en {self.model_class.__name__}"
                    )
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            # Aplicar ordenamiento
            if order_by and hasattr(self.model_class, order_by):
                stmt = stmt.order_by(getattr(self.model_class, order_by))
            else:
                stmt = stmt.order_by(self.model_class.id)
            
            # Aplicar paginación
            if offset is not None:
                stmt = stmt.offset(offset)
            if limit is not None:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            entities = result.scalars().all()
            
            self._logger.debug(
                f"Búsqueda por criterios en {self.model_class.__name__} completada",
                count=len(entities),
                criteria=criteria
            )
            
            return list(entities)
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error en búsqueda por criterios de {self.model_class.__name__}: {e}",
                criteria=criteria,
                error_type=type(e).__name__
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_by_criteria",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado en búsqueda por criterios de {self.model_class.__name__}: {e}",
                criteria=criteria,
                error_type=type(e).__name__
            )
            raise RepositoryError(
                message=f"Error inesperado en búsqueda por criterios: {e}",
                operation="find_by_criteria",
                entity_type=self.model_class.__name__,
                original_error=e
            )
    
    # ========================================================================
    # OPERACIONES DE TRANSACCIÓN
    # ========================================================================
    
    async def commit(self) -> None:
        """
        Confirma la transacción actual.
        
        Raises:
            RepositoryError: Si ocurre un error durante el commit
        """
        try:
            await self.session.commit()
            self._logger.debug(f"Transacción confirmada para {self.model_class.__name__}")
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error al confirmar transacción para {self.model_class.__name__}: {e}",
                error_type=type(e).__name__
            )
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="commit",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado al confirmar transacción para {self.model_class.__name__}: {e}",
                error_type=type(e).__name__
            )
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado al confirmar transacción: {e}",
                operation="commit",
                entity_type=self.model_class.__name__,
                original_error=e
            )
    
    async def rollback(self) -> None:
        """
        Revierte la transacción actual.
        
        Raises:
            RepositoryError: Si ocurre un error durante el rollback
        """
        try:
            await self.session.rollback()
            self._logger.debug(f"Transacción revertida para {self.model_class.__name__}")
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error al revertir transacción para {self.model_class.__name__}: {e}",
                error_type=type(e).__name__
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="rollback",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado al revertir transacción para {self.model_class.__name__}: {e}",
                error_type=type(e).__name__
            )
            raise RepositoryError(
                message=f"Error inesperado al revertir transacción: {e}",
                operation="rollback",
                entity_type=self.model_class.__name__,
                original_error=e
            )
    
    # ========================================================================
    # MÉTODOS ABSTRACTOS PARA IMPLEMENTACIÓN ESPECÍFICA
    # ========================================================================
    
    @abstractmethod
    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        """
        Obtiene una entidad por un campo único específico.
        
        Este método debe ser implementado por cada repositorio específico
        según los campos únicos de su modelo.
        
        Args:
            field_name: Nombre del campo único
            value: Valor a buscar
            
        Returns:
            Entidad encontrada o None si no existe
        """
        pass
    
    # ========================================================================
    # MÉTODOS DE UTILIDAD
    # ========================================================================
    
    def _build_select_statement(self, *options):
        """
        Construye un statement SELECT base con opciones de carga.
        
        Args:
            *options: Opciones de carga (selectinload, joinedload, etc.)
            
        Returns:
            Statement SELECT configurado
        """
        stmt = select(self.model_class)
        if options:
            stmt = stmt.options(*options)
        return stmt
    
    def _log_operation_start(self, operation: str, **context):
        """
        Registra el inicio de una operación.
        
        Args:
            operation: Nombre de la operación
            **context: Contexto adicional para el log
        """
        if settings.debug_mode:
            self._logger.debug(
                f"Iniciando operación {operation} en {self.model_class.__name__}",
                operation=operation,
                **context
            )
    
    def _log_operation_success(self, operation: str, **context):
        """
        Registra el éxito de una operación.
        
        Args:
            operation: Nombre de la operación
            **context: Contexto adicional para el log
        """
        self._logger.info(
            f"Operación {operation} completada exitosamente en {self.model_class.__name__}",
            operation=operation,
            **context
        )
    
    def _validate_entity(self, entity: ModelType) -> None:
        """
        Valida una entidad antes de operaciones de base de datos.
        
        Args:
            entity: Entidad a validar
            
        Raises:
            RepositoryError: Si la entidad no es válida
        """
        if not isinstance(entity, self.model_class):
            raise RepositoryError(
                message=f"La entidad debe ser una instancia de {self.model_class.__name__}",
                operation="validate",
                entity_type=self.model_class.__name__
            )
    
    def get_model_class(self) -> Type[ModelType]:
        """
        Retorna la clase del modelo gestionado por este repositorio.
        
        Returns:
            Clase del modelo
        """
        return self.model_class
    
    def get_session(self) -> AsyncSession:
        """
        Retorna la sesión de base de datos actual.
        
        Returns:
            Sesión asíncrona de SQLAlchemy
        """
        return self.session