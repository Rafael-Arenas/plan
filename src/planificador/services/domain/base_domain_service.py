# src/planificador/services/domain/base_domain_service.py

"""
Servicio base para servicios de dominio.

Este módulo define la clase BaseDomainService que proporciona funcionalidades
comunes para todos los servicios de dominio, incluyendo operaciones CRUD básicas,
validaciones, manejo de transacciones y logging estructurado.
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
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from ...models.base import BaseModel
from ...exceptions.base import (
    BusinessLogicError,
    ValidationError,
    NotFoundError,
    ConflictError,
)
from ...exceptions import (
    NotFoundError,
    ValidationError,
    ConflictError,
    create_not_found_error,
    create_validation_error,
    create_conflict_error
)
from ...config.config import get_settings
from ...utils.date_utils import get_current_datetime

# Type variable para el modelo genérico
ModelType = TypeVar('ModelType', bound=BaseModel)


class BaseDomainService(Generic[ModelType], ABC):
    """
    Servicio base genérico para servicios de dominio.
    
    Proporciona funcionalidades comunes como operaciones CRUD básicas,
    validaciones, manejo de transacciones, logging estructurado y
    gestión de errores específicos del dominio.
    
    Attributes:
        session: Sesión asíncrona de SQLAlchemy
        settings: Configuraciones del sistema
        _logger: Logger configurado para el servicio
        _service_name: Nombre del servicio para logging y errores
    """
    
    def __init__(
        self,
        session: AsyncSession,
        service_name: Optional[str] = None
    ):
        """
        Inicializa el servicio base de dominio.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
            service_name: Nombre del servicio (se infiere de la clase si no se proporciona)
        """
        self.session = session
        self.settings = get_settings()
        self._logger = logger.bind(service=service_name or self.__class__.__name__)
        self._service_name = service_name or self.__class__.__name__
        
        # Configurar contexto de logging
        self._logger = self._logger.bind(
            service_type="domain_service",
            service_name=self._service_name
        )
    
    @property
    @abstractmethod
    def model_class(self) -> Type[ModelType]:
        """
        Clase del modelo SQLAlchemy asociado al servicio.
        
        Returns:
            Type[ModelType]: Clase del modelo
        """
        pass
    
    @property
    @abstractmethod
    def entity_name(self) -> str:
        """
        Nombre de la entidad para mensajes de error y logging.
        
        Returns:
            str: Nombre de la entidad (ej: "cliente", "proyecto")
        """
        pass
    
    # ============================================================================
    # GESTIÓN DE TRANSACCIONES
    # ============================================================================
    
    @asynccontextmanager
    async def transaction(self):
        """
        Context manager para manejo de transacciones.
        
        Proporciona rollback automático en caso de error y commit
        automático en caso de éxito.
        
        Yields:
            AsyncSession: Sesión de base de datos
            
        Raises:
            DomainTransactionError: Si ocurre un error durante la transacción
        """
        try:
            self._logger.debug(f"Iniciando transacción en {self._service_name}")
            yield self.session
            await self.session.commit()
            self._logger.debug(f"Transacción completada exitosamente en {self._service_name}")
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos en transacción: {e}")
            await self.session.rollback()
            raise BusinessLogicError(
                message=f"Error de base de datos durante la transacción: {e}"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en transacción: {e}")
            await self.session.rollback()
            raise BusinessLogicError(
                message=f"Error inesperado durante la transacción: {e}"
            )
    
    # ============================================================================
    # VALIDACIONES COMUNES
    # ============================================================================
    
    async def _validate_entity_exists(
        self,
        entity_id: Union[int, str],
        operation: str = "validation"
    ) -> ModelType:
        """
        Valida que una entidad existe por su ID.
        
        Args:
            entity_id: ID de la entidad
            operation: Nombre de la operación para contexto de error
            
        Returns:
            ModelType: La entidad encontrada
            
        Raises:
            NotFoundError: Si la entidad no existe
            BusinessLogicError: Si ocurre un error durante la validación
        """
        try:
            entity = await self.session.get(self.model_class, entity_id)
            if not entity:
                self._logger.warning(
                    f"{self.entity_name.capitalize()} no encontrado",
                    extra={"entity_id": entity_id, "operation": operation}
                )
                raise create_not_found_error(
                    entity_type=self.entity_name,
                    entity_id=entity_id
                )
            
            self._logger.debug(
                f"{self.entity_name.capitalize()} encontrado",
                extra={"entity_id": entity_id, "operation": operation}
            )
            return entity
            
        except NotFoundError:
            raise
        except Exception as e:
            self._logger.error(f"Error al validar existencia de {self.entity_name}: {e}")
            raise BusinessLogicError(
                message=f"Error al validar existencia de {self.entity_name}: {e}"
            )
    
    def _validate_required_fields(
        self,
        data: Dict[str, Any],
        required_fields: List[str],
        operation: str = "validation"
    ) -> None:
        """
        Valida que los campos requeridos estén presentes y no sean vacíos.
        
        Args:
            data: Datos a validar
            required_fields: Lista de campos requeridos
            operation: Nombre de la operación para contexto de error
            
        Raises:
            ValidationError: Si faltan campos requeridos
        """
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                empty_fields.append(field)
        
        if missing_fields or empty_fields:
            error_details = {}
            if missing_fields:
                error_details["missing_fields"] = missing_fields
            if empty_fields:
                error_details["empty_fields"] = empty_fields
            
            self._logger.warning(
                f"Campos requeridos faltantes o vacíos en {self.entity_name}",
                extra={
                    "operation": operation,
                    "missing_fields": missing_fields,
                    "empty_fields": empty_fields
                }
            )
            
            raise ValidationError(
                message=f"Campos requeridos faltantes o vacíos: {missing_fields + empty_fields}"
            )
    
    def _validate_field_length(
        self,
        data: Dict[str, Any],
        field_constraints: Dict[str, Dict[str, int]],
        operation: str = "validation"
    ) -> None:
        """
        Valida la longitud de campos de texto.
        
        Args:
            data: Datos a validar
            field_constraints: Diccionario con restricciones de longitud
                              {campo: {"min": min_length, "max": max_length}}
            operation: Nombre de la operación para contexto de error
            
        Raises:
            ValidationError: Si algún campo no cumple las restricciones
        """
        validation_errors = {}
        
        for field, constraints in field_constraints.items():
            if field in data and data[field] is not None:
                value = str(data[field]).strip()
                min_length = constraints.get("min", 0)
                max_length = constraints.get("max", float('inf'))
                
                if len(value) < min_length:
                    validation_errors[field] = f"Debe tener al menos {min_length} caracteres"
                elif len(value) > max_length:
                    validation_errors[field] = f"No puede exceder {max_length} caracteres"
        
        if validation_errors:
            self._logger.warning(
                f"Errores de longitud de campos en {self.entity_name}",
                extra={"operation": operation, "validation_errors": validation_errors}
            )
            
            raise ValidationError(
                message=f"Errores de validación de longitud en campos: {list(validation_errors.keys())}"
            )
    
    # ============================================================================
    # MÉTODOS ABSTRACTOS PARA IMPLEMENTAR EN SERVICIOS ESPECÍFICOS
    # ============================================================================
    
    @abstractmethod
    async def _validate_business_rules(
        self,
        data: Dict[str, Any],
        operation: str,
        entity_id: Optional[Union[int, str]] = None
    ) -> None:
        """
        Valida reglas de negocio específicas del dominio.
        
        Args:
            data: Datos a validar
            operation: Operación que se está realizando
            entity_id: ID de la entidad (para actualizaciones)
            
        Raises:
            DomainBusinessRuleError: Si se violan reglas de negocio
        """
        pass
    
    @abstractmethod
    async def _transform_data_for_create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforma datos antes de crear una entidad.
        
        Args:
            data: Datos originales
            
        Returns:
            Dict[str, Any]: Datos transformados
        """
        pass
    
    @abstractmethod
    async def _transform_data_for_update(
        self,
        data: Dict[str, Any],
        current_entity: ModelType
    ) -> Dict[str, Any]:
        """
        Transforma datos antes de actualizar una entidad.
        
        Args:
            data: Datos de actualización
            current_entity: Entidad actual
            
        Returns:
            Dict[str, Any]: Datos transformados
        """
        pass
    
    @abstractmethod
    async def _after_create(self, entity: ModelType, original_data: Dict[str, Any]) -> None:
        """
        Ejecuta lógica posterior a la creación de una entidad.
        
        Args:
            entity: Entidad creada
            original_data: Datos originales utilizados para la creación
        """
        pass
    
    @abstractmethod
    async def _after_update(
        self,
        entity: ModelType,
        original_data: Dict[str, Any],
        previous_entity: ModelType
    ) -> None:
        """
        Ejecuta lógica posterior a la actualización de una entidad.
        
        Args:
            entity: Entidad actualizada
            original_data: Datos utilizados para la actualización
            previous_entity: Estado anterior de la entidad
        """
        pass
    
    @abstractmethod
    async def _after_delete(self, entity: ModelType) -> None:
        """
        Ejecuta lógica posterior a la eliminación de una entidad.
        
        Args:
            entity: Entidad eliminada
        """
        pass
    
    # ============================================================================
    # OPERACIONES CRUD BÁSICAS
    # ============================================================================
    
    async def create(self, data: Dict[str, Any]) -> ModelType:
        """
        Crea una nueva entidad.
        
        Args:
            data: Datos para crear la entidad
            
        Returns:
            ModelType: Entidad creada
            
        Raises:
            ValidationError: Si los datos no son válidos
            BusinessLogicError: Si se violan reglas de negocio o ocurre un error durante la creación
        """
        operation = "create"
        self._logger.info(f"Iniciando creación de {self.entity_name}")
        
        try:
            # Validar reglas de negocio
            await self._validate_business_rules(data, operation)
            
            # Transformar datos
            transformed_data = await self._transform_data_for_create(data)
            
            # Crear entidad
            async with self.transaction():
                entity = self.model_class(**transformed_data)
                self.session.add(entity)
                await self.session.flush()  # Para obtener el ID
                
                # Ejecutar lógica posterior
                await self._after_create(entity, data)
            
            self._logger.info(
                f"{self.entity_name.capitalize()} creado exitosamente",
                extra={"entity_id": entity.id, "operation": operation}
            )
            
            return entity
            
        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"Error al crear {self.entity_name}: {e}")
            raise BusinessLogicError(
                message=f"Error al crear {self.entity_name}: {e}"
            )
    
    async def get_by_id(self, entity_id: Union[int, str]) -> ModelType:
        """
        Obtiene una entidad por su ID.
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            ModelType: Entidad encontrada
            
        Raises:
            NotFoundError: Si la entidad no existe
            DomainServiceError: Si ocurre un error durante la consulta
        """
        operation = "get_by_id"
        self._logger.debug(f"Obteniendo {self.entity_name} por ID: {entity_id}")
        
        try:
            entity = await self._validate_entity_exists(entity_id, operation)
            
            self._logger.debug(
                f"{self.entity_name.capitalize()} obtenido exitosamente",
                extra={"entity_id": entity_id, "operation": operation}
            )
            
            return entity
            
        except NotFoundError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener {self.entity_name}: {e}")
            raise BusinessLogicError(
                message=f"Error al obtener {self.entity_name}: {e}"
            )
    
    async def update(
        self,
        entity_id: Union[int, str],
        data: Dict[str, Any]
    ) -> ModelType:
        """
        Actualiza una entidad existente.
        
        Args:
            entity_id: ID de la entidad a actualizar
            data: Datos de actualización
            
        Returns:
            ModelType: Entidad actualizada
            
        Raises:
            NotFoundError: Si la entidad no existe
            DomainValidationError: Si los datos no son válidos
            DomainBusinessRuleError: Si se violan reglas de negocio
            DomainServiceError: Si ocurre un error durante la actualización
        """
        operation = "update"
        self._logger.info(f"Iniciando actualización de {self.entity_name}: {entity_id}")
        
        try:
            # Obtener entidad actual
            current_entity = await self._validate_entity_exists(entity_id, operation)
            previous_entity = current_entity  # Para referencia posterior
            
            # Validar reglas de negocio
            await self._validate_business_rules(data, operation, entity_id)
            
            # Transformar datos
            transformed_data = await self._transform_data_for_update(data, current_entity)
            
            # Actualizar entidad
            async with self.transaction():
                for key, value in transformed_data.items():
                    setattr(current_entity, key, value)
                
                await self.session.flush()
                
                # Ejecutar lógica posterior
                await self._after_update(current_entity, data, previous_entity)
            
            self._logger.info(
                f"{self.entity_name.capitalize()} actualizado exitosamente",
                extra={"entity_id": entity_id, "operation": operation}
            )
            
            return current_entity
            
        except (NotFoundError, DomainValidationError, DomainBusinessRuleError):
            raise
        except Exception as e:
            self._logger.error(f"Error al actualizar {self.entity_name}: {e}")
            raise BusinessLogicError(
                message=f"Error al actualizar {self.entity_name}: {e}"
            )
    
    async def delete(self, entity_id: Union[int, str]) -> bool:
        """
        Elimina una entidad.
        
        Args:
            entity_id: ID de la entidad a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
            
        Raises:
            NotFoundError: Si la entidad no existe
            DomainBusinessRuleError: Si no se puede eliminar por reglas de negocio
            DomainServiceError: Si ocurre un error durante la eliminación
        """
        operation = "delete"
        self._logger.info(f"Iniciando eliminación de {self.entity_name}: {entity_id}")
        
        try:
            # Obtener entidad
            entity = await self._validate_entity_exists(entity_id, operation)
            
            # Eliminar entidad
            async with self.transaction():
                await self.session.delete(entity)
                await self.session.flush()
                
                # Ejecutar lógica posterior
                await self._after_delete(entity)
            
            self._logger.info(
                f"{self.entity_name.capitalize()} eliminado exitosamente",
                extra={"entity_id": entity_id, "operation": operation}
            )
            
            return True
            
        except (NotFoundError, DomainBusinessRuleError):
            raise
        except Exception as e:
            self._logger.error(f"Error al eliminar {self.entity_name}: {e}")
            raise BusinessLogicError(
                message=f"Error al eliminar {self.entity_name}: {e}"
            )
    
    # ============================================================================
    # UTILIDADES DE LOGGING
    # ============================================================================
    
    def _log_operation_start(self, operation: str, **context) -> None:
        """
        Registra el inicio de una operación.
        
        Args:
            operation: Nombre de la operación
            **context: Contexto adicional para el log
        """
        self._logger.info(
            f"Iniciando operación: {operation}",
            extra={"operation": operation, **context}
        )
    
    def _log_operation_success(self, operation: str, **context) -> None:
        """
        Registra el éxito de una operación.
        
        Args:
            operation: Nombre de la operación
            **context: Contexto adicional para el log
        """
        self._logger.info(
            f"Operación completada exitosamente: {operation}",
            extra={"operation": operation, "status": "success", **context}
        )
    
    def _log_operation_error(self, operation: str, error: Exception, **context) -> None:
        """
        Registra un error en una operación.
        
        Args:
            operation: Nombre de la operación
            error: Excepción ocurrida
            **context: Contexto adicional para el log
        """
        self._logger.error(
            f"Error en operación: {operation} - {error}",
            extra={
                "operation": operation,
                "status": "error",
                "error_type": type(error).__name__,
                "error_message": str(error),
                **context
            }
        )