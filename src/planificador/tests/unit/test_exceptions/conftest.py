# src/planificador/tests/unit/test_exceptions/conftest.py

"""
Configuración y fixtures para tests de excepciones.

Este módulo proporciona fixtures comunes y utilidades para testing
del sistema de excepciones del planificador.
"""

import pytest
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

from planificador.exceptions import (
    ErrorCode,
    PlanificadorBaseException,
    ValidationError,
    NotFoundError,
    ConflictError,
    BusinessLogicError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    ConnectionError,
    ConfigurationError,
    ExternalServiceError,
    FileSystemError,
    PydanticValidationError,
    DateValidationError,
    TimeValidationError,
    FormatValidationError,
    RangeValidationError,
    LengthValidationError,
)


@pytest.fixture
def sample_error_details() -> Dict[str, Any]:
    """Fixture que proporciona detalles de error de ejemplo."""
    return {
        'field': 'test_field',
        'value': 'test_value',
        'constraint': 'unique_constraint',
        'table': 'test_table'
    }


@pytest.fixture
def sample_context() -> Dict[str, Any]:
    """Fixture que proporciona contexto de error de ejemplo."""
    return {
        'user_id': 123,
        'operation': 'create_user',
        'timestamp': '2025-01-26T10:00:00Z',
        'request_id': 'req-123456'
    }


@pytest.fixture
def sample_pydantic_errors() -> List[Dict[str, Any]]:
    """Fixture que proporciona errores de Pydantic de ejemplo."""
    return [
        {
            'loc': ('email',),
            'msg': 'field required',
            'type': 'value_error.missing',
            'ctx': {}
        },
        {
            'loc': ('age',),
            'msg': 'ensure this value is greater than 0',
            'type': 'value_error.number.not_gt',
            'ctx': {'limit_value': 0}
        }
    ]


@pytest.fixture
def sample_dates():
    """Fixture que proporciona fechas de ejemplo para testing."""
    return {
        'valid_date': date(2025, 1, 26),
        'min_date': date(2025, 1, 1),
        'max_date': date(2025, 12, 31),
        'invalid_date_str': '2025-13-45',
        'future_date': date(2025, 12, 25)
    }


@pytest.fixture
def sample_times():
    """Fixture que proporciona tiempos de ejemplo para testing."""
    return {
        'valid_time': time(14, 30, 0),
        'min_time': time(8, 0, 0),
        'max_time': time(18, 0, 0),
        'invalid_time_str': '25:70:90',
        'midnight': time(0, 0, 0)
    }


@pytest.fixture
def sample_datetimes():
    """Fixture que proporciona datetimes de ejemplo para testing."""
    return {
        'valid_datetime': datetime(2025, 1, 26, 14, 30, 0),
        'min_datetime': datetime(2025, 1, 1, 0, 0, 0),
        'max_datetime': datetime(2025, 12, 31, 23, 59, 59),
        'invalid_datetime_str': '2025-13-45T25:70:90'
    }


@pytest.fixture
def mock_database_session():
    """Fixture que proporciona una sesión de base de datos mock."""
    session = Mock()
    session.rollback = Mock()
    session.commit = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def mock_sqlalchemy_error():
    """Fixture que proporciona un error de SQLAlchemy mock."""
    from sqlalchemy.exc import SQLAlchemyError
    
    error = Mock(spec=SQLAlchemyError)
    error.args = ('Test SQLAlchemy error',)
    error.__str__ = Mock(return_value='Test SQLAlchemy error')
    return error


class ExceptionTestHelper:
    """Clase helper para testing de excepciones."""
    
    @staticmethod
    def assert_exception_structure(
        exception: PlanificadorBaseException,
        expected_message: str,
        expected_error_code: ErrorCode,
        expected_details: Optional[Dict[str, Any]] = None,
        expected_context: Optional[Dict[str, Any]] = None
    ):
        """Valida la estructura completa de una excepción."""
        assert str(exception) == f"[{expected_error_code.value}] {expected_message}"
        assert exception.message == expected_message
        assert exception.error_code == expected_error_code
        
        if expected_details:
            for key, value in expected_details.items():
                assert key in exception.details
                assert exception.details[key] == value
        
        if expected_context:
            for key, value in expected_context.items():
                assert key in exception.context
                assert exception.context[key] == value
    
    @staticmethod
    def assert_exception_serialization(exception: PlanificadorBaseException):
        """Valida que la excepción se pueda serializar correctamente."""
        serialized = exception.to_dict()
        
        assert 'error_type' in serialized
        assert 'message' in serialized
        assert 'error_code' in serialized
        assert 'details' in serialized
        assert 'context' in serialized
        
        assert serialized['error_type'] == exception.__class__.__name__
        assert serialized['message'] == exception.message
        assert serialized['error_code'] == exception.error_code.value
        assert serialized['details'] == exception.details
        assert serialized['context'] == exception.context
    
    @staticmethod
    def assert_method_chaining(exception: PlanificadorBaseException):
        """Valida que los métodos de la excepción permitan method chaining."""
        result1 = exception.add_context('test_key', 'test_value')
        result2 = exception.add_detail('test_detail', 'test_detail_value')
        
        assert result1 is exception
        assert result2 is exception
        assert exception.context['test_key'] == 'test_value'
        assert exception.details['test_detail'] == 'test_detail_value'


@pytest.fixture
def exception_helper():
    """Fixture que proporciona la clase helper para testing de excepciones."""
    return ExceptionTestHelper


# Parametrized fixtures para testing exhaustivo
@pytest.fixture(params=[
    ErrorCode.UNKNOWN_ERROR,
    ErrorCode.VALIDATION_ERROR,
    ErrorCode.NOT_FOUND,
    ErrorCode.CONFLICT,
    ErrorCode.BUSINESS_RULE_VIOLATION,
    ErrorCode.AUTHENTICATION_FAILED,
    ErrorCode.AUTHORIZATION_FAILED
])
def all_error_codes(request):
    """Fixture parametrizada con todos los códigos de error."""
    return request.param


@pytest.fixture(params=[
    'email@example.com',
    'invalid-email',
    'test@domain',
    '@domain.com',
    'test@',
    ''
])
def email_test_cases(request):
    """Fixture parametrizada con casos de prueba para emails."""
    return request.param


@pytest.fixture(params=[
    '+56912345678',
    '912345678',
    '123456789',
    'invalid-phone',
    '123',
    ''
])
def phone_test_cases(request):
    """Fixture parametrizada con casos de prueba para teléfonos."""
    return request.param