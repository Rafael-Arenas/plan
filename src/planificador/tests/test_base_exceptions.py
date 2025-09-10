"""Tests para excepciones base del sistema Planificador.

Este módulo contiene tests unitarios para todas las excepciones base
definidas en planificador.exceptions.base, incluyendo:
- PlanificadorBaseException
- ValidationError
- NotFoundError
- ConflictError
- BusinessLogicError
- AuthenticationError
- AuthorizationError
- Funciones helper para crear excepciones comunes
"""

import pytest
from typing import Dict, Any, Optional

from planificador.exceptions.base import (
    ErrorCode,
    PlanificadorBaseException,
    ValidationError,
    NotFoundError,
    ConflictError,
    BusinessLogicError,
    AuthenticationError,
    AuthorizationError,
    create_validation_error,
    create_not_found_error,
    create_conflict_error,
)


class TestErrorCode:
    """Tests para el enum ErrorCode."""

    def test_error_code_values(self):
        """Verifica que todos los códigos de error tengan valores correctos."""
        assert ErrorCode.UNKNOWN_ERROR.value == "UNKNOWN_ERROR"
        assert ErrorCode.INTERNAL_ERROR.value == "INTERNAL_ERROR"
        assert ErrorCode.VALIDATION_ERROR.value == "VALIDATION_ERROR"
        assert ErrorCode.INVALID_INPUT.value == "INVALID_INPUT"
        assert ErrorCode.MISSING_REQUIRED_FIELD.value == "MISSING_REQUIRED_FIELD"
        assert ErrorCode.INVALID_FORMAT.value == "INVALID_FORMAT"
        assert ErrorCode.NOT_FOUND.value == "NOT_FOUND"
        assert ErrorCode.ALREADY_EXISTS.value == "ALREADY_EXISTS"
        assert ErrorCode.CONFLICT.value == "CONFLICT"
        assert ErrorCode.BUSINESS_RULE_VIOLATION.value == "BUSINESS_RULE_VIOLATION"
        assert ErrorCode.INVALID_STATE.value == "INVALID_STATE"
        assert ErrorCode.OPERATION_NOT_ALLOWED.value == "OPERATION_NOT_ALLOWED"
        assert ErrorCode.AUTHENTICATION_FAILED.value == "AUTHENTICATION_FAILED"
        assert ErrorCode.AUTHORIZATION_FAILED.value == "AUTHORIZATION_FAILED"
        assert ErrorCode.INSUFFICIENT_PERMISSIONS.value == "INSUFFICIENT_PERMISSIONS"

    def test_error_code_enum_completeness(self):
        """Verifica que el enum contenga todos los códigos esperados."""
        expected_codes = {
            # Errores generales
            "UNKNOWN_ERROR",
            "INTERNAL_ERROR",
            # Errores de validación
            "VALIDATION_ERROR",
            "INVALID_INPUT",
            "MISSING_REQUIRED_FIELD",
            "INVALID_FORMAT",
            "REQUIRED_FIELD_ERROR",
            "LENGTH_VALIDATION_ERROR",
            "RANGE_VALIDATION_ERROR",
            "FORMAT_VALIDATION_ERROR",
            "DATE_VALIDATION_ERROR",
            "TIME_VALIDATION_ERROR",
            "DATETIME_VALIDATION_ERROR",
            "FOREIGN_KEY_VALIDATION_ERROR",
            "UNIQUE_CONSTRAINT_ERROR",
            "PYDANTIC_VALIDATION_ERROR",
            "BUSINESS_RULE_VALIDATION_ERROR",
            # Errores de recursos
            "NOT_FOUND",
            "ALREADY_EXISTS",
            "CONFLICT",
            # Errores de lógica de negocio
            "BUSINESS_RULE_VIOLATION",
            "BUSINESS_LOGIC_ERROR",
            "INVALID_STATE",
            "OPERATION_NOT_ALLOWED",
            # Errores de autenticación/autorización
            "AUTHENTICATION_FAILED",
            "AUTHENTICATION_ERROR",
            "AUTHORIZATION_FAILED",
            "AUTHORIZATION_ERROR",
            "INSUFFICIENT_PERMISSIONS",
            # Errores de infraestructura
            "DATABASE_ERROR",
            "DATABASE_CONNECTION_ERROR",
            "DATABASE_TIMEOUT_ERROR",
            "DATABASE_INTEGRITY_ERROR",
            "CONNECTION_ERROR",
            "EXTERNAL_SERVICE_ERROR",
            "FILE_SYSTEM_ERROR",
            "CONFIGURATION_ERROR",
            "INFRASTRUCTURE_ERROR",
            "MIGRATION_ERROR",
        }
        actual_codes = {code.value for code in ErrorCode}
        assert actual_codes == expected_codes


class TestPlanificadorBaseException:
    """Tests para la excepción base PlanificadorBaseException."""

    def test_base_exception_creation_minimal(self):
        """Verifica creación de excepción base con parámetros mínimos."""
        exception = PlanificadorBaseException(
            message="Error de prueba",
            error_code=ErrorCode.UNKNOWN_ERROR
        )
        
        assert str(exception) == "UNKNOWN_ERROR: Error de prueba"
        assert exception.message == "Error de prueba"
        assert exception.error_code == ErrorCode.UNKNOWN_ERROR
        assert exception.details == {}
        assert exception.context == {}

    def test_base_exception_creation_complete(self):
        """Verifica creación de excepción base con todos los parámetros."""
        details = {"field": "test_field", "value": "invalid_value"}
        context = {"operation": "test_operation", "user_id": "123"}
        
        exception = PlanificadorBaseException(
            message="Error completo de prueba",
            error_code=ErrorCode.VALIDATION_ERROR,
            details=details,
            context=context
        )
        
        assert str(exception) == "VALIDATION_ERROR: Error completo de prueba"
        assert exception.message == "Error completo de prueba"
        assert exception.error_code == ErrorCode.VALIDATION_ERROR
        assert exception.details == details
        assert exception.context == context

    def test_base_exception_inheritance(self):
        """Verifica que PlanificadorBaseException herede de Exception."""
        exception = PlanificadorBaseException(
            message="Test",
            error_code=ErrorCode.UNKNOWN_ERROR
        )
        
        assert isinstance(exception, Exception)
        assert isinstance(exception, PlanificadorBaseException)


class TestValidationError:
    """Tests para ValidationError."""

    def test_validation_error_creation_minimal(self):
        """Verifica creación de ValidationError con parámetros mínimos."""
        exception = ValidationError(
            message="Error de validación",
            field="test_field"
        )
        
        assert str(exception) == "VALIDATION_ERROR: Error de validación"
        assert exception.message == "Error de validación"
        assert exception.error_code == ErrorCode.VALIDATION_ERROR
        assert exception.details["field"] == "test_field"
        assert "invalid_value" not in exception.details

    def test_validation_error_creation_complete(self):
        """Verifica creación de ValidationError con todos los parámetros."""
        details = {"constraint": "min_length"}
        context = {"operation": "user_creation"}
        
        exception = ValidationError(
            message="Valor inválido",
            field="email",
            value="invalid-email",
            details=details,
            context=context
        )
        
        assert str(exception) == "VALIDATION_ERROR: Valor inválido"
        assert exception.message == "Valor inválido"
        assert exception.error_code == ErrorCode.VALIDATION_ERROR
        assert exception.details["field"] == "email"
        assert exception.details["invalid_value"] == "invalid-email"
        assert exception.details["constraint"] == "min_length"
        assert exception.context == context

    def test_validation_error_inheritance(self):
        """Verifica que ValidationError herede de PlanificadorBaseException."""
        exception = ValidationError(
            message="Test",
            field="test_field"
        )
        
        assert isinstance(exception, PlanificadorBaseException)
        assert isinstance(exception, ValidationError)


class TestNotFoundError:
    """Tests para NotFoundError."""

    def test_not_found_error_creation_minimal(self):
        """Verifica creación de NotFoundError con parámetros mínimos."""
        exception = NotFoundError(
            message="Recurso no encontrado",
            resource_type="User"
        )
        
        assert str(exception) == "NOT_FOUND: Recurso no encontrado"
        assert exception.message == "Recurso no encontrado"
        assert exception.error_code == ErrorCode.NOT_FOUND
        assert exception.details["resource_type"] == "User"
        assert "resource_id" not in exception.details

    def test_not_found_error_creation_complete(self):
        """Verifica creación de NotFoundError con todos los parámetros."""
        details = {"table": "users"}
        context = {"operation": "user_lookup"}
        
        exception = NotFoundError(
            message="Usuario no encontrado",
            resource_type="User",
            resource_id="123",
            details=details,
            context=context
        )
        
        assert str(exception) == "NOT_FOUND: Usuario no encontrado"
        assert exception.message == "Usuario no encontrado"
        assert exception.error_code == ErrorCode.NOT_FOUND
        assert exception.details["resource_type"] == "User"
        assert exception.details["resource_id"] == "123"
        assert exception.details["table"] == "users"
        assert exception.context == context

    def test_not_found_error_inheritance(self):
        """Verifica que NotFoundError herede de PlanificadorBaseException."""
        exception = NotFoundError(
            message="Test",
            resource_type="Test"
        )
        
        assert isinstance(exception, PlanificadorBaseException)
        assert isinstance(exception, NotFoundError)


class TestConflictError:
    """Tests para ConflictError."""

    def test_conflict_error_creation_minimal(self):
        """Verifica creación de ConflictError con parámetros mínimos."""
        exception = ConflictError(
            message="Conflicto detectado",
            conflicting_field="email",
            conflicting_value="test@example.com"
        )
        
        assert str(exception) == "CONFLICT: Conflicto detectado"
        assert exception.message == "Conflicto detectado"
        assert exception.error_code == ErrorCode.CONFLICT
        assert exception.details["conflicting_field"] == "email"
        assert exception.details["conflicting_value"] == "test@example.com"

    def test_conflict_error_creation_complete(self):
        """Verifica creación de ConflictError con todos los parámetros."""
        details = {"constraint": "unique_email", "resource_type": "User"}
        context = {"operation": "user_creation"}
        
        exception = ConflictError(
            message="Email ya existe",
            conflicting_field="email",
            conflicting_value="test@example.com",
            details=details,
            context=context
        )
        
        assert str(exception) == "CONFLICT: Email ya existe"
        assert exception.message == "Email ya existe"
        assert exception.error_code == ErrorCode.CONFLICT
        assert exception.details["resource_type"] == "User"
        assert exception.details["conflicting_field"] == "email"
        assert exception.details["conflicting_value"] == "test@example.com"
        assert exception.details["constraint"] == "unique_email"

    def test_exception_serialization_to_dict(self):
        """Verifica que las excepciones se puedan serializar a diccionario."""
        exception = ValidationError(
            message="Error de validación",
            field="email",
            value="invalid-email"
        )
        
        # Convertir a diccionario
        exception_dict = {
            'message': exception.message,
            'error_code': exception.error_code.value,
            'details': exception.details,
            'context': exception.context
        }
        
        # Verificar contenido
        assert exception_dict['message'] == "Error de validación"
        assert exception_dict['error_code'] == "VALIDATION_ERROR"
        assert exception_dict['details']['field'] == "email"
        assert exception_dict['details']['invalid_value'] == "invalid-email"

    def test_exception_json_serialization(self):
        """Verifica que las excepciones se puedan serializar a JSON."""
        import json
        
        exception = ConflictError(
            message="Recurso en conflicto",
            conflicting_field="email",
            conflicting_value="test@example.com",
            details={"resource_type": "User"}
        )
        
        # Crear diccionario serializable
        serializable_dict = {
            'message': exception.message,
            'error_code': exception.error_code.value,
            'details': exception.details,
            'context': exception.context
        }
        
        # Serializar a JSON
        json_str = json.dumps(serializable_dict)
        
        # Deserializar y verificar
        deserialized = json.loads(json_str)
        assert deserialized['message'] == "Recurso en conflicto"
        assert deserialized['error_code'] == "CONFLICT"
        assert deserialized['details']['resource_type'] == "User"
        assert deserialized['details']['conflicting_field'] == "email"

    def test_conflict_error_inheritance(self):
        """Verifica que ConflictError herede de PlanificadorBaseException."""
        exception = ConflictError(
            message="Test",
            conflicting_field="test_field",
            conflicting_value="test_value"
        )
        
        assert isinstance(exception, PlanificadorBaseException)
        assert isinstance(exception, ConflictError)


class TestBusinessLogicError:
    """Tests para BusinessLogicError."""

    def test_business_logic_error_creation_minimal(self):
        """Verifica creación de BusinessLogicError con parámetros mínimos."""
        exception = BusinessLogicError(
            message="Regla de negocio violada",
            rule="minimum_age"
        )
        
        assert str(exception) == "BUSINESS_LOGIC_ERROR: Regla de negocio violada"
        assert exception.message == "Regla de negocio violada"
        assert exception.error_code == ErrorCode.BUSINESS_LOGIC_ERROR
        assert exception.details["violated_rule"] == "minimum_age"
        assert exception.context == {}

    def test_business_logic_error_creation_complete(self):
        """Verifica creación de BusinessLogicError con todos los parámetros."""
        context = {"user_age": 16, "minimum_required": 18}
        details = {"rule_type": "age_validation"}
        
        exception = BusinessLogicError(
            message="Usuario menor de edad",
            rule="minimum_age",
            context=context,
            details=details
        )
        
        assert str(exception) == "BUSINESS_LOGIC_ERROR: Usuario menor de edad"
        assert exception.message == "Usuario menor de edad"
        assert exception.error_code == ErrorCode.BUSINESS_LOGIC_ERROR
        assert exception.details["violated_rule"] == "minimum_age"
        assert exception.details["rule_type"] == "age_validation"
        assert exception.context == context

    def test_business_logic_error_inheritance(self):
        """Verifica que BusinessLogicError herede de PlanificadorBaseException."""
        exception = BusinessLogicError(
            message="Test",
            rule="test_rule"
        )
        
        assert isinstance(exception, PlanificadorBaseException)
        assert isinstance(exception, BusinessLogicError)


class TestAuthenticationError:
    """Tests para AuthenticationError."""

    def test_authentication_error_creation_minimal(self):
        """Verifica creación de AuthenticationError con parámetros mínimos."""
        exception = AuthenticationError(
            message="Credenciales inválidas"
        )
        
        assert str(exception) == "AUTHENTICATION_ERROR: Credenciales inválidas"
        assert exception.message == "Credenciales inválidas"
        assert exception.error_code == ErrorCode.AUTHENTICATION_ERROR
        assert exception.details == {}
        assert exception.context == {}

    def test_authentication_error_creation_complete(self):
        """Verifica creación de AuthenticationError con todos los parámetros."""
        details = {"attempt_count": 3, "lockout_time": "30min", "authentication_method": "password", "user_identifier": "user@example.com"}
        context = {"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0"}
        
        exception = AuthenticationError(
            message="Demasiados intentos fallidos",
            details=details,
            context=context
        )
        
        assert str(exception) == "AUTHENTICATION_ERROR: Demasiados intentos fallidos"
        assert exception.message == "Demasiados intentos fallidos"
        assert exception.error_code == ErrorCode.AUTHENTICATION_ERROR
        assert exception.details["authentication_method"] == "password"
        assert exception.details["user_identifier"] == "user@example.com"
        assert exception.details["attempt_count"] == 3
        assert exception.context == context

    def test_authentication_error_inheritance(self):
        """Verifica que AuthenticationError herede de PlanificadorBaseException."""
        exception = AuthenticationError(
            message="Test"
        )
        
        assert isinstance(exception, PlanificadorBaseException)
        assert isinstance(exception, AuthenticationError)


class TestAuthorizationError:
    """Tests para AuthorizationError."""

    def test_authorization_error_creation_minimal(self):
        """Verifica creación de AuthorizationError con parámetros mínimos."""
        exception = AuthorizationError(
            message="Acceso denegado"
        )
        
        assert str(exception) == "AUTHORIZATION_ERROR: Acceso denegado"
        assert exception.message == "Acceso denegado"
        assert exception.error_code == ErrorCode.AUTHORIZATION_ERROR
        assert exception.details == {}
        assert exception.context == {}

    def test_authorization_error_creation_complete(self):
        """Verifica creación de AuthorizationError con todos los parámetros."""
        user_permissions = ["read", "write"]
        details = {"policy": "admin_only", "user_permissions": user_permissions, "resource_type": "Project", "resource_id": "proj_123"}
        context = {"user_id": "123", "resource": "project_settings"}
        
        exception = AuthorizationError(
            message="Permisos insuficientes",
            required_permission="admin",
            details=details,
            context=context
        )
        
        assert str(exception) == "AUTHORIZATION_ERROR: Permisos insuficientes"
        assert exception.message == "Permisos insuficientes"
        assert exception.error_code == ErrorCode.AUTHORIZATION_ERROR
        assert exception.details["required_permission"] == "admin"
        assert exception.details["user_permissions"] == user_permissions
        assert exception.details["resource_type"] == "Project"
        assert exception.details["resource_id"] == "proj_123"
        assert exception.details["policy"] == "admin_only"
        assert exception.context == context

    def test_authorization_error_inheritance(self):
        """Verifica que AuthorizationError herede de PlanificadorBaseException."""
        exception = AuthorizationError(
            message="Test"
        )
        
        assert isinstance(exception, PlanificadorBaseException)
        assert isinstance(exception, AuthorizationError)


class TestHelperFunctions:
    """Tests para funciones helper de creación de excepciones."""

    def test_create_validation_error_minimal(self):
        """Verifica create_validation_error con parámetros mínimos."""
        exception = create_validation_error(
            field="email",
            value="invalid-email",
            reason="formato inválido"
        )
        
        assert isinstance(exception, ValidationError)
        assert "Validación fallida para campo 'email': formato inválido" in exception.message
        assert exception.error_code == ErrorCode.VALIDATION_ERROR
        assert exception.details["field"] == "email"
        assert exception.details["invalid_value"] == "invalid-email"

    def test_create_validation_error_complete(self):
        """Verifica create_validation_error con todos los parámetros."""
        exception = create_validation_error(
            field="age",
            value="abc",
            reason="debe ser un número entero positivo"
        )
        
        assert isinstance(exception, ValidationError)
        assert "Validación fallida para campo 'age': debe ser un número entero positivo" in exception.message
        assert exception.error_code == ErrorCode.VALIDATION_ERROR
        assert exception.details["field"] == "age"
        assert exception.details["invalid_value"] == "abc"

    def test_create_not_found_error_minimal(self):
        """Verifica create_not_found_error con parámetros mínimos."""
        exception = create_not_found_error(
            resource_type="User",
            resource_id="123"
        )
        
        assert isinstance(exception, NotFoundError)
        assert "User con ID 123 no encontrado" in exception.message
        assert exception.error_code == ErrorCode.NOT_FOUND
        assert exception.details["resource_type"] == "User"
        assert exception.details["resource_id"] == "123"

    def test_create_not_found_error_complete(self):
        """Verifica create_not_found_error con todos los parámetros."""
        exception = create_not_found_error(
            resource_type="Project",
            resource_id="proj_456"
        )
        
        assert isinstance(exception, NotFoundError)
        assert "Project con ID proj_456 no encontrado" in exception.message
        assert exception.error_code == ErrorCode.NOT_FOUND
        assert exception.details["resource_type"] == "Project"
        assert exception.details["resource_id"] == "proj_456"

    def test_create_conflict_error_minimal(self):
        """Verifica create_conflict_error con parámetros mínimos."""
        exception = create_conflict_error(
            resource_type="User",
            field="email",
            value="test@example.com"
        )
        
        assert isinstance(exception, ConflictError)
        assert "Ya existe un User con email 'test@example.com'" in exception.message
        assert exception.error_code == ErrorCode.CONFLICT
        assert exception.details["resource_type"] == "User"
        assert exception.details["conflicting_field"] == "email"
        assert exception.details["conflicting_value"] == "test@example.com"

    def test_create_conflict_error_complete(self):
        """Verifica create_conflict_error con todos los parámetros."""
        exception = create_conflict_error(
            resource_type="Project",
            field="name",
            value="Proyecto Alpha"
        )
        
        assert isinstance(exception, ConflictError)
        assert "Ya existe un Project con name 'Proyecto Alpha'" in exception.message
        assert exception.error_code == ErrorCode.CONFLICT
        assert exception.details["resource_type"] == "Project"
        assert exception.details["conflicting_field"] == "name"
        assert exception.details["conflicting_value"] == "Proyecto Alpha"


class TestExceptionChaining:
    """Tests para verificar el encadenamiento correcto de excepciones."""

    def test_exception_chaining_with_context(self):
        """Verifica que las excepciones pueden incluir contexto adicional."""
        context = {"operation": "user_creation", "step": "validation"}
        
        exception = ValidationError(
            message="Error de validación",
            field="test_field",
            context=context
        )
        
        assert exception.context == context
        assert str(exception) == "VALIDATION_ERROR: Error de validación"

    def test_exception_raising_preserves_details(self):
        """Verifica que al lanzar excepciones se preserven los detalles."""
        def inner_function():
            raise ValueError("Error interno")
        
        def outer_function():
            try:
                inner_function()
            except ValueError as e:
                raise ValidationError(
                    message="Error de validación",
                    field="test_field",
                    value="invalid_value"
                ) from e
        
        with pytest.raises(ValidationError) as exc_info:
            outer_function()
        
        exception = exc_info.value
        assert exception.details["field"] == "test_field"
        assert exception.details["invalid_value"] == "invalid_value"
        assert exception.__cause__ is not None


class TestExceptionSerialization:
    """Tests para verificar que las excepciones se puedan serializar correctamente."""

    def test_exception_str_representation(self):
        """Verifica que las excepciones tengan representación string correcta."""
        exception = ValidationError(
            message="Error de validación detallado",
            field="email",
            value="invalid-email"
        )
        
        str_repr = str(exception)
        assert str_repr == "VALIDATION_ERROR: Error de validación detallado"

    def test_exception_details_access(self):
        """Verifica que se puedan acceder a todos los detalles de la excepción."""
        details = {"constraint": "unique", "table": "users", "resource_type": "User"}
        
        exception = ConflictError(
            message="Conflicto de unicidad",
            conflicting_field="email",
            conflicting_value="test@example.com",
            details=details
        )
        
        # Verificar que todos los atributos sean accesibles
        assert hasattr(exception, 'message')
        assert hasattr(exception, 'error_code')
        assert hasattr(exception, 'details')
        assert hasattr(exception, 'context')
        
        # Verificar valores
        assert exception.details["resource_type"] == "User"
        assert exception.details["conflicting_field"] == "email"
        assert exception.details["conflicting_value"] == "test@example.com"
        assert exception.details["constraint"] == "unique"

    def test_exception_serialization_to_dict(self):
        """Verifica que las excepciones se puedan serializar a diccionario."""
        exception = ValidationError(
            message="Error de validación",
            field="email",
            value="invalid-email"
        )
        
        # Convertir a diccionario
        exception_dict = {
            'message': exception.message,
            'error_code': exception.error_code.value,
            'details': exception.details,
            'context': exception.context
        }
        
        # Verificar contenido
        assert exception_dict['message'] == "Error de validación"
        assert exception_dict['error_code'] == "VALIDATION_ERROR"
        assert exception_dict['details']['field'] == "email"
        assert exception_dict['details']['invalid_value'] == "invalid-email"

    def test_exception_json_serialization(self):
        """Verifica que las excepciones se puedan serializar a JSON."""
        import json
        
        exception = ConflictError(
            message="Recurso en conflicto",
            conflicting_field="email",
            conflicting_value="test@example.com",
            details={"resource_type": "User"}
        )
        
        # Crear diccionario serializable
        serializable_dict = {
            'message': exception.message,
            'error_code': exception.error_code.value,
            'details': exception.details
        }
        
        # Serializar a JSON
        json_str = json.dumps(serializable_dict)
        
        # Deserializar y verificar
        deserialized = json.loads(json_str)
        assert deserialized['message'] == "Recurso en conflicto"
        assert deserialized['error_code'] == "CONFLICT"
        assert deserialized['details']['resource_type'] == "User"
        assert deserialized['details']['conflicting_field'] == "email"