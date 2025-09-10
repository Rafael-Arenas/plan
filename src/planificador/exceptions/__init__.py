# src/planificador/exceptions/__init__.py

"""
Sistema de excepciones personalizado para el planificador.

Este módulo centraliza todas las excepciones del sistema organizadas por categorías:
- Base: Excepciones fundamentales del sistema
- Infrastructure: Excepciones de infraestructura (BD, conexiones, etc.)
- Validation: Excepciones de validación de datos
"""

# Importaciones de excepciones base
from .base import (
    ErrorCode,
    PlanificadorBaseException,
    ValidationError,
    NotFoundError,
    ConflictError,
    BusinessLogicError,
    AuthenticationError,
    AuthorizationError,
)

# Importaciones de excepciones de infraestructura
from .infrastructure import (
    InfrastructureError,
    DatabaseError,
    ConnectionError,
    ConfigurationError,
    ExternalServiceError,
    FileSystemError,
    
    # Excepciones específicas de BD
    DatabaseConnectionError,
    DatabaseIntegrityError,
    DatabaseTimeoutError,
    MigrationError,
    
    # Helper functions
    create_database_error,
    create_connection_error,
    create_config_error,
    create_external_service_error,
)

# Importaciones de excepciones de validación
from .validation import (
    PydanticValidationError,
    DateValidationError,
    TimeValidationError,
    DateTimeValidationError,
    FormatValidationError,
    RangeValidationError,
    LengthValidationError,
    RequiredFieldError,
    UniqueConstraintError,
    ForeignKeyValidationError,
    BusinessRuleValidationError,
    
    # Helper functions
    validate_email_format,
    validate_phone_format,
    validate_date_range,
    validate_time_range,
    validate_datetime_range,
    validate_text_length,
    validate_numeric_range,
    validate_required_field,
    convert_pydantic_error,
)


# Lista de todas las excepciones exportadas
__all__ = [
    # Base exceptions
    'ErrorCode',
    'PlanificadorBaseException',
    'ValidationError',
    'NotFoundError',
    'ConflictError',
    'BusinessLogicError',
    'AuthenticationError',
    'AuthorizationError',
    
    # Infrastructure exceptions
    'InfrastructureError',
    'DatabaseError',
    'ConnectionError',
    'ConfigurationError',
    'ExternalServiceError',
    'FileSystemError',
    'DatabaseConnectionError',
    'DatabaseIntegrityError',
    'DatabaseTimeoutError',
    'MigrationError',
    
    # Validation exceptions
    'PydanticValidationError',
    'DateValidationError',
    'TimeValidationError',
    'DateTimeValidationError',
    'FormatValidationError',
    'RangeValidationError',
    'LengthValidationError',
    'RequiredFieldError',
    'UniqueConstraintError',
    'ForeignKeyValidationError',
    'BusinessRuleValidationError',
    
    # Helper functions - Infrastructure
    'create_database_error',
    'create_connection_error',
    'create_config_error',
    'create_external_service_error',
    
    # Helper functions - Validation
    'validate_email_format',
    'validate_phone_format',
    'validate_date_range',
    'validate_time_range',
    'validate_datetime_range',
    'validate_text_length',
    'validate_numeric_range',
    'validate_required_field',
    'convert_pydantic_error',
]