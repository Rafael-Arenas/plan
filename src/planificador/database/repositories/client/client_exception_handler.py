"""Módulo especializado para manejo unificado de excepciones de clientes.

Este módulo centraliza todo el manejo de excepciones relacionadas con
operaciones de clientes, proporcionando un punto único de control para
la conversión, logging y manejo de errores.

Autor: Sistema de Modularización
Fecha: 21 de agosto de 2025
"""

from typing import Optional, Any, Dict
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    DataError,
    OperationalError,
    InvalidRequestError
)
from loguru import logger
import traceback

from planificador.exceptions.client_exceptions import (
    ClientNotFoundError,
    ClientValidationError,
    ClientDuplicateError,
    create_client_validation_error,
    create_client_not_found_error
)
from planificador.exceptions.repository_exceptions import (
    RepositoryError,
    convert_sqlalchemy_error
)


class ClientExceptionHandler:
    """Manejador centralizado de excepciones para operaciones de clientes.
    
    Esta clase proporciona métodos especializados para el manejo, conversión
    y logging de excepciones relacionadas con operaciones de clientes,
    asegurando consistencia en el manejo de errores en todo el sistema.
    
    Attributes:
        _logger: Logger estructurado para la clase
        _operation_context: Contexto de la operación actual
    """
    
    def __init__(self):
        """Inicializa el manejador de excepciones."""
        self._logger = logger.bind(component="ClientExceptionHandler")
        self._operation_context: Optional[str] = None
    
    def set_operation_context(self, operation: str) -> None:
        """Establece el contexto de la operación actual.
        
        Args:
            operation: Nombre de la operación en curso
        """
        self._operation_context = operation
        self._logger = logger.bind(
            component="ClientExceptionHandler",
            operation=operation
        )
    
    async def handle_sqlalchemy_error(
        self,
        error: SQLAlchemyError,
        operation: str,
        entity_id: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Maneja errores de SQLAlchemy de forma especializada.
        
        Args:
            error: Error de SQLAlchemy a manejar
            operation: Operación que causó el error
            entity_id: ID de la entidad afectada (opcional)
            additional_context: Contexto adicional para logging
            
        Raises:
            ClientDuplicateError: Para errores de integridad/duplicados
            RepositoryError: Para otros errores de base de datos
        """
        # Preparar contexto para logging
        context = {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        if entity_id:
            context["entity_id"] = entity_id
        
        if additional_context:
            context.update(additional_context)
        
        # Logging detallado del error
        self._logger.error(
            f"Error SQLAlchemy en {operation}: {error}",
            **context
        )
        
        # Manejo especializado por tipo de error
        if isinstance(error, IntegrityError):
            await self._handle_integrity_error(error, operation, entity_id)
        elif isinstance(error, DataError):
            await self._handle_data_error(error, operation, entity_id)
        elif isinstance(error, OperationalError):
            await self._handle_operational_error(error, operation, entity_id)
        elif isinstance(error, InvalidRequestError):
            await self._handle_invalid_request_error(error, operation, entity_id)
        else:
            # Error genérico de SQLAlchemy
            raise convert_sqlalchemy_error(
                error=error,
                operation=operation,
                entity_type="Client",
                entity_id=entity_id
            )
    
    async def _handle_integrity_error(
        self,
        error: IntegrityError,
        operation: str,
        entity_id: Optional[str] = None
    ) -> None:
        """Maneja errores de integridad de datos.
        
        Args:
            error: Error de integridad
            operation: Operación que causó el error
            entity_id: ID de la entidad afectada
            
        Raises:
            ClientDuplicateError: Para violaciones de unicidad
            RepositoryError: Para otros errores de integridad
        """
        error_message = str(error).lower()
        
        # Detectar violaciones de unicidad específicas
        if "unique" in error_message or "duplicate" in error_message:
            if "name" in error_message:
                raise ClientDuplicateError(
                    message="Ya existe un cliente con este nombre",
                    field="name",
                    operation=operation,
                    client_id=entity_id
                )
            elif "code" in error_message:
                raise ClientDuplicateError(
                    message="Ya existe un cliente con este código",
                    field="code",
                    operation=operation,
                    client_id=entity_id
                )
            elif "email" in error_message:
                raise ClientDuplicateError(
                    message="Ya existe un cliente con este email",
                    field="email",
                    operation=operation,
                    client_id=entity_id
                )
            else:
                raise ClientDuplicateError(
                    message="Violación de restricción de unicidad",
                    field="unknown",
                    operation=operation,
                    client_id=entity_id
                )
        
        # Otros errores de integridad
        raise convert_sqlalchemy_error(
            error=error,
            operation=operation,
            entity_type="Client",
            entity_id=entity_id
        )
    
    async def _handle_data_error(
        self,
        error: DataError,
        operation: str,
        entity_id: Optional[str] = None
    ) -> None:
        """Maneja errores de datos inválidos.
        
        Args:
            error: Error de datos
            operation: Operación que causó el error
            entity_id: ID de la entidad afectada
            
        Raises:
            ClientValidationError: Para datos inválidos
        """
        error_message = str(error).lower()
        
        # Detectar tipos específicos de errores de datos
        if "date" in error_message or "datetime" in error_message:
            raise create_client_validation_error(
                field="date_field",
                value="invalid_date",
                reason="Formato de fecha inválido",
                operation=operation
            )
        elif "numeric" in error_message or "integer" in error_message:
            raise create_client_validation_error(
                field="numeric_field",
                value="invalid_number",
                reason="Valor numérico inválido",
                operation=operation
            )
        elif "string" in error_message or "varchar" in error_message:
            raise create_client_validation_error(
                field="text_field",
                value="invalid_text",
                reason="Longitud de texto excedida o formato inválido",
                operation=operation
            )
        
        # Error genérico de datos
        raise create_client_validation_error(
            field="unknown",
            value="unknown",
            reason=f"Error de validación de datos: {str(error)}",
            operation=operation
        )
    
    async def _handle_operational_error(
        self,
        error: OperationalError,
        operation: str,
        entity_id: Optional[str] = None
    ) -> None:
        """Maneja errores operacionales de base de datos.
        
        Args:
            error: Error operacional
            operation: Operación que causó el error
            entity_id: ID de la entidad afectada
            
        Raises:
            RepositoryError: Para errores operacionales
        """
        self._logger.critical(
            f"Error operacional crítico en {operation}: {error}",
            operation=operation,
            entity_id=entity_id,
            error_type="OperationalError"
        )
        
        raise RepositoryError(
            message=f"Error operacional en base de datos: {str(error)}",
            operation=operation,
            entity_type="Client",
            entity_id=entity_id,
            original_error=error
        )
    
    async def _handle_invalid_request_error(
        self,
        error: InvalidRequestError,
        operation: str,
        entity_id: Optional[str] = None
    ) -> None:
        """Maneja errores de solicitud inválida.
        
        Args:
            error: Error de solicitud inválida
            operation: Operación que causó el error
            entity_id: ID de la entidad afectada
            
        Raises:
            RepositoryError: Para solicitudes inválidas
        """
        self._logger.warning(
            f"Solicitud inválida en {operation}: {error}",
            operation=operation,
            entity_id=entity_id,
            error_type="InvalidRequestError"
        )
        
        raise RepositoryError(
            message=f"Solicitud inválida: {str(error)}",
            operation=operation,
            entity_type="Client",
            entity_id=entity_id,
            original_error=error
        )
    
    async def handle_validation_error(
        self,
        field: str,
        value: Any,
        reason: str,
        operation: str,
        client_id: Optional[str] = None
    ) -> None:
        """Maneja errores de validación de datos.
        
        Args:
            field: Campo que falló la validación
            value: Valor que causó el error
            reason: Razón del error de validación
            operation: Operación que causó el error
            client_id: ID del cliente afectado
            
        Raises:
            ClientValidationError: Error de validación específico
        """
        self._logger.warning(
            f"Error de validación en {operation}: {field}={value} - {reason}",
            operation=operation,
            field=field,
            value=str(value),
            reason=reason,
            client_id=client_id
        )
        
        raise create_client_validation_error(
            field=field,
            value=value,
            reason=reason,
            operation=operation
        )
    
    async def handle_not_found_error(
        self,
        client_id: Optional[str] = None,
        search_criteria: Optional[Dict[str, Any]] = None,
        operation: str = "unknown"
    ) -> None:
        """Maneja errores de cliente no encontrado.
        
        Args:
            client_id: ID del cliente no encontrado
            search_criteria: Criterios de búsqueda utilizados
            operation: Operación que causó el error
            
        Raises:
            ClientNotFoundError: Error de cliente no encontrado
        """
        context = {
            "operation": operation,
            "client_id": client_id,
            "search_criteria": search_criteria
        }
        
        self._logger.info(
            f"Cliente no encontrado en {operation}",
            **context
        )
        
        if client_id:
            raise create_client_not_found_error(
                client_id=client_id,
                operation=operation
            )
        else:
            raise ClientNotFoundError(
                message="Cliente no encontrado con los criterios especificados",
                operation=operation,
                search_criteria=search_criteria
            )
    
    async def handle_unexpected_error(
        self,
        error: Exception,
        operation: str,
        entity_id: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Maneja errores inesperados no categorizados.
        
        Args:
            error: Error inesperado
            operation: Operación que causó el error
            entity_id: ID de la entidad afectada
            additional_context: Contexto adicional
            
        Raises:
            RepositoryError: Error de repositorio genérico
        """
        # Preparar contexto completo
        context = {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }
        
        if entity_id:
            context["entity_id"] = entity_id
        
        if additional_context:
            context.update(additional_context)
        
        # Logging crítico para errores inesperados
        self._logger.critical(
            f"Error inesperado en {operation}: {error}",
            **context
        )
        
        raise RepositoryError(
            message=f"Error inesperado en {operation}: {str(error)}",
            operation=operation,
            entity_type="Client",
            entity_id=entity_id,
            original_error=error
        )
    
    def log_operation_success(
        self,
        operation: str,
        entity_id: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> None:
        """Registra el éxito de una operación.
        
        Args:
            operation: Operación exitosa
            entity_id: ID de la entidad afectada
            additional_info: Información adicional
        """
        context = {
            "operation": operation,
            "status": "success"
        }
        
        if entity_id:
            context["entity_id"] = entity_id
        
        if additional_info:
            context.update(additional_info)
        
        self._logger.info(
            f"Operación {operation} completada exitosamente",
            **context
        )
    
    def get_error_summary(self, error: Exception) -> Dict[str, Any]:
        """Obtiene un resumen estructurado del error.
        
        Args:
            error: Error a resumir
            
        Returns:
            Diccionario con resumen del error
        """
        return {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "is_client_error": isinstance(error, (
                ClientNotFoundError,
                ClientValidationError,
                ClientDuplicateError
            )),
            "is_repository_error": isinstance(error, RepositoryError),
            "is_sqlalchemy_error": isinstance(error, SQLAlchemyError),
            "operation_context": self._operation_context
        }