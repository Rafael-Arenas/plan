# src/planificador/utils/__init__.py

"""
Módulo de utilidades para el sistema Planificador AkGroup.

Este paquete contiene funciones auxiliares y utilidades que son utilizadas
a lo largo de toda la aplicación para tareas comunes como manejo de fechas,
validaciones, formateo de datos y constantes del sistema.

Módulos:
    date_utils: Utilidades para manejo de fechas con Pendulum
    validators: Validaciones personalizadas
    formatters: Formateo de datos
    constants: Constantes del sistema
    helpers: Funciones auxiliares generales
"""

from .date_utils import (
    get_current_time,
    get_current_date,
    get_relative_date,
    format_date,
    format_datetime,
    parse_date,
    parse_datetime,
    get_business_days,
    is_business_day,
    add_business_days,
    calculate_business_days,
    is_work_hours,
    get_week_range,
    get_month_range,
    get_quarter_range,
    get_year_range,
    calculate_duration,
    get_timezone_info,
    convert_timezone,
    get_date_config,
    # Funciones wrapper para compatibilidad
    get_current_week_range,
    get_current_month_range,
    get_business_days_in_range,
    calculate_business_days_between,
    get_work_hours_range,
    format_date_for_display,
    DateFormat,
    WeekDay
)

__all__ = [
    # Funciones de fecha y tiempo
    "get_current_time",
    "get_current_date",
    "get_relative_date",
    "format_date",
    "format_datetime",
    "parse_date",
    "parse_datetime",
    "get_business_days",
    "is_business_day",
    "add_business_days",
    "calculate_business_days",
    "is_work_hours",
    "get_week_range",
    "get_month_range",
    "get_quarter_range",
    "get_year_range",
    "calculate_duration",
    "get_timezone_info",
    "convert_timezone",
    "get_date_config",
    # Funciones wrapper para compatibilidad
    "get_current_week_range",
    "get_current_month_range",
    "get_business_days_in_range",
    "calculate_business_days_between",
    "get_work_hours_range",
    "format_date_for_display",
    "DateFormat",
    "WeekDay",
]