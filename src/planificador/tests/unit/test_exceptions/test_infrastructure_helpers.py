# src/planificador/tests/unit/test_exceptions/test_infrastructure_helpers.py

"""
Tests para funciones helper de excepciones de infraestructura.

Este módulo contiene tests exhaustivos para todas las funciones helper
que facilitan la creación de excepciones de infraestructura con contexto
apropiado y parámetros específicos.
"""

import pytest
from typing import Any, Dict, Optional
from unittest.mock import Mock

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
from planificador.exceptions.infrastructure import (
    create_database_error,
    create_connection_error,
    create_configuration_error,
    create_external_service_error,
    create_file_system_error,
    create_database_connection_error,
    create_database_integrity_error,
    create_database_timeout_error,
    create_migration_error,
)


class TestCreateDatabaseError:
    """Tests para la función create_database_error."""
    
    def test_basic_database_error_creation(self):
        """Verifica la creación básica de DatabaseError."""
        message = "Database operation failed"
        
        exception = create_database_error(message)
        
        assert isinstance(exception, DatabaseError)
        assert exception.message == message
        assert exception.error_code == ErrorCode.DATABASE_ERROR
    
    def test_database_error_with_query(self):
        """Verifica la creación con query específica."""
        message = "Query execution failed"
        query = "SELECT * FROM users WHERE active = true"
        
        exception = create_database_error(message, query=query)
        
        assert exception.query == query
        assert exception.details['query'] == query
    
    def test_database_error_with_table(self):
        """Verifica la creación con tabla específica."""
        message = "Table operation failed"
        table = "users"
        
        exception = create_database_error(message, table=table)
        
        assert exception.table == table
        assert exception.details['table'] == table
    
    def test_database_error_with_operation(self):
        """Verifica la creación con operación específica."""
        message = "Database operation failed"
        operation = "INSERT"
        
        exception = create_database_error(message, operation=operation)
        
        assert exception.operation == operation
        assert exception.details['operation'] == operation
    
    def test_database_error_with_original_error(self):
        """Verifica la creación con error original."""
        message = "Database connection lost"
        original_error = Exception("Connection timeout")
        
        exception = create_database_error(message, original_error=original_error)
        
        assert exception.original_error == original_error
        assert exception.details['original_error'] == str(original_error)
    
    def test_database_error_with_all_parameters(self, sample_context):
        """Verifica la creación con todos los parámetros."""
        message = "Complete database error"
        query = "UPDATE users SET last_login = NOW()"
        table = "users"
        operation = "UPDATE"
        original_error = Exception("Lock timeout")
        
        exception = create_database_error(
            message=message,
            query=query,
            table=table,
            operation=operation,
            original_error=original_error,
            context=sample_context
        )
        
        assert exception.message == message
        assert exception.query == query
        assert exception.table == table
        assert exception.operation == operation
        assert exception.original_error == original_error
        assert exception.context == sample_context


class TestCreateDatabaseConnectionError:
    """Tests para la función create_database_connection_error."""
    
    def test_basic_connection_error_creation(self):
        """Verifica la creación básica de DatabaseConnectionError."""
        message = "Cannot connect to database"
        
        exception = create_database_connection_error(message)
        
        assert isinstance(exception, DatabaseConnectionError)
        assert exception.message == message
        assert exception.error_code == ErrorCode.DATABASE_CONNECTION_ERROR
    
    def test_connection_error_with_host_and_port(self):
        """Verifica la creación con host y puerto."""
        message = "Connection refused"
        host = "localhost"
        port = 5432
        
        exception = create_database_connection_error(
            message=message,
            host=host,
            port=port
        )
        
        assert exception.host == host
        assert exception.port == port
        assert exception.details['host'] == host
        assert exception.details['port'] == port
    
    def test_connection_error_with_database_name(self):
        """Verifica la creación con nombre de base de datos."""
        message = "Database not found"
        database = "planificador_test"
        
        exception = create_database_connection_error(
            message=message,
            database=database
        )
        
        assert exception.database == database
        assert exception.details['database'] == database
    
    def test_connection_error_with_all_parameters(self):
        """Verifica la creación con todos los parámetros."""
        message = "Complete connection error"
        host = "db.example.com"
        port = 3306
        database = "production_db"
        original_error = Exception("Network unreachable")
        
        exception = create_database_connection_error(
            message=message,
            host=host,
            port=port,
            database=database,
            original_error=original_error
        )
        
        assert exception.host == host
        assert exception.port == port
        assert exception.database == database
        assert exception.original_error == original_error


class TestCreateDatabaseIntegrityError:
    """Tests para la función create_database_integrity_error."""
    
    def test_basic_integrity_error_creation(self):
        """Verifica la creación básica de DatabaseIntegrityError."""
        message = "Constraint violation"
        
        exception = create_database_integrity_error(message)
        
        assert isinstance(exception, DatabaseIntegrityError)
        assert exception.message == message
        assert exception.error_code == ErrorCode.DATABASE_INTEGRITY_ERROR
    
    def test_integrity_error_with_constraint(self):
        """Verifica la creación con constraint específica."""
        message = "Foreign key constraint failed"
        constraint = "fk_user_id"
        
        exception = create_database_integrity_error(
            message=message,
            constraint=constraint
        )
        
        assert exception.constraint == constraint
        assert exception.details['constraint'] == constraint
    
    def test_integrity_error_with_table(self):
        """Verifica la creación con tabla específica."""
        message = "Unique constraint violation"
        table = "users"
        constraint = "unique_email"
        
        exception = create_database_integrity_error(
            message=message,
            table=table,
            constraint=constraint
        )
        
        assert exception.table == table
        assert exception.constraint == constraint
        assert exception.details['table'] == table
        assert exception.details['constraint'] == constraint


class TestCreateDatabaseTimeoutError:
    """Tests para la función create_database_timeout_error."""
    
    def test_basic_timeout_error_creation(self):
        """Verifica la creación básica de DatabaseTimeoutError."""
        message = "Query timeout"
        
        exception = create_database_timeout_error(message)
        
        assert isinstance(exception, DatabaseTimeoutError)
        assert exception.message == message
        assert exception.error_code == ErrorCode.DATABASE_TIMEOUT_ERROR
    
    def test_timeout_error_with_timeout_seconds(self):
        """Verifica la creación con timeout en segundos."""
        message = "Query exceeded timeout"
        timeout_seconds = 30
        
        exception = create_database_timeout_error(
            message=message,
            timeout_seconds=timeout_seconds
        )
        
        assert exception.timeout_seconds == timeout_seconds
        assert exception.details['timeout_seconds'] == timeout_seconds
    
    def test_timeout_error_with_query(self):
        """Verifica la creación con query específica."""
        message = "Long running query timeout"
        query = "SELECT COUNT(*) FROM large_table JOIN another_table"
        timeout_seconds = 60
        
        exception = create_database_timeout_error(
            message=message,
            query=query,
            timeout_seconds=timeout_seconds
        )
        
        assert exception.query == query
        assert exception.timeout_seconds == timeout_seconds
        assert exception.details['query'] == query
        assert exception.details['timeout_seconds'] == timeout_seconds


class TestCreateMigrationError:
    """Tests para la función create_migration_error."""
    
    def test_basic_migration_error_creation(self):
        """Verifica la creación básica de MigrationError."""
        message = "Migration failed"
        
        exception = create_migration_error(message)
        
        assert isinstance(exception, MigrationError)
        assert exception.message == message
        assert exception.error_code == ErrorCode.MIGRATION_ERROR
    
    def test_migration_error_with_version(self):
        """Verifica la creación con versión de migración."""
        message = "Migration script failed"
        migration_version = "001_create_users_table"
        
        exception = create_migration_error(
            message=message,
            migration_version=migration_version
        )
        
        assert exception.migration_version == migration_version
        assert exception.details['migration_version'] == migration_version
    
    def test_migration_error_with_direction(self):
        """Verifica la creación con dirección de migración."""
        message = "Rollback failed"
        migration_version = "002_add_user_preferences"
        direction = "down"
        
        exception = create_migration_error(
            message=message,
            migration_version=migration_version,
            direction=direction
        )
        
        assert exception.migration_version == migration_version
        assert exception.direction == direction
        assert exception.details['migration_version'] == migration_version
        assert exception.details['direction'] == direction


class TestCreateConnectionError:
    """Tests para la función create_connection_error."""
    
    def test_basic_connection_error_creation(self):
        """Verifica la creación básica de ConnectionError."""
        message = "Connection failed"
        
        exception = create_connection_error(message)
        
        assert isinstance(exception, ConnectionError)
        assert exception.message == message
        assert exception.error_code == ErrorCode.CONNECTION_ERROR
    
    def test_connection_error_with_endpoint(self):
        """Verifica la creación con endpoint específico."""
        message = "Cannot connect to service"
        endpoint = "https://api.example.com/v1"
        
        exception = create_connection_error(message, endpoint=endpoint)
        
        assert exception.endpoint == endpoint
        assert exception.details['endpoint'] == endpoint
    
    def test_connection_error_with_timeout(self):
        """Verifica la creación con timeout."""
        message = "Connection timeout"
        endpoint = "redis://cache:6379"
        timeout_seconds = 10
        
        exception = create_connection_error(
            message=message,
            endpoint=endpoint,
            timeout_seconds=timeout_seconds
        )
        
        assert exception.timeout_seconds == timeout_seconds
        assert exception.details['timeout_seconds'] == timeout_seconds
    
    def test_connection_error_with_retry_count(self):
        """Verifica la creación con número de reintentos."""
        message = "Connection failed after retries"
        endpoint = "amqp://rabbitmq:5672"
        retry_count = 5
        
        exception = create_connection_error(
            message=message,
            endpoint=endpoint,
            retry_count=retry_count
        )
        
        assert exception.retry_count == retry_count
        assert exception.details['retry_count'] == retry_count


class TestCreateConfigurationError:
    """Tests para la función create_configuration_error."""
    
    def test_basic_configuration_error_creation(self):
        """Verifica la creación básica de ConfigurationError."""
        message = "Invalid configuration"
        
        exception = create_configuration_error(message)
        
        assert isinstance(exception, ConfigurationError)
        assert exception.message == message
        assert exception.error_code == ErrorCode.CONFIGURATION_ERROR
    
    def test_configuration_error_with_config_key(self):
        """Verifica la creación con clave de configuración."""
        message = "Missing required configuration"
        config_key = "DATABASE_URL"
        
        exception = create_configuration_error(message, config_key=config_key)
        
        assert exception.config_key == config_key
        assert exception.details['config_key'] == config_key
    
    def test_configuration_error_with_config_file(self):
        """Verifica la creación con archivo de configuración."""
        message = "Configuration file not found"
        config_file = "/etc/app/config.yaml"
        
        exception = create_configuration_error(message, config_file=config_file)
        
        assert exception.config_file == config_file
        assert exception.details['config_file'] == config_file
    
    def test_configuration_error_with_expected_and_actual_values(self):
        """Verifica la creación con valores esperados y actuales."""
        message = "Invalid log level"
        config_key = "LOG_LEVEL"
        expected_value = "DEBUG, INFO, WARNING, ERROR, CRITICAL"
        actual_value = "INVALID_LEVEL"
        
        exception = create_configuration_error(
            message=message,
            config_key=config_key,
            expected_value=expected_value,
            actual_value=actual_value
        )
        
        assert exception.expected_value == expected_value
        assert exception.actual_value == actual_value
        assert exception.details['expected_value'] == expected_value
        assert exception.details['actual_value'] == actual_value


class TestCreateExternalServiceError:
    """Tests para la función create_external_service_error."""
    
    def test_basic_external_service_error_creation(self):
        """Verifica la creación básica de ExternalServiceError."""
        message = "External service unavailable"
        
        exception = create_external_service_error(message)
        
        assert isinstance(exception, ExternalServiceError)
        assert exception.message == message
        assert exception.error_code == ErrorCode.EXTERNAL_SERVICE_ERROR
    
    def test_external_service_error_with_service_name(self):
        """Verifica la creación con nombre del servicio."""
        message = "Payment service error"
        service_name = "stripe"
        
        exception = create_external_service_error(message, service_name=service_name)
        
        assert exception.service_name == service_name
        assert exception.details['service_name'] == service_name
    
    def test_external_service_error_with_status_code(self):
        """Verifica la creación con código de estado HTTP."""
        message = "API request failed"
        service_name = "weather_api"
        status_code = 503
        
        exception = create_external_service_error(
            message=message,
            service_name=service_name,
            status_code=status_code
        )
        
        assert exception.status_code == status_code
        assert exception.details['status_code'] == status_code
    
    def test_external_service_error_with_response_body(self):
        """Verifica la creación con cuerpo de respuesta."""
        message = "API error response"
        service_name = "notification_service"
        status_code = 400
        response_body = '{"error": "Invalid API key", "code": "AUTH_FAILED"}'
        
        exception = create_external_service_error(
            message=message,
            service_name=service_name,
            status_code=status_code,
            response_body=response_body
        )
        
        assert exception.response_body == response_body
        assert exception.details['response_body'] == response_body


class TestCreateFileSystemError:
    """Tests para la función create_file_system_error."""
    
    def test_basic_file_system_error_creation(self):
        """Verifica la creación básica de FileSystemError."""
        message = "File operation failed"
        
        exception = create_file_system_error(message)
        
        assert isinstance(exception, FileSystemError)
        assert exception.message == message
        assert exception.error_code == ErrorCode.FILE_SYSTEM_ERROR
    
    def test_file_system_error_with_file_path(self):
        """Verifica la creación con ruta de archivo."""
        message = "File not found"
        file_path = "/var/log/application.log"
        
        exception = create_file_system_error(message, file_path=file_path)
        
        assert exception.file_path == file_path
        assert exception.details['file_path'] == file_path
    
    def test_file_system_error_with_operation(self):
        """Verifica la creación con operación específica."""
        message = "Permission denied"
        file_path = "/etc/app/config.json"
        operation = "write"
        
        exception = create_file_system_error(
            message=message,
            file_path=file_path,
            operation=operation
        )
        
        assert exception.operation == operation
        assert exception.details['operation'] == operation
    
    def test_file_system_error_with_permissions(self):
        """Verifica la creación con permisos específicos."""
        message = "Insufficient permissions"
        file_path = "/var/log/secure.log"
        operation = "read"
        permissions = "600"
        
        exception = create_file_system_error(
            message=message,
            file_path=file_path,
            operation=operation,
            permissions=permissions
        )
        
        assert exception.permissions == permissions
        assert exception.details['permissions'] == permissions


class TestInfrastructureHelperIntegration:
    """Tests de integración para funciones helper de infraestructura."""
    
    def test_all_helpers_return_correct_exception_types(self):
        """Verifica que todas las funciones helper retornen el tipo correcto."""
        test_cases = [
            (create_database_error, DatabaseError),
            (create_database_connection_error, DatabaseConnectionError),
            (create_database_integrity_error, DatabaseIntegrityError),
            (create_database_timeout_error, DatabaseTimeoutError),
            (create_migration_error, MigrationError),
            (create_connection_error, ConnectionError),
            (create_configuration_error, ConfigurationError),
            (create_external_service_error, ExternalServiceError),
            (create_file_system_error, FileSystemError),
        ]
        
        for helper_func, expected_type in test_cases:
            exception = helper_func("Test message")
            assert isinstance(exception, expected_type)
            assert isinstance(exception, InfrastructureError)
    
    def test_all_helpers_preserve_context(self, sample_context):
        """Verifica que todas las funciones helper preserven el contexto."""
        helper_functions = [
            create_database_error,
            create_database_connection_error,
            create_database_integrity_error,
            create_database_timeout_error,
            create_migration_error,
            create_connection_error,
            create_configuration_error,
            create_external_service_error,
            create_file_system_error,
        ]
        
        for helper_func in helper_functions:
            exception = helper_func("Test message", context=sample_context)
            assert exception.context == sample_context
    
    def test_helpers_with_original_error_preservation(self):
        """Verifica que las funciones helper preserven el error original."""
        original_error = Exception("Original error message")
        
        helper_functions = [
            create_database_error,
            create_database_connection_error,
            create_connection_error,
            create_configuration_error,
            create_external_service_error,
            create_file_system_error,
        ]
        
        for helper_func in helper_functions:
            exception = helper_func("Test message", original_error=original_error)
            assert exception.original_error == original_error
            assert exception.details['original_error'] == str(original_error)