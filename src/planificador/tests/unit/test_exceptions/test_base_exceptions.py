# src/planificador/tests/unit/test_exceptions/test_base_exceptions.py

"""
Tests para excepciones base del sistema de planificación.

Este módulo contiene tests exhaustivos para todas las excepciones base
que forman la jerarquía fundamental del sistema de excepciones.
"""

import pytest
from typing import Any, Dict

from planificador.exceptions import (
    ErrorCode,
    PlanificadorBaseException,
    ValidationError,
    NotFoundError,
    ConflictError,
    BusinessLogicError,
    AuthenticationError,
    AuthorizationError,
)


class TestErrorCode:
    """Tests para el enum ErrorCode."""
    
    def test_error_code_values(self):
        """Verifica que todos los códigos de error tengan valores correctos."""
        assert ErrorCode.UNKNOWN_ERROR.value == "UNKNOWN_ERROR"
        assert ErrorCode.INTERNAL_ERROR.value == "INTERNAL_ERROR"
        assert ErrorCode.VALIDATION_ERROR.value == "VALIDATION_ERROR"
        assert ErrorCode.INVALID_INPUT.value == "INVALID_INPUT"
        assert ErrorCode.NOT_FOUND.value == "NOT_FOUND"
        assert ErrorCode.CONFLICT.value == "CONFLICT"
        assert ErrorCode.BUSINESS_RULE_VIOLATION.value == "BUSINESS_RULE_VIOLATION"
        assert ErrorCode.AUTHENTICATION_FAILED.value == "AUTHENTICATION_FAILED"
        assert ErrorCode.AUTHORIZATION_FAILED.value == "AUTHORIZATION_FAILED"
    
    def test_error_code_enum_completeness(self):
        """Verifica que el enum contenga todos los códigos esperados."""
        expected_codes = {
            # Errores generales
            'UNKNOWN_ERROR', 'INTERNAL_ERROR',
            # Errores de validación
            'VALIDATION_ERROR', 'INVALID_INPUT', 'MISSING_REQUIRED_FIELD', 'INVALID_FORMAT',
            'PYDANTIC_VALIDATION_ERROR', 'DATE_VALIDATION_ERROR', 'TIME_VALIDATION_ERROR',
            'DATETIME_VALIDATION_ERROR', 'FORMAT_VALIDATION_ERROR', 'RANGE_VALIDATION_ERROR',
            'LENGTH_VALIDATION_ERROR', 'REQUIRED_FIELD_ERROR', 'UNIQUE_CONSTRAINT_ERROR',
            'FOREIGN_KEY_VALIDATION_ERROR', 'BUSINESS_RULE_VALIDATION_ERROR',
            # Errores de recursos
            'NOT_FOUND', 'ALREADY_EXISTS', 'CONFLICT',
            # Errores de lógica de negocio
            'BUSINESS_RULE_VIOLATION', 'BUSINESS_LOGIC_ERROR', 'INVALID_STATE', 'OPERATION_NOT_ALLOWED',
            # Errores de autenticación y autorización
            'AUTHENTICATION_FAILED', 'AUTHENTICATION_ERROR', 'AUTHORIZATION_FAILED',
            'AUTHORIZATION_ERROR', 'INSUFFICIENT_PERMISSIONS',
            # Errores de infraestructura
            'INFRASTRUCTURE_ERROR', 'DATABASE_ERROR', 'DATABASE_CONNECTION_ERROR',
            'DATABASE_INTEGRITY_ERROR', 'DATABASE_TIMEOUT_ERROR', 'MIGRATION_ERROR',
            'CONNECTION_ERROR', 'CONFIGURATION_ERROR', 'EXTERNAL_SERVICE_ERROR', 'FILE_SYSTEM_ERROR'
        }
        
        actual_codes = {code.value for code in ErrorCode}
        assert actual_codes == expected_codes


class TestPlanificadorBaseException:
    """Tests para la excepción base PlanificadorBaseException."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica de la excepción."""
        message = "Test error message"
        exception = PlanificadorBaseException(message)
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.UNKNOWN_ERROR
        assert exception.details == {}
        assert exception.context == {}
    
    def test_initialization_with_all_parameters(self, sample_error_details, sample_context):
        """Verifica la inicialización con todos los parámetros."""
        message = "Test error with all params"
        error_code = ErrorCode.VALIDATION_ERROR
        
        exception = PlanificadorBaseException(
            message=message,
            error_code=error_code,
            details=sample_error_details,
            context=sample_context
        )
        
        assert exception.message == message
        assert exception.error_code == error_code
        assert exception.details == sample_error_details
        assert exception.context == sample_context
    
    def test_string_representation(self):
        """Verifica la representación en string de la excepción."""
        message = "Test error"
        error_code = ErrorCode.NOT_FOUND
        exception = PlanificadorBaseException(message, error_code=error_code)
        
        expected_str = f"{error_code.value}: {message}"
        assert str(exception) == expected_str
    
    def test_repr_representation(self):
        """Verifica la representación detallada de la excepción."""
        message = "Test error"
        error_code = ErrorCode.CONFLICT
        details = {'key': 'value'}
        context = {'user': 'test'}
        
        exception = PlanificadorBaseException(
            message=message,
            error_code=error_code,
            details=details,
            context=context
        )
        
        repr_str = repr(exception)
        assert "PlanificadorBaseException" in repr_str
        assert message in repr_str
        assert error_code.name in repr_str
        assert str(details) in repr_str
        assert str(context) in repr_str
    
    def test_to_dict_serialization(self, exception_helper):
        """Verifica la serialización a diccionario."""
        message = "Test serialization"
        error_code = ErrorCode.BUSINESS_RULE_VIOLATION
        details = {'field': 'test_field', 'value': 123}
        context = {'operation': 'test_op'}
        
        exception = PlanificadorBaseException(
            message=message,
            error_code=error_code,
            details=details,
            context=context
        )
        
        exception_helper.assert_exception_serialization(exception)
    
    def test_add_context_method(self):
        """Verifica el método add_context."""
        exception = PlanificadorBaseException("Test")
        
        result = exception.add_context('user_id', 123)
        
        assert result is exception  # Method chaining
        assert exception.context['user_id'] == 123
    
    def test_add_detail_method(self):
        """Verifica el método add_detail."""
        exception = PlanificadorBaseException("Test")
        
        result = exception.add_detail('field_name', 'test_field')
        
        assert result is exception  # Method chaining
        assert exception.details['field_name'] == 'test_field'
    
    def test_method_chaining(self, exception_helper):
        """Verifica que los métodos permitan method chaining."""
        exception = PlanificadorBaseException("Test")
        exception_helper.assert_method_chaining(exception)
    
    def test_inheritance_from_exception(self):
        """Verifica que herede correctamente de Exception."""
        exception = PlanificadorBaseException("Test")
        assert isinstance(exception, Exception)
        assert isinstance(exception, PlanificadorBaseException)


class TestValidationError:
    """Tests para ValidationError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica."""
        message = "Validation failed"
        exception = ValidationError(message)
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.VALIDATION_ERROR
        assert isinstance(exception, PlanificadorBaseException)
    
    def test_initialization_with_field(self):
        """Verifica la inicialización con campo específico."""
        message = "Invalid email"
        field = "email"
        
        exception = ValidationError(message, field=field)
        
        assert exception.message == message
        assert exception.details['field'] == field
    
    def test_initialization_with_value(self):
        """Verifica la inicialización con valor inválido."""
        message = "Invalid value"
        field = "age"
        value = -5
        
        exception = ValidationError(message, field=field, value=value)
        
        assert exception.details['field'] == field
        assert exception.details['invalid_value'] == value
    
    def test_initialization_with_all_params(self, sample_context):
        """Verifica la inicialización con todos los parámetros."""
        message = "Complete validation error"
        field = "username"
        value = "invalid_user"
        
        exception = ValidationError(
            message=message,
            field=field,
            value=value,
            context=sample_context
        )
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.VALIDATION_ERROR
        assert exception.details['field'] == field
        assert exception.details['invalid_value'] == value
        assert exception.context == sample_context


class TestNotFoundError:
    """Tests para NotFoundError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica."""
        message = "Resource not found"
        exception = NotFoundError(message)
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.NOT_FOUND
    
    def test_initialization_with_resource_type(self):
        """Verifica la inicialización con tipo de recurso."""
        message = "User not found"
        resource_type = "User"
        
        exception = NotFoundError(message, resource_type=resource_type)
        
        assert exception.details['resource_type'] == resource_type
    
    def test_initialization_with_resource_id(self):
        """Verifica la inicialización con ID de recurso."""
        message = "Client not found"
        resource_type = "Client"
        resource_id = 123
        
        exception = NotFoundError(
            message=message,
            resource_type=resource_type,
            resource_id=resource_id
        )
        
        assert exception.details['resource_type'] == resource_type
        assert exception.details['resource_id'] == resource_id


class TestConflictError:
    """Tests para ConflictError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica."""
        message = "Data conflict detected"
        exception = ConflictError(message)
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.CONFLICT
    
    def test_initialization_with_conflicting_field(self):
        """Verifica la inicialización con campo en conflicto."""
        message = "Email already exists"
        conflicting_field = "email"
        conflicting_value = "test@example.com"
        
        exception = ConflictError(
            message=message,
            conflicting_field=conflicting_field,
            conflicting_value=conflicting_value
        )
        
        assert exception.details['conflicting_field'] == conflicting_field
        assert exception.details['conflicting_value'] == conflicting_value


class TestBusinessLogicError:
    """Tests para BusinessLogicError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica."""
        message = "Business rule violated"
        exception = BusinessLogicError(message)
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.BUSINESS_LOGIC_ERROR
    
    def test_initialization_with_rule(self):
        """Verifica la inicialización con regla específica."""
        message = "Cannot assign more than 40 hours per week"
        rule = "max_weekly_hours"
        
        exception = BusinessLogicError(message, rule=rule)
        
        assert exception.details['violated_rule'] == rule


class TestAuthenticationError:
    """Tests para AuthenticationError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica."""
        message = "Authentication failed"
        exception = AuthenticationError(message)
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.AUTHENTICATION_ERROR
    
    def test_initialization_with_context(self):
        """Verifica la inicialización con contexto adicional."""
        message = "Invalid credentials"
        context = {"username": "testuser", "ip": "192.168.1.1"}
        
        exception = AuthenticationError(message, context=context)
        
        assert exception.context == context


class TestAuthorizationError:
    """Tests para AuthorizationError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica."""
        message = "Access denied"
        exception = AuthorizationError(message)
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.AUTHORIZATION_ERROR
    
    def test_initialization_with_required_permission(self):
        """Verifica la inicialización con permiso requerido."""
        message = "Insufficient permissions"
        required_permission = "admin_access"
        
        exception = AuthorizationError(
            message=message,
            required_permission=required_permission
        )
        
        assert exception.details['required_permission'] == required_permission


class TestExceptionHierarchy:
    """Tests para verificar la jerarquía de excepciones."""
    
    @pytest.mark.parametrize("exception_class", [
        ValidationError,
        NotFoundError,
        ConflictError,
        BusinessLogicError,
        AuthenticationError,
        AuthorizationError,
    ])
    def test_inheritance_hierarchy(self, exception_class):
        """Verifica que todas las excepciones hereden de PlanificadorBaseException."""
        exception = exception_class("Test message")
        
        assert isinstance(exception, PlanificadorBaseException)
        assert isinstance(exception, Exception)
    
    def test_exception_error_codes(self):
        """Verifica que cada excepción tenga el código de error correcto."""
        test_cases = [
            (ValidationError, ErrorCode.VALIDATION_ERROR),
            (NotFoundError, ErrorCode.NOT_FOUND),
            (ConflictError, ErrorCode.CONFLICT),
            (BusinessLogicError, ErrorCode.BUSINESS_LOGIC_ERROR),
            (AuthenticationError, ErrorCode.AUTHENTICATION_ERROR),
            (AuthorizationError, ErrorCode.AUTHORIZATION_ERROR),
        ]
        
        for exception_class, expected_code in test_cases:
            exception = exception_class("Test")
            assert exception.error_code == expected_code