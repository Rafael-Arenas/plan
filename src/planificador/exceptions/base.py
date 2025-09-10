# src/planificador/exceptions/base.py

"""
Excepciones base para el sistema de planificación.

Este módulo define las excepciones fundamentales que sirven como base
para todas las demás excepciones del sistema. Proporciona una jerarquía
consistente y facilita el manejo centralizado de errores.
"""

from typing import Any, Dict, Optional, Union
from enum import Enum


class ErrorCode(Enum):
    """Códigos de error estándar del sistema."""
    
    # Errores generales
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    
    # Errores de validación
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    PYDANTIC_VALIDATION_ERROR = "PYDANTIC_VALIDATION_ERROR"
    DATE_VALIDATION_ERROR = "DATE_VALIDATION_ERROR"
    TIME_VALIDATION_ERROR = "TIME_VALIDATION_ERROR"
    DATETIME_VALIDATION_ERROR = "DATETIME_VALIDATION_ERROR"
    FORMAT_VALIDATION_ERROR = "FORMAT_VALIDATION_ERROR"
    RANGE_VALIDATION_ERROR = "RANGE_VALIDATION_ERROR"
    LENGTH_VALIDATION_ERROR = "LENGTH_VALIDATION_ERROR"
    REQUIRED_FIELD_ERROR = "REQUIRED_FIELD_ERROR"
    UNIQUE_CONSTRAINT_ERROR = "UNIQUE_CONSTRAINT_ERROR"
    FOREIGN_KEY_VALIDATION_ERROR = "FOREIGN_KEY_VALIDATION_ERROR"
    BUSINESS_RULE_VALIDATION_ERROR = "BUSINESS_RULE_VALIDATION_ERROR"
    
    # Errores de recursos
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    CONFLICT = "CONFLICT"
    
    # Errores de lógica de negocio
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR"
    INVALID_STATE = "INVALID_STATE"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    
    # Errores de autenticación y autorización
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Errores de infraestructura
    INFRASTRUCTURE_ERROR = "INFRASTRUCTURE_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_INTEGRITY_ERROR = "DATABASE_INTEGRITY_ERROR"
    DATABASE_TIMEOUT_ERROR = "DATABASE_TIMEOUT_ERROR"
    MIGRATION_ERROR = "MIGRATION_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    FILE_SYSTEM_ERROR = "FILE_SYSTEM_ERROR"


class PlanificadorBaseException(Exception):
    """
    Excepción base para todas las excepciones del sistema de planificación.
    
    Proporciona funcionalidad común como códigos de error, detalles adicionales
    y contexto para facilitar el debugging y logging.
    
    Attributes:
        message: Mensaje descriptivo del error
        error_code: Código de error estándar
        details: Información adicional sobre el error
        context: Contexto donde ocurrió el error
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[ErrorCode] = None,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or ErrorCode.UNKNOWN_ERROR
        self.details = details or {}
        self.context = context or {}
        self.original_error = original_error
        
        # Agregar original_error a los detalles si está presente
        if original_error:
            self.details['original_error'] = str(original_error)
    
    def __str__(self) -> str:
        """Representación en string de la excepción."""
        return f"{self.error_code.value}: {self.message}"
    
    def __repr__(self) -> str:
        """Representación detallada de la excepción."""
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"error_code={self.error_code}, "
            f"details={self.details}, "
            f"context={self.context})"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la excepción a un diccionario para serialización.
        
        Returns:
            Diccionario con toda la información de la excepción
        """
        result = {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code.value,
            'details': self.details,
            'context': self.context
        }
        
        # Agregar timestamp si no existe
        if 'timestamp' not in result:
            from datetime import datetime
            result['timestamp'] = datetime.now().isoformat()
            
        return result
    
    def add_context(self, key_or_dict: Union[str, Dict[str, Any]], value: Any = None) -> 'PlanificadorBaseException':
        """
        Añade información de contexto a la excepción.
        
        Args:
            key_or_dict: Clave del contexto o diccionario con múltiples contextos
            value: Valor del contexto (solo si key_or_dict es una clave)
            
        Returns:
            La misma instancia para permitir method chaining
        """
        if isinstance(key_or_dict, dict):
            self.context.update(key_or_dict)
        else:
            if value is None:
                raise ValueError("Value is required when key_or_dict is a string")
            self.context[key_or_dict] = value
        return self
    
    def add_detail(self, key: str, value: Any) -> 'PlanificadorBaseException':
        """
        Añade detalles adicionales a la excepción.
        
        Args:
            key: Clave del detalle
            value: Valor del detalle
            
        Returns:
            La misma instancia para permitir method chaining
        """
        self.details[key] = value
        return self


class ValidationError(PlanificadorBaseException):
    """
    Excepción lanzada cuando los datos de entrada no son válidos.
    
    Se utiliza para errores de validación de esquemas, campos requeridos,
    formatos incorrectos, etc.
    """
    
    def __init__(
        self, 
        message: str, 
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            message, 
            error_code=ErrorCode.VALIDATION_ERROR, 
            **kwargs
        )
        if field:
            self.add_detail('field', field)
        if value is not None:
            self.add_detail('invalid_value', value)
    
    @property
    def field(self) -> Optional[str]:
        """Obtiene el campo que falló la validación."""
        return self.details.get('field')
    
    @property
    def value(self) -> Optional[Any]:
        """Obtiene el valor inválido."""
        return self.details.get('invalid_value')


class NotFoundError(PlanificadorBaseException):
    """
    Excepción lanzada cuando un recurso solicitado no se encuentra.
    
    Se utiliza para entidades que no existen en la base de datos,
    archivos no encontrados, etc.
    """
    
    def __init__(
        self, 
        message: str, 
        resource_type: Optional[str] = None,
        resource_id: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            message, 
            error_code=ErrorCode.NOT_FOUND, 
            **kwargs
        )
        if resource_type:
            self.add_detail('resource_type', resource_type)
        if resource_id is not None:
            self.add_detail('resource_id', resource_id)


class ConflictError(PlanificadorBaseException):
    """
    Excepción lanzada cuando existe un conflicto en los datos.
    
    Se utiliza para violaciones de unicidad, conflictos de concurrencia,
    estados inconsistentes, etc.
    """
    
    def __init__(
        self, 
        message: str, 
        conflicting_field: Optional[str] = None,
        conflicting_value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            message, 
            error_code=ErrorCode.CONFLICT, 
            **kwargs
        )
        if conflicting_field:
            self.add_detail('conflicting_field', conflicting_field)
        if conflicting_value is not None:
            self.add_detail('conflicting_value', conflicting_value)


class BusinessLogicError(PlanificadorBaseException):
    """
    Excepción lanzada cuando se viola una regla de negocio.
    
    Se utiliza para validaciones específicas del dominio,
    reglas de negocio complejas, estados inválidos, etc.
    """
    
    def __init__(
        self, 
        message: str, 
        rule: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message, 
            error_code=ErrorCode.BUSINESS_LOGIC_ERROR, 
            **kwargs
        )
        if rule:
            self.add_detail('violated_rule', rule)


class AuthenticationError(PlanificadorBaseException):
    """
    Excepción lanzada cuando falla la autenticación.
    
    Se utiliza para credenciales inválidas, tokens expirados,
    usuarios no autenticados, etc.
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message, 
            error_code=ErrorCode.AUTHENTICATION_ERROR, 
            **kwargs
        )


class AuthorizationError(PlanificadorBaseException):
    """
    Excepción lanzada cuando el usuario no tiene permisos suficientes.
    
    Se utiliza para acceso denegado, permisos insuficientes,
    operaciones no autorizadas, etc.
    """
    
    def __init__(
        self, 
        message: str, 
        required_permission: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message, 
            error_code=ErrorCode.AUTHORIZATION_ERROR, 
            **kwargs
        )
        if required_permission:
            self.add_detail('required_permission', required_permission)


# Funciones helper para crear excepciones comunes
def create_validation_error(
    field: str, 
    value: Any, 
    reason: str
) -> ValidationError:
    """
    Crea una excepción de validación con información estándar.
    
    Args:
        field: Campo que falló la validación
        value: Valor inválido
        reason: Razón por la que falló la validación
        
    Returns:
        Instancia de ValidationError
    """
    message = f"Validación fallida para campo '{field}': {reason}"
    return ValidationError(message, field=field, value=value)


def create_not_found_error(
    resource_type: str, 
    resource_id: Any
) -> NotFoundError:
    """
    Crea una excepción de recurso no encontrado con información estándar.
    
    Args:
        resource_type: Tipo de recurso (ej: 'Project', 'Employee')
        resource_id: ID del recurso no encontrado
        
    Returns:
        Instancia de NotFoundError
    """
    message = f"{resource_type} con ID {resource_id} no encontrado"
    return NotFoundError(message, resource_type=resource_type, resource_id=resource_id)


def create_conflict_error(
    resource_type: str, 
    field: str, 
    value: Any
) -> ConflictError:
    """
    Crea una excepción de conflicto con información estándar.
    
    Args:
        resource_type: Tipo de recurso
        field: Campo que causa el conflicto
        value: Valor que causa el conflicto
        
    Returns:
        Instancia de ConflictError
    """
    message = f"Ya existe un {resource_type} con {field} '{value}'"
    return ConflictError(
        message, 
        conflicting_field=field, 
        conflicting_value=value
    ).add_detail('resource_type', resource_type)