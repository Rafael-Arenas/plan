# src/planificador/utils/date_utils.py

"""
Utilidades para manejo de fechas y tiempo usando Pendulum.

Este módulo proporciona una interfaz unificada para todas las operaciones
relacionadas con fechas y tiempo en la aplicación, utilizando Pendulum
como biblioteca base para un manejo más robusto y preciso de fechas.

Funciones principales:
    - Obtención de fechas y tiempos actuales
    - Formateo y parsing de fechas
    - Cálculos de rangos temporales
    - Manejo de días laborables
    - Conversión de zonas horarias
    - Configuración centralizada de fechas

Ejemplos:
    >>> from planificador.utils.date_utils import get_current_date, format_date
    >>> fecha_actual = get_current_date()
    >>> fecha_formateada = format_date(fecha_actual, 'DD/MM/YYYY')
"""

from typing import Optional, Tuple, List, Union, Dict, Any
from datetime import date, datetime, time
from enum import Enum
import pendulum
from pendulum import DateTime, Date, Duration
from loguru import logger

from ..config.config import get_settings
from ..exceptions import (
    ValidationError,
    ConfigurationError,
    create_configuration_error
)


class DateFormat(str, Enum):
    """Formatos de fecha predefinidos para la aplicación."""
    
    # Formatos de fecha
    ISO_DATE = "YYYY-MM-DD"  # 2024-01-15
    EUROPEAN_DATE = "DD/MM/YYYY"  # 15/01/2024
    US_DATE = "MM/DD/YYYY"  # 01/15/2024
    SPANISH_DATE = "DD-MM-YYYY"  # 15-01-2024
    READABLE_DATE = "DD [de] MMMM [de] YYYY"  # 15 de enero de 2024
    SHORT_DATE = "DD/MM/YY"  # 15/01/24
    
    # Formatos de fecha y hora
    ISO_DATETIME = "YYYY-MM-DD HH:mm:ss"  # 2024-01-15 14:30:00
    EUROPEAN_DATETIME = "DD/MM/YYYY HH:mm"  # 15/01/2024 14:30
    READABLE_DATETIME = "DD [de] MMMM [de] YYYY [a las] HH:mm"  # 15 de enero de 2024 a las 14:30
    TIMESTAMP = "YYYY-MM-DD HH:mm:ss.SSS"  # 2024-01-15 14:30:00.123
    
    # Formatos de tiempo
    TIME_24H = "HH:mm"  # 14:30
    TIME_12H = "hh:mm A"  # 02:30 PM
    TIME_SECONDS = "HH:mm:ss"  # 14:30:00


class WeekDay(int, Enum):
    """Días de la semana (1=Lunes, 7=Domingo)."""
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


def _get_date_config():
    """Obtiene la configuración de fechas desde la configuración global."""
    try:
        settings = get_settings()
        if not hasattr(settings, 'dates') or settings.dates is None:
            logger.error("Configuración de fechas no encontrada en settings")
            raise ConfigurationError(
                message="Configuración de fechas no disponible",
                config_key="dates",
                config_value=None
            )
        return settings.dates
    except ConfigurationError:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener configuración de fechas: {e}")
        raise create_configuration_error(
            message="Error al acceder a configuración de fechas",
            config_key="dates",
            original_error=e
        )


def get_current_time(timezone: Optional[str] = None) -> DateTime:
    """
    Obtiene la fecha y hora actual.
    
    Args:
        timezone: Zona horaria específica. Si es None, usa la configurada por defecto.
        
    Returns:
        DateTime: Fecha y hora actual en la zona horaria especificada.
        
    Examples:
        >>> now = get_current_time()
        >>> now_utc = get_current_time('UTC')
    """
    try:
        tz = timezone or _get_date_config().default_timezone
        current = pendulum.now(tz)
        logger.debug(f"Obtenida fecha/hora actual: {current} (timezone: {tz})")
        return current
    except ConfigurationError:
        # Re-lanzar errores de configuración
        raise
    except Exception as e:
        logger.error(f"Error al obtener fecha/hora actual con timezone {timezone}: {e}")
        # Intentar fallback a UTC
        try:
            fallback = pendulum.now('UTC')
            logger.warning(f"Usando UTC como fallback: {fallback}")
            return fallback
        except Exception as fallback_error:
            logger.error(f"Error en fallback UTC: {fallback_error}")
            raise ValidationError(
                message=f"Error al obtener fecha/hora actual: {e}",
                field="timezone",
                value=timezone
            )


def get_current_date(timezone: Optional[str] = None) -> Date:
    """
    Obtiene la fecha actual (sin hora).
    
    Args:
        timezone: Zona horaria específica. Si es None, usa la configurada por defecto.
        
    Returns:
        Date: Fecha actual en la zona horaria especificada.
        
    Examples:
        >>> today = get_current_date()
        >>> today_utc = get_current_date('UTC')
    """
    return get_current_time(timezone).date()


def get_relative_date(
    base_date: Optional[Union[DateTime, Date, date]] = None,
    days: int = 0,
    weeks: int = 0,
    months: int = 0,
    years: int = 0,
    timezone: Optional[str] = None
) -> Date:
    """
    Obtiene una fecha relativa a una fecha base.
    
    Args:
        base_date: Fecha base. Si es None, usa la fecha actual.
        days: Días a añadir/restar.
        weeks: Semanas a añadir/restar.
        months: Meses a añadir/restar.
        years: Años a añadir/restar.
        timezone: Zona horaria para la fecha base si es None.
        
    Returns:
        Date: Fecha resultante.
        
    Examples:
        >>> mañana = get_relative_date(days=1)
        >>> hace_una_semana = get_relative_date(weeks=-1)
        >>> el_mes_que_viene = get_relative_date(months=1)
    """
    if base_date is None:
        base = get_current_date(timezone)
    elif isinstance(base_date, date) and not isinstance(base_date, DateTime):
        base = pendulum.parse(base_date.isoformat()).date()
    elif isinstance(base_date, DateTime):
        base = base_date.date()
    else:
        base = base_date
    
    try:
        # Convertir a DateTime para hacer los cálculos
        base_dt = pendulum.parse(base.isoformat())
        result_dt = base_dt.add(years=years, months=months, weeks=weeks, days=days)
        result = result_dt.date()
        
        logger.debug(
            f"Fecha relativa calculada: {base} + {years}y {months}m {weeks}w {days}d = {result}"
        )
        return result
    except Exception as e:
        logger.error(f"Error al calcular fecha relativa: {e}")
        raise ValidationError(f"Error en cálculo de fecha relativa: {e}")


def format_date(
    date_obj: Optional[Union[DateTime, Date, date]],
    format_str: Optional[Union[DateFormat, str]] = None,
    locale: Optional[str] = None
) -> str:
    """
    Formatea una fecha según el formato especificado.
    
    Args:
        date_obj: Fecha a formatear. Si es None, retorna cadena vacía.
        format_str: Formato de salida. Si es None, usa el formato por defecto.
        locale: Idioma para el formateo. Si es None, usa el configurado por defecto.
        
    Returns:
        str: Fecha formateada, o cadena vacía si date_obj es None.
        
    Examples:
        >>> fecha = get_current_date()
        >>> format_date(fecha, DateFormat.READABLE_DATE)
        '15 de enero de 2024'
        >>> format_date(None)
        ''
    """
    if date_obj is None:
        return ""
    
    try:
        fmt = format_str or _get_date_config().default_date_format
        loc = locale or _get_date_config().locale
        
        # Convertir a objeto Pendulum si es necesario
        if isinstance(date_obj, date) and not isinstance(date_obj, DateTime):
            pendulum_date = pendulum.parse(date_obj.isoformat())
        elif isinstance(date_obj, DateTime):
            pendulum_date = date_obj
        else:
            pendulum_date = date_obj
        
        # Aplicar locale
        pendulum_date = pendulum_date.in_locale(loc)
        
        # Formatear
        if isinstance(fmt, DateFormat):
            formatted = pendulum_date.format(fmt.value)
        else:
            formatted = pendulum_date.format(fmt)
        
        logger.debug(f"Fecha formateada: {date_obj} -> {formatted} (formato: {fmt}, locale: {loc})")
        return formatted
    except ConfigurationError:
        # Re-lanzar errores de configuración
        raise
    except Exception as e:
        logger.error(f"Error al formatear fecha {date_obj}: {e}")
        # Fallback a formato ISO
        try:
            return str(date_obj)
        except Exception:
            logger.error(f"Error en fallback de formateo para {date_obj}")
            raise ValidationError(
                message=f"Error al formatear fecha: {e}",
                field="date_obj",
                value=str(date_obj) if date_obj else None
            )


def format_datetime(
    datetime_obj: Union[DateTime, datetime],
    format_str: Optional[Union[DateFormat, str]] = None,
    locale: Optional[str] = None
) -> str:
    """
    Formatea una fecha y hora según el formato especificado.
    
    Args:
        datetime_obj: Fecha y hora a formatear.
        format_str: Formato de salida. Si es None, usa el formato por defecto.
        locale: Idioma para el formateo. Si es None, usa el configurado por defecto.
        
    Returns:
        str: Fecha y hora formateada.
        
    Examples:
        >>> ahora = get_current_time()
        >>> format_datetime(ahora, DateFormat.READABLE_DATETIME)
        '15 de enero de 2024 a las 14:30'
    """
    fmt = format_str or _get_date_config().default_datetime_format
    loc = locale or _get_date_config().locale
    
    try:
        # Convertir a objeto Pendulum si es necesario
        if isinstance(datetime_obj, datetime) and not isinstance(datetime_obj, DateTime):
            pendulum_dt = pendulum.instance(datetime_obj)
        else:
            pendulum_dt = datetime_obj
        
        # Aplicar locale
        pendulum_dt = pendulum_dt.in_locale(loc)
        
        # Formatear
        if isinstance(fmt, DateFormat):
            formatted = pendulum_dt.format(fmt.value)
        else:
            formatted = pendulum_dt.format(fmt)
        
        logger.debug(f"Fecha/hora formateada: {datetime_obj} -> {formatted} (formato: {fmt}, locale: {loc})")
        return formatted
    except Exception as e:
        logger.error(f"Error al formatear fecha/hora: {e}")
        # Fallback a formato ISO
        return str(datetime_obj)


def parse_date(date_str: str, format_str: Optional[str] = None) -> Date:
    """
    Convierte una cadena de texto en un objeto Date.
    
    Args:
        date_str: Cadena de fecha a convertir.
        format_str: Formato esperado. Si es None, intenta detectar automáticamente.
        
    Returns:
        Date: Objeto Date resultante.
        
    Raises:
        ValidationError: Si la cadena no puede ser parseada.
    
    Examples:
        >>> fecha = parse_date('15/01/2024', 'DD/MM/YYYY')
        >>> fecha_auto = parse_date('2024-01-15')  # Detección automática
    """
    if not date_str or not isinstance(date_str, str):
        raise ValidationError(
            message="La cadena de fecha no puede estar vacía",
            field="date_str",
            value=date_str
        )
    
    try:
        if format_str:
            parsed = pendulum.from_format(date_str, format_str)
        else:
            parsed = pendulum.parse(date_str)
        
        result = parsed.date()
        logger.debug(f"Fecha parseada: '{date_str}' -> {result} (formato: {format_str or 'auto'})")
        return result
    except (ValueError, TypeError) as e:
        logger.error(f"Error de formato al parsear fecha '{date_str}': {e}")
        raise ValidationError(
            message=f"Formato de fecha inválido: {date_str}",
            field="date_str",
            value=date_str
        )
    except Exception as e:
        logger.error(f"Error inesperado al parsear fecha '{date_str}': {e}")
        raise ValidationError(
            message=f"Error al parsear fecha: {e}",
            field="date_str",
            value=date_str
        )


def parse_datetime(datetime_str: str, format_str: Optional[str] = None) -> DateTime:
    """
    Convierte una cadena de texto en un objeto DateTime.
    
    Args:
        datetime_str: Cadena de fecha y hora a convertir.
        format_str: Formato esperado. Si es None, intenta detectar automáticamente.
        
    Returns:
        DateTime: Objeto DateTime resultante.
        
    Raises:
        ValidationError: Si la cadena no puede ser parseada.
        
    Examples:
        >>> dt = parse_datetime('15/01/2024 14:30', 'DD/MM/YYYY HH:mm')
        >>> dt_auto = parse_datetime('2024-01-15T14:30:00')  # Detección automática
    """
    if not datetime_str or not isinstance(datetime_str, str):
        raise ValidationError(
            message="La cadena de fecha/hora no puede estar vacía",
            field="datetime_str",
            value=datetime_str
        )
    
    try:
        if format_str:
            parsed = pendulum.from_format(datetime_str, format_str)
        else:
            parsed = pendulum.parse(datetime_str)
        
        logger.debug(f"Fecha/hora parseada: '{datetime_str}' -> {parsed} (formato: {format_str or 'auto'})")
        return parsed
    except (ValueError, TypeError) as e:
        logger.error(f"Error de formato al parsear fecha/hora '{datetime_str}': {e}")
        raise ValidationError(
            message=f"Formato de fecha/hora inválido: {datetime_str}",
            field="datetime_str",
            value=datetime_str
        )
    except Exception as e:
        logger.error(f"Error inesperado al parsear fecha/hora '{datetime_str}': {e}")
        raise ValidationError(
            message=f"Error al parsear fecha/hora: {e}",
            field="datetime_str",
            value=datetime_str
        )


def is_business_day(
    date_obj: Union[DateTime, Date, date],
    custom_business_days: Optional[List[int]] = None,
    custom_holidays: Optional[List[str]] = None
) -> bool:
    """
    Verifica si una fecha es un día laborable.
    
    Args:
        date_obj: Fecha a verificar.
        custom_business_days: Lista personalizada de días laborables.
        custom_holidays: Lista personalizada de días festivos.
        
    Returns:
        bool: True si es día laborable, False en caso contrario.
        
    Examples:
        >>> is_business_day(get_current_date())
        True
        >>> is_business_day(parse_date('2024-01-01'))  # Año Nuevo
        False
    """
    business_days = custom_business_days or _get_date_config().business_days
    holidays = custom_holidays or _get_date_config().fixed_holidays
    
    try:
        # Convertir a objeto Pendulum si es necesario
        if isinstance(date_obj, date) and not isinstance(date_obj, DateTime):
            pendulum_date = pendulum.parse(date_obj.isoformat())
        elif isinstance(date_obj, DateTime):
            pendulum_date = date_obj
        else:
            pendulum_date = date_obj
        
        # Verificar día de la semana
        # Pendulum: 0=Lunes, 6=Domingo
        # DateSettings: 1=Lunes, 7=Domingo
        pendulum_weekday = pendulum_date.weekday()  # 0-6
        config_weekday = pendulum_weekday + 1  # Convertir a 1-7
        if config_weekday not in business_days:
            return False
        
        # Verificar días festivos fijos
        date_str = pendulum_date.format('MM-DD')
        if date_str in holidays:
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error al verificar día laborable: {e}")
        return False


# Funciones wrapper para compatibilidad con repositorios
def get_current_week_range(
    week_start: WeekDay = WeekDay.MONDAY
) -> Tuple[Date, Date]:
    """
    Obtiene el rango de fechas de la semana actual.
    
    Args:
        week_start: Día de inicio de la semana.
        
    Returns:
        Tuple[Date, Date]: Tupla con (fecha_inicio, fecha_fin) de la semana actual.
        
    Examples:
        >>> inicio, fin = get_current_week_range()
    """
    return get_week_range(get_current_date(), week_start)


def get_current_month_range() -> Tuple[Date, Date]:
    """
    Obtiene el rango de fechas del mes actual.
    
    Returns:
        Tuple[Date, Date]: Tupla con (primer_día, último_día) del mes actual.
        
    Examples:
        >>> inicio, fin = get_current_month_range()
    """
    return get_month_range(get_current_date())


def get_business_days_in_range(
    start_date: Union[DateTime, Date, date],
    end_date: Union[DateTime, Date, date],
    custom_business_days: Optional[List[int]] = None,
    custom_holidays: Optional[List[str]] = None
) -> int:
    """
    Calcula el número de días laborables en un rango (alias de get_business_days).
    
    Args:
        start_date: Fecha de inicio.
        end_date: Fecha de fin.
        custom_business_days: Lista personalizada de días laborables.
        custom_holidays: Lista personalizada de días festivos.
        
    Returns:
        int: Número de días laborables en el rango.
        
    Examples:
        >>> inicio = parse_date('2024-01-15')
        >>> fin = parse_date('2024-01-19')
        >>> get_business_days_in_range(inicio, fin)
        5
    """
    return get_business_days(start_date, end_date, include_end=False)


def calculate_business_days_between(
    start_date: Union[DateTime, Date, date],
    end_date: Union[DateTime, Date, date],
    custom_business_days: Optional[List[int]] = None,
    custom_holidays: Optional[List[str]] = None
) -> int:
    """
    Calcula el número de días laborables entre dos fechas (alias de get_business_days).
    
    Args:
        start_date: Fecha de inicio.
        end_date: Fecha de fin.
        custom_business_days: Lista personalizada de días laborables.
        custom_holidays: Lista personalizada de días festivos.
        
    Returns:
        int: Número de días laborables entre las fechas.
        
    Examples:
        >>> inicio = parse_date('2024-01-15')
        >>> fin = parse_date('2024-01-19')
        >>> calculate_business_days_between(inicio, fin)
        5
    """
    return get_business_days(start_date, end_date, include_end=False)


def get_work_hours_range(
    date_obj: Optional[Union[DateTime, Date, date]] = None,
    custom_start_time: Optional[time] = None,
    custom_end_time: Optional[time] = None
) -> Tuple[DateTime, DateTime]:
    """
    Obtiene el rango de horas laborables para una fecha específica.
    
    Args:
        date_obj: Fecha de referencia. Si es None, usa la fecha actual.
        custom_start_time: Hora de inicio personalizada.
        custom_end_time: Hora de fin personalizada.
        
    Returns:
        Tuple[DateTime, DateTime]: Tupla con (inicio_laboral, fin_laboral).
        
    Examples:
        >>> inicio, fin = get_work_hours_range()
        >>> inicio, fin = get_work_hours_range(parse_date('2024-01-15'))
    """
    if date_obj is None:
        date_obj = get_current_date()
    
    config = _get_date_config()
    start_time = custom_start_time or config.work_start_time
    end_time = custom_end_time or config.work_end_time
    
    try:
        # Convertir a objeto Pendulum
        if isinstance(date_obj, date) and not isinstance(date_obj, DateTime):
            pendulum_date = pendulum.parse(date_obj.isoformat())
        else:
            pendulum_date = date_obj
        
        # Crear DateTime para inicio y fin del día laboral
        work_start = pendulum_date.replace(
            hour=start_time.hour,
            minute=start_time.minute,
            second=start_time.second,
            microsecond=0
        )
        work_end = pendulum_date.replace(
            hour=end_time.hour,
            minute=end_time.minute,
            second=end_time.second,
            microsecond=0
        )
        
        logger.debug(f"Rango horario laboral: {work_start} a {work_end}")
        return work_start, work_end
    except Exception as e:
        logger.error(f"Error al calcular rango horario laboral: {e}")
        raise ValidationError(f"Error en cálculo de rango horario laboral: {e}")


def format_date_for_display(
    date_obj: Union[DateTime, Date, date],
    format_type: str = 'default',
    locale: Optional[str] = None
) -> str:
    """
    Formatea una fecha para mostrar en la interfaz de usuario.
    
    Args:
        date_obj: Fecha a formatear.
        format_type: Tipo de formato ('default', 'short', 'long', 'readable').
        locale: Idioma para el formateo.
        
    Returns:
        str: Fecha formateada para mostrar.
        
    Examples:
        >>> fecha = get_current_date()
        >>> format_date_for_display(fecha, 'readable')
        '15 de enero de 2024'
    """
    format_map = {
        'default': DateFormat.EUROPEAN_DATE,
        'short': DateFormat.SHORT_DATE,
        'long': DateFormat.ISO_DATE,
        'readable': DateFormat.READABLE_DATE
    }
    
    format_str = format_map.get(format_type, DateFormat.EUROPEAN_DATE)
    return format_date(date_obj, format_str, locale)


def get_business_days(
    start_date: Union[DateTime, Date, date],
    end_date: Union[DateTime, Date, date],
    include_end: bool = True
) -> int:
    """
    Calcula el número de días laborables entre dos fechas.
    
    Args:
        start_date: Fecha de inicio.
        end_date: Fecha de fin.
        include_end: Si incluir la fecha de fin en el cálculo.
        
    Returns:
        int: Número de días laborables.
        
    Examples:
        >>> inicio = parse_date('2024-01-15')  # Lunes
        >>> fin = parse_date('2024-01-19')     # Viernes
        >>> get_business_days(inicio, fin)
        5
    """
    try:
        # Convertir a objetos Pendulum
        if isinstance(start_date, date) and not isinstance(start_date, DateTime):
            start = pendulum.parse(start_date.isoformat())
        else:
            start = start_date
            
        if isinstance(end_date, date) and not isinstance(end_date, DateTime):
            end = pendulum.parse(end_date.isoformat())
        else:
            end = end_date
        
        # Asegurar que start <= end
        if start > end:
            start, end = end, start
        
        business_days_count = 0
        current = start
        
        # Determinar la fecha límite según include_end
        end_limit = end if include_end else end.subtract(days=1)
        
        while current <= end_limit:
            if is_business_day(current.date()):
                business_days_count += 1
            current = current.add(days=1)
        
        logger.debug(
            f"Días laborables calculados: {start.date()} a {end.date()} = {business_days_count} días"
        )
        return business_days_count
    except Exception as e:
        logger.error(f"Error al calcular días laborables: {e}")
        return 0


def get_week_range(
    date_obj: Optional[Union[DateTime, Date, date]] = None,
    week_start: WeekDay = WeekDay.MONDAY
) -> Tuple[Date, Date]:
    """
    Obtiene el rango de fechas de la semana que contiene la fecha dada.
    
    Args:
        date_obj: Fecha de referencia. Si es None, usa la fecha actual.
        week_start: Día de inicio de la semana.
        
    Returns:
        Tuple[Date, Date]: Tupla con (fecha_inicio, fecha_fin) de la semana.
        
    Examples:
        >>> inicio, fin = get_week_range()
        >>> inicio, fin = get_week_range(parse_date('2024-01-15'), WeekDay.SUNDAY)
    """
    if date_obj is None:
        date_obj = get_current_date()
    
    try:
        # Convertir a objeto Pendulum
        if isinstance(date_obj, date) and not isinstance(date_obj, DateTime):
            pendulum_date = pendulum.parse(date_obj.isoformat())
        else:
            pendulum_date = date_obj
        
        # Calcular inicio de semana
        days_since_start = (pendulum_date.weekday() - week_start.value) % 7
        week_start_date = pendulum_date.subtract(days=days_since_start).date()
        week_end_date = week_start_date.add(days=6)
        
        logger.debug(f"Rango de semana: {week_start_date} a {week_end_date}")
        return week_start_date, week_end_date
    except Exception as e:
        logger.error(f"Error al calcular rango de semana: {e}")
        raise ValidationError(f"Error en cálculo de rango de semana: {e}")


def get_month_range(
    date_obj: Optional[Union[DateTime, Date, date]] = None
) -> Tuple[Date, Date]:
    """
    Obtiene el rango de fechas del mes que contiene la fecha dada.
    
    Args:
        date_obj: Fecha de referencia. Si es None, usa la fecha actual.
        
    Returns:
        Tuple[Date, Date]: Tupla con (primer_día, último_día) del mes.
        
    Examples:
        >>> inicio, fin = get_month_range()
        >>> inicio, fin = get_month_range(parse_date('2024-01-15'))
    """
    if date_obj is None:
        date_obj = get_current_date()
    
    try:
        # Convertir a objeto Pendulum
        if isinstance(date_obj, date) and not isinstance(date_obj, DateTime):
            pendulum_date = pendulum.parse(date_obj.isoformat())
        else:
            pendulum_date = date_obj
        
        month_start = pendulum_date.start_of('month').date()
        month_end = pendulum_date.end_of('month').date()
        
        logger.debug(f"Rango de mes: {month_start} a {month_end}")
        return month_start, month_end
    except Exception as e:
        logger.error(f"Error al calcular rango de mes: {e}")
        raise ValidationError(f"Error en cálculo de rango de mes: {e}")


def get_quarter_range(
    date_obj: Optional[Union[DateTime, Date, date]] = None
) -> Tuple[Date, Date]:
    """
    Obtiene el rango de fechas del trimestre que contiene la fecha dada.
    
    Args:
        date_obj: Fecha de referencia. Si es None, usa la fecha actual.
        
    Returns:
        Tuple[Date, Date]: Tupla con (primer_día, último_día) del trimestre.
        
    Examples:
        >>> inicio, fin = get_quarter_range()
        >>> inicio, fin = get_quarter_range(parse_date('2024-01-15'))
    """
    if date_obj is None:
        date_obj = get_current_date()
    
    try:
        # Convertir a objeto Pendulum
        if isinstance(date_obj, date) and not isinstance(date_obj, DateTime):
            pendulum_date = pendulum.parse(date_obj.isoformat())
        else:
            pendulum_date = date_obj
        
        quarter_start = pendulum_date.start_of('quarter').date()
        quarter_end = pendulum_date.end_of('quarter').date()
        
        logger.debug(f"Rango de trimestre: {quarter_start} a {quarter_end}")
        return quarter_start, quarter_end
    except Exception as e:
        logger.error(f"Error al calcular rango de trimestre: {e}")
        raise ValidationError(f"Error en cálculo de rango de trimestre: {e}")


def get_year_range(
    date_obj: Optional[Union[DateTime, Date, date]] = None
) -> Tuple[Date, Date]:
    """
    Obtiene el rango de fechas del año que contiene la fecha dada.
    
    Args:
        date_obj: Fecha de referencia. Si es None, usa la fecha actual.
        
    Returns:
        Tuple[Date, Date]: Tupla con (primer_día, último_día) del año.
        
    Examples:
        >>> inicio, fin = get_year_range()
        >>> inicio, fin = get_year_range(parse_date('2024-01-15'))
    """
    if date_obj is None:
        date_obj = get_current_date()
    
    try:
        # Convertir a objeto Pendulum
        if isinstance(date_obj, date) and not isinstance(date_obj, DateTime):
            pendulum_date = pendulum.parse(date_obj.isoformat())
        else:
            pendulum_date = date_obj
        
        year_start = pendulum_date.start_of('year').date()
        year_end = pendulum_date.end_of('year').date()
        
        logger.debug(f"Rango de año: {year_start} a {year_end}")
        return year_start, year_end
    except Exception as e:
        logger.error(f"Error al calcular rango de año: {e}")
        raise ValidationError(f"Error en cálculo de rango de año: {e}")


def calculate_duration(
    start: Union[DateTime, Date, date],
    end: Union[DateTime, Date, date],
    unit: str = 'days'
) -> float:
    """
    Calcula la duración entre dos fechas en la unidad especificada.
    
    Args:
        start: Fecha/hora de inicio.
        end: Fecha/hora de fin.
        unit: Unidad de medida ('days', 'hours', 'minutes', 'seconds', 'weeks', 'months', 'years').
        
    Returns:
        float: Duración en la unidad especificada.
        
    Examples:
        >>> inicio = parse_date('2024-01-01')
        >>> fin = parse_date('2024-01-15')
        >>> calculate_duration(inicio, fin, 'days')
        14.0
    """
    try:
        # Convertir a objetos Pendulum
        if isinstance(start, date) and not isinstance(start, DateTime):
            start_dt = pendulum.parse(start.isoformat())
        else:
            start_dt = start
            
        if isinstance(end, date) and not isinstance(end, DateTime):
            end_dt = pendulum.parse(end.isoformat())
        else:
            end_dt = end
        
        # Calcular diferencia
        diff = end_dt - start_dt
        
        # Convertir a la unidad solicitada
        if unit == 'days':
            result = diff.total_days()
        elif unit == 'hours':
            result = diff.total_hours()
        elif unit == 'minutes':
            result = diff.total_minutes()
        elif unit == 'seconds':
            result = diff.total_seconds()
        elif unit == 'weeks':
            result = diff.total_days() / 7
        elif unit == 'months':
            result = diff.total_days() / 30.44  # Promedio de días por mes
        elif unit == 'years':
            result = diff.total_days() / 365.25  # Considerando años bisiestos
        else:
            raise ValidationError(f"Unidad no soportada: {unit}")
        
        logger.debug(f"Duración calculada: {start} a {end} = {result} {unit}")
        return result
    except Exception as e:
        logger.error(f"Error al calcular duración: {e}")
        raise ValidationError(f"Error en cálculo de duración: {e}")


def get_timezone_info(timezone: Optional[str] = None) -> Dict[str, Any]:
    """
    Obtiene información sobre una zona horaria.
    
    Args:
        timezone: Zona horaria a consultar. Si es None, usa la configurada por defecto.
        
    Returns:
        Dict[str, Any]: Información de la zona horaria, o diccionario vacío si es inválida.
        
    Examples:
        >>> info = get_timezone_info('Europe/Madrid')
        >>> print(info['name'])  # 'Europe/Madrid'
        >>> get_timezone_info('Invalid/Timezone')
        {}
    """
    tz = timezone or _get_date_config().default_timezone
    
    try:
        now = pendulum.now(tz)
        
        info = {
            'name': tz,
            'abbreviation': now.timezone_name,
            'offset': now.offset_hours,
            'offset_string': now.format('Z'),
            'is_dst': now.is_dst(),
            'current_time': now.isoformat()
        }
        
        logger.debug(f"Información de zona horaria obtenida: {info}")
        return info
    except Exception as e:
        logger.error(f"Error al obtener información de zona horaria: {e}")
        return {}


def convert_timezone(
    datetime_obj: Union[DateTime, datetime],
    target_timezone: str,
    source_timezone: Optional[str] = None
) -> DateTime:
    """
    Convierte una fecha/hora de una zona horaria a otra.
    
    Args:
        datetime_obj: Fecha/hora a convertir.
        target_timezone: Zona horaria de destino.
        source_timezone: Zona horaria de origen. Si es None, usa la del objeto o la por defecto.
        
    Returns:
        DateTime: Fecha/hora convertida a la zona horaria de destino.
        
    Raises:
        ValidationError: Si hay errores en la conversión de zona horaria.
        
    Examples:
        >>> madrid_time = get_current_time('Europe/Madrid')
        >>> utc_time = convert_timezone(madrid_time, 'UTC')
    """
    if datetime_obj is None:
        raise ValidationError(
            message="La fecha/hora no puede ser None",
            field="datetime_obj",
            value=None
        )
    
    if not target_timezone or not isinstance(target_timezone, str):
        raise ValidationError(
            message="La zona horaria de destino debe ser una cadena válida",
            field="target_timezone",
            value=target_timezone
        )
    
    try:
        # Convertir a objeto Pendulum si es necesario
        if isinstance(datetime_obj, datetime) and not isinstance(datetime_obj, DateTime):
            if source_timezone:
                pendulum_dt = pendulum.instance(datetime_obj, tz=source_timezone)
            else:
                pendulum_dt = pendulum.instance(datetime_obj)
        else:
            pendulum_dt = datetime_obj
        
        # Si no tiene zona horaria, asignar la de origen
        if source_timezone and not pendulum_dt.timezone:
            pendulum_dt = pendulum_dt.in_timezone(source_timezone)
        
        # Convertir a la zona horaria de destino
        converted = pendulum_dt.in_timezone(target_timezone)
        
        logger.debug(
            f"Conversión de zona horaria: {pendulum_dt} -> {converted} "
            f"({source_timezone or 'auto'} -> {target_timezone})"
        )
        return converted
    except (ValueError, TypeError) as e:
        logger.error(f"Error de zona horaria inválida '{target_timezone}': {e}")
        raise ValidationError(
            message=f"Zona horaria inválida: {target_timezone}",
            field="target_timezone",
            value=target_timezone
        )
    except Exception as e:
        logger.error(f"Error inesperado al convertir zona horaria: {e}")
        raise ValidationError(
            message=f"Error en conversión de zona horaria: {e}",
            field="target_timezone",
            value=target_timezone
        )


def add_business_days(
    start_date: Union[DateTime, Date, date],
    business_days: int,
    custom_business_days: Optional[List[int]] = None,
    custom_holidays: Optional[List[str]] = None
) -> Date:
    """
    Añade días laborables a una fecha.
    
    Args:
        start_date: Fecha de inicio.
        business_days: Número de días laborables a añadir.
        custom_business_days: Lista personalizada de días laborables.
        custom_holidays: Lista personalizada de días festivos.
        
    Returns:
        Date: Fecha resultante después de añadir los días laborables.
        
    Examples:
        >>> inicio = parse_date('2024-01-15')  # Lunes
        >>> resultado = add_business_days(inicio, 5)  # Añadir 5 días laborables
    """
    try:
        # Convertir a objeto Pendulum
        if isinstance(start_date, date) and not isinstance(start_date, DateTime):
            current = pendulum.parse(start_date.isoformat())
        else:
            current = start_date
        
        days_added = 0
        
        while days_added < business_days:
            current = current.add(days=1)
            if is_business_day(current.date(), custom_business_days, custom_holidays):
                days_added += 1
        
        result = current.date()
        logger.debug(f"Días laborables añadidos: {start_date} + {business_days} = {result}")
        return result
    except Exception as e:
        logger.error(f"Error al añadir días laborables: {e}")
        raise ValidationError(f"Error al añadir días laborables: {e}")


def calculate_business_days(
    start_date: Union[DateTime, Date, date],
    end_date: Union[DateTime, Date, date],
    custom_business_days: Optional[List[int]] = None,
    custom_holidays: Optional[List[str]] = None
) -> int:
    """
    Calcula el número de días laborables entre dos fechas (alias de get_business_days).
    
    Args:
        start_date: Fecha de inicio.
        end_date: Fecha de fin.
        custom_business_days: Lista personalizada de días laborables.
        custom_holidays: Lista personalizada de días festivos.
        
    Returns:
        int: Número de días laborables.
        
    Examples:
        >>> inicio = parse_date('2024-01-15')  # Lunes
        >>> fin = parse_date('2024-01-19')     # Viernes
        >>> calculate_business_days(inicio, fin)
        5
    """
    return get_business_days(start_date, end_date, include_end=False)


def is_work_hours(
    datetime_obj: Union[DateTime, datetime],
    custom_start_time: Optional[time] = None,
    custom_end_time: Optional[time] = None
) -> bool:
    """
    Verifica si una fecha/hora está dentro del horario laboral.
    
    Args:
        datetime_obj: Fecha y hora a verificar.
        custom_start_time: Hora de inicio personalizada.
        custom_end_time: Hora de fin personalizada.
        
    Returns:
        bool: True si está dentro del horario laboral.
        
    Examples:
        >>> ahora = get_current_time()
        >>> is_work_hours(ahora)
        True
    """
    config = _get_date_config()
    start_time = custom_start_time or config.work_start_time
    end_time = custom_end_time or config.work_end_time
    
    try:
        # Convertir a objeto Pendulum si es necesario
        if isinstance(datetime_obj, datetime) and not isinstance(datetime_obj, DateTime):
            pendulum_dt = pendulum.instance(datetime_obj)
        else:
            pendulum_dt = datetime_obj
        
        current_time = pendulum_dt.time()
        
        # Verificar si está dentro del horario
        is_within_hours = start_time <= current_time <= end_time
        
        logger.debug(
            f"Verificación horario laboral: {current_time} "
            f"({start_time}-{end_time}) = {is_within_hours}"
        )
        return is_within_hours
    except Exception as e:
        logger.error(f"Error al verificar horario laboral: {e}")
        return False


# Funciones de conveniencia para configuración
def get_date_config():
    """
    Obtiene la configuración actual de fechas.
    
    Returns:
        DateSettings: Configuración actual de fechas.
        
    Raises:
        ConfigurationError: Si hay problemas con la configuración.
    """
    try:
        config = _get_date_config()
        logger.debug(f"Configuración de fechas obtenida: {config}")
        return config
    except ConfigurationError:
        # Re-lanzar errores de configuración
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener configuración de fechas: {e}")
        raise create_configuration_error(
            message="Error al acceder a configuración de fechas",
            config_key="date_config",
            original_error=e
        )


# Funciones de validación
def validate_date_range(
    start_date: Union[DateTime, Date, date],
    end_date: Union[DateTime, Date, date],
    allow_equal: bool = True
) -> bool:
    """
    Valida que un rango de fechas sea válido.
    
    Args:
        start_date: Fecha de inicio.
        end_date: Fecha de fin.
        allow_equal: Si permitir que las fechas sean iguales.
        
    Returns:
        bool: True si el rango es válido.
        
    Raises:
        ValidationError: Si hay errores en la validación de fechas.
        
    Examples:
        >>> validate_date_range(parse_date('2024-01-01'), parse_date('2024-01-15'))
        True
    """
    if start_date is None or end_date is None:
        raise ValidationError(
            message="Las fechas de inicio y fin no pueden ser None",
            field="date_range",
            value=f"{start_date} - {end_date}"
        )
    
    try:
        # Convertir a objetos comparables
        if isinstance(start_date, date) and not isinstance(start_date, DateTime):
            start = pendulum.parse(start_date.isoformat())
        else:
            start = start_date
            
        if isinstance(end_date, date) and not isinstance(end_date, DateTime):
            end = pendulum.parse(end_date.isoformat())
        else:
            end = end_date
        
        if allow_equal:
            is_valid = start <= end
        else:
            is_valid = start < end
        
        logger.debug(
            f"Validación de rango: {start_date} - {end_date} = {is_valid} "
            f"(allow_equal: {allow_equal})"
        )
        return is_valid
    except (ValueError, TypeError) as e:
        logger.error(f"Error de tipo/valor al validar rango de fechas: {e}")
        raise ValidationError(
            message=f"Fechas inválidas en el rango: {e}",
            field="date_range",
            value=f"{start_date} - {end_date}"
        )
    except Exception as e:
        logger.error(f"Error inesperado al validar rango de fechas: {e}")
        raise ValidationError(
            message=f"Error en validación de rango de fechas: {e}",
            field="date_range",
            value=f"{start_date} - {end_date}"
        )