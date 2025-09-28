# Repositorio de Asignaciones de Proyecto (ProjectAssignment)

## Descripción General

Este repositorio implementa una arquitectura modular para la gestión de asignaciones de proyecto en el sistema Planificador. Proporciona una interfaz unificada para todas las operaciones relacionadas con la entidad `ProjectAssignment`, incluyendo operaciones CRUD, consultas complejas, validaciones de negocio, estadísticas y gestión de relaciones.

## Arquitectura

### Patrón Facade
El repositorio utiliza el patrón Facade a través de `ProjectAssignmentRepositoryFacade`, que actúa como punto de entrada único y delega las operaciones a módulos especializados.

### Módulos Especializados

#### 1. **CrudOperations** (`modules/crud_operations.py`)
- **Propósito**: Operaciones básicas de Crear, Leer, Actualizar, Eliminar
- **Métodos principales**:
  - `create_assignment()`: Crear nueva asignación
  - `update_assignment()`: Actualizar asignación existente
  - `delete_assignment()`: Eliminar asignación
  - `get_assignment_by_id()`: Obtener asignación por ID

#### 2. **QueryOperations** (`modules/query_operations.py`)
- **Propósito**: Consultas comunes y optimizadas
- **Métodos principales**:
  - `get_all_assignments()`: Obtener todas las asignaciones
  - `get_assignments_by_employee()`: Asignaciones por empleado
  - `get_assignments_by_project()`: Asignaciones por proyecto
  - `get_active_assignments()`: Asignaciones activas
  - `get_assignments_by_date_range()`: Asignaciones en rango de fechas
  - `get_assignments_by_role()`: Asignaciones por rol
  - `get_assignments_with_filters()`: Consultas con múltiples filtros
  - `get_overlapping_assignments()`: Asignaciones superpuestas

#### 3. **RelationshipOperations** (`modules/relationship_operations.py`)
- **Propósito**: Gestión de relaciones con empleados y proyectos
- **Métodos principales**:
  - `get_assignments_with_employee_data()`: Asignaciones con datos del empleado
  - `get_assignments_with_project_data()`: Asignaciones con datos del proyecto
  - `get_assignments_with_full_data()`: Asignaciones con datos completos
  - `transfer_employee_assignments()`: Transferir asignaciones entre empleados
  - `reassign_project_assignments()`: Reasignar asignaciones entre proyectos
  - `get_employee_workload_summary()`: Resumen de carga de trabajo
  - `get_project_team_summary()`: Resumen del equipo del proyecto

#### 4. **StatisticsOperations** (`modules/statistics_operations.py`)
- **Propósito**: Cálculos de métricas y estadísticas
- **Métodos principales**:
  - `get_total_assignments_count()`: Conteo total de asignaciones
  - `get_active_assignments_count()`: Conteo de asignaciones activas
  - `get_assignments_by_status_count()`: Conteo por estado
  - `get_assignments_by_allocation_category_count()`: Conteo por categoría
  - `get_employee_assignment_stats()`: Estadísticas por empleado
  - `get_project_assignment_stats()`: Estadísticas por proyecto
  - `get_assignment_duration_stats()`: Estadísticas de duración
  - `get_workload_distribution_stats()`: Distribución de carga de trabajo
  - `get_assignment_trends()`: Tendencias de asignaciones
  - `get_overlap_statistics()`: Estadísticas de superposición
  - `get_role_distribution_stats()`: Distribución por roles
  - `get_comprehensive_dashboard_metrics()`: Métricas completas del dashboard

#### 5. **ValidationOperations** (`modules/validation_operations.py`)
- **Propósito**: Validaciones de negocio y reglas de asignación
- **Métodos principales**:
  - `validate_assignment_data()`: Validación de datos básicos
  - `validate_required_fields()`: Validación de campos requeridos
  - `validate_date_range()`: Validación de rango de fechas
  - `validate_allocation_percentage()`: Validación de porcentaje de asignación
  - `validate_hours_per_day()`: Validación de horas por día
  - `validate_employee_exists()`: Validación de existencia del empleado
  - `validate_project_exists()`: Validación de existencia del proyecto
  - `validate_no_overlapping_assignments()`: Validación de no superposición
  - `validate_workload_limits()`: Validación de límites de carga de trabajo
  - `validate_assignment_deletion()`: Validación de eliminación
  - `validate_business_rules()`: Validación de reglas de negocio específicas

## Interfaces

Cada módulo implementa una interfaz específica ubicada en el directorio `interfaces/`:

- `ICrudOperations`: Define operaciones CRUD básicas
- `IQueryOperations`: Define operaciones de consulta
- `IRelationshipOperations`: Define operaciones de relaciones
- `IStatisticsOperations`: Define operaciones de estadísticas
- `IValidationOperations`: Define operaciones de validación

## Uso Básico

### Inicialización

```python
from sqlalchemy.ext.asyncio import AsyncSession
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade

# Inicializar el facade con una sesión de base de datos
facade = ProjectAssignmentRepositoryFacade(session)
```

### Operaciones CRUD

```python
from planificador.schemas.project_assignment import ProjectAssignmentCreate, ProjectAssignmentUpdate

# Crear una nueva asignación
assignment_data = ProjectAssignmentCreate(
    employee_id=1,
    project_id=1,
    role="Developer",
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    allocation_percentage=80.0
)
new_assignment = await facade.create_assignment(assignment_data)

# Obtener asignación por ID
assignment = await facade.get_assignment_by_id(1)

# Actualizar asignación
update_data = ProjectAssignmentUpdate(allocation_percentage=90.0)
updated_assignment = await facade.update_assignment(1, update_data)

# Eliminar asignación
success = await facade.delete_assignment(1)
```

### Consultas

```python
# Obtener todas las asignaciones activas
active_assignments = await facade.get_active_assignments()

# Obtener asignaciones por empleado
employee_assignments = await facade.get_assignments_by_employee(employee_id=1)

# Obtener asignaciones por proyecto
project_assignments = await facade.get_assignments_by_project(project_id=1)

# Consulta con múltiples filtros
filtered_assignments = await facade.get_assignments_with_filters(
    employee_id=1,
    status="active",
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31)
)
```

### Estadísticas

```python
# Obtener conteo total de asignaciones
total_count = await facade.get_total_assignments_count()

# Obtener estadísticas por empleado
employee_stats = await facade.get_employee_assignment_stats(employee_id=1)

# Obtener métricas completas del dashboard
dashboard_metrics = await facade.get_comprehensive_dashboard_metrics()
```

### Validaciones

```python
# Validar datos de asignación
assignment_data = {
    "employee_id": 1,
    "project_id": 1,
    "start_date": date(2024, 1, 1),
    "end_date": date(2024, 12, 31),
    "allocation_percentage": 80.0
}

await facade.validate_assignment_data(assignment_data)

# Validar que no hay asignaciones superpuestas
await facade.validate_no_overlapping_assignments(
    employee_id=1,
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31)
)
```

## Manejo de Errores

El repositorio utiliza un sistema de excepciones estructurado:

- **ValidationError**: Para errores de validación de datos
- **RepositoryError**: Para errores generales del repositorio
- **SQLAlchemyError**: Para errores específicos de base de datos (convertidos automáticamente)

### Ejemplo de Manejo de Errores

```python
from planificador.exceptions import ValidationError, RepositoryError

try:
    assignment = await facade.create_assignment(assignment_data)
except ValidationError as e:
    # Manejar error de validación
    logger.error(f"Error de validación: {e.message}")
except RepositoryError as e:
    # Manejar error del repositorio
    logger.error(f"Error del repositorio: {e.message}")
```

## Configuración y Dependencias

### Dependencias Requeridas

- **SQLAlchemy**: ORM para operaciones de base de datos
- **Pydantic**: Para esquemas de validación
- **Loguru**: Para logging estructurado
- **Pendulum**: Para manejo de fechas y tiempo

### Configuración

El repositorio utiliza la configuración global del sistema ubicada en:
```
src/planificador/config/config.py
```

## Testing

Para ejecutar las pruebas del repositorio:

```bash
# Ejecutar todas las pruebas del repositorio
poetry run pytest src/planificador/tests/repositories/test_project_assignment_repository.py

# Ejecutar pruebas específicas
poetry run pytest src/planificador/tests/repositories/test_project_assignment_repository.py::TestCrudOperations
```

## Consideraciones de Performance

1. **Consultas Optimizadas**: Uso de eager loading para relaciones frecuentemente accedidas
2. **Paginación**: Implementación de límites y offsets en consultas grandes
3. **Índices**: Asegurar índices apropiados en campos de búsqueda frecuente
4. **Conexiones Asíncronas**: Uso de aiosqlite para operaciones no bloqueantes

## Extensibilidad

Para agregar nuevas funcionalidades:

1. **Nuevas Operaciones**: Agregar métodos a los módulos existentes
2. **Nuevos Módulos**: Crear nuevos módulos especializados siguiendo el patrón existente
3. **Nuevas Validaciones**: Extender `ValidationOperations` con reglas específicas
4. **Nuevas Estadísticas**: Agregar métodos a `StatisticsOperations`

## Mantenimiento

### Logging
Todos los módulos utilizan Loguru para logging estructurado. Los logs incluyen:
- Información de operaciones exitosas
- Detalles de errores con contexto
- Métricas de performance para operaciones críticas

### Monitoreo
El repositorio proporciona métricas para monitoreo:
- Conteos de operaciones por tipo
- Tiempos de respuesta de consultas
- Errores por categoría

## Contribución

Al contribuir al repositorio:

1. Seguir las convenciones de nomenclatura establecidas
2. Implementar tests para nuevas funcionalidades
3. Documentar nuevos métodos con docstrings completos
4. Mantener la compatibilidad con la interfaz pública
5. Seguir los principios SOLID y patrones establecidos