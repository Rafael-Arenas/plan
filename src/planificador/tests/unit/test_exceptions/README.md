# Tests del Sistema de Excepciones

## Descripción

Este directorio contiene una suite completa de tests para el sistema de excepciones del proyecto Planificador. Los tests están diseñados para verificar la funcionalidad, robustez y rendimiento de todas las excepciones personalizadas y sus funciones helper.

## Estructura de Archivos

```
test_exceptions/
├── __init__.py                     # Inicialización del módulo de tests
├── conftest.py                     # Configuración y fixtures compartidas
├── test_base_exceptions.py         # Tests para excepciones base
├── test_infrastructure_exceptions.py # Tests para excepciones de infraestructura
├── test_validation_exceptions.py   # Tests para excepciones de validación
├── test_infrastructure_helpers.py  # Tests para helpers de infraestructura
├── test_validation_helpers.py      # Tests para helpers de validación
├── test_integration.py             # Tests de integración del sistema
├── .coveragerc                     # Configuración de coverage
├── run_tests.py                    # Script de ejecución de tests
└── README.md                       # Esta documentación
```

## Cobertura de Tests

### Excepciones Base
- ✅ `ErrorCode` enum y sus valores
- ✅ `PlanificadorBaseException` y sus métodos
- ✅ `ValidationError` y subclases
- ✅ `NotFoundError`, `ConflictError`, `BusinessLogicError`
- ✅ `AuthenticationError`, `AuthorizationError`

### Excepciones de Infraestructura
- ✅ `InfrastructureError` y jerarquía
- ✅ `DatabaseError` y subclases específicas
- ✅ `ConnectionError`, `ConfigurationError`
- ✅ `ExternalServiceError`, `FileSystemError`

### Excepciones de Validación
- ✅ `PydanticValidationError`
- ✅ Excepciones de fecha/tiempo (`DateValidationError`, `TimeValidationError`, etc.)
- ✅ Excepciones de formato y rango
- ✅ `RequiredFieldError`, `LengthValidationError`

### Funciones Helper
- ✅ Helpers de infraestructura (`create_database_error`, etc.)
- ✅ Helpers de validación (`validate_email_format`, etc.)
- ✅ Funciones de creación de excepciones específicas

### Tests de Integración
- ✅ Jerarquía de herencia de excepciones
- ✅ Serialización y deserialización
- ✅ Encadenamiento de excepciones
- ✅ Manejo de contexto
- ✅ Compatibilidad con logging
- ✅ Tests de rendimiento

## Ejecución de Tests

### Métodos de Ejecución

#### 1. Script Personalizado (Recomendado)
```bash
# Tests básicos
python src/planificador/tests/unit/test_exceptions/run_tests.py

# Tests con coverage
python src/planificador/tests/unit/test_exceptions/run_tests.py --coverage

# Tests con coverage y reporte HTML
python src/planificador/tests/unit/test_exceptions/run_tests.py --coverage --html

# Tests verbose
python src/planificador/tests/unit/test_exceptions/run_tests.py --verbose

# Solo tests rápidos (sin performance)
python src/planificador/tests/unit/test_exceptions/run_tests.py --fast

# Validar coverage mínimo del 90%
python src/planificador/tests/unit/test_exceptions/run_tests.py --coverage --threshold 90
```

#### 2. Poetry + Pytest Directo
```bash
# Ejecutar todos los tests de excepciones
poetry run pytest src/planificador/tests/unit/test_exceptions/ -v

# Ejecutar tests específicos
poetry run pytest src/planificador/tests/unit/test_exceptions/test_base_exceptions.py -v

# Ejecutar con coverage
poetry run coverage run -m pytest src/planificador/tests/unit/test_exceptions/
poetry run coverage report --show-missing
```

#### 3. Tests por Categoría
```bash
# Solo tests de excepciones base
poetry run pytest src/planificador/tests/unit/test_exceptions/test_base_exceptions.py

# Solo tests de infraestructura
poetry run pytest src/planificador/tests/unit/test_exceptions/test_infrastructure_exceptions.py

# Solo tests de validación
poetry run pytest src/planificador/tests/unit/test_exceptions/test_validation_exceptions.py

# Solo tests de integración
poetry run pytest src/planificador/tests/unit/test_exceptions/test_integration.py
```

### Opciones Avanzadas

#### Filtros de Tests
```bash
# Solo tests que contengan "serialization"
poetry run pytest src/planificador/tests/unit/test_exceptions/ -k "serialization"

# Excluir tests de performance
poetry run pytest src/planificador/tests/unit/test_exceptions/ -k "not performance"

# Solo tests de DatabaseError
poetry run pytest src/planificador/tests/unit/test_exceptions/ -k "DatabaseError"
```

#### Configuración de Output
```bash
# Output mínimo
poetry run pytest src/planificador/tests/unit/test_exceptions/ -q

# Output detallado
poetry run pytest src/planificador/tests/unit/test_exceptions/ -v

# Output muy detallado
poetry run pytest src/planificador/tests/unit/test_exceptions/ -vv

# Mostrar prints
poetry run pytest src/planificador/tests/unit/test_exceptions/ -s
```

## Análisis de Coverage

### Configuración
El archivo `.coveragerc` está configurado para:
- ✅ Analizar solo el código de excepciones
- ✅ Excluir archivos de tests del análisis
- ✅ Incluir análisis de branches
- ✅ Generar reportes en múltiples formatos

### Reportes Disponibles

#### Reporte de Consola
```bash
poetry run coverage report --show-missing
```

#### Reporte HTML Interactivo
```bash
poetry run coverage html
# Abrir htmlcov/index.html en el navegador
```

#### Reporte XML (para CI/CD)
```bash
poetry run coverage xml
# Genera coverage.xml
```

#### Reporte JSON
```bash
poetry run coverage json
# Genera coverage.json
```

### Métricas de Coverage Objetivo

| Componente | Coverage Objetivo | Coverage Actual |
|------------|-------------------|------------------|
| Excepciones Base | 100% | ✅ |
| Excepciones de Infraestructura | 100% | ✅ |
| Excepciones de Validación | 100% | ✅ |
| Funciones Helper | 95% | ✅ |
| Tests de Integración | 90% | ✅ |
| **Total del Sistema** | **≥ 95%** | **✅** |

## Fixtures y Utilidades

### Fixtures Disponibles (conftest.py)

#### `sample_context`
```python
@pytest.fixture
def sample_context():
    return {
        "user_id": "12345",
        "session_id": "abcdef",
        "request_id": "req_123"
    }
```

#### `mock_original_error`
```python
@pytest.fixture
def mock_original_error():
    return ValueError("Original error message")
```

#### `sample_validation_errors`
```python
@pytest.fixture
def sample_validation_errors():
    # Lista de errores de validación de Pydantic
```

### Utilidades de Testing

#### `assert_exception_structure`
```python
def assert_exception_structure(exception, expected_code, expected_message):
    """Verifica la estructura básica de una excepción."""
```

#### `assert_serialization_complete`
```python
def assert_serialization_complete(exception):
    """Verifica que una excepción pueda ser completamente serializada."""
```

## Casos de Test Específicos

### Tests de Excepciones Base
- Inicialización correcta con parámetros
- Métodos `__str__` y `__repr__`
- Serialización con `to_dict()`
- Manejo de contexto con `add_context()`
- Manejo de detalles con `add_detail()`
- Herencia correcta de `Exception`

### Tests de Excepciones de Infraestructura
- Parámetros específicos por tipo de excepción
- Preservación de errores originales
- Contexto de operaciones de base de datos
- Información de conexión y configuración

### Tests de Excepciones de Validación
- Validación de campos específicos
- Manejo de errores de Pydantic
- Validación de fechas, tiempos y formatos
- Validación de rangos y longitudes

### Tests de Funciones Helper
- Creación correcta de excepciones
- Preservación de parámetros
- Validación de entrada
- Manejo de casos edge

### Tests de Integración
- Jerarquía de herencia completa
- Serialización/deserialización JSON
- Encadenamiento de excepciones múltiples
- Compatibilidad con logging estándar
- Rendimiento en operaciones masivas

## Mantenimiento y Extensión

### Agregar Nuevos Tests

1. **Para nueva excepción**:
   ```python
   # En el archivo apropiado (base/infrastructure/validation)
   def test_new_exception_initialization(self):
       exception = NewException("message", param1="value1")
       assert exception.message == "message"
       assert exception.param1 == "value1"
   ```

2. **Para nueva función helper**:
   ```python
   # En test_*_helpers.py apropiado
   def test_new_helper_function(self):
       result = new_helper_function(param="value")
       assert isinstance(result, ExpectedException)
       assert result.param == "value"
   ```

3. **Para test de integración**:
   ```python
   # En test_integration.py
   def test_new_integration_scenario(self):
       # Test de comportamiento conjunto
   ```

### Actualizar Coverage

1. **Ejecutar análisis**:
   ```bash
   python run_tests.py --coverage --html
   ```

2. **Revisar reporte HTML**:
   - Abrir `htmlcov/index.html`
   - Identificar líneas no cubiertas
   - Agregar tests para casos faltantes

3. **Validar umbral**:
   ```bash
   python run_tests.py --coverage --threshold 95
   ```

### Mejores Prácticas

#### Nomenclatura de Tests
- `test_[component]_[scenario]_[expected_result]`
- Ejemplo: `test_database_error_with_query_preserves_parameters`

#### Estructura de Tests
```python
def test_component_scenario(self):
    # Arrange: Preparar datos
    
    # Act: Ejecutar acción
    
    # Assert: Verificar resultado
```

#### Documentación de Tests
- Docstring explicando el propósito
- Comentarios para lógica compleja
- Casos edge documentados

## Troubleshooting

### Problemas Comunes

#### Tests Fallan por Imports
```bash
# Verificar que el proyecto esté instalado
poetry install

# Verificar PYTHONPATH
poetry run python -c "import planificador.exceptions; print('OK')"
```

#### Coverage Bajo
1. Revisar reporte HTML para identificar líneas no cubiertas
2. Agregar tests para casos edge
3. Verificar que todos los branches estén cubiertos

#### Tests Lentos
```bash
# Ejecutar solo tests rápidos
python run_tests.py --fast

# Identificar tests lentos
poetry run pytest --durations=10 src/planificador/tests/unit/test_exceptions/
```

#### Errores de Dependencias
```bash
# Verificar dependencias
python run_tests.py --check-deps

# Instalar dependencias faltantes
poetry add --group dev pytest coverage
```

### Logs y Debugging

#### Habilitar Logs en Tests
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Debug de Tests Específicos
```bash
# Ejecutar test específico con debug
poetry run pytest src/planificador/tests/unit/test_exceptions/test_base_exceptions.py::TestPlanificadorBaseException::test_initialization -vv -s
```

## Integración con CI/CD

### GitHub Actions
```yaml
- name: Run Exception Tests
  run: |
    poetry run python src/planificador/tests/unit/test_exceptions/run_tests.py --coverage --threshold 95
    poetry run coverage xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: exception-tests
      name: Exception Tests
      entry: poetry run python src/planificador/tests/unit/test_exceptions/run_tests.py --fast
      language: system
      pass_filenames: false
```

## Contacto y Soporte

Para preguntas sobre los tests de excepciones:
1. Revisar esta documentación
2. Ejecutar `python run_tests.py --help`
3. Consultar logs de ejecución
4. Revisar código fuente de tests para ejemplos

---

**Última actualización**: 2025-01-16  
**Versión de tests**: 1.0.0  
**Coverage objetivo**: ≥ 95%  
**Estado**: ✅ Completado y funcional