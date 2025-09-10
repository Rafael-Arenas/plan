# src/planificador/tests/unit/test_exceptions/test_integration.py

"""
Tests de integración para el sistema de excepciones.

Este módulo contiene tests que verifican el comportamiento conjunto
del sistema de excepciones, incluyendo la interacción entre diferentes
tipos de excepciones, herencia, serialización y manejo de contexto.
"""

import pytest
import json
from datetime import date, time, datetime
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

from planificador.exceptions import (
    ErrorCode,
    PlanificadorBaseException,
    ValidationError,
    NotFoundError,
    ConflictError,
    BusinessLogicError,
    AuthenticationError,
    AuthorizationError,
    InfrastructureError,
    DatabaseError,
    DatabaseConnectionError,
    DatabaseIntegrityError,
    DatabaseTimeoutError,
    MigrationError,
    ConnectionError,
    ConfigurationError,
    ExternalServiceError,
    FileSystemError,
    PydanticValidationError,
    DateValidationError,
    TimeValidationError,
    DateTimeValidationError,
    FormatValidationError,
    RangeValidationError,
    LengthValidationError,
    RequiredFieldError,
)


class TestExceptionHierarchy:
    """Tests para verificar la jerarquía de excepciones."""
    
    def test_all_exceptions_inherit_from_base(self):
        """Verifica que todas las excepciones hereden de PlanificadorBaseException."""
        exception_classes = [
            ValidationError,
            NotFoundError,
            ConflictError,
            BusinessLogicError,
            AuthenticationError,
            AuthorizationError,
            InfrastructureError,
            DatabaseError,
            DatabaseConnectionError,
            DatabaseIntegrityError,
            DatabaseTimeoutError,
            MigrationError,
            ConnectionError,
            ConfigurationError,
            ExternalServiceError,
            FileSystemError,
            PydanticValidationError,
            DateValidationError,
            TimeValidationError,
            DateTimeValidationError,
            FormatValidationError,
            RangeValidationError,
            LengthValidationError,
            RequiredFieldError,
        ]
        
        for exception_class in exception_classes:
            if exception_class == PydanticValidationError:
                exception = exception_class(pydantic_errors=[{"type": "value_error", "loc": ("test_field",), "msg": "Test message", "input": "test_value"}])
            elif exception_class == RequiredFieldError:
                exception = exception_class("test_field")
            elif exception_class in [DateValidationError, TimeValidationError, DateTimeValidationError]:
                exception = exception_class("test_field", "test_value", "Test message")
            elif exception_class == FormatValidationError:
                exception = exception_class("test_field", "test_value", expected_format="test format")
            elif exception_class == RangeValidationError:
                exception = exception_class("test_field", 150, min_value=0, max_value=120)
            elif exception_class == LengthValidationError:
                exception = exception_class("test_field", "test_value", min_length=5, max_length=10)
            else:
                exception = exception_class("Test message")
            assert isinstance(exception, PlanificadorBaseException)
            assert isinstance(exception, Exception)
    
    def test_validation_exceptions_inherit_from_validation_error(self):
        """Verifica que las excepciones de validación hereden de ValidationError."""
        validation_exception_classes = [
            PydanticValidationError,
            DateValidationError,
            TimeValidationError,
            DateTimeValidationError,
            FormatValidationError,
            RangeValidationError,
            LengthValidationError,
            RequiredFieldError,
        ]
        
        for exception_class in validation_exception_classes:
            if exception_class == PydanticValidationError:
                exception = exception_class(pydantic_errors=[{"type": "value_error", "loc": ("test_field",), "msg": "Test message", "input": "test_value"}])
            elif exception_class == RequiredFieldError:
                exception = exception_class("test_field")
            elif exception_class in [DateValidationError, TimeValidationError, DateTimeValidationError]:
                exception = exception_class("test_field", "test_value", "Test message")
            elif exception_class == FormatValidationError:
                exception = exception_class("test_field", "test_value", expected_format="test format")
            elif exception_class == RangeValidationError:
                exception = exception_class("test_field", 150, min_value=0, max_value=120)
            elif exception_class == LengthValidationError:
                exception = exception_class("test_field", "test_value", min_length=5, max_length=10)
            else:
                exception = exception_class("Test message", "test_field", "test_value")
            assert isinstance(exception, ValidationError)
            assert isinstance(exception, PlanificadorBaseException)
    
    def test_infrastructure_exceptions_inherit_from_infrastructure_error(self):
        """Verifica que las excepciones de infraestructura hereden de InfrastructureError."""
        infrastructure_exception_classes = [
            DatabaseError,
            DatabaseConnectionError,
            DatabaseIntegrityError,
            DatabaseTimeoutError,
            MigrationError,
            ConnectionError,
            ConfigurationError,
            ExternalServiceError,
            FileSystemError,
        ]
        
        for exception_class in infrastructure_exception_classes:
            exception = exception_class("Test message")
            assert isinstance(exception, InfrastructureError)
            assert isinstance(exception, PlanificadorBaseException)
    
    def test_database_exceptions_inherit_from_database_error(self):
        """Verifica que las excepciones de base de datos hereden de DatabaseError."""
        database_exception_classes = [
            DatabaseConnectionError,
            DatabaseIntegrityError,
            DatabaseTimeoutError,
            MigrationError,
        ]
        
        for exception_class in database_exception_classes:
            exception = exception_class("Test message")
            assert isinstance(exception, DatabaseError)
            assert isinstance(exception, InfrastructureError)
            assert isinstance(exception, PlanificadorBaseException)


class TestExceptionSerialization:
    """Tests para verificar la serialización de excepciones."""
    
    def test_all_exceptions_can_be_serialized(self):
        """Verifica que todas las excepciones puedan ser serializadas."""
        test_cases = [
            ValidationError("Validation failed", "email", "invalid@"),
            NotFoundError("User not found", "User", "123"),
            ConflictError("Email already exists", "User", "email"),
            BusinessLogicError("Invalid business rule"),
            AuthenticationError("Invalid credentials"),
            AuthorizationError("Access denied"),
            DatabaseError("Database operation failed"),
            DatabaseConnectionError("Connection failed", host="localhost", port=5432),
            DatabaseIntegrityError("Constraint violation", constraint="unique_email"),
            DatabaseTimeoutError("Query timeout", timeout_seconds=30),
            MigrationError("Migration failed", migration_version="001_create_users"),
            ConnectionError("Service unavailable", endpoint="https://api.example.com"),
            ConfigurationError("Missing config", config_key="DATABASE_URL"),
            ExternalServiceError("API error", service_name="payment_service", status_code=503),
            FileSystemError("File not found", file_path="/var/log/app.log"),
            PydanticValidationError(pydantic_errors=[{"type": "value_error", "loc": ("field",), "msg": "Pydantic error", "input": "value"}]),
            DateValidationError("Invalid date", "birth_date", date(2025, 1, 1)),
            TimeValidationError("Invalid time", "start_time", "25:00"),
            DateTimeValidationError("Invalid datetime", "created_at", "invalid"),
            FormatValidationError("phone", "123", expected_format="formato de teléfono válido"),
            RangeValidationError("age", 150, min_value=0, max_value=120),
            LengthValidationError("password", "123", min_length=8, max_length=50),
            RequiredFieldError("email"),
        ]
        
        for exception in test_cases:
            # Verificar que to_dict() funciona
            exception_dict = exception.to_dict()
            assert isinstance(exception_dict, dict)
            assert "error_code" in exception_dict
            assert "message" in exception_dict
            assert "timestamp" in exception_dict
            
            # Verificar que puede ser serializado a JSON
            json_str = json.dumps(exception_dict, default=str)
            assert isinstance(json_str, str)
            
            # Verificar que puede ser deserializado
            deserialized = json.loads(json_str)
            assert isinstance(deserialized, dict)
    
    def test_exception_serialization_with_context_and_details(self, sample_context):
        """Verifica la serialización con contexto y detalles adicionales."""
        exception = DatabaseError(
            message="Database operation failed",
            query="SELECT * FROM users",
            table="users",
            operation="SELECT",
            context=sample_context
        )
        
        exception.add_detail("retry_count", 3)
        exception.add_detail("execution_time_ms", 5000)
        
        exception_dict = exception.to_dict()
        
        # Verificar que el contexto está incluido
        assert exception_dict["context"] == sample_context
        
        # Verificar que los detalles están incluidos
        assert exception_dict["details"]["query"] == "SELECT * FROM users"
        assert exception_dict["details"]["table"] == "users"
        assert exception_dict["details"]["operation"] == "SELECT"
        assert exception_dict["details"]["retry_count"] == 3
        assert exception_dict["details"]["execution_time_ms"] == 5000


class TestExceptionChaining:
    """Tests para verificar el encadenamiento de excepciones."""
    
    def test_exception_chaining_preserves_original_error(self):
        """Verifica que el encadenamiento preserve el error original."""
        original_error = ValueError("Original error message")
        
        # Crear excepción de infraestructura con error original
        infrastructure_error = DatabaseError(
            message="Database operation failed",
            original_error=original_error
        )
        
        assert infrastructure_error.original_error == original_error
        assert infrastructure_error.details["original_error"] == str(original_error)
        
        # Crear excepción de validación con error original
        validation_error = FormatValidationError(
            field="email",
            value="invalid@",
            expected_format="formato de email válido",
            original_error=original_error
        )
        
        assert validation_error.original_error == original_error
        assert validation_error.details["original_error"] == str(original_error)
    
    def test_nested_exception_chaining(self):
        """Verifica el encadenamiento anidado de excepciones."""
        # Error de nivel más bajo (sistema)
        system_error = OSError("Connection refused")
        
        # Error de infraestructura que envuelve el error del sistema
        connection_error = ConnectionError(
            message="Failed to connect to external service",
            endpoint="https://api.example.com",
            original_error=system_error
        )
        
        # Error de negocio que envuelve el error de infraestructura
        business_error = BusinessLogicError(
            message="Unable to process payment",
            original_error=connection_error
        )
        
        # Verificar la cadena de errores
        assert business_error.original_error == connection_error
        assert connection_error.original_error == system_error
        
        # Verificar que la serialización incluye toda la cadena
        business_dict = business_error.to_dict()
        assert "original_error" in business_dict["details"]
        
        connection_dict = connection_error.to_dict()
        assert "original_error" in connection_dict["details"]
        assert connection_dict["details"]["original_error"] == str(system_error)


class TestExceptionContextManagement:
    """Tests para verificar el manejo de contexto en excepciones."""
    
    def test_context_propagation_across_exception_types(self, sample_context):
        """Verifica que el contexto se propague entre diferentes tipos de excepciones."""
        exceptions_with_context = [
            ValidationError("Validation failed", "email", "invalid@", context=sample_context),
            DatabaseError("DB error", context=sample_context),
            ExternalServiceError("API error", service_name="test", context=sample_context),
        ]
        
        for exception in exceptions_with_context:
            assert exception.context == sample_context
            
            # Verificar que el contexto se incluye en la serialización
            exception_dict = exception.to_dict()
            assert exception_dict["context"] == sample_context
    
    def test_context_modification_and_chaining(self, sample_context):
        """Verifica la modificación y encadenamiento de contexto."""
        # Crear excepción inicial con contexto
        initial_exception = DatabaseError(
            message="Initial database error",
            context=sample_context
        )
        
        # Modificar contexto
        additional_context = {"retry_attempt": 2, "fallback_used": True}
        initial_exception.add_context(additional_context)
        
        # Verificar que el contexto se ha combinado
        expected_context = {**sample_context, **additional_context}
        assert initial_exception.context == expected_context
        
        # Crear nueva excepción que encadena la anterior
        chained_exception = BusinessLogicError(
            message="Business operation failed",
            original_error=initial_exception,
            context={"operation": "user_registration"}
        )
        
        # Verificar que ambas excepciones mantienen su contexto
        assert chained_exception.context == {"operation": "user_registration"}
        assert initial_exception.context == expected_context


class TestExceptionErrorCodes:
    """Tests para verificar la consistencia de códigos de error."""
    
    def test_all_exceptions_have_valid_error_codes(self):
        """Verifica que todas las excepciones tengan códigos de error válidos."""
        exception_code_mapping = {
            ValidationError: ErrorCode.VALIDATION_ERROR,
            NotFoundError: ErrorCode.NOT_FOUND,
            ConflictError: ErrorCode.CONFLICT,
            BusinessLogicError: ErrorCode.BUSINESS_LOGIC_ERROR,
            AuthenticationError: ErrorCode.AUTHENTICATION_ERROR,
            AuthorizationError: ErrorCode.AUTHORIZATION_ERROR,
            InfrastructureError: ErrorCode.INFRASTRUCTURE_ERROR,
            DatabaseError: ErrorCode.DATABASE_ERROR,
            DatabaseConnectionError: ErrorCode.DATABASE_CONNECTION_ERROR,
            DatabaseIntegrityError: ErrorCode.DATABASE_INTEGRITY_ERROR,
            DatabaseTimeoutError: ErrorCode.DATABASE_TIMEOUT_ERROR,
            MigrationError: ErrorCode.MIGRATION_ERROR,
            ConnectionError: ErrorCode.CONNECTION_ERROR,
            ConfigurationError: ErrorCode.CONFIGURATION_ERROR,
            ExternalServiceError: ErrorCode.EXTERNAL_SERVICE_ERROR,
            FileSystemError: ErrorCode.FILE_SYSTEM_ERROR,
            PydanticValidationError: ErrorCode.PYDANTIC_VALIDATION_ERROR,
            DateValidationError: ErrorCode.DATE_VALIDATION_ERROR,
            TimeValidationError: ErrorCode.TIME_VALIDATION_ERROR,
            DateTimeValidationError: ErrorCode.DATETIME_VALIDATION_ERROR,
            FormatValidationError: ErrorCode.FORMAT_VALIDATION_ERROR,
            RangeValidationError: ErrorCode.RANGE_VALIDATION_ERROR,
            LengthValidationError: ErrorCode.LENGTH_VALIDATION_ERROR,
            RequiredFieldError: ErrorCode.REQUIRED_FIELD_ERROR,
        }
        
        for exception_class, expected_code in exception_code_mapping.items():
            if exception_class in [ValidationError, InfrastructureError]:
                # Estas son clases base que requieren parámetros específicos
                if exception_class == ValidationError:
                    exception = exception_class("Test", "field", "value")
                else:
                    exception = exception_class("Test")
            elif issubclass(exception_class, ValidationError) and exception_class != ValidationError:
                # Manejar cada tipo de excepción de validación con sus parámetros específicos
                if exception_class == PydanticValidationError:
                    exception = exception_class([{"type": "value_error", "loc": ("field",), "msg": "Test error"}])
                elif exception_class == DateValidationError:
                    exception = exception_class("field", "invalid_date")
                elif exception_class == TimeValidationError:
                    exception = exception_class("field", "invalid_time")
                elif exception_class == DateTimeValidationError:
                    exception = exception_class("field", "invalid_datetime")
                elif exception_class == FormatValidationError:
                    exception = exception_class("field", "value", expected_format="test_format")
                elif exception_class == RangeValidationError:
                    exception = exception_class("field", 100, min_value=0, max_value=50)
                elif exception_class == LengthValidationError:
                    exception = exception_class("field", "test", min_length=10)
                elif exception_class == RequiredFieldError:
                    exception = exception_class("field")
                else:
                    exception = exception_class("field", "value")
            else:
                exception = exception_class("Test")
            
            assert exception.error_code == expected_code
    
    def test_error_code_uniqueness(self):
        """Verifica que todos los códigos de error sean únicos."""
        error_codes = [code.value for code in ErrorCode]
        assert len(error_codes) == len(set(error_codes)), "Error codes must be unique"


class TestExceptionStringRepresentation:
    """Tests para verificar la representación en string de excepciones."""
    
    def test_exception_str_representation(self):
        """Verifica que todas las excepciones tengan representación string apropiada."""
        test_cases = [
            (ValidationError("Validation failed", "email", "invalid@"), "VALIDATION_ERROR: Validation failed"),
            (NotFoundError("User not found", "User", "123"), "NOT_FOUND: User not found"),
            (DatabaseError("DB error"), "DATABASE_ERROR: DB error"),
            (ExternalServiceError("API error", service_name="test"), "EXTERNAL_SERVICE_ERROR: API error"),
        ]
        
        for exception, expected_start in test_cases:
            str_repr = str(exception)
            assert str_repr == expected_start
    
    def test_exception_repr_representation(self):
        """Verifica que todas las excepciones tengan representación repr apropiada."""
        exception = DatabaseError(
            message="Database connection failed",
            query="SELECT * FROM users",
            table="users"
        )
        
        repr_str = repr(exception)
        
        # Verificar que incluye el nombre de la clase y información relevante
        assert "DatabaseError" in repr_str
        assert "DATABASE_ERROR" in repr_str
        assert "Database connection failed" in repr_str


class TestExceptionPerformance:
    """Tests para verificar el rendimiento del sistema de excepciones."""
    
    def test_exception_creation_performance(self):
        """Verifica que la creación de excepciones sea eficiente."""
        import time
        
        start_time = time.time()
        
        # Crear múltiples excepciones
        for i in range(1000):
            exception = DatabaseError(
                message=f"Error {i}",
                query=f"SELECT * FROM table_{i}",
                table=f"table_{i}",
                operation="SELECT"
            )
            # Agregar contexto y detalles
            exception.add_context({"iteration": i})
            exception.add_detail("timestamp", time.time())
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # La creación de 1000 excepciones no debería tomar más de 1 segundo
        assert execution_time < 1.0, f"Exception creation took {execution_time:.3f}s, expected < 1.0s"
    
    def test_exception_serialization_performance(self):
        """Verifica que la serialización de excepciones sea eficiente."""
        import time
        
        # Crear excepción compleja
        exception = DatabaseError(
            message="Complex database error",
            query="SELECT * FROM users JOIN profiles ON users.id = profiles.user_id WHERE users.active = true",
            table="users",
            operation="SELECT",
            context={
                "user_id": "12345",
                "session_id": "abcdef",
                "request_id": "req_123",
                "additional_data": {"nested": "value", "list": [1, 2, 3, 4, 5]}
            }
        )
        
        # Agregar múltiples detalles
        for i in range(50):
            exception.add_detail(f"detail_{i}", f"value_{i}")
        
        start_time = time.time()
        
        # Serializar múltiples veces
        for _ in range(100):
            exception_dict = exception.to_dict()
            json_str = json.dumps(exception_dict, default=str)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 100 serializaciones no deberían tomar más de 0.5 segundos
        assert execution_time < 0.5, f"Serialization took {execution_time:.3f}s, expected < 0.5s"


class TestExceptionCompatibility:
    """Tests para verificar la compatibilidad del sistema de excepciones."""
    
    def test_exception_compatibility_with_standard_exception_handling(self):
        """Verifica que las excepciones sean compatibles con manejo estándar de Python."""
        exception = DatabaseError("Database error")
        
        # Verificar que puede ser capturada como Exception estándar
        try:
            raise exception
        except Exception as e:
            assert isinstance(e, DatabaseError)
            assert isinstance(e, PlanificadorBaseException)
            assert isinstance(e, Exception)
        
        # Verificar que puede ser capturada por tipo específico
        try:
            raise exception
        except DatabaseError as e:
            assert e.message == "Database error"
        
        # Verificar que puede ser capturada por tipo padre
        try:
            raise exception
        except InfrastructureError as e:
            assert isinstance(e, DatabaseError)
    
    def test_exception_compatibility_with_logging(self):
        """Verifica que las excepciones sean compatibles con logging."""
        import logging
        from io import StringIO
        
        # Configurar logger para capturar output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("test_logger")
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        
        exception = DatabaseError(
            message="Database connection failed",
            query="SELECT * FROM users",
            context={"user_id": "123"}
        )
        
        # Verificar que puede ser loggeada
        try:
            raise exception
        except DatabaseError as e:
            logger.error("Database error occurred", exc_info=True)
            logger.error(f"Exception details: {e.to_dict()}")
        
        log_output = log_stream.getvalue()
        
        # Verificar que el log contiene información relevante
        assert "Database error occurred" in log_output
        assert "DatabaseError" in log_output
        assert "Database connection failed" in log_output
        
        # Limpiar
        logger.removeHandler(handler)
        handler.close()