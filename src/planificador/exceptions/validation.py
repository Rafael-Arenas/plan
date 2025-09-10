# src/planificador/exceptions/validation.py

"""
Excepciones de validación para el sistema de planificación.

Este módulo define excepciones específicas para validaciones:
- Validaciones de Pydantic
- Validaciones de fechas y tiempo
- Validaciones de formato
- Validaciones de rango
- Validaciones de lógica de negocio
"""

from typing import Any, Dict, List, Optional, Union
from datetime import date, datetime, time
import re
from .base import ValidationError, ErrorCode


class PydanticValidationError(ValidationError):
    """
    Excepción para errores de validación de Pydantic.
    
    Convierte errores de Pydantic en excepciones del sistema
    con formato consistente.
    """
    
    def __init__(self, pydantic_errors: List[Dict[str, Any]], **kwargs):
        # Extraer el primer error para el mensaje principal
        first_error = pydantic_errors[0] if pydantic_errors else {}
        field = '.'.join(str(loc) for loc in first_error.get('loc', []))
        error_type = first_error.get('type', 'validation_error')
        error_msg = first_error.get('msg', 'Error de validación')
        
        message = f"Error de validación en campo '{field}': {error_msg}"
        
        super().__init__(message, field=field, **kwargs)
        self.error_code = ErrorCode.PYDANTIC_VALIDATION_ERROR
        
        # Agregar todos los errores como detalles
        self.add_detail('pydantic_errors', pydantic_errors)
        self.add_detail('error_count', len(pydantic_errors))


class DateValidationError(ValidationError):
    """
    Excepción para errores de validación de fechas.
    """
    
    def __init__(
        self, 
        field: str, 
        value: Any, 
        reason: Optional[str] = None, 
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
        **kwargs
    ):
        reason = reason or "Fecha inválida"
        message = f"Fecha inválida en campo '{field}': {reason}"
        super().__init__(message, field=field, value=value, **kwargs)
        self.error_code = ErrorCode.DATE_VALIDATION_ERROR
        
        self.add_detail('reason', reason)
        if min_date:
            self.add_detail('min_date', min_date.isoformat())
        if max_date:
            self.add_detail('max_date', max_date.isoformat())


class TimeValidationError(ValidationError):
    """
    Excepción para errores de validación de tiempo.
    """
    
    def __init__(
        self, 
        field: str, 
        value: Any, 
        reason: Optional[str] = None, 
        min_time: Optional[time] = None,
        max_time: Optional[time] = None,
        **kwargs
    ):
        reason = reason or "Hora inválida"
        message = f"Hora inválida en campo '{field}': {reason}"
        super().__init__(message, field=field, value=value, **kwargs)
        self.error_code = ErrorCode.TIME_VALIDATION_ERROR
        
        self.add_detail('reason', reason)
        if min_time:
            self.add_detail('min_time', min_time.isoformat())
        if max_time:
            self.add_detail('max_time', max_time.isoformat())


class DateTimeValidationError(ValidationError):
    """
    Excepción para errores de validación de fecha y hora.
    """
    
    def __init__(
        self, 
        field: str, 
        value: Any, 
        reason: Optional[str] = None, 
        min_datetime: Optional[datetime] = None,
        max_datetime: Optional[datetime] = None,
        **kwargs
    ):
        reason = reason or "Fecha y hora inválida"
        message = f"Fecha y hora inválida en campo '{field}': {reason}"
        super().__init__(message, field=field, value=value, **kwargs)
        self.error_code = ErrorCode.DATETIME_VALIDATION_ERROR
        
        self.add_detail('reason', reason)
        if min_datetime:
            self.add_detail('min_datetime', min_datetime.isoformat())
        if max_datetime:
            self.add_detail('max_datetime', max_datetime.isoformat())


class FormatValidationError(ValidationError):
    """
    Excepción para errores de formato (email, teléfono, etc.).
    """
    
    def __init__(
        self, 
        field: str, 
        value: Any, 
        expected_format: Optional[str] = None, 
        pattern: Optional[str] = None,
        **kwargs
    ):
        expected_format = expected_format or "formato válido"
        message = f"Formato inválido en campo '{field}': se esperaba {expected_format}"
        super().__init__(message, field=field, value=value, **kwargs)
        self.error_code = ErrorCode.FORMAT_VALIDATION_ERROR
        
        self.add_detail('expected_format', expected_format)
        if pattern:
            self.add_detail('regex_pattern', pattern)


class RangeValidationError(ValidationError):
    """
    Excepción para errores de rango (números, longitud de texto, etc.).
    """
    
    def __init__(
        self, 
        field: str, 
        value: Any, 
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        **kwargs
    ):
        if min_value is not None and max_value is not None:
            reason = f"debe estar entre {min_value} y {max_value}"
        elif min_value is not None:
            reason = f"debe ser mayor o igual a {min_value}"
        elif max_value is not None:
            reason = f"debe ser menor o igual a {max_value}"
        else:
            reason = "está fuera del rango permitido"
            
        message = f"Valor en campo '{field}' {reason}"
        super().__init__(message, field=field, value=value, **kwargs)
        self.error_code = ErrorCode.RANGE_VALIDATION_ERROR
        
        if min_value is not None:
            self.add_detail('min_value', min_value)
        if max_value is not None:
            self.add_detail('max_value', max_value)


class LengthValidationError(ValidationError):
    """
    Excepción para errores de longitud de texto.
    """
    
    def __init__(
        self, 
        field: str, 
        value: str, 
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        **kwargs
    ):
        current_length = len(value) if value else 0
        
        if min_length is not None and max_length is not None:
            reason = f"debe tener entre {min_length} y {max_length} caracteres (actual: {current_length})"
        elif min_length is not None:
            reason = f"debe tener al menos {min_length} caracteres (actual: {current_length})"
        elif max_length is not None:
            reason = f"debe tener máximo {max_length} caracteres (actual: {current_length})"
        else:
            reason = f"longitud inválida (actual: {current_length})"
            
        message = f"Texto en campo '{field}' {reason}"
        super().__init__(message, field=field, value=value, **kwargs)
        self.error_code = ErrorCode.LENGTH_VALIDATION_ERROR
        
        self.add_detail('current_length', current_length)
        if min_length is not None:
            self.add_detail('min_length', min_length)
        if max_length is not None:
            self.add_detail('max_length', max_length)


class RequiredFieldError(ValidationError):
    """
    Excepción para campos requeridos que están vacíos.
    """
    
    def __init__(self, field: str, **kwargs):
        message = f"El campo '{field}' es requerido y no puede estar vacío"
        super().__init__(message, field=field, value=None, **kwargs)
        self.error_code = ErrorCode.REQUIRED_FIELD_ERROR


class UniqueConstraintError(ValidationError):
    """
    Excepción para violaciones de restricciones de unicidad.
    """
    
    def __init__(self, field: str, value: Any, entity_type: str, **kwargs):
        message = f"El valor '{value}' para el campo '{field}' ya existe en {entity_type}"
        super().__init__(message, field=field, value=value, **kwargs)
        self.error_code = ErrorCode.UNIQUE_CONSTRAINT_ERROR
        
        self.add_detail('entity_type', entity_type)
        self.add_detail('constraint_type', 'unique')


class ForeignKeyValidationError(ValidationError):
    """
    Excepción para errores de clave foránea.
    """
    
    def __init__(
        self, 
        field: str, 
        value: Any, 
        referenced_entity: str, 
        **kwargs
    ):
        message = f"El valor '{value}' en campo '{field}' no existe en {referenced_entity}"
        super().__init__(message, field=field, value=value, **kwargs)
        self.error_code = ErrorCode.FOREIGN_KEY_VALIDATION_ERROR
        
        self.add_detail('referenced_entity', referenced_entity)
        self.add_detail('constraint_type', 'foreign_key')


class BusinessRuleValidationError(ValidationError):
    """
    Excepción para violaciones de reglas de negocio.
    """
    
    def __init__(self, rule_name: str, description: str, **kwargs):
        message = f"Violación de regla de negocio '{rule_name}': {description}"
        super().__init__(message, **kwargs)
        self.error_code = ErrorCode.BUSINESS_RULE_VALIDATION_ERROR
        
        self.add_detail('rule_name', rule_name)
        self.add_detail('rule_type', 'business_rule')


# ============================================================================
# FUNCIONES HELPER PARA VALIDACIONES COMUNES
# ============================================================================

def validate_email_format(email: str, field: str = 'email') -> None:
    """
    Valida el formato de un email.
    
    Args:
        email: Email a validar
        field: Nombre del campo (para el mensaje de error)
        
    Raises:
        FormatValidationError: Si el formato es inválido
    """
    # Validación más estricta: no permite puntos consecutivos, espacios, ni formatos inválidos
    if not email or '..' in email or ' ' in email:
        raise FormatValidationError(
            field, 
            email, 
            'formato de email válido (ejemplo@dominio.com)',
            'email_pattern'
        )
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise FormatValidationError(
            field, 
            email, 
            'formato de email válido (ejemplo@dominio.com)',
            email_pattern
        )


def validate_phone_format(phone: str, field: str = 'phone') -> None:
    """
    Valida el formato de un teléfono.
    
    Args:
        phone: Teléfono a validar
        field: Nombre del campo (para el mensaje de error)
        
    Raises:
        FormatValidationError: Si el formato es inválido
    """
    # Patrón para teléfonos (permite varios formatos)
    phone_pattern = r'^[+]?[0-9\s\-\(\)]{7,15}$'
    if not re.match(phone_pattern, phone):
        raise FormatValidationError(
            field, 
            phone, 
            'formato de teléfono válido (+123456789 o 123-456-7890)',
            phone_pattern
        )


def validate_date_range(
    start_date: date, 
    end_date: date, 
    start_field: str = 'start_date',
    end_field: str = 'end_date'
) -> None:
    """
    Valida que una fecha de inicio sea anterior a una fecha de fin.
    
    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin
        start_field: Nombre del campo de inicio
        end_field: Nombre del campo de fin
        
    Raises:
        DateValidationError: Si el rango es inválido
    """
    if start_date >= end_date:
        raise DateValidationError(
            f"{start_field}-{end_field}",
            {'start_date': start_date, 'end_date': end_date},
            f"La fecha de inicio ({start_date}) debe ser anterior a la fecha de fin ({end_date})"
        )


def validate_time_range(
    start_time: time, 
    end_time: time, 
    start_field: str = 'start_time',
    end_field: str = 'end_time'
) -> None:
    """
    Valida que una hora de inicio sea anterior a una hora de fin.
    
    Args:
        start_time: Hora de inicio
        end_time: Hora de fin
        start_field: Nombre del campo de inicio
        end_field: Nombre del campo de fin
        
    Raises:
        TimeValidationError: Si el rango es inválido
    """
    if start_time >= end_time:
        raise TimeValidationError(
            f"{start_field}-{end_field}",
            {'start_time': start_time, 'end_time': end_time},
            f"La hora de inicio ({start_time}) debe ser anterior a la hora de fin ({end_time})"
        )


def validate_datetime_range(
    start_datetime: datetime, 
    end_datetime: datetime, 
    start_field: str = 'start_datetime',
    end_field: str = 'end_datetime'
) -> None:
    """
    Valida que una fecha-hora de inicio sea anterior a una fecha-hora de fin.
    
    Args:
        start_datetime: Fecha-hora de inicio
        end_datetime: Fecha-hora de fin
        start_field: Nombre del campo de inicio
        end_field: Nombre del campo de fin
        
    Raises:
        DateTimeValidationError: Si el rango es inválido
    """
    if start_datetime >= end_datetime:
        raise DateTimeValidationError(
            f"{start_field}-{end_field}",
            {'start_datetime': start_datetime, 'end_datetime': end_datetime},
            f"La fecha-hora de inicio ({start_datetime}) debe ser anterior a la fecha-hora de fin ({end_datetime})"
        )


def validate_text_length(
    text: str, 
    field: str, 
    min_length: Optional[int] = None, 
    max_length: Optional[int] = None
) -> None:
    """
    Valida la longitud de un texto.
    
    Args:
        text: Texto a validar
        field: Nombre del campo
        min_length: Longitud mínima (opcional)
        max_length: Longitud máxima (opcional)
        
    Raises:
        LengthValidationError: Si la longitud es inválida
    """
    current_length = len(text) if text else 0
    
    if min_length is not None and current_length < min_length:
        raise LengthValidationError(field, text, min_length=min_length)
    
    if max_length is not None and current_length > max_length:
        raise LengthValidationError(field, text, max_length=max_length)


def validate_numeric_range(
    value: Union[int, float], 
    field: str, 
    min_value: Optional[Union[int, float]] = None, 
    max_value: Optional[Union[int, float]] = None
) -> None:
    """
    Valida que un valor numérico esté en un rango específico.
    
    Args:
        value: Valor a validar
        field: Nombre del campo
        min_value: Valor mínimo (opcional)
        max_value: Valor máximo (opcional)
        
    Raises:
        RangeValidationError: Si el valor está fuera del rango
    """
    if min_value is not None and value < min_value:
        raise RangeValidationError(field, value, min_value=min_value)
    
    if max_value is not None and value > max_value:
        raise RangeValidationError(field, value, max_value=max_value)


def validate_required_field(value: Any, field: str) -> None:
    """
    Valida que un campo requerido no esté vacío.
    
    Args:
        value: Valor a validar
        field: Nombre del campo
        
    Raises:
        RequiredFieldError: Si el campo está vacío
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise RequiredFieldError(field)


def convert_pydantic_error(pydantic_errors: List[Dict[str, Any]]) -> PydanticValidationError:
    """
    Convierte errores de Pydantic en excepciones del sistema.
    
    Args:
        pydantic_errors: Lista de errores de Pydantic
        
    Returns:
        Instancia de PydanticValidationError
    """
    return PydanticValidationError(pydantic_errors)