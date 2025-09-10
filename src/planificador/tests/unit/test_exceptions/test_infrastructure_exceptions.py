# src/planificador/tests/unit/test_exceptions/test_infrastructure_exceptions.py

"""
Tests para excepciones de infraestructura del sistema de planificación.

Este módulo contiene tests exhaustivos para todas las excepciones relacionadas
con infraestructura: base de datos, conexiones, configuración, servicios externos
y sistema de archivos.
"""

import pytest
from typing import Any, Dict, Optional

from planificador.exceptions import (
    ErrorCode,
    InfrastructureError,
    DatabaseError,
    DatabaseConnectionError,
    DatabaseIntegrityError,
    DatabaseTimeoutError,
    MigrationError,
    ConnectionError,
    ConfigurationError,
    ExternalServiceError,
    FileSystemError,
)


class TestInfrastructureError:
    """Tests para la excepción base InfrastructureError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica de InfrastructureError."""
        message = "Infrastructure failure"
        exception = InfrastructureError(message)
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.INFRASTRUCTURE_ERROR
        assert exception.component is None
        assert exception.operation is None
        assert exception.original_error is None
    
    def test_initialization_with_component(self):
        """Verifica la inicialización con componente específico."""
        message = "Database service failed"
        component = "database"
        
        exception = InfrastructureError(message, component=component)
        
        assert exception.component == component
        assert exception.details['component'] == component
    
    def test_initialization_with_operation(self):
        """Verifica la inicialización con operación específica."""
        message = "Connection failed"
        operation = "connect"
        
        exception = InfrastructureError(message, operation=operation)
        
        assert exception.operation == operation
        assert exception.details['operation'] == operation
    
    def test_initialization_with_original_error(self):
        """Verifica la inicialización con error original."""
        message = "Service unavailable"
        original_error = ConnectionError("Network timeout")
        
        exception = InfrastructureError(message, original_error=original_error)
        
        assert exception.original_error == original_error
        assert exception.details['original_error'] == str(original_error)
    
    def test_initialization_with_all_parameters(self, sample_context):
        """Verifica la inicialización con todos los parámetros."""
        message = "Complete infrastructure error"
        component = "cache"
        operation = "get"
        original_error = Exception("Cache miss")
        
        exception = InfrastructureError(
            message=message,
            component=component,
            operation=operation,
            original_error=original_error,
            context=sample_context
        )
        
        assert exception.message == message
        assert exception.component == component
        assert exception.operation == operation
        assert exception.original_error == original_error
        assert exception.context == sample_context
        assert exception.details['component'] == component
        assert exception.details['operation'] == operation
        assert exception.details['original_error'] == str(original_error)


class TestDatabaseError:
    """Tests para DatabaseError y sus subclases."""
    
    def test_database_error_basic_initialization(self):
        """Verifica la inicialización básica de DatabaseError."""
        message = "Database operation failed"
        exception = DatabaseError(message)
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.DATABASE_ERROR
        assert isinstance(exception, InfrastructureError)
    
    def test_database_error_with_query(self):
        """Verifica DatabaseError con query específica."""
        message = "Query execution failed"
        query = "SELECT * FROM users WHERE id = ?"
        
        exception = DatabaseError(message, query=query)
        
        assert exception.query == query
        assert exception.details['query'] == query
    
    def test_database_error_with_table(self):
        """Verifica DatabaseError con tabla específica."""
        message = "Table operation failed"
        table = "users"
        
        exception = DatabaseError(message, table=table)
        
        assert exception.table == table
        assert exception.details['table'] == table
    
    def test_database_connection_error(self):
        """Verifica DatabaseConnectionError."""
        message = "Cannot connect to database"
        host = "localhost"
        port = 5432
        database = "planificador"
        
        exception = DatabaseConnectionError(
            message=message,
            host=host,
            port=port,
            database=database
        )
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.DATABASE_CONNECTION_ERROR
        assert exception.host == host
        assert exception.port == port
        assert exception.database == database
        assert exception.details['host'] == host
        assert exception.details['port'] == port
        assert exception.details['database'] == database
        assert isinstance(exception, DatabaseError)
    
    def test_database_integrity_error(self):
        """Verifica DatabaseIntegrityError."""
        message = "Foreign key constraint violation"
        constraint = "fk_user_id"
        table = "orders"
        
        exception = DatabaseIntegrityError(
            message=message,
            constraint=constraint,
            table=table
        )
        
        assert exception.constraint == constraint
        assert exception.table == table
        assert exception.error_code == ErrorCode.DATABASE_INTEGRITY_ERROR
        assert exception.details['constraint'] == constraint
        assert exception.details['table'] == table
        assert isinstance(exception, DatabaseError)
    
    def test_database_timeout_error(self):
        """Verifica DatabaseTimeoutError."""
        message = "Query timeout exceeded"
        timeout_seconds = 30
        query = "SELECT COUNT(*) FROM large_table"
        
        exception = DatabaseTimeoutError(
            message=message,
            timeout_seconds=timeout_seconds,
            query=query
        )
        
        assert exception.timeout_seconds == timeout_seconds
        assert exception.query == query
        assert exception.error_code == ErrorCode.DATABASE_TIMEOUT_ERROR
        assert exception.details['timeout_seconds'] == timeout_seconds
        assert exception.details['query'] == query
        assert isinstance(exception, DatabaseError)
    
    def test_migration_error(self):
        """Verifica MigrationError."""
        message = "Migration failed"
        migration_version = "001_create_users"
        direction = "up"
        
        exception = MigrationError(
            message=message,
            migration_version=migration_version,
            direction=direction
        )
        
        assert exception.migration_version == migration_version
        assert exception.direction == direction
        assert exception.error_code == ErrorCode.MIGRATION_ERROR
        assert exception.details['migration_version'] == migration_version
        assert exception.details['direction'] == direction
        assert isinstance(exception, DatabaseError)


class TestConnectionError:
    """Tests para ConnectionError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica de ConnectionError."""
        message = "Connection failed"
        exception = ConnectionError(message)
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.CONNECTION_ERROR
        assert isinstance(exception, InfrastructureError)
    
    def test_initialization_with_endpoint(self):
        """Verifica la inicialización con endpoint específico."""
        message = "Cannot connect to service"
        endpoint = "https://api.example.com"
        
        exception = ConnectionError(message, endpoint=endpoint)
        
        assert exception.endpoint == endpoint
        assert exception.details['endpoint'] == endpoint
    
    def test_initialization_with_timeout(self):
        """Verifica la inicialización con timeout."""
        message = "Connection timeout"
        endpoint = "redis://localhost:6379"
        timeout_seconds = 5
        
        exception = ConnectionError(
            message=message,
            endpoint=endpoint,
            timeout_seconds=timeout_seconds
        )
        
        assert exception.timeout_seconds == timeout_seconds
        assert exception.details['timeout_seconds'] == timeout_seconds
    
    def test_initialization_with_retry_count(self):
        """Verifica la inicialización con número de reintentos."""
        message = "Connection failed after retries"
        endpoint = "tcp://broker:9092"
        retry_count = 3
        
        exception = ConnectionError(
            message=message,
            endpoint=endpoint,
            retry_count=retry_count
        )
        
        assert exception.retry_count == retry_count
        assert exception.details['retry_count'] == retry_count


class TestConfigurationError:
    """Tests para ConfigurationError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica de ConfigurationError."""
        message = "Invalid configuration"
        exception = ConfigurationError(message)
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.CONFIGURATION_ERROR
        assert isinstance(exception, InfrastructureError)
    
    def test_initialization_with_config_key(self):
        """Verifica la inicialización con clave de configuración."""
        message = "Missing required configuration"
        config_key = "DATABASE_URL"
        
        exception = ConfigurationError(message, config_key=config_key)
        
        assert exception.config_key == config_key
        assert exception.details['config_key'] == config_key
    
    def test_initialization_with_config_file(self):
        """Verifica la inicialización con archivo de configuración."""
        message = "Configuration file not found"
        config_file = "/etc/planificador/config.yaml"
        
        exception = ConfigurationError(message, config_file=config_file)
        
        assert exception.config_file == config_file
        assert exception.details['config_file'] == config_file
    
    def test_initialization_with_expected_value(self):
        """Verifica la inicialización con valor esperado."""
        message = "Invalid configuration value"
        config_key = "LOG_LEVEL"
        expected_value = "DEBUG, INFO, WARNING, ERROR"
        actual_value = "INVALID"
        
        exception = ConfigurationError(
            message=message,
            config_key=config_key,
            expected_value=expected_value,
            actual_value=actual_value
        )
        
        assert exception.expected_value == expected_value
        assert exception.actual_value == actual_value
        assert exception.details['expected_value'] == expected_value
        assert exception.details['actual_value'] == actual_value


class TestExternalServiceError:
    """Tests para ExternalServiceError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica de ExternalServiceError."""
        message = "External service unavailable"
        exception = ExternalServiceError(message)
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.EXTERNAL_SERVICE_ERROR
        assert isinstance(exception, InfrastructureError)
    
    def test_initialization_with_service_name(self):
        """Verifica la inicialización con nombre del servicio."""
        message = "Payment service error"
        service_name = "stripe"
        
        exception = ExternalServiceError(message, service_name=service_name)
        
        assert exception.service_name == service_name
        assert exception.details['service_name'] == service_name
    
    def test_initialization_with_status_code(self):
        """Verifica la inicialización con código de estado HTTP."""
        message = "API request failed"
        service_name = "weather_api"
        status_code = 503
        
        exception = ExternalServiceError(
            message=message,
            service_name=service_name,
            status_code=status_code
        )
        
        assert exception.status_code == status_code
        assert exception.details['status_code'] == status_code
    
    def test_initialization_with_response_body(self):
        """Verifica la inicialización con cuerpo de respuesta."""
        message = "API error response"
        service_name = "notification_service"
        status_code = 400
        response_body = '{"error": "Invalid request"}'
        
        exception = ExternalServiceError(
            message=message,
            service_name=service_name,
            status_code=status_code,
            response_body=response_body
        )
        
        assert exception.response_body == response_body
        assert exception.details['response_body'] == response_body


class TestFileSystemError:
    """Tests para FileSystemError."""
    
    def test_basic_initialization(self):
        """Verifica la inicialización básica de FileSystemError."""
        message = "File operation failed"
        exception = FileSystemError(message)
        
        assert exception.message == message
        assert exception.error_code == ErrorCode.FILE_SYSTEM_ERROR
        assert isinstance(exception, InfrastructureError)
    
    def test_initialization_with_file_path(self):
        """Verifica la inicialización con ruta de archivo."""
        message = "File not found"
        file_path = "/var/log/planificador.log"
        
        exception = FileSystemError(message, file_path=file_path)
        
        assert exception.file_path == file_path
        assert exception.details['file_path'] == file_path
    
    def test_initialization_with_operation(self):
        """Verifica la inicialización con operación específica."""
        message = "Permission denied"
        file_path = "/etc/planificador/config.yaml"
        operation = "write"
        
        exception = FileSystemError(
            message=message,
            file_path=file_path,
            operation=operation
        )
        
        assert exception.operation == operation
        assert exception.details['operation'] == operation
    
    def test_initialization_with_permissions(self):
        """Verifica la inicialización con permisos."""
        message = "Insufficient permissions"
        file_path = "/var/log/app.log"
        operation = "read"
        permissions = "644"
        
        exception = FileSystemError(
            message=message,
            file_path=file_path,
            operation=operation,
            permissions=permissions
        )
        
        assert exception.permissions == permissions
        assert exception.details['permissions'] == permissions


class TestInfrastructureExceptionHierarchy:
    """Tests para verificar la jerarquía de excepciones de infraestructura."""
    
    @pytest.mark.parametrize("exception_class", [
        DatabaseError,
        DatabaseConnectionError,
        DatabaseIntegrityError,
        DatabaseTimeoutError,
        MigrationError,
        ConnectionError,
        ConfigurationError,
        ExternalServiceError,
        FileSystemError,
    ])
    def test_inheritance_hierarchy(self, exception_class):
        """Verifica que todas las excepciones hereden de InfrastructureError."""
        exception = exception_class("Test message")
        
        assert isinstance(exception, InfrastructureError)
        assert isinstance(exception, Exception)
    
    def test_database_exception_hierarchy(self):
        """Verifica la jerarquía específica de excepciones de base de datos."""
        database_exceptions = [
            DatabaseConnectionError,
            DatabaseIntegrityError,
            DatabaseTimeoutError,
            MigrationError,
        ]
        
        for exception_class in database_exceptions:
            exception = exception_class("Test")
            assert isinstance(exception, DatabaseError)
            assert isinstance(exception, InfrastructureError)
    
    def test_exception_error_codes(self):
        """Verifica que cada excepción tenga el código de error correcto."""
        test_cases = [
            (InfrastructureError, ErrorCode.INFRASTRUCTURE_ERROR),
            (DatabaseError, ErrorCode.DATABASE_ERROR),
            (DatabaseConnectionError, ErrorCode.DATABASE_CONNECTION_ERROR),
            (DatabaseIntegrityError, ErrorCode.DATABASE_INTEGRITY_ERROR),
            (DatabaseTimeoutError, ErrorCode.DATABASE_TIMEOUT_ERROR),
            (MigrationError, ErrorCode.MIGRATION_ERROR),
            (ConnectionError, ErrorCode.CONNECTION_ERROR),
            (ConfigurationError, ErrorCode.CONFIGURATION_ERROR),
            (ExternalServiceError, ErrorCode.EXTERNAL_SERVICE_ERROR),
            (FileSystemError, ErrorCode.FILE_SYSTEM_ERROR),
        ]
        
        for exception_class, expected_code in test_cases:
            exception = exception_class("Test")
            assert exception.error_code == expected_code


class TestInfrastructureExceptionSerialization:
    """Tests para verificar la serialización de excepciones de infraestructura."""
    
    def test_infrastructure_error_serialization(self, exception_helper):
        """Verifica la serialización de InfrastructureError."""
        exception = InfrastructureError(
            message="Test infrastructure error",
            component="test_component",
            operation="test_operation",
            original_error=Exception("Original error")
        )
        
        exception_helper.assert_exception_serialization(exception)
    
    def test_database_error_serialization(self, exception_helper):
        """Verifica la serialización de DatabaseError."""
        exception = DatabaseError(
            message="Test database error",
            query="SELECT * FROM test",
            table="test_table"
        )
        
        exception_helper.assert_exception_serialization(exception)
    
    def test_connection_error_serialization(self, exception_helper):
        """Verifica la serialización de ConnectionError."""
        exception = ConnectionError(
            message="Test connection error",
            endpoint="https://api.test.com",
            timeout_seconds=30,
            retry_count=3
        )
        
        exception_helper.assert_exception_serialization(exception)