# Sistema de Excepciones del Planificador

Este documento describe el sistema de excepciones personalizado implementado para el sistema de planificación. El sistema está organizado en una jerarquía clara que facilita el manejo de errores y proporciona información detallada sobre problemas específicos del dominio.

**Última actualización:** 26 de agosto de 2025

## Estructura del Sistema

### Organización por Módulos

```
exceptions/
├── __init__.py          # Punto de entrada y exportaciones
├── base.py              # Excepciones base del sistema
├── validation.py        # Excepciones de validación
├── infrastructure.py    # Excepciones de infraestructura
├── repository/          # Excepciones específicas de repositorios (EN DESARROLLO)
│   ├── __init__.py      # Exportaciones del módulo repository
│   ├── base_repository_exceptions.py     # Excepciones base de repositorios
│   ├── alert_repository_exceptions.py    # Excepciones del repositorio de alertas
│   ├── client_repository_exceptions.py   # Excepciones del repositorio de clientes
│   ├── employee_repository_exceptions.py # Excepciones del repositorio de empleados
│   ├── project_repository_exceptions.py  # Excepciones del repositorio de proyectos
│   ├── schedule_repository_exceptions.py # Excepciones del repositorio de horarios
│   ├── status_code_repository_exceptions.py # Excepciones del repositorio de códigos de estado
│   ├── team_repository_exceptions.py     # Excepciones del repositorio de equipos
│   ├── vacation_repository_exceptions.py # Excepciones del repositorio de vacaciones
│   └── workload_repository_exceptions.py # Excepciones del repositorio de cargas de trabajo
└── README.md           # Esta documentación
```

### Jerarquía de Excepciones

```
PlanificadorBaseException
├── ValidationError
│   ├── PydanticValidationError
│   ├── DateValidationError
│   ├── TimeValidationError
│   ├── DateTimeValidationError
│   ├── FormatValidationError
│   ├── RangeValidationError
│   ├── LengthValidationError
│   ├── RequiredFieldError
│   ├── UniqueConstraintError
│   ├── ForeignKeyValidationError
│   └── BusinessRuleValidationError
├── NotFoundError
├── ConflictError
├── BusinessLogicError
├── AuthenticationError
├── AuthorizationError
└── InfrastructureError
    ├── DatabaseError
    │   ├── DatabaseConnectionError
    │   ├── DatabaseIntegrityError
    │   ├── DatabaseTimeoutError
    │   └── MigrationError
    ├── ConnectionError
    ├── ConfigurationError
    ├── ExternalServiceError
    └── FileSystemError
```

## Códigos de Error

El sistema utiliza códigos de error estandarizados definidos en el enum `ErrorCode`:

### Códigos Base
- `VALIDATION_ERROR`: Errores de validación de datos
- `NOT_FOUND`: Recurso no encontrado
- `CONFLICT`: Conflicto en el estado del recurso
- `BUSINESS_LOGIC_ERROR`: Violación de reglas de negocio
- `AUTHENTICATION_ERROR`: Errores de autenticación
- `AUTHORIZATION_ERROR`: Errores de autorización
- `INTERNAL_ERROR`: Errores internos del sistema

### Códigos de Infraestructura
- `DATABASE_ERROR`: Error general de base de datos
- `DATABASE_CONNECTION_ERROR`: Error de conexión a la base de datos
- `DATABASE_INTEGRITY_ERROR`: Error de integridad de datos
- `DATABASE_TIMEOUT_ERROR`: Timeout en operaciones de base de datos
- `MIGRATION_ERROR`: Error en migraciones de base de datos
- `CONNECTION_ERROR`: Error de conexión a servicios externos
- `CONFIGURATION_ERROR`: Error de configuración del sistema
- `EXTERNAL_SERVICE_ERROR`: Error en servicios externos
- `FILE_SYSTEM_ERROR`: Error del sistema de archivos

## Categorías de Excepciones

### 1. Excepciones Base (`base.py`)

Excepciones fundamentales que sirven como base para todas las demás:

- **`PlanificadorBaseException`**: Excepción base del sistema
- **`ValidationError`**: Errores de validación de datos
- **`NotFoundError`**: Entidades no encontradas
- **`ConflictError`**: Conflictos en operaciones
- **`BusinessLogicError`**: Errores de lógica de negocio
- **`AuthenticationError`**: Errores de autenticación
- **`AuthorizationError`**: Errores de autorización

### 2. Excepciones de Validación (`validation.py`)

Excepciones específicas para validación de datos:

- **`PydanticValidationError`**: Errores de validación de Pydantic
- **`DateValidationError`**: Errores de validación de fechas
- **`TimeValidationError`**: Errores de validación de tiempo
- **`DateTimeValidationError`**: Errores de validación de fecha y hora
- **`FormatValidationError`**: Errores de formato de datos
- **`RangeValidationError`**: Errores de rango de valores
- **`LengthValidationError`**: Errores de longitud de datos
- **`RequiredFieldError`**: Errores de campos requeridos
- **`UniqueConstraintError`**: Errores de restricción única
- **`ForeignKeyValidationError`**: Errores de clave foránea
- **`BusinessRuleValidationError`**: Errores de reglas de negocio

### 3. Excepciones de Infraestructura (`infrastructure.py`)

Excepciones relacionadas con la infraestructura del sistema:

- **`InfrastructureError`**: Error base de infraestructura
- **`DatabaseError`**: Errores de base de datos
  - `DatabaseConnectionError`: Errores de conexión a BD
  - `DatabaseIntegrityError`: Errores de integridad de datos
  - `DatabaseTimeoutError`: Timeouts en operaciones
  - `MigrationError`: Errores en migraciones
- **`ConnectionError`**: Errores de conexión a servicios externos
- **`ConfigurationError`**: Errores de configuración del sistema
- **`ExternalServiceError`**: Errores de servicios externos
- **`FileSystemError`**: Errores del sistema de archivos

## Funciones Helper Disponibles

### Funciones de Infraestructura
- `create_database_error(operation, table, original_error)`: Crea errores de base de datos
- `create_connection_error(service, host, port)`: Crea errores de conexión
- `create_config_error(config_key, reason)`: Crea errores de configuración
- `create_external_service_error(service_name, endpoint, status_code, response_body)`: Crea errores de servicios externos

### Funciones de Validación
- `validate_email_format(email, field)`: Valida formato de email
- `validate_phone_format(phone, field)`: Valida formato de teléfono
- `validate_date_range(start_date, end_date, start_field, end_field)`: Valida rangos de fecha
- `validate_time_range(start_time, end_time, start_field, end_field)`: Valida rangos de tiempo
- `validate_datetime_range(start_datetime, end_datetime, start_field, end_field)`: Valida rangos de fecha y hora
- `validate_text_length(text, field, min_length, max_length)`: Valida longitud de texto
- `validate_numeric_range(value, field, min_value, max_value)`: Valida rangos numéricos
- `validate_required_field(value, field)`: Valida campos requeridos
- `convert_pydantic_error(pydantic_errors)`: Convierte errores de Pydantic

## Ejemplos de Uso

### Uso de Excepciones de Infraestructura

```python
from planificador.exceptions import (
    create_database_error,
    create_connection_error,
    create_config_error
)

# Error de base de datos
try:
    # Operación de base de datos
    pass
except Exception as e:
    raise create_database_error(
        operation="insert",
        table="users",
        original_error=e
    )

# Error de conexión
raise create_connection_error(
    service="redis",
    host="localhost",
    port=6379
)

# Error de configuración
raise create_config_error(
    config_key="DATABASE_URL",
    reason="Variable de entorno no definida"
)
```

### Uso de Validaciones

```python
from planificador.exceptions import (
    validate_email_format,
    validate_date_range,
    validate_required_field
)

# Validar email
validate_email_format("usuario@ejemplo.com", "email")

# Validar rango de fechas
validate_date_range(
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    start_field="fecha_inicio",
    end_field="fecha_fin"
)

# Validar campo requerido
validate_required_field("valor", "nombre_campo")
```

## Uso del Sistema

### Importación de Excepciones

```python
# Importación desde el módulo principal
from planificador.exceptions import (
    PlanificadorBaseException,
    ValidationError,
    NotFoundError,
    RepositoryError,
    get_domain_exception,
    DOMAIN_EXCEPTIONS
)

# Importación de excepciones específicas de repositorio
from planificador.exceptions.repository import (
    AlertRepositoryError,
    AlertStateTransitionError,
    convert_sqlalchemy_error
)

# Importación de excepciones de validación
from planificador.exceptions.validation import (
    DateValidationError,
    RequiredFieldError,
    UniqueConstraintError
)
```

### Manejo de Excepciones en Repositorios

```python
from sqlalchemy.exc import SQLAlchemyError
from planificador.exceptions.repository import convert_sqlalchemy_error, RepositoryError

class ClientRepository:
    async def create_client(self, client_data: dict):
        try:
            # Lógica de creación del cliente
            result = await self.session.execute(insert_statement)
            await self.session.commit()
            return result
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_client",
                entity_type="Client",
                entity_id=client_data.get("id")
            )
        except Exception as e:
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado al crear cliente: {e}",
                operation="create_client",
                entity_type="Client",
                original_error=e
            )
```

### Uso de Excepciones por Dominio

```python
from planificador.exceptions import get_domain_exception

def handle_client_error(error_type: str, message: str):
    """Maneja errores específicos del dominio cliente."""
    exception_class = get_domain_exception("client", error_type)
    raise exception_class(message=message)

# Ejemplo de uso
if not client_exists:
    handle_client_error("not_found", "Cliente no encontrado")
```

### Manejo de Excepciones de Validación

```python
from planificador.exceptions.validation import (
    RequiredFieldError,
    LengthValidationError,
    DateValidationError
)

def validate_client_data(client_data: dict):
    if not client_data.get('name'):
        raise RequiredFieldError(
            message="El nombre del cliente es requerido",
            field="name",
            details={"provided_data": client_data}
        )
    
    if len(client_data['name']) > 100:
        raise LengthValidationError(
            message="El nombre del cliente excede la longitud máxima",
            field="name",
            max_length=100,
            actual_length=len(client_data['name'])
        )
```

### Manejo Global de Excepciones

```python
try:
    # Operación que puede fallar
    result = await repository.create_client(client_data)
except AlertRepositoryError as e:
    logger.error(f"Error específico de alertas: {e.message}")
    # Manejo específico para errores de alertas
except RepositoryError as e:
    logger.error(f"Error de repositorio: {e.message}")
    # Manejo específico para errores de repositorio
except ValidationError as e:
    logger.error(f"Error de validación: {e.message}")
    # Manejo específico para errores de validación
except PlanificadorBaseException as e:
    logger.error(f"Error del sistema: {e.message}")
    # Manejo general para errores del sistema
```

### Ejemplos de Uso

#### 1. Manejo de Entidades No Encontradas

```python
from planificador.exceptions import ProjectNotFoundError

def get_project(project_id: int):
    project = repository.get_by_id(project_id)
    if not project:
        raise ProjectNotFoundError(project_id=project_id)
    return project

# Uso con función helper
from planificador.exceptions import create_not_found_error

def get_employee(employee_id: int):
    employee = repository.get_by_id(employee_id)
    if not employee:
        raise create_not_found_error('Employee', employee_id)
    return employee
```

#### 2. Validación de Datos

```python
from planificador.exceptions import (
    ProjectValidationError,
    validate_email_format,
    validate_date_range
)
from datetime import date

def create_project(data: dict):
    # Validación de fechas
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if start_date and end_date:
        try:
            validate_date_range(start_date, end_date)
        except DateValidationError as e:
            raise ProjectValidationError(
                'dates', 
                {'start_date': start_date, 'end_date': end_date},
                str(e)
            )
    
    # Validación de email del cliente
    client_email = data.get('client_email')
    if client_email:
        validate_email_format(client_email, 'client_email')
```

#### 3. Manejo de Errores de Base de Datos

```python
from planificador.exceptions import create_database_error
from sqlalchemy.exc import SQLAlchemyError

def save_project(project):
    try:
        session.add(project)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise create_database_error('create', 'projects', e)
```

#### 4. Conversión de Errores de Pydantic

```python
from planificador.exceptions import convert_pydantic_error
from pydantic import ValidationError as PydanticValidationError

def validate_project_data(data: dict):
    try:
        project_schema = ProjectCreate(**data)
        return project_schema
    except PydanticValidationError as e:
        raise convert_pydantic_error(e.errors())
```

#### 5. Uso del Mapeo de Excepciones

```python
from planificador.exceptions import get_domain_exception

def handle_entity_error(entity_type: str, error_type: str, **kwargs):
    exception_class = get_domain_exception(entity_type, error_type)
    raise exception_class(**kwargs)

# Ejemplo de uso
handle_entity_error('Project', 'not_found', project_id=123)
# Equivale a: raise ProjectNotFoundError(project_id=123)
```

### Captura y Manejo de Excepciones

```python
from planificador.exceptions import (
    PlanificadorBaseException,
    ValidationError,
    NotFoundError,
    DatabaseError
)
from loguru import logger

def handle_service_operation():
    try:
        # Operación del servicio
        result = some_service_operation()
        return result
        
    except NotFoundError as e:
        logger.warning(f"Entidad no encontrada: {e}")
        # Retornar respuesta 404
        return None
        
    except ValidationError as e:
        logger.warning(f"Error de validación: {e}")
        # Retornar respuesta 400 con detalles
        return {'error': 'validation_failed', 'details': e.to_dict()}
        
    except DatabaseError as e:
        logger.error(f"Error de base de datos: {e}")
        # Retornar respuesta 500
        return {'error': 'internal_error'}
        
    except PlanificadorBaseException as e:
        logger.error(f"Error del sistema: {e}")
        # Manejo genérico de errores del sistema
        return {'error': 'system_error', 'details': e.to_dict()}
```

## Funciones Helper Disponibles

### Funciones de Dominio
- `create_not_found_error(entity_type, entity_id)`
- `create_validation_error(entity_type, field, value, reason)`
- `create_conflict_error(entity_type, field, value)`
- `create_business_logic_error(entity_type, operation, reason)`

### Funciones de Infraestructura
- `create_database_error(operation, table, original_error)`
- `create_connection_error(service, host, port)`
- `create_config_error(config_key, reason)`
- `create_external_service_error(service_name, endpoint, status_code, response_body)`

### Funciones de Validación
- `validate_email_format(email, field)`
- `validate_phone_format(phone, field)`
- `validate_date_range(start_date, end_date, start_field, end_field)`
- `validate_time_range(start_time, end_time, start_field, end_field)`
- `validate_datetime_range(start_datetime, end_datetime, start_field, end_field)`
- `validate_text_length(text, field, min_length, max_length)`
- `validate_numeric_range(value, field, min_value, max_value)`
- `validate_required_field(value, field)`
- `convert_pydantic_error(pydantic_errors)`

## Mejores Prácticas

### 1. Uso de Funciones Helper
- Siempre usar las funciones `create_*` para crear excepciones de infraestructura
- Usar las funciones `validate_*` para validaciones comunes
- Agregar detalles específicos usando `add_detail()` cuando sea necesario

### 2. Manejo de Errores
- Capturar excepciones específicas en lugar de `Exception` genérica
- Proporcionar contexto útil en los mensajes de error
- Usar logging apropiado para registrar errores

### 3. Validación de Datos
- Validar datos de entrada lo antes posible
- Usar las funciones de validación proporcionadas
- Convertir errores de Pydantic usando `convert_pydantic_error()`

### 4. Estructura de Excepciones
- Heredar de `PlanificadorBaseException` para nuevas excepciones
- Mantener jerarquías lógicas de excepciones
- Proporcionar códigos de error únicos y descriptivos

## Integración con el Sistema

### Servicios
Los servicios deben usar las excepciones específicas del dominio:

```python
class ProjectService:
    def get_project(self, project_id: int) -> Project:
        project = self.repository.get_by_id(project_id)
        if not project:
            raise NotFoundError(f"Proyecto con ID {project_id} no encontrado")
        return project
    
    def create_project(self, data: ProjectCreate) -> Project:
        # Validar fechas
        if data.start_date > data.end_date:
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        # Verificar duplicados
        if self.repository.exists_by_reference(data.reference):
            raise ConflictError(f"Ya existe un proyecto con referencia {data.reference}")
        
        return self.repository.create(data)
```

### Repositorios
Los repositorios deben convertir errores de SQLAlchemy:

```python
from planificador.exceptions.repository import convert_sqlalchemy_error

class BaseRepository:
    def create(self, entity):
        try:
            self.session.add(entity)
            self.session.commit()
            return entity
        except SQLAlchemyError as e:
            self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="create",
                entity_type=self.__class__.__name__.replace("Repository", ""),
                entity_id=getattr(entity, 'id', None)
            )
```

### APIs
Las APIs deben convertir excepciones a respuestas HTTP:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from planificador.exceptions import (
    PlanificadorBaseException,
    NotFoundError,
    ValidationError,
    ConflictError
)

app = FastAPI()

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": "not_found", "message": str(exc)}
    )

@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "validation_failed", "message": str(exc)}
    )

@app.exception_handler(ConflictError)
async def conflict_error_handler(request: Request, exc: ConflictError):
    return JSONResponse(
        status_code=409,
        content={"error": "conflict", "message": str(exc)}
    )

@app.exception_handler(PlanificadorBaseException)
async def planificador_exception_handler(request: Request, exc: PlanificadorBaseException):
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": str(exc)}
    )
```

### Testing

```python
import pytest
from planificador.exceptions import (
    ValidationError,
    create_database_error,
    validate_email_format
)

def test_database_error_creation():
    """Test para creación de errores de base de datos."""
    original_error = Exception("Connection failed")
    error = create_database_error(
        operation="insert",
        table="users",
        original_error=original_error
    )
    
    assert "insert" in str(error)
    assert "users" in str(error)

def test_email_validation():
    """Test para validación de email."""
    # Email válido - no debe lanzar excepción
    validate_email_format("usuario@ejemplo.com", "email")
    
    # Email inválido - debe lanzar excepción
    with pytest.raises(ValidationError):
        validate_email_format("email_invalido", "email")

def test_validation_error_with_details():
    """Test para ValidationError con detalles."""
    error = ValidationError("Error de validación")
    
    assert "Error de validación" in str(error)
```

Este sistema de excepciones proporciona una base sólida para el manejo de errores en todo el sistema, facilitando el debugging, logging y la experiencia del usuario final.

## Notas Importantes

### Estado Actual del Sistema
El sistema de excepciones está completamente implementado con:
- **Excepciones base**: Implementadas en `base.py`
- **Excepciones de validación**: Implementadas en `validation.py`
- **Excepciones de infraestructura**: Implementadas en `infrastructure.py`
- **Excepciones de repositorio**: Implementadas en el directorio `repository/`

Todos los archivos están disponibles y funcionales.

### Estructura de Repositorios
El directorio `repository/` contiene excepciones especializadas para cada entidad:
- **Implementados**: Alert, Client, Employee, Project, Schedule, StatusCode, Team, Vacation, Workload
- **Patrón consistente**: Cada repositorio tiene su propio archivo con excepciones específicas
- **Funciones de creación**: Cada excepción tiene una función `create_*` correspondiente

## Consideraciones de Rendimiento

- Las excepciones son costosas computacionalmente
- Usar para casos excepcionales, no para control de flujo
- Proporcionar información suficiente sin ser excesivo
- Considerar el impacto en logs y monitoreo
- Usar funciones helper para creación eficiente de excepciones

### Convenciones de Naming

- **Excepciones de infraestructura**: `{Component}Error` (ej: `DatabaseError`)
- **Excepciones de validación**: `{Type}ValidationError` (ej: `EmailValidationError`)
- **Códigos de error**: `{COMPONENT}_{ERROR_TYPE}` (ej: `DATABASE_ERROR`)
- **Funciones helper**: `create_{component}_error`, `validate_{type}_format`

### Extensibilidad

Para agregar nuevas excepciones:

1. **Heredar de la clase base apropiada** (`PlanificadorBaseException`, `ValidationError`, etc.)
2. **Definir códigos de error únicos** siguiendo las convenciones
3. **Crear funciones helper** para facilitar el uso
4. **Agregar a `__all__`** en `__init__.py`
5. **Documentar en este README**

---

**Última actualización**: 26 de agosto de 2025
**Versión del sistema**: 2.0
**Estado**: Sistema de excepciones completamente implementado

*Este sistema de excepciones está diseñado para proporcionar un manejo de errores robusto, informativo y mantenible en toda la aplicación del planificador. La estructura modular permite extensibilidad mientras mantiene consistencia en el manejo de errores.*