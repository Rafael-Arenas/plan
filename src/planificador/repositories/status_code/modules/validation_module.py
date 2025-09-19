# src/planificador/repositories/status_code/modules/validation_module.py

"""
Módulo de validación para operaciones de validación del repositorio StatusCode.

Este módulo implementa las operaciones de validación de datos y reglas de negocio
para códigos de estado, incluyendo validación de unicidad y consistencia.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de validación
    - Business Rules: Implementación de reglas de negocio específicas
    - Error Handling: Manejo robusto de errores con logging estructurado

Uso:
    ```python
    validation_module = StatusCodeValidationModule(session)
    is_unique = await validation_module.is_code_unique("NEW_CODE")
    is_valid = await validation_module.validate_status_code_data(data)
    conflicts = await validation_module.check_display_order_conflicts(order)
    ```
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.status_code import StatusCode
from planificador.repositories.status_code.interfaces.validation_interface import IStatusCodeValidationOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    StatusCodeRepositoryError,
    convert_sqlalchemy_error
)


class StatusCodeValidationModule(BaseRepository[StatusCode], IStatusCodeValidationOperations):
    """
    Módulo para operaciones de validación del repositorio StatusCode.
    
    Implementa las operaciones de validación de datos y reglas de negocio
    para códigos de estado, incluyendo validación de unicidad, consistencia
    y reglas específicas del dominio.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo StatusCode
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de validación para StatusCode.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, StatusCode)

    async def is_code_unique(self, code: str, exclude_id: Optional[int] = None) -> bool:
        """
        Valida si un código es único en el sistema.
        
        Args:
            code: Código a validar
            exclude_id: ID a excluir de la validación (para actualizaciones)
            
        Returns:
            bool: True si el código es único, False si ya existe
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(f"Validando unicidad del código: {code}")
            
            stmt = select(StatusCode).where(StatusCode.code == code)
            if exclude_id:
                stmt = stmt.where(StatusCode.id != exclude_id)
            
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            is_unique = existing is None
            self._logger.debug(f"Código {code} es único: {is_unique}")
            
            return is_unique
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al validar unicidad del código: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="is_code_unique",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar unicidad del código: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al validar unicidad del código: {e}",
                operation="is_code_unique",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def is_name_unique(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Valida si un nombre es único en el sistema.
        
        Args:
            name: Nombre a validar
            exclude_id: ID a excluir de la validación (para actualizaciones)
            
        Returns:
            bool: True si el nombre es único, False si ya existe
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(f"Validando unicidad del nombre: {name}")
            
            stmt = select(StatusCode).where(StatusCode.name == name)
            if exclude_id:
                stmt = stmt.where(StatusCode.id != exclude_id)
            
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            is_unique = existing is None
            self._logger.debug(f"Nombre {name} es único: {is_unique}")
            
            return is_unique
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al validar unicidad del nombre: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="is_name_unique",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar unicidad del nombre: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al validar unicidad del nombre: {e}",
                operation="is_name_unique",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def validate_status_code_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida los datos de un código de estado según las reglas de negocio.
        
        Args:
            data: Diccionario con los datos a validar
            
        Returns:
            Tuple[bool, List[str]]: (es_válido, lista_de_errores)
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(f"Validando datos del código de estado: {data.get('code', 'N/A')}")
            
            errors = []
            
            # Validar campos requeridos
            required_fields = ['code', 'name']
            for field in required_fields:
                if not data.get(field):
                    errors.append(f"El campo '{field}' es requerido")
            
            # Validar longitud del código
            if data.get('code') and len(data['code']) > 50:
                errors.append("El código no puede exceder 50 caracteres")
            
            # Validar longitud del nombre
            if data.get('name') and len(data['name']) > 100:
                errors.append("El nombre no puede exceder 100 caracteres")
            
            # Validar display_order
            if 'display_order' in data:
                display_order = data['display_order']
                if display_order is not None and display_order < 0:
                    errors.append("El orden de visualización debe ser mayor o igual a 0")
            
            # Validar unicidad del código
            if data.get('code'):
                exclude_id = data.get('id')
                if not await self.is_code_unique(data['code'], exclude_id):
                    errors.append(f"El código '{data['code']}' ya existe")
            
            # Validar unicidad del nombre
            if data.get('name'):
                exclude_id = data.get('id')
                if not await self.is_name_unique(data['name'], exclude_id):
                    errors.append(f"El nombre '{data['name']}' ya existe")
            
            is_valid = len(errors) == 0
            self._logger.debug(f"Validación completada. Válido: {is_valid}, Errores: {len(errors)}")
            
            return is_valid, errors
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al validar datos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_status_code_data",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar datos: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al validar datos: {e}",
                operation="validate_status_code_data",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def check_display_order_conflicts(
        self, 
        display_order: int, 
        exclude_id: Optional[int] = None
    ) -> List[StatusCode]:
        """
        Verifica si hay conflictos con el orden de visualización.
        
        Args:
            display_order: Orden de visualización a verificar
            exclude_id: ID a excluir de la verificación
            
        Returns:
            List[StatusCode]: Lista de códigos con el mismo orden
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la verificación
        """
        try:
            self._logger.debug(f"Verificando conflictos de display_order: {display_order}")
            
            stmt = select(StatusCode).where(StatusCode.display_order == display_order)
            if exclude_id:
                stmt = stmt.where(StatusCode.id != exclude_id)
            
            result = await self.session.execute(stmt)
            conflicts = list(result.scalars().all())
            
            self._logger.debug(f"Encontrados {len(conflicts)} conflictos de display_order")
            return conflicts
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al verificar conflictos de display_order: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="check_display_order_conflicts",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al verificar conflictos de display_order: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al verificar conflictos de display_order: {e}",
                operation="check_display_order_conflicts",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def validate_default_status_rules(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida las reglas específicas para códigos de estado por defecto.
        
        Args:
            data: Diccionario con los datos a validar
            
        Returns:
            Tuple[bool, List[str]]: (es_válido, lista_de_errores)
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug("Validando reglas de códigos de estado por defecto")
            
            errors = []
            
            # Si se marca como default, debe estar activo
            if data.get('is_default') and not data.get('is_active', True):
                errors.append("Un código de estado por defecto debe estar activo")
            
            # Verificar si ya existe otro código por defecto
            if data.get('is_default'):
                exclude_id = data.get('id')
                stmt = select(StatusCode).where(StatusCode.is_default == True)
                if exclude_id:
                    stmt = stmt.where(StatusCode.id != exclude_id)
                
                result = await self.session.execute(stmt)
                existing_default = result.scalar_one_or_none()
                
                if existing_default:
                    errors.append(f"Ya existe un código por defecto: {existing_default.code}")
            
            is_valid = len(errors) == 0
            self._logger.debug(f"Validación de reglas por defecto completada. Válido: {is_valid}")
            
            return is_valid, errors
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al validar reglas por defecto: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_default_status_rules",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar reglas por defecto: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al validar reglas por defecto: {e}",
                operation="validate_default_status_rules",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def validate_business_rules(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida todas las reglas de negocio para un código de estado.
        
        Args:
            data: Diccionario con los datos a validar
            
        Returns:
            Tuple[bool, List[str]]: (es_válido, lista_de_errores_consolidados)
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug("Validando todas las reglas de negocio")
            
            all_errors = []
            
            # Validar datos básicos
            is_valid_data, data_errors = await self.validate_status_code_data(data)
            all_errors.extend(data_errors)
            
            # Validar reglas de códigos por defecto
            is_valid_default, default_errors = await self.validate_default_status_rules(data)
            all_errors.extend(default_errors)
            
            is_valid = len(all_errors) == 0
            self._logger.debug(f"Validación completa de reglas de negocio. Válido: {is_valid}, Total errores: {len(all_errors)}")
            
            return is_valid, all_errors
            
        except Exception as e:
            self._logger.error(f"Error al validar reglas de negocio: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error al validar reglas de negocio: {e}",
                operation="validate_business_rules",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    # ==========================================
    # IMPLEMENTACIÓN DE MÉTODOS ABSTRACTOS DE LA INTERFAZ
    # ==========================================

    async def validate_code_uniqueness(
        self, 
        code: str, 
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Valida que un código sea único en el sistema.
        
        Args:
            code: Código a validar
            exclude_id: ID a excluir de la validación (para actualizaciones)
            
        Returns:
            bool: True si el código es único, False si ya existe
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        try:
            query = select(StatusCode).where(StatusCode.code == code)
            
            if exclude_id is not None:
                query = query.where(StatusCode.id != exclude_id)
            
            result = await self.session.execute(query)
            existing_code = result.scalar_one_or_none()
            
            is_unique = existing_code is None
            
            self._logger.info(
                f"Validación de unicidad de código: {code}, "
                f"único: {is_unique}, excluir_id: {exclude_id}"
            )
            
            return is_unique
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error validando unicidad de código {code}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_code_uniqueness",
                entity_type=self.model_class.__name__,
                entity_id=exclude_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando unicidad de código {code}: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado validando unicidad de código: {e}",
                operation="validate_code_uniqueness",
                entity_type=self.model_class.__name__,
                entity_id=exclude_id,
                original_error=e
            )

    async def validate_sort_order_uniqueness(
        self, 
        sort_order: int, 
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Valida que un orden de clasificación sea único.
        
        Args:
            sort_order: Orden de clasificación a validar
            exclude_id: ID a excluir de la validación (para actualizaciones)
            
        Returns:
            bool: True si el orden es único, False si ya existe
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        try:
            query = select(StatusCode).where(StatusCode.sort_order == sort_order)
            
            if exclude_id is not None:
                query = query.where(StatusCode.id != exclude_id)
            
            result = await self.session.execute(query)
            existing_order = result.scalar_one_or_none()
            
            is_unique = existing_order is None
            
            self._logger.info(
                f"Validación de unicidad de orden: {sort_order}, "
                f"único: {is_unique}, excluir_id: {exclude_id}"
            )
            
            return is_unique
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error validando unicidad de orden {sort_order}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_sort_order_uniqueness",
                entity_type=self.model_class.__name__,
                entity_id=exclude_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando unicidad de orden {sort_order}: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado validando unicidad de orden: {e}",
                operation="validate_sort_order_uniqueness",
                entity_type=self.model_class.__name__,
                entity_id=exclude_id,
                original_error=e
            )

    async def validate_status_code_can_be_deactivated(self, entity_id: int) -> bool:
        """
        Valida si un código de estado puede ser desactivado.
        
        Verifica que la desactivación no afecte registros activos
        o procesos en curso.
        
        Args:
            entity_id: ID del código de estado
            
        Returns:
            bool: True si puede ser desactivado, False en caso contrario
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        try:
            # Verificar que el código de estado existe
            status_code = await self.get_by_id(entity_id)
            if not status_code:
                self._logger.warning(f"Código de estado {entity_id} no encontrado para validación de desactivación")
                return False
            
            # Si ya está inactivo, no se puede desactivar
            if not status_code.is_active:
                self._logger.info(f"Código de estado {entity_id} ya está inactivo")
                return False
            
            # TODO: Implementar validaciones específicas de negocio
            # Por ejemplo, verificar si está siendo usado en horarios activos,
            # cargas de trabajo en curso, etc.
            
            can_be_deactivated = True
            
            self._logger.info(
                f"Validación de desactivación para código {entity_id}: {can_be_deactivated}"
            )
            
            return can_be_deactivated
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error validando desactivación de código {entity_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_status_code_can_be_deactivated",
                entity_type=self.model_class.__name__,
                entity_id=entity_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando desactivación de código {entity_id}: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado validando desactivación: {e}",
                operation="validate_status_code_can_be_deactivated",
                entity_type=self.model_class.__name__,
                entity_id=entity_id,
                original_error=e
            )

    async def validate_status_code_can_be_deleted(self, entity_id: int) -> bool:
        """
        Valida si un código de estado puede ser eliminado.
        
        Verifica que el código no esté siendo utilizado en horarios,
        cargas de trabajo u otras entidades relacionadas.
        
        Args:
            entity_id: ID del código de estado
            
        Returns:
            bool: True si puede ser eliminado, False en caso contrario
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        try:
            # Verificar que el código de estado existe
            status_code = await self.get_by_id(entity_id)
            if not status_code:
                self._logger.warning(f"Código de estado {entity_id} no encontrado para validación de eliminación")
                return False
            
            # TODO: Implementar validaciones específicas de negocio
            # Por ejemplo, verificar si está siendo usado en:
            # - Horarios de trabajo
            # - Cargas de trabajo
            # - Registros históricos importantes
            # - Configuraciones del sistema
            
            can_be_deleted = True
            
            self._logger.info(
                f"Validación de eliminación para código {entity_id}: {can_be_deleted}"
            )
            
            return can_be_deleted
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error validando eliminación de código {entity_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_status_code_can_be_deleted",
                entity_type=self.model_class.__name__,
                entity_id=entity_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando eliminación de código {entity_id}: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado validando eliminación: {e}",
                operation="validate_status_code_can_be_deleted",
                entity_type=self.model_class.__name__,
                entity_id=entity_id,
                original_error=e
            )

    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[StatusCode]:
        """
        Obtiene una entidad por un campo único específico.
        
        Args:
            field_name: Nombre del campo único
            value: Valor a buscar
            
        Returns:
            Optional[StatusCode]: La entidad encontrada o None
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        try:
            # Validar que el campo existe en el modelo
            if not hasattr(StatusCode, field_name):
                raise ValueError(f"Campo '{field_name}' no existe en el modelo StatusCode")
            
            field = getattr(StatusCode, field_name)
            query = select(StatusCode).where(field == value)
            
            result = await self.session.execute(query)
            entity = result.scalar_one_or_none()
            
            self._logger.debug(
                f"Búsqueda por campo único {field_name}={value}: "
                f"{'encontrado' if entity else 'no encontrado'}"
            )
            
            return entity
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando por campo {field_name}={value}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_unique_field",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando por campo {field_name}={value}: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado en búsqueda por campo único: {e}",
                operation="get_by_unique_field",
                entity_type=self.model_class.__name__,
                original_error=e
            )