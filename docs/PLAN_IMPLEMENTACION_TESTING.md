# Plan de Implementación del Sistema de Testing

**Proyecto**: Planificador2  
**Fecha de Creación**: 21 de agosto de 2025  
**Versión**: 1.0  
**Autor**: Sistema de Testing Planificador

## Resumen Ejecutivo

Este documento presenta un plan estructurado para implementar un sistema de testing robusto y completo para la aplicación Planificador2, siguiendo las mejores prácticas de Python 3.13 y las recomendaciones específicas del proyecto.

## Estado Actual del Proyecto

### ✅ Fortalezas Identificadas
- **Configuración pytest**: `pyproject.toml` configurado con `asyncio_mode = "auto"`
- **Dependencias de testing**: pytest, pytest-asyncio, coverage, pytest-cov instaladas
- **Estructura de directorios**: `src/planificador/tests/` con subdirectorios organizados
- **Arquitectura bien definida**: Modelos, repositorios, servicios, esquemas claramente separados
- **Sistema de excepciones**: Jerarquía robusta en `src/planificador/exceptions/`
- **Gestión con Poetry**: Configuración completa para dependencias y scripts

### ❌ Áreas que Requieren Implementación
- **conftest.py**: Configuración base de fixtures y configuraciones globales
- **Tests unitarios**: Para modelos, repositorios, servicios, esquemas
- **Tests de integración**: Para flujos completos de negocio
- **Tests de performance**: Para operaciones críticas
- **Fixtures y mocks**: Para datos de prueba y dependencias externas
- **Configuración de cobertura**: Métricas y reportes detallados

## Arquitectura de Testing Propuesta

### Estructura de Capas

```
src/planificador/tests/
├── conftest.py                 # Configuración global y fixtures base
├── fixtures/                   # Fixtures reutilizables
│   ├── __init__.py
│   ├── database_fixtures.py    # Fixtures de base de datos
│   ├── model_fixtures.py       # Fixtures de modelos
│   └── service_fixtures.py     # Fixtures de servicios
├── unit/                       # Tests unitarios
│   ├── __init__.py
│   ├── test_models/           # Tests de modelos SQLAlchemy
│   ├── test_schemas/          # Tests de esquemas Pydantic
│   ├── test_repositories/     # Tests de repositorios
│   ├── test_services/         # Tests de servicios
│   ├── test_exceptions/       # Tests del sistema de excepciones
│   └── test_utils/           # Tests de utilidades
├── integration/               # Tests de integración
│   ├── __init__.py
│   ├── test_api_flows/       # Tests de flujos API completos
│   ├── test_database_flows/  # Tests de operaciones de BD
│   └── test_business_flows/  # Tests de lógica de negocio
├── performance/              # Tests de rendimiento
│   ├── __init__.py
│   ├── test_repository_performance.py
│   └── test_service_performance.py
└── utils/                    # Utilidades de testing
    ├── __init__.py
    ├── test_helpers.py       # Funciones auxiliares
    └── mock_factories.py     # Factories para mocks
```

## Dependencias Adicionales Requeridas

### Dependencias de Desarrollo a Agregar

```bash
# Mocking y factories
poetry add --group dev pytest-mock factory-boy faker

# Performance y paralelización
poetry add --group dev pytest-benchmark pytest-xdist

# Testing avanzado
poetry add --group dev hypothesis pytest-html pytest-clarity

# Cobertura avanzada
poetry add --group dev pytest-cov coverage[toml]

# Fixtures temporales
poetry add --group dev pytest-tmp-path-factory
```

## Plan de Implementación por Fases

### Fase 1: Fundamentos (Semana 1)

#### 1.1 Configuración Base
- [ ] **conftest.py**: Configuración global de pytest
- [ ] **Fixtures de base de datos**: Sesiones de prueba, rollback automático
- [ ] **Configuración de logging**: Logs específicos para testing
- [ ] **Variables de entorno de testing**: Configuración aislada

#### 1.2 Tests de Modelos SQLAlchemy
- [ ] **Tests de creación**: Validación de instancias
- [ ] **Tests de relaciones**: Foreign keys, backref
- [ ] **Tests de constraints**: Unique, not null, check constraints
- [ ] **Tests de métodos**: Métodos personalizados de modelos

#### 1.3 Tests de Esquemas Pydantic
- [ ] **Tests de validación**: Campos requeridos, tipos, formatos
- [ ] **Tests de serialización**: to_dict, JSON serialization
- [ ] **Tests de deserialización**: from_dict, JSON parsing
- [ ] **Tests de validadores personalizados**: Custom validators

### Fase 2: Lógica de Negocio (Semana 2)

#### 2.1 Tests de Repositorios
- [ ] **Tests CRUD básicos**: Create, Read, Update, Delete
- [ ] **Tests de consultas complejas**: Filtros, joins, agregaciones
- [ ] **Tests de manejo de errores**: SQLAlchemy exceptions
- [ ] **Tests de transacciones**: Rollback, commit
- [ ] **Tests asíncronos**: Operaciones async/await

#### 2.2 Tests de Servicios
- [ ] **Tests de lógica de negocio**: Reglas específicas del dominio
- [ ] **Tests de validaciones**: Business rules validation
- [ ] **Tests de transformaciones**: Data mapping, calculations
- [ ] **Tests de dependencias**: Inyección de dependencias

#### 2.3 Tests del Sistema de Excepciones
- [ ] **Tests de jerarquía**: Herencia correcta
- [ ] **Tests de conversión**: SQLAlchemy → Custom exceptions
- [ ] **Tests de contexto**: Información adicional en excepciones
- [ ] **Tests de logging**: Registro apropiado de errores

### Fase 3: Integración y Performance (Semana 3)

#### 3.1 Tests de Integración
- [ ] **Tests de flujos completos**: End-to-end scenarios
- [ ] **Tests de API**: Request/response cycles
- [ ] **Tests de base de datos**: Operaciones complejas
- [ ] **Tests de configuración**: Settings y environment

#### 3.2 Tests de Performance
- [ ] **Benchmarks de repositorios**: Operaciones CRUD
- [ ] **Benchmarks de servicios**: Lógica de negocio
- [ ] **Tests de carga**: Múltiples operaciones concurrentes
- [ ] **Profiling de memoria**: Memory usage analysis

#### 3.3 Cobertura y Calidad
- [ ] **Configuración de cobertura**: 90%+ target
- [ ] **Reportes HTML**: Visualización de cobertura
- [ ] **CI/CD integration**: Automated testing
- [ ] **Quality gates**: Minimum coverage enforcement

## Estrategias Específicas por Componente

### Testing de Repositorios Asíncronos

```python
# Ejemplo de estructura de test para repositorios
@pytest.mark.asyncio
class TestClientRepository:
    async def test_create_client_success(self, client_repository, valid_client_data):
        """Test successful client creation"""
        client = await client_repository.create(valid_client_data)
        assert client.id is not None
        assert client.name == valid_client_data["name"]
    
    async def test_create_client_duplicate_email_raises_exception(self, client_repository):
        """Test duplicate email raises appropriate exception"""
        with pytest.raises(ValidationError) as exc_info:
            await client_repository.create({"email": "existing@example.com"})
        assert "email already exists" in str(exc_info.value)
```

### Testing de Servicios de Dominio

```python
# Ejemplo de estructura de test para servicios
@pytest.mark.asyncio
class TestProjectService:
    async def test_calculate_project_workload(self, project_service, mock_workload_repo):
        """Test project workload calculation"""
        mock_workload_repo.get_by_project_id.return_value = [mock_workload_1, mock_workload_2]
        
        total_hours = await project_service.calculate_total_workload(project_id=1)
        
        assert total_hours == 40.0
        mock_workload_repo.get_by_project_id.assert_called_once_with(1)
```

### Testing de Esquemas Pydantic

```python
# Ejemplo de estructura de test para esquemas
class TestClientSchema:
    def test_valid_client_creation(self, valid_client_data):
        """Test valid client schema creation"""
        client = ClientCreate(**valid_client_data)
        assert client.name == valid_client_data["name"]
        assert client.email == valid_client_data["email"]
    
    def test_invalid_email_raises_validation_error(self):
        """Test invalid email format raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            ClientCreate(name="Test", email="invalid-email")
        assert "email" in str(exc_info.value)
```

### Testing del Sistema de Excepciones

```python
# Ejemplo de estructura de test para excepciones
class TestExceptionSystem:
    def test_repository_error_creation(self):
        """Test RepositoryError creation with context"""
        error = RepositoryError(
            message="Test error",
            operation="create",
            entity_type="Client",
            entity_id=1
        )
        assert error.operation == "create"
        assert error.entity_type == "Client"
        assert error.entity_id == 1
    
    def test_convert_sqlalchemy_error(self):
        """Test SQLAlchemy error conversion"""
        sql_error = IntegrityError("statement", "params", "orig")
        converted = convert_sqlalchemy_error(
            error=sql_error,
            operation="create",
            entity_type="Client"
        )
        assert isinstance(converted, ValidationError)
```

## Configuraciones Específicas

### conftest.py Base

```python
# src/planificador/tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from planificador.config.config import settings
from planificador.database.base import Base

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    """Create test database session with rollback."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        transaction = await session.begin()
        yield session
        await transaction.rollback()
```

### Configuración de Cobertura

```toml
# Agregar a pyproject.toml
[tool.coverage.run]
source = ["src/planificador"]
omit = [
    "src/planificador/tests/*",
    "src/planificador/__pycache__/*",
    "src/planificador/main.py",
    "src/planificador/init_db.py"
]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:"
]
show_missing = true
precision = 2

[tool.coverage.html]
directory = "htmlcov"
```

## Comandos de Testing

### Comandos Básicos

```bash
# Ejecutar todos los tests
poetry run pytest

# Ejecutar tests con cobertura
poetry run pytest --cov=src/planificador --cov-report=html --cov-report=term

# Ejecutar tests específicos
poetry run pytest src/planificador/tests/unit/test_repositories/

# Ejecutar tests en paralelo
poetry run pytest -n auto

# Ejecutar tests con benchmark
poetry run pytest --benchmark-only

# Ejecutar tests con reporte HTML
poetry run pytest --html=reports/report.html --self-contained-html
```

### Scripts de Automatización

```bash
# Agregar a pyproject.toml
[tool.poetry.scripts]
test = "pytest"
test-cov = "pytest --cov=src/planificador --cov-report=html --cov-report=term"
test-fast = "pytest -x -v"
test-benchmark = "pytest --benchmark-only"
```

## Métricas de Calidad

### Objetivos de Cobertura
- **Modelos**: 95%+ (crítico para integridad de datos)
- **Repositorios**: 90%+ (operaciones de base de datos)
- **Servicios**: 85%+ (lógica de negocio)
- **Esquemas**: 90%+ (validación de datos)
- **Excepciones**: 100% (manejo de errores)
- **Utilidades**: 80%+ (funciones auxiliares)

### Métricas de Performance
- **Operaciones CRUD**: < 100ms por operación
- **Consultas complejas**: < 500ms
- **Carga de datos**: < 1s para 1000 registros
- **Memory usage**: < 100MB para test suite completa

## Herramientas de Calidad Adicionales

### Linting y Formateo

```bash
# Configurar Ruff para linting
poetry add --group dev ruff

# Ejecutar linting
poetry run ruff check src/planificador/tests/

# Formatear código
poetry run ruff format src/planificador/tests/
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: poetry run pytest
        language: system
        pass_filenames: false
        always_run: true
```

## Cronograma de Implementación

### Semana 1: Fundamentos
- **Días 1-2**: Configuración base (conftest.py, fixtures)
- **Días 3-4**: Tests de modelos SQLAlchemy
- **Días 5-7**: Tests de esquemas Pydantic

### Semana 2: Lógica de Negocio
- **Días 1-3**: Tests de repositorios
- **Días 4-5**: Tests de servicios
- **Días 6-7**: Tests del sistema de excepciones

### Semana 3: Integración y Performance
- **Días 1-2**: Tests de integración
- **Días 3-4**: Tests de performance
- **Días 5-7**: Cobertura, reportes y documentación

## Beneficios Esperados

### Inmediatos
- **Detección temprana de bugs**: Identificación de errores antes de producción
- **Refactoring seguro**: Cambios con confianza en la estabilidad
- **Documentación viva**: Tests como especificación del comportamiento

### A Mediano Plazo
- **Reducción de bugs en producción**: 70-80% menos incidencias
- **Tiempo de desarrollo más eficiente**: Debugging más rápido
- **Onboarding mejorado**: Nuevos desarrolladores entienden el código más rápido

### A Largo Plazo
- **Mantenibilidad**: Código más fácil de mantener y evolucionar
- **Escalabilidad**: Arquitectura preparada para crecimiento
- **Calidad del producto**: Mayor confiabilidad y estabilidad

## Próximos Pasos

1. **Revisar y aprobar** este plan de implementación
2. **Instalar dependencias adicionales** según la lista proporcionada
3. **Comenzar con Fase 1**: Configuración base y tests fundamentales
4. **Establecer métricas de seguimiento**: Cobertura y performance baselines
5. **Configurar CI/CD**: Integración con pipeline de desarrollo

## Recursos y Referencias

- **Documentación pytest**: https://docs.pytest.org/
- **SQLAlchemy Testing**: https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
- **Pydantic Testing**: https://docs.pydantic.dev/latest/concepts/testing/
- **Async Testing**: https://pytest-asyncio.readthedocs.io/
- **Coverage.py**: https://coverage.readthedocs.io/

---

**Nota**: Este plan debe ser revisado y ajustado según las necesidades específicas del equipo y los recursos disponibles. La implementación puede ser adaptada para ejecutarse en paralelo o con diferentes prioridades según el contexto del proyecto.