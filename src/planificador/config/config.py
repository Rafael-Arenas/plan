# src/planificador/config/config.py

from typing import Optional, List
from datetime import time
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
import os
from pathlib import Path
from loguru import logger

# Importar excepciones de infraestructura
from ..exceptions.infrastructure import (
    ConfigurationError,
    create_configuration_error
)


class DatabaseSettings(BaseSettings):
    """
    Configuraciones específicas de la base de datos.
    """
    url: str = Field(
        default="sqlite+aiosqlite:///./planificador.db",
        description="URL de conexión a la base de datos"
    )
    echo: bool = Field(
        default=False,
        description="Habilita logging de queries SQL"
    )
    pool_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Tamaño del pool de conexiones"
    )
    max_overflow: int = Field(
        default=30,
        ge=0,
        le=100,
        description="Conexiones adicionales permitidas"
    )
    pool_recycle: int = Field(
        default=3600,
        ge=300,
        description="Tiempo en segundos para reciclar conexiones"
    )
    pool_pre_ping: bool = Field(
        default=True,
        description="Verifica conexiones antes de usar"
    )
    
    @field_validator('url', mode='before')
    def validate_database_url(cls, v):
        """Valida que la URL de la base de datos tenga el formato correcto."""
        try:
            if not v:
                raise create_configuration_error(
                    message="La URL de la base de datos no puede estar vacía",
                    config_key="database_url",
                    config_file="config.py",
                    expected_value="URL válida de base de datos",
                    actual_value=v or "None"
                )
            
            # Validaciones específicas para diferentes tipos de base de datos
            if v.startswith('sqlite'):
                if '+aiosqlite' not in v:
                    raise create_configuration_error(
                        message="Para SQLite asíncrono, usa 'sqlite+aiosqlite:///' en la URL",
                        config_key="database_url",
                        config_file="config.py",
                        expected_value="sqlite+aiosqlite:///path/to/db.db",
                        actual_value=v
                    )
            elif v.startswith('postgresql'):
                if '+asyncpg' not in v:
                    raise create_configuration_error(
                        message="Para PostgreSQL asíncrono, usa 'postgresql+asyncpg://' en la URL",
                        config_key="database_url",
                        config_file="config.py",
                        expected_value="postgresql+asyncpg://user:pass@host:port/db",
                        actual_value=v
                    )
            elif v.startswith('mysql'):
                if '+aiomysql' not in v:
                    raise create_configuration_error(
                        message="Para MySQL asíncrono, usa 'mysql+aiomysql://' en la URL",
                        config_key="database_url",
                        config_file="config.py",
                        expected_value="mysql+aiomysql://user:pass@host:port/db",
                        actual_value=v
                    )
            
            logger.debug(f"URL de base de datos validada: {v}")
            return v
        except ConfigurationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado al validar URL de base de datos: {e}")
            raise create_configuration_error(
                message=f"Error inesperado al validar URL de base de datos: {e}",
                config_key="database_url",
                config_file="config.py",
                original_error=e
            )


class DateSettings(BaseSettings):
    """
    Configuraciones específicas para el manejo de fechas con Pendulum.
    """
    
    # Zona horaria por defecto
    default_timezone: str = Field(
        default="America/Santiago",
        description="Zona horaria por defecto para la aplicación"
    )
    
    # Idioma para formateo de fechas
    locale: str = Field(
        default="es",
        description="Idioma para el formateo de fechas (es, en, fr, etc.)"
    )
    
    # Formato de fecha por defecto
    default_date_format: str = Field(
        default="DD/MM/YYYY",
        description="Formato de fecha por defecto"
    )
    
    # Formato de fecha y hora por defecto
    default_datetime_format: str = Field(
        default="DD/MM/YYYY HH:mm",
        description="Formato de fecha y hora por defecto"
    )
    
    # Días laborables (1=Lunes, 7=Domingo)
    business_days: List[int] = Field(
        default=[1, 2, 3, 4, 5],  # Lunes a Viernes
        description="Lista de días laborables (1=Lunes, 7=Domingo)"
    )
    
    # Días festivos fijos (formato MM-DD)
    fixed_holidays: List[str] = Field(
        default=[
            "01-01",  # Año Nuevo
            "05-01",  # Día del Trabajo
            "05-21",  # Día de las Glorias Navales
            "06-29",  # San Pedro y San Pablo
            "07-16",  # Día de la Virgen del Carmen
            "08-15",  # Asunción de la Virgen
            "09-18",  # Independencia de Chile
            "09-19",  # Día de las Glorias del Ejército
            "12-25",  # Navidad
        ],
        description="Lista de días festivos fijos en formato MM-DD"
    )
    
    # Horario laboral
    work_start_hour: int = Field(
        default=9,
        ge=0,
        le=23,
        description="Hora de inicio del horario laboral (0-23)"
    )
    
    work_start_minute: int = Field(
        default=0,
        ge=0,
        le=59,
        description="Minuto de inicio del horario laboral (0-59)"
    )
    
    work_end_hour: int = Field(
        default=18,
        ge=0,
        le=23,
        description="Hora de fin del horario laboral (0-23)"
    )
    
    work_end_minute: int = Field(
        default=0,
        ge=0,
        le=59,
        description="Minuto de fin del horario laboral (0-59)"
    )
    
    @property
    def work_start_time(self) -> time:
        """Hora de inicio del horario laboral como objeto time."""
        return time(self.work_start_hour, self.work_start_minute)
    
    @property
    def work_end_time(self) -> time:
        """Hora de fin del horario laboral como objeto time."""
        return time(self.work_end_hour, self.work_end_minute)
    
    @field_validator('business_days')
    def validate_business_days(cls, v):
        """Valida que los días laborables estén en el rango correcto."""
        try:
            if not all(1 <= day <= 7 for day in v):
                invalid_days = [day for day in v if not (1 <= day <= 7)]
                raise create_configuration_error(
                    message=f"Días laborables inválidos. Deben estar entre 1-7 (1=Lunes, 7=Domingo)",
                    config_key="business_days",
                    config_file="config.py",
                    expected_value="Lista de enteros entre 1-7",
                    actual_value=f"Días inválidos: {invalid_days}"
                )
            logger.debug(f"Días laborables validados: {v}")
            return v
        except ConfigurationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado al validar días laborables: {e}")
            raise create_configuration_error(
                message=f"Error inesperado al validar días laborables: {e}",
                config_key="business_days",
                config_file="config.py",
                original_error=e
            )
    
    @field_validator('fixed_holidays')
    def validate_fixed_holidays(cls, v):
        """Valida el formato de los días festivos."""
        try:
            import re
            pattern = r'^\d{2}-\d{2}$'  # Exactamente MM-DD
            
            for holiday in v:
                if not re.match(pattern, holiday):
                    raise create_configuration_error(
                        message=f"Formato de fecha festiva inválido: {holiday}. Use MM-DD",
                        config_key="fixed_holidays",
                        config_file="config.py",
                        expected_value="Formato MM-DD",
                        actual_value=holiday
                    )
                
                try:
                    month, day = holiday.split('-')
                    if not (1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                        raise create_configuration_error(
                            message=f"Fecha inválida en día festivo: {holiday}. Mes debe estar entre 1-12, día entre 1-31",
                            config_key="fixed_holidays",
                            config_file="config.py",
                            expected_value="Mes: 1-12, Día: 1-31",
                            actual_value=f"Mes: {month}, Día: {day}"
                        )
                except ValueError as parse_error:
                    if "invalid literal" in str(parse_error):
                        raise create_configuration_error(
                            message=f"Formato de fecha festiva inválido: {holiday}. Use MM-DD",
                            config_key="fixed_holidays",
                            config_file="config.py",
                            expected_value="Números válidos en formato MM-DD",
                            actual_value=holiday
                        )
                    raise create_configuration_error(
                        message=f"Error al parsear día festivo: {holiday}",
                        config_key="fixed_holidays",
                        config_file="config.py",
                        original_error=parse_error
                    )
            logger.debug(f"Días festivos fijos validados: {v}")
            return v
        except ConfigurationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado al validar días festivos fijos: {e}")
            raise create_configuration_error(
                message=f"Error inesperado al validar días festivos fijos: {e}",
                config_key="fixed_holidays",
                config_file="config.py",
                original_error=e
            )
    
    @field_validator('default_timezone')
    def validate_timezone(cls, v):
        """Valida que la zona horaria sea válida."""
        try:
            import pendulum
            pendulum.now(v)
            logger.debug(f"Zona horaria validada: {v}")
            return v
        except Exception as e:
            logger.error(f"Error al validar zona horaria: {e}")
            raise create_configuration_error(
                message=f"Zona horaria inválida: {v}",
                config_key="default_timezone",
                config_file="config.py",
                expected_value="Zona horaria válida (ej: 'America/Santiago')",
                actual_value=v,
                original_error=e
            )
    
    @field_validator('locale')
    def validate_locale(cls, v):
        """Valida que el locale sea válido."""
        try:
            valid_locales = ['es', 'en', 'fr', 'de', 'it', 'pt']
            if v not in valid_locales:
                raise create_configuration_error(
                    message=f"Locale inválido. Debe ser uno de: {valid_locales}",
                    config_key="locale",
                    config_file="config.py",
                    expected_value=f"Uno de: {valid_locales}",
                    actual_value=v
                )
            logger.debug(f"Locale validado: {v}")
            return v
        except ConfigurationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado al validar locale: {e}")
            raise create_configuration_error(
                message=f"Error inesperado al validar locale: {e}",
                config_key="locale",
                config_file="config.py",
                original_error=e
            )


class Settings(BaseSettings):
    """
    Configuraciones principales de la aplicación.
    Carga configuraciones desde variables de entorno o valores por defecto.
    """
    
    # Configuraciones generales de la aplicación
    app_name: str = Field(
        default="Planificador AkGroup",
        description="Nombre de la aplicación"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Versión de la aplicación"
    )
    debug_mode: bool = Field(
        default=False,
        description="Modo de depuración"
    )
    
    # Configuraciones de la base de datos
    database_url: str = Field(
        default="sqlite+aiosqlite:///./planificador.db",
        description="URL de conexión a la base de datos"
    )
    
    # Configuraciones de fechas
    dates: DateSettings = Field(
        default_factory=DateSettings,
        description="Configuraciones para el manejo de fechas"
    )
    
    # Configuraciones de logging
    log_level: str = Field(
        default="INFO",
        description="Nivel de logging"
    )
    log_file: Optional[str] = Field(
        default=None,
        description="Archivo de log (opcional)"
    )
    
    # Configuraciones de seguridad
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Clave secreta para JWT y encriptación"
    )
    
    # Configuraciones de la API
    api_prefix: str = Field(
        default="/api/v1",
        description="Prefijo para las rutas de la API"
    )
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Orígenes permitidos para CORS"
    )
    
    # Configuraciones de archivos y directorios
    base_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent.parent,
        description="Directorio base del proyecto"
    )
    
    @property
    def logs_dir(self) -> Path:
        """Directorio para archivos de log."""
        logs_path = self.base_dir / "logs"
        logs_path.mkdir(exist_ok=True)
        return logs_path
    
    @property
    def data_dir(self) -> Path:
        """Directorio para archivos de datos."""
        data_path = self.base_dir / "data"
        data_path.mkdir(exist_ok=True)
        return data_path
    
    @property
    def temp_dir(self) -> Path:
        """Directorio para archivos temporales."""
        temp_path = self.base_dir / "temp"
        temp_path.mkdir(exist_ok=True)
        return temp_path
    
    @property
    def database_settings(self) -> DatabaseSettings:
        """Retorna configuraciones específicas de la base de datos."""
        return DatabaseSettings(
            url=self.database_url,
            echo=self.debug_mode
        )
    
    @field_validator('log_level', mode='before')
    def validate_log_level(cls, v):
        """Valida que el nivel de logging sea válido."""
        try:
            valid_levels = ['TRACE', 'DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL']
            if v.upper() not in valid_levels:
                raise create_configuration_error(
                    message=f"Nivel de log inválido: {v}. Debe ser uno de: {valid_levels}",
                    config_key="log_level",
                    config_file="config.py",
                    expected_value=f"Uno de: {valid_levels}",
                    actual_value=v
                )
            logger.debug(f"Nivel de log validado: {v.upper()}")
            return v.upper()
        except ConfigurationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado al validar nivel de log: {e}")
            raise create_configuration_error(
                message=f"Error inesperado al validar nivel de log: {e}",
                config_key="log_level",
                config_file="config.py",
                original_error=e
            )
    
    @field_validator('secret_key', mode='before')
    def validate_secret_key(cls, v):
        """Valida que la clave secreta tenga una longitud mínima."""
        try:
            if len(v) < 32:
                raise create_configuration_error(
                    message="La clave secreta debe tener al menos 32 caracteres",
                    config_key="secret_key",
                    config_file="config.py",
                    expected_value="Mínimo 32 caracteres",
                    actual_value=f"Longitud actual: {len(v)} caracteres"
                )
            logger.debug("Clave secreta validada correctamente")
            return v
        except ConfigurationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado al validar clave secreta: {e}")
            raise create_configuration_error(
                message=f"Error inesperado al validar clave secreta: {e}",
                config_key="secret_key",
                config_file="config.py",
                original_error=e
            )
    
    @field_validator('cors_origins', mode='before')
    def validate_cors_origins(cls, v):
        """Valida que los orígenes CORS sean URLs válidas."""
        try:
            if not isinstance(v, list):
                raise create_configuration_error(
                    message="cors_origins debe ser una lista",
                    config_key="cors_origins",
                    config_file="config.py",
                    expected_value="Lista de URLs",
                    actual_value=f"Tipo: {type(v).__name__}"
                )
            
            import re
            url_pattern = re.compile(
                r'^https?://'  # http:// o https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
                r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # dominio
                r'localhost|'  # localhost
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
                r'(?::\d+)?'  # puerto opcional
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            for origin in v:
                if origin != "*" and not url_pattern.match(origin):
                    raise create_configuration_error(
                        message=f"Origen CORS inválido: {origin}",
                        config_key="cors_origins",
                        config_file="config.py",
                        expected_value="URL válida o '*' para todos los orígenes",
                        actual_value=origin
                    )
            
            logger.debug(f"Orígenes CORS validados: {v}")
            return v
        except ConfigurationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado al validar orígenes CORS: {e}")
            raise create_configuration_error(
                message=f"Error inesperado al validar orígenes CORS: {e}",
                config_key="cors_origins",
                config_file="config.py",
                original_error=e
            )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "env_prefix": "PLANIFICADOR_",
        "env_nested_delimiter": "__"
    }


# Instancia global de la configuración para ser usada en toda la aplicación
settings = Settings()


# Función para obtener configuraciones (compatible con tests)
def get_settings() -> Settings:
    """
    Obtiene la instancia de configuraciones.
    Útil para dependency injection y testing.
    """
    return settings


# Función para recargar configuraciones (útil para testing)
def reload_settings() -> Settings:
    """
    Recarga las configuraciones desde las variables de entorno.
    Útil para testing o cuando se cambian variables de entorno en runtime.
    """
    global settings
    settings = Settings()
    return settings


# Función para validar configuraciones al inicio
def validate_settings() -> None:
    """
    Valida que todas las configuraciones críticas estén correctamente establecidas.
    Debe llamarse al inicio de la aplicación.
    """
    try:
        # Valida configuraciones de base de datos
        db_settings = settings.database_settings
        
        # Valida que el directorio base exista
        if not settings.base_dir.exists():
            logger.error(f"El directorio base no existe: {settings.base_dir}")
            raise create_configuration_error(
                message=f"El directorio base no existe: {settings.base_dir}",
                config_key="base_dir",
                config_file="config.py",
                expected_value="Directorio existente",
                actual_value=str(settings.base_dir)
            )
        
        # En producción, valida que la clave secreta no sea la por defecto
        if not settings.debug_mode and settings.secret_key == "your-secret-key-change-in-production":
            logger.error("Clave secreta por defecto detectada en producción")
            raise create_configuration_error(
                message="Debes cambiar la clave secreta por defecto en producción",
                config_key="secret_key",
                config_file="config.py",
                expected_value="Clave secreta personalizada",
                actual_value="Clave por defecto de desarrollo"
            )
        
        logger.info("✅ Configuraciones validadas correctamente")
        logger.info(f"📊 Base de datos: {settings.database_url}")
        logger.info(f"🔧 Modo debug: {settings.debug_mode}")
        logger.info(f"📝 Nivel de log: {settings.log_level}")
        
    except ConfigurationError:
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado en configuraciones: {e}")
        raise create_configuration_error(
            message=f"Error inesperado al validar configuraciones: {e}",
            config_key="general",
            config_file="config.py",
            original_error=e
        )