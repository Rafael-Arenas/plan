# src/planificador/exceptions/infrastructure.py

"""
Excepciones de infraestructura para el sistema de planificación.

Este módulo define excepciones relacionadas con la infraestructura del sistema,
incluyendo errores de base de datos, conexiones, configuración, servicios externos
y sistema de archivos.
"""

from typing import Any, Dict, Optional, Union
from .base import PlanificadorBaseException, ErrorCode


class InfrastructureError(PlanificadorBaseException):
    """
    Excepción base para errores de infraestructura.
    
    Esta clase sirve como base para todas las excepciones relacionadas con
    componentes de infraestructura del sistema.
    """
    
    def __init__(
        self, 
        message: str, 
        component: Optional[str] = None,
        operation: Optional[str] = None,
        original_error: Optional[Exception] = None,
        **kwargs
    ):
        # Establecer error_code por defecto si no se proporciona
        if 'error_code' not in kwargs:
            kwargs['error_code'] = ErrorCode.INFRASTRUCTURE_ERROR
        
        # Pasar original_error a la clase base
        kwargs['original_error'] = original_error
        super().__init__(message, **kwargs)
        if component:
            self.add_detail('component', component)
        if operation:
            self.add_detail('operation', operation)
    
    @property
    def component(self) -> Optional[str]:
        """Obtiene el componente donde ocurrió el error."""
        return self.details.get('component')
    
    @property
    def operation(self) -> Optional[str]:
        """Obtiene la operación que se estaba realizando."""
        return self.details.get('operation')
    



class DatabaseError(InfrastructureError):
    """
    Excepción base para errores de base de datos.
    
    Se utiliza para errores generales de base de datos que no
    encajan en categorías más específicas.
    """
    
    def __init__(
        self, 
        message: str, 
        query: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs
    ):
        # Asegurar que se use el código de error correcto
        kwargs['error_code'] = ErrorCode.DATABASE_ERROR
        super().__init__(
            message, 
            component="database",
            **kwargs
        )
        if query:
            self.add_detail('query', query)
        if table:
            self.add_detail('table', table)
    
    @property
    def query(self) -> Optional[str]:
        """Obtiene la consulta SQL que causó el error."""
        return self.details.get('query')
    
    @property
    def table(self) -> Optional[str]:
        """Obtiene la tabla afectada por el error."""
        return self.details.get('table')


class DatabaseConnectionError(DatabaseError):
    """
    Excepción para errores de conexión a la base de datos.
    
    Se lanza cuando no se puede establecer o mantener una conexión
    con la base de datos.
    """
    
    def __init__(
        self, 
        message: str, 
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        **kwargs
    ):
        kwargs['error_code'] = ErrorCode.DATABASE_CONNECTION_ERROR
        InfrastructureError.__init__(
            self,
            message, 
            component="database",
            operation="connection",
            **kwargs
        )
        if host:
            self.add_detail('host', host)
        if port:
            self.add_detail('port', port)
        if database:
            self.add_detail('database', database)
    
    @property
    def host(self) -> Optional[str]:
        """Obtiene el host de la conexión."""
        return self.details.get('host')
    
    @property
    def port(self) -> Optional[int]:
        """Obtiene el puerto de la conexión."""
        return self.details.get('port')
    
    @property
    def database(self) -> Optional[str]:
        """Obtiene el nombre de la base de datos."""
        return self.details.get('database')


class DatabaseIntegrityError(DatabaseError):
    """
    Excepción para errores de integridad de datos.
    
    Se lanza cuando se violan restricciones de integridad como
    claves foráneas, restricciones únicas, etc.
    """
    
    def __init__(
        self, 
        message: str, 
        constraint: Optional[str] = None,
        constraint_type: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs
    ):
        kwargs['error_code'] = ErrorCode.DATABASE_INTEGRITY_ERROR
        InfrastructureError.__init__(
            self,
            message, 
            component="database",
            operation="integrity_check",
            **kwargs
        )
        if constraint:
            self.add_detail('constraint', constraint)
        if constraint_type:
            self.add_detail('constraint_type', constraint_type)
        if table:
            self.add_detail('table', table)
    
    @property
    def constraint(self) -> Optional[str]:
        """Obtiene la restricción violada."""
        return self.details.get('constraint')
    
    @property
    def constraint_type(self) -> Optional[str]:
        """Obtiene el tipo de restricción violada."""
        return self.details.get('constraint_type')
    
    @property
    def table(self) -> Optional[str]:
        """Obtiene la tabla donde ocurrió el error de integridad."""
        return self.details.get('table')


class DatabaseTimeoutError(DatabaseError):
    """
    Excepción para errores de timeout en operaciones de base de datos.
    
    Se lanza cuando una operación de base de datos excede el tiempo
    límite establecido.
    """
    
    def __init__(
        self, 
        message: str, 
        timeout_seconds: Optional[float] = None,
        query: Optional[str] = None,
        **kwargs
    ):
        kwargs['error_code'] = ErrorCode.DATABASE_TIMEOUT_ERROR
        InfrastructureError.__init__(
            self,
            message, 
            component="database",
            operation="timeout",
            **kwargs
        )
        if timeout_seconds:
            self.add_detail('timeout_seconds', timeout_seconds)
        if query:
            self.add_detail('query', query)
    
    @property
    def timeout_seconds(self) -> Optional[float]:
        """Obtiene el tiempo límite en segundos."""
        return self.details.get('timeout_seconds')
    
    @property
    def query(self) -> Optional[str]:
        """Obtiene la consulta que causó el timeout."""
        return self.details.get('query')


class MigrationError(DatabaseError):
    """
    Excepción para errores en migraciones de base de datos.
    
    Se lanza cuando fallan las migraciones de esquema de base de datos
    o cuando hay problemas con el versionado.
    """
    
    def __init__(
        self, 
        message: str, 
        migration_version: Optional[str] = None,
        migration_file: Optional[str] = None,
        direction: Optional[str] = None,
        **kwargs
    ):
        kwargs['error_code'] = ErrorCode.MIGRATION_ERROR
        InfrastructureError.__init__(
            self,
            message, 
            component="database",
            operation="migration",
            **kwargs
        )
        if migration_version:
            self.add_detail('migration_version', migration_version)
        if migration_file:
            self.add_detail('migration_file', migration_file)
        if direction:
            self.add_detail('direction', direction)
    
    @property
    def migration_version(self) -> Optional[str]:
        """Obtiene la versión de migración."""
        return self.details.get('migration_version')
    
    @property
    def migration_file(self) -> Optional[str]:
        """Obtiene el archivo de migración."""
        return self.details.get('migration_file')
    
    @property
    def direction(self) -> Optional[str]:
        """Obtiene la dirección de la migración (up/down)."""
        return self.details.get('direction')


class ConnectionError(InfrastructureError):
    """
    Excepción para errores de conexión general.
    
    Se utiliza para errores de conexión que no son específicos
    de base de datos (APIs, servicios web, etc.).
    """
    
    def __init__(
        self, 
        message: str, 
        endpoint: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        retry_count: Optional[int] = None,
        **kwargs
    ):
        kwargs['error_code'] = ErrorCode.CONNECTION_ERROR
        super().__init__(
            message, 
            component="connection",
            **kwargs
        )
        if endpoint:
            self.add_detail('endpoint', endpoint)
        if timeout_seconds:
            self.add_detail('timeout_seconds', timeout_seconds)
        if retry_count:
            self.add_detail('retry_count', retry_count)
    
    @property
    def endpoint(self) -> Optional[str]:
        """Obtiene el endpoint de la conexión."""
        return self.details.get('endpoint')
    
    @property
    def timeout_seconds(self) -> Optional[float]:
        """Obtiene el tiempo límite en segundos."""
        return self.details.get('timeout_seconds')
    
    @property
    def retry_count(self) -> Optional[int]:
        """Obtiene el número de reintentos."""
        return self.details.get('retry_count')


class ConfigurationError(InfrastructureError):
    """
    Excepción para errores de configuración.
    
    Se lanza cuando hay problemas con la configuración del sistema,
    variables de entorno faltantes, archivos de configuración inválidos, etc.
    """
    
    def __init__(
        self, 
        message: str, 
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        expected_value: Optional[str] = None,
        actual_value: Optional[str] = None,
        **kwargs
    ):
        kwargs['error_code'] = ErrorCode.CONFIGURATION_ERROR
        super().__init__(
            message, 
            component="configuration",
            **kwargs
        )
        if config_key:
            self.add_detail('config_key', config_key)
        if config_file:
            self.add_detail('config_file', config_file)
        if expected_value:
            self.add_detail('expected_value', expected_value)
        if actual_value:
            self.add_detail('actual_value', actual_value)
    
    @property
    def config_key(self) -> Optional[str]:
        """Obtiene la clave de configuración."""
        return self.details.get('config_key')
    
    @property
    def config_file(self) -> Optional[str]:
        """Obtiene el archivo de configuración."""
        return self.details.get('config_file')
    
    @property
    def expected_value(self) -> Optional[str]:
        """Obtiene el valor esperado."""
        return self.details.get('expected_value')
    
    @property
    def actual_value(self) -> Optional[str]:
        """Obtiene el valor actual."""
        return self.details.get('actual_value')


class ExternalServiceError(InfrastructureError):
    """
    Excepción para errores de servicios externos.
    
    Se lanza cuando fallan las comunicaciones con servicios externos,
    APIs de terceros, servicios web, etc.
    """
    
    def __init__(
        self, 
        message: str, 
        service_name: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        **kwargs
    ):
        kwargs['error_code'] = ErrorCode.EXTERNAL_SERVICE_ERROR
        super().__init__(
            message, 
            component="external_service",
            **kwargs
        )
        if service_name:
            self.add_detail('service_name', service_name)
        if endpoint:
            self.add_detail('endpoint', endpoint)
        if status_code:
            self.add_detail('status_code', status_code)
        if response_body:
            self.add_detail('response_body', response_body)
    
    @property
    def service_name(self) -> Optional[str]:
        """Obtiene el nombre del servicio."""
        return self.details.get('service_name')
    
    @property
    def endpoint(self) -> Optional[str]:
        """Obtiene el endpoint del servicio."""
        return self.details.get('endpoint')
    
    @property
    def status_code(self) -> Optional[int]:
        """Obtiene el código de estado HTTP."""
        return self.details.get('status_code')
    
    @property
    def response_body(self) -> Optional[str]:
        """Obtiene el cuerpo de la respuesta."""
        return self.details.get('response_body')


class FileSystemError(InfrastructureError):
    """
    Excepción para errores del sistema de archivos.
    
    Se lanza cuando hay problemas con operaciones de archivos,
    permisos, espacio en disco, etc.
    """
    
    def __init__(
        self, 
        message: str, 
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        permissions: Optional[str] = None,
        **kwargs
    ):
        kwargs['error_code'] = ErrorCode.FILE_SYSTEM_ERROR
        super().__init__(
            message, 
            component="filesystem",
            operation=operation,
            **kwargs
        )
        if file_path:
            self.add_detail('file_path', file_path)
        if permissions:
            self.add_detail('permissions', permissions)
    
    @property
    def file_path(self) -> Optional[str]:
        """Obtiene la ruta del archivo."""
        return self.details.get('file_path')
    
    @property
    def operation(self) -> Optional[str]:
        """Obtiene la operación que falló."""
        return self.details.get('operation')
    
    @property
    def permissions(self) -> Optional[str]:
        """Obtiene los permisos requeridos."""
        return self.details.get('permissions')


# ============================================================================
# FUNCIONES HELPER PARA CREAR EXCEPCIONES
# ============================================================================

def create_database_error(
    message: str,
    query: Optional[str] = None,
    table: Optional[str] = None,
    operation: Optional[str] = None,
    original_error: Optional[Exception] = None,
    **kwargs
) -> DatabaseError:
    """
    Crea una excepción DatabaseError con parámetros estandarizados.
    
    Args:
        message: Mensaje descriptivo del error
        query: Consulta SQL que causó el error
        table: Tabla afectada por el error
        operation: Operación que causó el error (ej: 'create', 'update', 'delete')
        original_error: Excepción original que causó el error
        **kwargs: Argumentos adicionales
        
    Returns:
        Instancia de DatabaseError
    """
    return DatabaseError(
        message=message,
        query=query,
        table=table,
        operation=operation,
        original_error=original_error,
        **kwargs
    )


def create_connection_error(
    message: str,
    endpoint: Optional[str] = None,
    timeout_seconds: Optional[float] = None,
    retry_count: Optional[int] = None,
    **kwargs
) -> ConnectionError:
    """
    Crea una excepción ConnectionError con parámetros estandarizados.
    
    Args:
        message: Mensaje descriptivo del error
        endpoint: Endpoint al que se intentó conectar
        timeout_seconds: Tiempo límite en segundos
        retry_count: Número de reintentos realizados
        **kwargs: Argumentos adicionales
        
    Returns:
        Instancia de ConnectionError
    """
    return ConnectionError(
        message=message,
        endpoint=endpoint,
        timeout_seconds=timeout_seconds,
        retry_count=retry_count,
        **kwargs
    )


def create_config_error(
    component: str,
    config_key: str,
    expected_type: str
) -> ConfigurationError:
    """
    Crea una excepción de error de configuración.
    
    Args:
        component: Componente donde ocurrió el error
        config_key: Clave de configuración problemática
        expected_type: Tipo esperado para la configuración
    
    Returns:
        ConfigurationError: Instancia de la excepción
    """
    message = f"Error de configuración en {component}: clave '{config_key}' debe ser de tipo {expected_type}"
    config_error = ConfigurationError(
        message=message,
        config_key=config_key
    )
    config_error.add_detail("component", component)
    config_error.add_detail("expected_type", expected_type)
    return config_error


def create_external_service_error(
    message: str,
    service_name: Optional[str] = None,
    endpoint: Optional[str] = None,
    status_code: Optional[int] = None,
    response_body: Optional[str] = None,
    **kwargs
) -> ExternalServiceError:
    """
    Crea una excepción ExternalServiceError con parámetros estandarizados.
    
    Args:
        message: Mensaje descriptivo del error
        service_name: Nombre del servicio externo
        endpoint: Endpoint que falló
        status_code: Código de estado HTTP recibido
        response_body: Cuerpo de la respuesta del servicio
        **kwargs: Argumentos adicionales
    
    Returns:
        Instancia de ExternalServiceError
    """
    return ExternalServiceError(
        message=message,
        service_name=service_name,
        endpoint=endpoint,
        status_code=status_code,
        response_body=response_body,
        **kwargs
    )


def create_filesystem_error(
    message: str,
    file_path: Optional[str] = None,
    operation: Optional[str] = None,
    **kwargs
) -> FileSystemError:
    """
    Crea una excepción FileSystemError con parámetros estandarizados.
    
    Args:
        message: Mensaje descriptivo del error
        file_path: Ruta del archivo afectado
        operation: Operación que falló
        **kwargs: Argumentos adicionales
        
    Returns:
        Instancia de FileSystemError
    """
    return FileSystemError(
        message=message,
        file_path=file_path,
        operation=operation,
        **kwargs
    )


def create_database_connection_error(
    message: str,
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: Optional[str] = None,
    **kwargs
) -> DatabaseConnectionError:
    """
    Crea una excepción DatabaseConnectionError con parámetros estandarizados.
    
    Args:
        message: Mensaje descriptivo del error
        host: Host de la base de datos
        port: Puerto de la base de datos
        database: Nombre de la base de datos
        **kwargs: Argumentos adicionales
        
    Returns:
        Instancia de DatabaseConnectionError
    """
    return DatabaseConnectionError(
        message=message,
        host=host,
        port=port,
        database=database,
        **kwargs
    )


def create_database_integrity_error(
    message: str,
    constraint: Optional[str] = None,
    constraint_type: Optional[str] = None,
    **kwargs
) -> DatabaseIntegrityError:
    """
    Crea una excepción DatabaseIntegrityError con parámetros estandarizados.
    
    Args:
        message: Mensaje descriptivo del error
        constraint: Nombre de la restricción violada
        constraint_type: Tipo de restricción (unique, foreign_key, etc.)
        **kwargs: Argumentos adicionales
        
    Returns:
        Instancia de DatabaseIntegrityError
    """
    return DatabaseIntegrityError(
        message=message,
        constraint=constraint,
        constraint_type=constraint_type,
        **kwargs
    )


def create_database_timeout_error(
    message: str,
    timeout_seconds: Optional[float] = None,
    **kwargs
) -> DatabaseTimeoutError:
    """
    Crea una excepción DatabaseTimeoutError con parámetros estandarizados.
    
    Args:
        message: Mensaje descriptivo del error
        timeout_seconds: Tiempo de timeout en segundos
        **kwargs: Argumentos adicionales
        
    Returns:
        Instancia de DatabaseTimeoutError
    """
    return DatabaseTimeoutError(
        message=message,
        timeout_seconds=timeout_seconds,
        **kwargs
    )


def create_migration_error(
    message: str,
    migration_version: Optional[str] = None,
    migration_file: Optional[str] = None,
    **kwargs
) -> MigrationError:
    """
    Crea una excepción MigrationError con parámetros estandarizados.
    
    Args:
        message: Mensaje descriptivo del error
        migration_version: Versión de la migración
        migration_file: Archivo de migración afectado
        **kwargs: Argumentos adicionales
        
    Returns:
        Instancia de MigrationError
    """
    return MigrationError(
        message=message,
        migration_version=migration_version,
        migration_file=migration_file,
        **kwargs
    )


def create_configuration_error(
    message: str,
    config_key: Optional[str] = None,
    config_file: Optional[str] = None,
    expected_value: Optional[str] = None,
    actual_value: Optional[str] = None,
    **kwargs
) -> ConfigurationError:
    """
    Crea una excepción ConfigurationError con parámetros estandarizados.
    
    Args:
        message: Mensaje descriptivo del error
        config_key: Clave de configuración problemática
        config_file: Archivo de configuración afectado
        expected_value: Valor esperado para la configuración
        actual_value: Valor actual de la configuración
        **kwargs: Argumentos adicionales
        
    Returns:
        Instancia de ConfigurationError
    """
    return ConfigurationError(
        message=message,
        config_key=config_key,
        config_file=config_file,
        expected_value=expected_value,
        actual_value=actual_value,
        **kwargs
    )


def create_file_system_error(
    message: str,
    file_path: Optional[str] = None,
    operation: Optional[str] = None,
    permissions: Optional[str] = None,
    **kwargs
) -> FileSystemError:
    """
    Crea una excepción FileSystemError con parámetros estandarizados.
    
    Args:
        message: Mensaje descriptivo del error
        file_path: Ruta del archivo afectado
        operation: Operación que falló
        permissions: Permisos requeridos
        **kwargs: Argumentos adicionales
        
    Returns:
        Instancia de FileSystemError
    """
    return FileSystemError(
        message=message,
        file_path=file_path,
        operation=operation,
        permissions=permissions,
        **kwargs
    )