# src/planificador/utils/date_examples.py

"""
Ejemplos de uso de la configuración de fechas con Pendulum.

Este archivo demuestra cómo utilizar las funciones de date_utils.py
y cómo configurar las fechas en la aplicación.
"""

from datetime import datetime, date
import pendulum
from .date_utils import (
    get_current_time,
    get_current_date,
    add_business_days,
    subtract_business_days,
    format_date,
    format_datetime,
    parse_date,
    parse_datetime,
    is_business_day,
    calculate_business_days,
    get_week_range,
    get_month_range,
    get_quarter_range,
    get_year_range,
    calculate_duration,
    is_work_hours,
    get_timezone_info,
    convert_timezone,
    get_date_config
)
from ..config.config import get_settings
from loguru import logger


def ejemplo_configuracion_basica():
    """
    Ejemplo de cómo acceder a la configuración de fechas.
    """
    print("=== Configuración de Fechas ===")
    
    # Obtener configuración actual
    config = get_date_config()
    settings = get_settings()
    
    print(f"Zona horaria por defecto: {config.default_timezone}")
    print(f"Idioma: {config.locale}")
    print(f"Formato de fecha: {config.default_date_format}")
    print(f"Formato de fecha y hora: {config.default_datetime_format}")
    print(f"Días laborables: {config.business_days}")
    print(f"Horario laboral: {config.work_start_time} - {config.work_end_time}")
    print(f"Días festivos: {config.fixed_holidays[:3]}...")  # Primeros 3
    print()


def ejemplo_fechas_actuales():
    """
    Ejemplo de obtención de fechas y horas actuales.
    """
    print("=== Fechas y Horas Actuales ===")
    
    # Hora actual en zona horaria por defecto
    now = get_current_time()
    print(f"Hora actual: {now}")
    
    # Hora actual en UTC
    now_utc = get_current_time('UTC')
    print(f"Hora actual UTC: {now_utc}")
    
    # Fecha actual
    today = get_current_date()
    print(f"Fecha actual: {today}")
    
    # Fecha actual en otra zona horaria
    today_ny = get_current_date('America/New_York')
    print(f"Fecha en Nueva York: {today_ny}")
    print()


def ejemplo_formateo_fechas():
    """
    Ejemplo de formateo de fechas y horas.
    """
    print("=== Formateo de Fechas ===")
    
    fecha = pendulum.parse('2024-01-15')
    fecha_hora = pendulum.parse('2024-01-15 14:30:00')
    
    # Formateo con configuración por defecto
    print(f"Fecha formateada: {format_date(fecha)}")
    print(f"Fecha y hora formateada: {format_datetime(fecha_hora)}")
    
    # Formateo personalizado
    print(f"Fecha personalizada: {format_date(fecha, 'dddd, D [de] MMMM [de] YYYY')}")
    print(f"Hora personalizada: {format_datetime(fecha_hora, 'DD/MM/YYYY [a las] HH:mm')}")
    
    # Formateo en inglés
    print(f"Fecha en inglés: {format_date(fecha, locale='en')}")
    print()


def ejemplo_parseo_fechas():
    """
    Ejemplo de parseo de fechas desde strings.
    """
    print("=== Parseo de Fechas ===")
    
    # Parseo de fechas
    fecha1 = parse_date('15/01/2024')
    fecha2 = parse_date('2024-01-15')
    print(f"Fecha parseada 1: {fecha1}")
    print(f"Fecha parseada 2: {fecha2}")
    
    # Parseo de fechas y horas
    fecha_hora1 = parse_datetime('15/01/2024 14:30')
    fecha_hora2 = parse_datetime('2024-01-15T14:30:00')
    print(f"Fecha y hora parseada 1: {fecha_hora1}")
    print(f"Fecha y hora parseada 2: {fecha_hora2}")
    print()


def ejemplo_dias_laborables():
    """
    Ejemplo de trabajo con días laborables.
    """
    print("=== Días Laborables ===")
    
    fecha = pendulum.parse('2024-01-15')  # Lunes
    
    # Verificar si es día laborable
    print(f"¿{fecha.format('dddd DD/MM/YYYY')} es día laborable? {is_business_day(fecha)}")
    
    # Agregar días laborables
    fecha_futura = add_business_days(fecha, 5)
    print(f"5 días laborables después: {fecha_futura.format('dddd DD/MM/YYYY')}")
    
    # Restar días laborables
    fecha_pasada = subtract_business_days(fecha, 3)
    print(f"3 días laborables antes: {fecha_pasada.format('dddd DD/MM/YYYY')}")
    
    # Calcular días laborables entre fechas
    inicio = pendulum.parse('2024-01-01')
    fin = pendulum.parse('2024-01-31')
    dias_laborables = calculate_business_days(inicio, fin)
    print(f"Días laborables en enero 2024: {dias_laborables}")
    print()


def ejemplo_rangos_fechas():
    """
    Ejemplo de obtención de rangos de fechas.
    """
    print("=== Rangos de Fechas ===")
    
    fecha = pendulum.parse('2024-01-15')
    
    # Rango de la semana
    inicio_semana, fin_semana = get_week_range(fecha)
    print(f"Semana: {inicio_semana.format('DD/MM')} - {fin_semana.format('DD/MM/YYYY')}")
    
    # Rango del mes
    inicio_mes, fin_mes = get_month_range(fecha)
    print(f"Mes: {inicio_mes.format('DD/MM')} - {fin_mes.format('DD/MM/YYYY')}")
    
    # Rango del trimestre
    inicio_trimestre, fin_trimestre = get_quarter_range(fecha)
    print(f"Trimestre: {inicio_trimestre.format('DD/MM')} - {fin_trimestre.format('DD/MM/YYYY')}")
    
    # Rango del año
    inicio_año, fin_año = get_year_range(fecha)
    print(f"Año: {inicio_año.format('DD/MM')} - {fin_año.format('DD/MM/YYYY')}")
    print()


def ejemplo_duraciones():
    """
    Ejemplo de cálculo de duraciones.
    """
    print("=== Cálculo de Duraciones ===")
    
    inicio = pendulum.parse('2024-01-01 09:00:00')
    fin = pendulum.parse('2024-01-15 17:30:00')
    
    duracion = calculate_duration(inicio, fin)
    print(f"Duración total: {duracion}")
    print(f"Días: {duracion.days}")
    print(f"Horas totales: {duracion.total_seconds() / 3600:.1f}")
    print()


def ejemplo_horario_laboral():
    """
    Ejemplo de verificación de horario laboral.
    """
    print("=== Horario Laboral ===")
    
    # Diferentes horas del día
    horas_prueba = [
        '2024-01-15 08:30:00',  # Antes del horario
        '2024-01-15 10:00:00',  # Durante el horario
        '2024-01-15 14:30:00',  # Durante el horario
        '2024-01-15 19:00:00',  # Después del horario
    ]
    
    for hora_str in horas_prueba:
        hora = pendulum.parse(hora_str)
        en_horario = is_work_hours(hora)
        print(f"{hora.format('HH:mm')}: {'✓' if en_horario else '✗'} {'En horario' if en_horario else 'Fuera de horario'}")
    print()


def ejemplo_zonas_horarias():
    """
    Ejemplo de trabajo con zonas horarias.
    """
    print("=== Zonas Horarias ===")
    
    # Hora actual en Santiago
    santiago = get_current_time('America/Santiago')
    print(f"Santiago: {santiago.format('HH:mm DD/MM/YYYY')}")
    
    # Convertir a otras zonas horarias
    nueva_york = convert_timezone(santiago, 'America/New_York')
    madrid = convert_timezone(santiago, 'Europe/Madrid')
    
    print(f"Nueva York: {nueva_york.format('HH:mm DD/MM/YYYY')}")
    print(f"Madrid: {madrid.format('HH:mm DD/MM/YYYY')}")
    
    # Información de zona horaria
    info_santiago = get_timezone_info('America/Santiago')
    print(f"Información Santiago: {info_santiago['name']}, UTC{info_santiago['offset']}")
    print()


def ejemplo_completo():
    """
    Ejecuta todos los ejemplos de uso.
    """
    print("🕐 EJEMPLOS DE USO - CONFIGURACIÓN DE FECHAS CON PENDULUM\n")
    
    try:
        ejemplo_configuracion_basica()
        ejemplo_fechas_actuales()
        ejemplo_formateo_fechas()
        ejemplo_parseo_fechas()
        ejemplo_dias_laborables()
        ejemplo_rangos_fechas()
        ejemplo_duraciones()
        ejemplo_horario_laboral()
        ejemplo_zonas_horarias()
        
        print("✅ Todos los ejemplos ejecutados correctamente")
        
    except Exception as e:
        logger.error(f"Error en ejemplos: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    ejemplo_completo()