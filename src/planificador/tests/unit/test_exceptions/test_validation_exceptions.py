# src/planificador/tests/unit/test_exceptions/test_validation_exceptions.py

"""
Tests para excepciones de validación del sistema de planificación.

Este módulo contiene tests exhaustivos para todas las excepciones específicas
de validación: Pydantic, fechas, tiempo, formato, rango, longitud y campos requeridos.
"""

import pytest
from datetime import datetime, date, time
from typing import Any, Dict, List, Optional

from planificador.exceptions import (
    ErrorCode,
    ValidationError,
    PydanticValidationError,
    DateValidationError,
    TimeValidationError,
    DateTimeValidationError,
    FormatValidationError,
    RangeValidationError,
    LengthValidationError,
    RequiredFieldError,
)


class TestPydanticValidationError:
    """Tests para PydanticValidationError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica de PydanticValidationError."""
        pydantic_errors = [{'loc': ('field',), 'msg': 'Pydantic validation failed', 'type': 'value_error'}]
        exception = PydanticValidationError(pydantic_errors=pydantic_errors)
        
        assert 'field' in exception.message
        assert exception.error_code == ErrorCode.PYDANTIC_VALIDATION_ERROR
        assert isinstance(exception, ValidationError)
    
    def test_initialization_with_validation_errors(self):
        """Verifica la inicialización con errores de validación específicos."""
        pydantic_errors = [
            {'loc': ('email',), 'msg': 'Invalid email format', 'type': 'value_error'},
            {'loc': ('age',), 'msg': 'Must be positive integer', 'type': 'value_error'}
        ]
        
        exception = PydanticValidationError(pydantic_errors=pydantic_errors)
        
        assert exception.details['pydantic_errors'] == pydantic_errors
        assert exception.details['error_count'] == 2
        assert 'email' in exception.message
    
    def test_initialization_with_model_name(self):
        """Verifica la inicialización con nombre del modelo."""
        pydantic_errors = [{'loc': ('username',), 'msg': 'Required field', 'type': 'missing'}]
        model_name = "UserCreateSchema"
        
        exception = PydanticValidationError(
            pydantic_errors=pydantic_errors
        )
        exception.add_detail('model_name', model_name)
        
        assert exception.details['model_name'] == model_name
        assert exception.details['pydantic_errors'] == pydantic_errors
    
    def test_initialization_with_input_data(self):
        """Verifica la inicialización con datos de entrada."""
        pydantic_errors = [{'loc': ('email',), 'msg': 'Invalid format', 'type': 'value_error'}]
        input_data = {'email': 'invalid-email', 'age': -5}
        
        exception = PydanticValidationError(
            pydantic_errors=pydantic_errors
        )
        exception.add_detail('input_data', input_data)
        
        assert exception.details['input_data'] == input_data
        assert exception.details['pydantic_errors'] == pydantic_errors


class TestDateValidationError:
    """Tests para DateValidationError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica de DateValidationError."""
        field = "birth_date"
        value = "invalid-date"
        reason = "Formato de fecha inválido"
        
        exception = DateValidationError(field=field, value=value)
        exception.add_detail('reason', reason)
        
        assert field in exception.message
        assert exception.error_code == ErrorCode.DATE_VALIDATION_ERROR
        assert isinstance(exception, ValidationError)
    
    def test_initialization_with_invalid_date(self):
        """Verifica la inicialización con fecha inválida."""
        field = "future_date"
        invalid_date = date(2025, 12, 31)
        reason = "La fecha no puede estar en el futuro"
        
        exception = DateValidationError(field=field, value=invalid_date)
        exception.add_detail('reason', reason)
        
        assert exception.field == field
        assert exception.value == invalid_date
    
    def test_initialization_with_expected_format(self):
        """Verifica la inicialización con formato esperado."""
        field = "date_string"
        invalid_date_str = "31/12/2024"
        reason = "Formato de fecha inválido, se esperaba YYYY-MM-DD"
        
        exception = DateValidationError(
            field=field,
            value=invalid_date_str,
        )
        exception.add_detail('reason', reason)
        exception.add_detail('expected_format', 'YYYY-MM-DD')
        
        assert exception.field == field
        assert exception.value == invalid_date_str
        assert exception.details['expected_format'] == "YYYY-MM-DD"
    
    def test_initialization_with_date_range(self):
        """Verifica la inicialización con rango de fechas."""
        field = "project_date"
        invalid_date = date(1900, 1, 1)
        min_date = date(2020, 1, 1)
        max_date = date(2030, 12, 31)
        reason = "Fecha fuera del rango permitido"
        
        exception = DateValidationError(
            field=field,
            value=invalid_date
        )
        exception.add_detail('reason', reason)
        exception.add_detail('min_date', min_date.isoformat())
        exception.add_detail('max_date', max_date.isoformat())
        
        assert exception.field == field
        assert exception.value == invalid_date
        assert exception.details['min_date'] == min_date.isoformat()
        assert exception.details['max_date'] == max_date.isoformat()


class TestTimeValidationError:
    """Tests para TimeValidationError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica de TimeValidationError."""
        field = "start_time"
        value = "invalid-time"
        reason = "Formato de hora inválido"
        
        exception = TimeValidationError(field=field, value=value)
        exception.add_detail('reason', reason)
        
        assert field in exception.message
        assert exception.error_code == ErrorCode.TIME_VALIDATION_ERROR
        assert isinstance(exception, ValidationError)
    
    def test_initialization_with_invalid_time(self):
        """Verifica la inicialización con tiempo inválido."""
        field = "work_time"
        invalid_time = time(23, 30)
        reason = "Hora fuera del horario laboral"
        
        exception = TimeValidationError(field=field, value=invalid_time)
        exception.add_detail('reason', reason)
        
        assert exception.field == field
        assert exception.value == invalid_time
    
    def test_initialization_with_time_range(self):
        """Verifica la inicialización con rango de tiempo."""
        field = "meeting_time"
        invalid_time = time(6, 0)
        min_time = time(9, 0)
        max_time = time(17, 0)
        reason = "Hora fuera del rango permitido"
        
        exception = TimeValidationError(
            field=field,
            value=invalid_time
        )
        exception.add_detail('reason', reason)
        exception.add_detail('min_time', min_time.isoformat())
        exception.add_detail('max_time', max_time.isoformat())
        
        assert exception.field == field
        assert exception.value == invalid_time
        assert exception.details['min_time'] == min_time.isoformat()
        assert exception.details['max_time'] == max_time.isoformat()
    
    def test_initialization_with_expected_format(self):
        """Verifica la inicialización con formato esperado."""
        field = "time_string"
        invalid_time_str = "11:30 PM"
        reason = "Formato de hora inválido, se esperaba HH:MM"
        
        exception = TimeValidationError(
            field=field,
            value=invalid_time_str
        )
        exception.add_detail('reason', reason)
        exception.add_detail('expected_format', 'HH:MM')
        
        assert exception.field == field
        assert exception.value == invalid_time_str
        assert exception.details['expected_format'] == "HH:MM"


class TestDateTimeValidationError:
    """Tests para DateTimeValidationError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica de DateTimeValidationError."""
        field = "event_datetime"
        value = "invalid-datetime"
        reason = "Formato de fecha y hora inválido"
        
        exception = DateTimeValidationError(field=field, value=value)
        exception.add_detail('reason', reason)
        
        assert field in exception.message
        assert exception.error_code == ErrorCode.DATETIME_VALIDATION_ERROR
        assert isinstance(exception, ValidationError)
    
    def test_initialization_with_invalid_datetime(self):
        """Verifica la inicialización con datetime inválido."""
        field = "appointment_datetime"
        invalid_datetime = datetime(2020, 1, 1, 12, 0)
        reason = "Fecha y hora en el pasado"
        
        exception = DateTimeValidationError(field=field, value=invalid_datetime)
        exception.add_detail('reason', reason)
        
        assert exception.field == field
        assert exception.value == invalid_datetime
    
    def test_initialization_with_timezone_info(self):
        """Verifica la inicialización con información de zona horaria."""
        field = "meeting_datetime"
        invalid_datetime = datetime(2024, 6, 15, 14, 30)
        reason = "Zona horaria incorrecta"
        timezone = "UTC"
        expected_timezone = "America/Santiago"
        
        exception = DateTimeValidationError(
            field=field,
            value=invalid_datetime
        )
        exception.add_detail('reason', reason)
        exception.add_detail('timezone', timezone)
        exception.add_detail('expected_timezone', expected_timezone)
        
        assert exception.field == field
        assert exception.value == invalid_datetime
        assert exception.details['timezone'] == timezone
        assert exception.details['expected_timezone'] == expected_timezone
    
    def test_initialization_with_datetime_range(self):
        """Verifica la inicialización con rango de datetime."""
        field = "event_datetime"
        invalid_datetime = datetime(2019, 1, 1, 0, 0)
        min_datetime = datetime(2020, 1, 1, 0, 0)
        max_datetime = datetime(2025, 12, 31, 23, 59)
        reason = "Fecha y hora fuera del rango permitido"
        
        exception = DateTimeValidationError(
            field=field,
            value=invalid_datetime
        )
        exception.add_detail('reason', reason)
        exception.add_detail('min_datetime', min_datetime.isoformat())
        exception.add_detail('max_datetime', max_datetime.isoformat())
        
        assert exception.field == field
        assert exception.value == invalid_datetime
        assert exception.details['min_datetime'] == min_datetime.isoformat()
        assert exception.details['max_datetime'] == max_datetime.isoformat()


class TestFormatValidationError:
    """Tests para FormatValidationError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica de FormatValidationError."""
        field = "email"
        value = "invalid-email"
        reason = "Formato de email inválido"
        
        exception = FormatValidationError(field=field, value=value)
        exception.add_detail('reason', reason)
        
        assert field in exception.message
        assert exception.error_code == ErrorCode.FORMAT_VALIDATION_ERROR
        assert isinstance(exception, ValidationError)
    
    def test_initialization_with_invalid_value(self):
        """Verifica la inicialización con valor inválido."""
        field = "email"
        invalid_value = "not-an-email"
        reason = "Formato de email inválido"
        
        exception = FormatValidationError(field=field, value=invalid_value)
        exception.add_detail('reason', reason)
        
        assert exception.field == field
        assert exception.value == invalid_value
    
    def test_initialization_with_expected_pattern(self):
        """Verifica la inicialización con patrón esperado."""
        field = "phone"
        invalid_value = "123-456"
        reason = "Formato de teléfono inválido"
        expected_pattern = r"^\+?[1-9]\d{1,14}$"
        
        exception = FormatValidationError(
            field=field,
            value=invalid_value
        )
        exception.add_detail('reason', reason)
        exception.add_detail('expected_pattern', expected_pattern)
        
        assert exception.field == field
        assert exception.value == invalid_value
        assert exception.details['expected_pattern'] == expected_pattern
    
    def test_initialization_with_format_type(self):
        """Verifica la inicialización con tipo de formato."""
        field = "website"
        invalid_value = "not-a-url"
        reason = "Formato de URL inválido"
        format_type = "URL"
        expected_pattern = r"^https?://"
        
        exception = FormatValidationError(
            field=field,
            value=invalid_value
        )
        exception.add_detail('reason', reason)
        exception.add_detail('format_type', format_type)
        exception.add_detail('expected_pattern', expected_pattern)
        
        assert exception.field == field
        assert exception.value == invalid_value
        assert exception.details['format_type'] == format_type


class TestRangeValidationError:
    """Tests para RangeValidationError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica de RangeValidationError."""
        field = "age"
        value = 150
        reason = "Valor fuera del rango permitido"
        
        exception = RangeValidationError(field=field, value=value)
        exception.add_detail('reason', reason)
        
        assert field in exception.message
        assert exception.error_code == ErrorCode.RANGE_VALIDATION_ERROR
        assert isinstance(exception, ValidationError)
    
    def test_initialization_with_numeric_range(self):
        """Verifica la inicialización con rango numérico."""
        field = "age"
        invalid_value = 16
        reason = "La edad debe estar entre 18 y 65 años"
        min_value = 18
        max_value = 65
        
        exception = RangeValidationError(
            field=field,
            value=invalid_value
        )
        exception.add_detail('reason', reason)
        exception.add_detail('min_value', min_value)
        exception.add_detail('max_value', max_value)
        
        assert exception.field == field
        assert exception.value == invalid_value
        assert exception.details['min_value'] == min_value
        assert exception.details['max_value'] == max_value
    
    def test_initialization_with_value_type(self):
        """Verifica la inicialización con tipo de valor."""
        field = "percentage"
        invalid_value = 150
        reason = "Porcentaje inválido"
        min_value = 0
        max_value = 100
        value_type = "percentage"
        
        exception = RangeValidationError(
            field=field,
            value=invalid_value
        )
        exception.add_detail('reason', reason)
        exception.add_detail('min_value', min_value)
        exception.add_detail('max_value', max_value)
        exception.add_detail('value_type', value_type)
        
        assert exception.field == field
        assert exception.value == invalid_value
        assert exception.details['value_type'] == value_type
    
    def test_initialization_with_inclusive_flags(self):
        """Verifica la inicialización con flags de inclusión."""
        field = "score"
        invalid_value = 0
        reason = "El puntaje debe ser mayor que 0"
        min_value = 0
        max_value = 100
        min_inclusive = False
        max_inclusive = True
        
        exception = RangeValidationError(
            field=field,
            value=invalid_value
        )
        exception.add_detail('reason', reason)
        exception.add_detail('min_value', min_value)
        exception.add_detail('max_value', max_value)
        exception.add_detail('min_inclusive', min_inclusive)
        exception.add_detail('max_inclusive', max_inclusive)
        
        assert exception.field == field
        assert exception.value == invalid_value
        assert exception.details['min_inclusive'] == min_inclusive
        assert exception.details['max_inclusive'] == max_inclusive


class TestLengthValidationError:
    """Tests para LengthValidationError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica de LengthValidationError."""
        field = "password"
        value = "123"
        reason = "Longitud inválida"
        
        exception = LengthValidationError(field=field, value=value)
        exception.add_detail('reason', reason)
        
        assert field in exception.message
        assert exception.error_code == ErrorCode.LENGTH_VALIDATION_ERROR
        assert isinstance(exception, ValidationError)
    
    def test_initialization_with_string_length(self):
        """Verifica la inicialización con longitud de string."""
        field = "password"
        invalid_value = "123"
        reason = "Contraseña muy corta"
        actual_length = 3
        min_length = 8
        max_length = 50
        
        exception = LengthValidationError(
            field=field,
            value=invalid_value
        )
        exception.add_detail('reason', reason)
        exception.add_detail('actual_length', actual_length)
        exception.add_detail('min_length', min_length)
        exception.add_detail('max_length', max_length)
        
        assert exception.field == field
        assert exception.value == invalid_value
        assert exception.details['actual_length'] == actual_length
        assert exception.details['min_length'] == min_length
        assert exception.details['max_length'] == max_length
    
    def test_initialization_with_collection_length(self):
        """Verifica la inicialización con longitud de colección."""
        field = "items"
        invalid_value = [1, 2, 3, 4, 5, 6]
        reason = "Demasiados elementos"
        actual_length = 6
        max_length = 5
        value_type = "list"
        
        exception = LengthValidationError(
            field=field,
            value=invalid_value
        )
        exception.add_detail('reason', reason)
        exception.add_detail('actual_length', actual_length)
        exception.add_detail('max_length', max_length)
        exception.add_detail('value_type', value_type)
        
        assert exception.field == field
        assert exception.value == invalid_value
        assert exception.details['value_type'] == value_type
    
    def test_initialization_with_field_name(self):
        """Verifica la inicialización con nombre de campo."""
        field = "username"
        invalid_value = "very_long_username_that_exceeds_limit"
        reason = "Nombre de usuario muy largo"
        actual_length = len(invalid_value)
        max_length = 20
        
        exception = LengthValidationError(
            field=field,
            value=invalid_value
        )
        exception.add_detail('reason', reason)
        exception.add_detail('actual_length', actual_length)
        exception.add_detail('max_length', max_length)
        
        assert exception.field == field
        assert exception.value == invalid_value


class TestRequiredFieldError:
    """Tests para RequiredFieldError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica de RequiredFieldError."""
        field = "email"
        reason = "Campo requerido faltante"
        
        exception = RequiredFieldError(field=field)
        
        assert field in exception.message
        assert exception.error_code == ErrorCode.REQUIRED_FIELD_ERROR
        assert isinstance(exception, ValidationError)
    
    def test_initialization_with_field_name(self):
        """Verifica la inicialización con nombre de campo."""
        field = "email"
        reason = "El email es requerido"
        
        exception = RequiredFieldError(field=field)
        
        assert exception.field == field
    
    def test_initialization_with_field_type(self):
        """Verifica la inicialización con tipo de campo."""
        field = "birth_date"
        reason = "Campo requerido faltante"
        field_type = "date"
        
        exception = RequiredFieldError(field=field)
        exception.add_detail('field_type', field_type)
        
        assert exception.field == field
        assert exception.details['field_type'] == field_type
    
    def test_initialization_with_context_info(self):
        """Verifica la inicialización con información de contexto."""
        field = "username"
        reason = "Campo requerido para creación de usuario"
        field_type = "string"
        context_info = "Formulario de registro de usuario"
        
        exception = RequiredFieldError(field=field)
        exception.add_detail('field_type', field_type)
        exception.add_detail('context_info', context_info)
        
        assert exception.field == field
        assert exception.details['context_info'] == context_info
    
    def test_initialization_with_missing_fields_list(self):
        """Verifica la inicialización con lista de campos faltantes."""
        field = "multiple_fields"
        reason = "Múltiples campos requeridos faltantes"
        missing_fields = ["email", "password", "username"]
        
        exception = RequiredFieldError(field=field)
        exception.add_detail('missing_fields', missing_fields)
        
        assert exception.field == field
        assert exception.details['missing_fields'] == missing_fields


class TestValidationExceptionHierarchy:
    """Tests para verificar la jerarquía de excepciones de validación."""
    
    @pytest.mark.parametrize("exception_class,init_args", [
        (PydanticValidationError, {"pydantic_errors": []}),
        (DateValidationError, {"field": "test", "value": "invalid"}),
        (TimeValidationError, {"field": "test", "value": "invalid"}),
        (DateTimeValidationError, {"field": "test", "value": "invalid"}),
        (FormatValidationError, {"field": "test", "value": "invalid"}),
        (RangeValidationError, {"field": "test", "value": "invalid"}),
        (LengthValidationError, {"field": "test", "value": "invalid"}),
        (RequiredFieldError, {"field": "test"}),
    ])
    def test_inheritance_hierarchy(self, exception_class, init_args):
        """Verifica que todas las excepciones hereden de ValidationError."""
        exception = exception_class(**init_args)
        
        assert isinstance(exception, ValidationError)
        assert isinstance(exception, Exception)
    
    def test_exception_error_codes(self):
        """Verifica que cada excepción tenga el código de error correcto."""
        test_cases = [
            (PydanticValidationError, ErrorCode.PYDANTIC_VALIDATION_ERROR, {"pydantic_errors": []}),
            (DateValidationError, ErrorCode.DATE_VALIDATION_ERROR, {"field": "test", "value": "invalid"}),
            (TimeValidationError, ErrorCode.TIME_VALIDATION_ERROR, {"field": "test", "value": "invalid"}),
            (DateTimeValidationError, ErrorCode.DATETIME_VALIDATION_ERROR, {"field": "test", "value": "invalid"}),
            (FormatValidationError, ErrorCode.FORMAT_VALIDATION_ERROR, {"field": "test", "value": "invalid"}),
            (RangeValidationError, ErrorCode.RANGE_VALIDATION_ERROR, {"field": "test", "value": "invalid"}),
            (LengthValidationError, ErrorCode.LENGTH_VALIDATION_ERROR, {"field": "test", "value": "invalid"}),
            (RequiredFieldError, ErrorCode.REQUIRED_FIELD_ERROR, {"field": "test"}),
        ]
        
        for exception_class, expected_code, init_args in test_cases:
            exception = exception_class(**init_args)
            assert exception.error_code == expected_code


class TestValidationExceptionSerialization:
    """Tests para verificar la serialización de excepciones de validación."""
    
    def test_pydantic_validation_error_serialization(self, exception_helper):
        """Verifica la serialización de PydanticValidationError."""
        exception = PydanticValidationError(
            pydantic_errors=[{'field': 'test', 'error': 'Invalid'}]
        )
        exception.add_detail('model_name', 'TestModel')
        exception.add_detail('input_data', {'test': 'invalid'})
        
        exception_helper.assert_exception_serialization(exception)
    
    def test_date_validation_error_serialization(self, exception_helper):
        """Verifica la serialización de DateValidationError."""
        exception = DateValidationError(
            field="test_date",
            value="2024-12-31"
        )
        exception.add_detail('reason', 'Fecha fuera de rango')
        exception.add_detail('min_date', date(2020, 1, 1).isoformat())
        exception.add_detail('max_date', date(2025, 12, 31).isoformat())
        
        exception_helper.assert_exception_serialization(exception)
    
    def test_range_validation_error_serialization(self, exception_helper):
        """Verifica la serialización de RangeValidationError."""
        exception = RangeValidationError(
            field="percentage",
            value=150
        )
        exception.add_detail('min_value', 0)
        exception.add_detail('max_value', 100)
        exception.add_detail('value_type', 'percentage')
        exception.add_detail('min_inclusive', True)
        exception.add_detail('max_inclusive', True)
        
        exception_helper.assert_exception_serialization(exception)