# src/planificador/tests/unit/test_exceptions/test_validation_helpers.py

"""
Tests para funciones helper de validación.

Este módulo contiene tests para todas las funciones de validación
y creación de excepciones de validación disponibles en el sistema.

Funciones probadas:
- validate_email_format
- validate_phone_format
- validate_date_range
- validate_time_range
- validate_datetime_range
- validate_text_length
- validate_numeric_range
- validate_required_field
- convert_pydantic_error
"""

import pytest
from datetime import date, time, datetime
from typing import Any, Dict, List

from planificador.exceptions.validation import (
    # Funciones de validación
    validate_email_format,
    validate_phone_format,
    validate_date_range,
    validate_time_range,
    validate_datetime_range,
    validate_text_length,
    validate_numeric_range,
    validate_required_field,
    convert_pydantic_error,
    
    # Excepciones para verificar tipos
    PydanticValidationError,
    DateValidationError,
    TimeValidationError,
    DateTimeValidationError,
    FormatValidationError,
    RangeValidationError,
    LengthValidationError,
    RequiredFieldError,
)


class TestValidateEmailFormat:
    """Tests para validate_email_format."""
    
    def test_valid_emails(self):
        """Test con emails válidos."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@numbers.com",
            "a@b.co"
        ]
        
        for email in valid_emails:
            # No debe lanzar excepción
            validate_email_format(email)
    
    def test_invalid_emails(self):
        """Test con emails inválidos."""
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            "user..name@domain.com",
            "",
            "user name@domain.com"  # espacios
        ]
        
        for email in invalid_emails:
            with pytest.raises(FormatValidationError) as exc_info:
                validate_email_format(email)
            
            assert "email" in exc_info.value.message
            assert email == exc_info.value.details.get("invalid_value")
    
    def test_custom_field_name(self):
        """Test con nombre de campo personalizado."""
        with pytest.raises(FormatValidationError) as exc_info:
            validate_email_format("invalid", field="correo_electronico")
        
        assert "correo_electronico" in exc_info.value.message
        assert "invalid" == exc_info.value.details.get("invalid_value")


class TestValidatePhoneFormat:
    """Tests para validate_phone_format."""
    
    def test_valid_phones(self):
        """Test con teléfonos válidos."""
        valid_phones = [
            "+1234567890",
            "123-456-7890",
            "(123) 456-7890",
            "123 456 7890",
            "1234567890"
        ]
        
        for phone in valid_phones:
            # No debe lanzar excepción
            validate_phone_format(phone)
    
    def test_invalid_phones(self):
        """Test con teléfonos inválidos."""
        invalid_phones = [
            "123",  # muy corto
            "abcd1234567890",  # letras
            "123456789012345678",  # muy largo
            "",
            "++123456789"  # doble +
        ]
        
        for phone in invalid_phones:
            with pytest.raises(FormatValidationError) as exc_info:
                validate_phone_format(phone)
            
            assert "teléfono" in exc_info.value.message
            assert phone == exc_info.value.details.get("invalid_value")


class TestValidateDateRange:
    """Tests para validate_date_range."""
    
    def test_valid_date_range(self):
        """Test con rango de fechas válido."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        
        # No debe lanzar excepción
        validate_date_range(start_date, end_date)
    
    def test_invalid_date_range(self):
        """Test con rango de fechas inválido."""
        start_date = date(2024, 12, 31)
        end_date = date(2024, 1, 1)
        
        with pytest.raises(DateValidationError) as exc_info:
            validate_date_range(start_date, end_date)
        
        assert "inicio" in exc_info.value.message
        assert "anterior" in exc_info.value.message
    
    def test_same_dates(self):
        """Test con fechas iguales (inválido)."""
        same_date = date(2024, 6, 15)
        
        with pytest.raises(DateValidationError):
            validate_date_range(same_date, same_date)
    
    def test_custom_field_names(self):
        """Test con nombres de campo personalizados."""
        start_date = date(2024, 12, 31)
        end_date = date(2024, 1, 1)
        
        with pytest.raises(DateValidationError) as exc_info:
            validate_date_range(
                start_date, end_date, 
                start_field="fecha_inicio", 
                end_field="fecha_fin"
            )
        
        assert "fecha_inicio-fecha_fin" in exc_info.value.details.get("field", "")


class TestValidateTimeRange:
    """Tests para validate_time_range."""
    
    def test_valid_time_range(self):
        """Test con rango de tiempo válido."""
        start_time = time(9, 0)
        end_time = time(17, 0)
        
        # No debe lanzar excepción
        validate_time_range(start_time, end_time)
    
    def test_invalid_time_range(self):
        """Test con rango de tiempo inválido."""
        start_time = time(17, 0)
        end_time = time(9, 0)
        
        with pytest.raises(TimeValidationError) as exc_info:
            validate_time_range(start_time, end_time)
        
        assert "inicio" in exc_info.value.message
        assert "anterior" in exc_info.value.message
    
    def test_same_times(self):
        """Test con tiempos iguales (inválido)."""
        same_time = time(12, 0)
        
        with pytest.raises(TimeValidationError):
            validate_time_range(same_time, same_time)


class TestValidateDatetimeRange:
    """Tests para validate_datetime_range."""
    
    def test_valid_datetime_range(self):
        """Test con rango de datetime válido."""
        start_dt = datetime(2024, 1, 1, 9, 0)
        end_dt = datetime(2024, 1, 1, 17, 0)
        
        # No debe lanzar excepción
        validate_datetime_range(start_dt, end_dt)
    
    def test_invalid_datetime_range(self):
        """Test con rango de datetime inválido."""
        start_dt = datetime(2024, 1, 1, 17, 0)
        end_dt = datetime(2024, 1, 1, 9, 0)
        
        with pytest.raises(DateTimeValidationError) as exc_info:
            validate_datetime_range(start_dt, end_dt)
        
        assert "inicio" in exc_info.value.message
        assert "anterior" in exc_info.value.message


class TestValidateTextLength:
    """Tests para validate_text_length."""
    
    def test_valid_length(self):
        """Test con longitud válida."""
        text = "Texto de prueba"
        
        # No debe lanzar excepción
        validate_text_length(text, "campo", min_length=5, max_length=20)
    
    def test_text_too_short(self):
        """Test con texto muy corto."""
        text = "Hi"
        
        with pytest.raises(LengthValidationError) as exc_info:
            validate_text_length(text, "campo", min_length=5)
        
        assert "al menos 5" in exc_info.value.message
        assert exc_info.value.details.get("current_length") == 2
    
    def test_text_too_long(self):
        """Test con texto muy largo."""
        text = "Este es un texto muy largo que excede el límite"
        
        with pytest.raises(LengthValidationError) as exc_info:
            validate_text_length(text, "campo", max_length=10)
        
        assert "máximo 10" in exc_info.value.message
        assert exc_info.value.details.get("current_length") == len(text)
    
    def test_empty_text(self):
        """Test con texto vacío."""
        with pytest.raises(LengthValidationError):
            validate_text_length("", "campo", min_length=1)
    
    def test_none_text(self):
        """Test con texto None."""
        with pytest.raises(LengthValidationError):
            validate_text_length(None, "campo", min_length=1)


class TestValidateNumericRange:
    """Tests para validate_numeric_range."""
    
    def test_valid_range_int(self):
        """Test con entero en rango válido."""
        # No debe lanzar excepción
        validate_numeric_range(5, "campo", min_value=1, max_value=10)
    
    def test_valid_range_float(self):
        """Test con float en rango válido."""
        # No debe lanzar excepción
        validate_numeric_range(5.5, "campo", min_value=1.0, max_value=10.0)
    
    def test_value_too_small(self):
        """Test con valor muy pequeño."""
        with pytest.raises(RangeValidationError) as exc_info:
            validate_numeric_range(0, "campo", min_value=1)
        
        assert "mayor o igual a 1" in exc_info.value.message
        assert exc_info.value.details.get("min_value") == 1
    
    def test_value_too_large(self):
        """Test con valor muy grande."""
        with pytest.raises(RangeValidationError) as exc_info:
            validate_numeric_range(15, "campo", max_value=10)
        
        assert "menor o igual a 10" in exc_info.value.message
        assert exc_info.value.details.get("max_value") == 10
    
    def test_boundary_values(self):
        """Test con valores en los límites."""
        # Valores exactos en los límites deben ser válidos
        validate_numeric_range(1, "campo", min_value=1, max_value=10)
        validate_numeric_range(10, "campo", min_value=1, max_value=10)


class TestValidateRequiredField:
    """Tests para validate_required_field."""
    
    def test_valid_values(self):
        """Test con valores válidos."""
        valid_values = [
            "texto",
            123,
            [1, 2, 3],
            {"key": "value"},
            True,
            0  # cero es válido
        ]
        
        for value in valid_values:
            # No debe lanzar excepción
            validate_required_field(value, "campo")
    
    def test_invalid_values(self):
        """Test con valores inválidos."""
        invalid_values = [
            None,
            "",
            "   ",  # solo espacios
            "\t\n"  # solo whitespace
        ]
        
        for value in invalid_values:
            with pytest.raises(RequiredFieldError) as exc_info:
                validate_required_field(value, "campo_requerido")
            
            assert "campo_requerido" in exc_info.value.message
            assert "requerido" in exc_info.value.message


class TestConvertPydanticError:
    """Tests para convert_pydantic_error."""
    
    def test_single_error(self):
        """Test con un solo error de Pydantic."""
        pydantic_errors = [
            {
                "loc": ("field_name",),
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
        
        exception = convert_pydantic_error(pydantic_errors)
        
        assert isinstance(exception, PydanticValidationError)
        assert "field_name" in exception.message
        assert "field required" in exception.message
        assert exception.details.get("error_count") == 1
    
    def test_multiple_errors(self):
        """Test con múltiples errores de Pydantic."""
        pydantic_errors = [
            {
                "loc": ("field1",),
                "msg": "field required",
                "type": "value_error.missing"
            },
            {
                "loc": ("field2",),
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt"
            }
        ]
        
        exception = convert_pydantic_error(pydantic_errors)
        
        assert isinstance(exception, PydanticValidationError)
        assert exception.details.get("error_count") == 2
        assert exception.details.get("pydantic_errors") == pydantic_errors
    
    def test_nested_field_error(self):
        """Test con error en campo anidado."""
        pydantic_errors = [
            {
                "loc": ("user", "profile", "email"),
                "msg": "invalid email format",
                "type": "value_error.email"
            }
        ]
        
        exception = convert_pydantic_error(pydantic_errors)
        
        assert "user.profile.email" in exception.message
        assert "invalid email format" in exception.message
    
    def test_empty_errors_list(self):
        """Test con lista vacía de errores."""
        exception = convert_pydantic_error([])
        
        assert isinstance(exception, PydanticValidationError)
        assert exception.details.get("error_count") == 0
    
    def test_error_serialization(self):
        """Test de serialización de errores."""
        pydantic_errors = [
            {
                "loc": ("test_field",),
                "msg": "test error",
                "type": "test_type"
            }
        ]
        
        exception = convert_pydantic_error(pydantic_errors)
        serialized = exception.to_dict()
        
        assert "pydantic_errors" in serialized["details"]
        assert "error_count" in serialized["details"]
        assert serialized["details"]["error_count"] == 1