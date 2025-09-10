# src/planificador/exceptions/repository/base_repository_exceptions.py
"""
Excepciones base para repositorios.

Este módulo define las excepciones específicas para operaciones de repositorio
y proporciona funciones para convertir errores de SQLAlchemy a excepciones personalizadas.
"""

from typing import Optional, Any, Dict
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    OperationalError,
    TimeoutError,
    DisconnectionError,
    InvalidRequestError,
    DataError,
    ProgrammingError
)
from ..base import PlanificadorBaseException
from ..infrastructure import DatabaseError


class RepositoryError(DatabaseError):
    """
    Excepción base para errores de repositorio.
    
    Esta excepción encapsula errores específicos de operaciones de repositorio
    y proporciona contexto adicional sobre la operación que falló.
    """
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[Any] = None,
        original_error: Optional[Exception] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            operation=operation,
            table=entity_type,
            original_error=original_error,
            **kwargs
        )
        # Atributos explícitos para acceso directo en tests y manejo de errores
        self.operation = operation
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.original_error = original_error
        
        # Añadir detalles estandarizados esperados por los tests
        if entity_type is not None:
            self.add_detail('entity_type', entity_type)
        # Siempre incluir la clave 'entity_id' (puede ser None) para consistencia
        self.add_detail('entity_id', str(entity_id) if entity_id is not None else None)


class RepositoryConnectionError(RepositoryError):
    """
    Error de conexión en operaciones de repositorio.
    
    Se lanza cuando hay problemas de conectividad con la base de datos
    durante operaciones de repositorio.
    """
    
    def __init__(
        self,
        message: str = "Error de conexión en repositorio",
        operation: Optional[str] = None,
        entity_type: Optional[str] = None,
        original_error: Optional[Exception] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            operation=operation,
            entity_type=entity_type,
            original_error=original_error,
            **kwargs
        )


class RepositoryIntegrityError(RepositoryError):
    """
    Error de integridad en operaciones de repositorio.
    
    Se lanza cuando se violan restricciones de integridad de la base de datos
    durante operaciones de repositorio.
    """
    
    def __init__(
        self,
        message: str = "Error de integridad en repositorio",
        operation: Optional[str] = None,
        entity_type: Optional[str] = None,
        constraint: Optional[str] = None,
        original_error: Optional[Exception] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            operation=operation,
            entity_type=entity_type,
            original_error=original_error,
            **kwargs
        )
        self.constraint = constraint


class RepositoryTimeoutError(RepositoryError):
    """
    Error de timeout en operaciones de repositorio.
    
    Se lanza cuando una operación de repositorio excede el tiempo límite.
    """
    
    def __init__(
        self,
        message: str = "Timeout en operación de repositorio",
        operation: Optional[str] = None,
        entity_type: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        original_error: Optional[Exception] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            operation=operation,
            entity_type=entity_type,
            original_error=original_error,
            **kwargs
        )
        self.timeout_seconds = timeout_seconds


class RepositoryTransactionError(RepositoryError):
    """
    Error de transacción en operaciones de repositorio.
    
    Se lanza cuando hay problemas con el manejo de transacciones
    en operaciones de repositorio.
    """
    
    def __init__(
        self,
        message: str = "Error de transacción en repositorio",
        operation: Optional[str] = None,
        entity_type: Optional[str] = None,
        transaction_state: Optional[str] = None,
        original_error: Optional[Exception] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            operation=operation,
            entity_type=entity_type,
            original_error=original_error,
            **kwargs
        )
        self.transaction_state = transaction_state


class RepositoryValidationError(RepositoryError):
    """
    Error de validación en operaciones de repositorio.
    
    Se lanza cuando los datos no cumplen con las validaciones
    requeridas por el repositorio.
    """
    
    def __init__(
        self,
        message: str = "Error de validación en repositorio",
        operation: Optional[str] = None,
        entity_type: Optional[str] = None,
        validation_errors: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            operation=operation,
            entity_type=entity_type,
            original_error=original_error,
            **kwargs
        )
        self.validation_errors = validation_errors or {}


def convert_sqlalchemy_error(
    error: SQLAlchemyError,
    operation: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[Any] = None
) -> RepositoryError:
    """
    Convierte errores de SQLAlchemy a excepciones específicas de repositorio.
    
    Esta función analiza el tipo de error de SQLAlchemy y lo convierte
    a la excepción de repositorio más apropiada, preservando la información
    del error original.
    
    Args:
        error: Error de SQLAlchemy a convertir
        operation: Operación que causó el error (ej: 'create', 'update', 'delete')
        entity_type: Tipo de entidad involucrada (ej: 'Client', 'Project')
        entity_id: ID de la entidad si está disponible
        
    Returns:
        Excepción de repositorio apropiada
    """
    error_message = str(error)
    
    # Error de integridad (claves foráneas, unique constraints, etc.)
    if isinstance(error, IntegrityError):
        constraint = None
        if hasattr(error, 'orig') and hasattr(error.orig, 'args'):
            # Intentar extraer el nombre de la restricción del mensaje
            for arg in error.orig.args:
                if isinstance(arg, str) and ('constraint' in arg.lower() or 'unique' in arg.lower()):
                    constraint = arg
                    break
        
        return RepositoryIntegrityError(
            message=f"Error de integridad en {operation or 'operación'} de {entity_type or 'entidad'}: {error_message}",
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            constraint=constraint,
            original_error=error
        )
    
    # Error de conexión o desconexión
    elif isinstance(error, (OperationalError, DisconnectionError)):
        return RepositoryConnectionError(
            message=f"Error de conexión en {operation or 'operación'} de {entity_type or 'entidad'}: {error_message}",
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            original_error=error
        )
    
    # Error de timeout
    elif isinstance(error, TimeoutError):
        return RepositoryTimeoutError(
            message=f"Timeout en {operation or 'operación'} de {entity_type or 'entidad'}: {error_message}",
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            original_error=error
        )
    
    # Error de datos inválidos
    elif isinstance(error, DataError):
        return RepositoryValidationError(
            message=f"Datos inválidos en {operation or 'operación'} de {entity_type or 'entidad'}: {error_message}",
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            original_error=error
        )
    
    # Error de programación (SQL inválido, etc.)
    elif isinstance(error, ProgrammingError):
        return RepositoryError(
            message=f"Error de programación en {operation or 'operación'} de {entity_type or 'entidad'}: {error_message}",
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            original_error=error
        )
    
    # Error de solicitud inválida
    elif isinstance(error, InvalidRequestError):
        return RepositoryTransactionError(
            message=f"Solicitud inválida en {operation or 'operación'} de {entity_type or 'entidad'}: {error_message}",
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            original_error=error
        )
    
    # Error genérico de SQLAlchemy
    else:
        return RepositoryError(
            message=f"Error de repositorio en {operation or 'operación'} de {entity_type or 'entidad'}: {error_message}",
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            original_error=error
        )