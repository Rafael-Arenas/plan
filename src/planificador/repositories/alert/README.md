# Repositorio de Alertas - Patrón Facade

## Descripción

Este módulo implementa un repositorio completo para la gestión de alertas utilizando el patrón Facade. Proporciona una interfaz unificada para todas las operaciones relacionadas con alertas, organizando la funcionalidad en módulos especializados para mejorar la mantenibilidad y escalabilidad.

## Arquitectura

### Patrón Facade
El repositorio utiliza el patrón Facade para proporcionar una interfaz simplificada que oculta la complejidad de múltiples subsistemas especializados.

```
AlertRepositoryFacade
├── CrudOperations          # Operaciones CRUD básicas
├── QueryOperations         # Consultas avanzadas y filtros
├── StatisticsOperations    # Estadísticas y métricas
├── StateManager           # Gestión de estados y transiciones
└── ValidationOperations   # Validaciones y verificaciones
```

### Componentes Principales

#### 1. AlertRepositoryFacade
**Archivo**: `alert_repository_facade.py`

Facade principal que integra todos los módulos especializados y proporciona una interfaz unificada.

```python
from planificador.repositories.alert import AlertRepositoryFacade
from sqlalchemy.ext.asyncio import AsyncSession

async def example_usage(session: AsyncSession):
    alert_repo = AlertRepositoryFacade(session)
    
    # Operaciones CRUD
    alert = await alert_repo.create_alert(alert_data)
    
    # Consultas avanzadas
    active_alerts = await alert_repo.get_active_alerts()
    
    # Estadísticas
    stats = await alert_repo.get_comprehensive_statistics()
    
    # Gestión de estados
    await alert_repo.mark_as_read(alert_id)
    
    # Validaciones
    is_valid = await alert_repo.validate_alert_exists(alert_id)
```

#### 2. IAlertRepository
**Archivo**: `alert_repository_interface.py`

Interfaz que define el contrato completo del repositorio de alertas.

#### 3. Módulos Especializados

##### CrudOperations
**Archivo**: `crud_operations.py`

Operaciones CRUD básicas:
- `create_alert()` - Crear nueva alerta
- `get_by_id()` - Obtener por ID
- `update_alert()` - Actualizar alerta
- `delete_alert()` - Eliminar alerta
- `bulk_create_alerts()` - Creación en lote

##### QueryOperations
**Archivo**: `query_operations.py`

Consultas avanzadas y filtros:
- `find_by_type()` - Buscar por tipo
- `find_by_status()` - Buscar por estado
- `get_active_alerts()` - Alertas activas
- `get_critical_alerts()` - Alertas críticas
- `find_by_date_range()` - Rango de fechas
- `get_all_with_filters()` - Filtros complejos

##### StatisticsOperations
**Archivo**: `statistics_operations.py`

Estadísticas y métricas:
- `count_total_alerts()` - Conteo total
- `count_by_status()` - Conteo por estado
- `get_daily_alert_counts()` - Conteos diarios
- `get_weekly_statistics()` - Estadísticas semanales
- `get_alert_trends()` - Tendencias
- `get_comprehensive_statistics()` - Estadísticas completas

##### StateManager
**Archivo**: `state_manager.py`

Gestión de estados y transiciones:
- `mark_as_read()` - Marcar como leída
- `mark_as_resolved()` - Marcar como resuelta
- `mark_as_ignored()` - Marcar como ignorada
- `reactivate_alert()` - Reactivar alerta
- `mark_multiple_as_read()` - Operaciones masivas
- `cleanup_old_resolved_alerts()` - Limpieza automática

##### ValidationOperations
**Archivo**: `validation_operations.py`

Validaciones y verificaciones:
- `validate_alert_exists()` - Validar existencia
- `validate_alert_data()` - Validar datos
- `validate_alert_consistency()` - Validar consistencia
- `validate_duplicate_alert()` - Detectar duplicados
- `get_data_integrity_report()` - Reporte de integridad

## Uso

### Instalación y Configuración

```python
from sqlalchemy.ext.asyncio import AsyncSession
from planificador.repositories.alert import AlertRepositoryFacade

# Crear instancia del repositorio
async def get_alert_repository(session: AsyncSession) -> AlertRepositoryFacade:
    return AlertRepositoryFacade(session)
```

### Ejemplos de Uso

#### Operaciones CRUD Básicas

```python
from planificador.schemas.alert.alert import AlertCreate, AlertUpdate

# Crear nueva alerta
alert_data = AlertCreate(
    title="Nueva alerta",
    description="Descripción de la alerta",
    type=AlertType.TASK_OVERDUE,
    user_id=1,
    project_id=1
)
new_alert = await alert_repo.create_alert(alert_data)

# Obtener alerta por ID
alert = await alert_repo.get_by_id(1)

# Actualizar alerta
update_data = AlertUpdate(description="Nueva descripción")
updated_alert = await alert_repo.update_alert(1, update_data)

# Eliminar alerta
success = await alert_repo.delete_alert(1)
```

#### Consultas Avanzadas

```python
# Obtener alertas activas
active_alerts = await alert_repo.get_active_alerts()

# Buscar por tipo
task_alerts = await alert_repo.find_by_type(AlertType.TASK_OVERDUE)

# Buscar por empleado
employee_alerts = await alert_repo.find_by_employee(employee_id=1)

# Filtros complejos
from planificador.schemas.alert.alert import AlertSearchFilter

filters = AlertSearchFilter(
    type=AlertType.CRITICAL,
    status=AlertStatus.ACTIVE,
    user_id=1
)
filtered_alerts = await alert_repo.get_all_with_filters(filters)
```

#### Estadísticas

```python
# Estadísticas básicas
total_alerts = await alert_repo.count_total_alerts()
unread_count = await alert_repo.count_unread_alerts()
critical_count = await alert_repo.count_critical_alerts()

# Estadísticas avanzadas
weekly_stats = await alert_repo.get_weekly_statistics()
trends = await alert_repo.get_alert_trends(days=30)
comprehensive_stats = await alert_repo.get_comprehensive_statistics()
```

#### Gestión de Estados

```python
# Cambios de estado individuales
await alert_repo.mark_as_read(alert_id=1)
await alert_repo.mark_as_resolved(alert_id=1)
await alert_repo.reactivate_alert(alert_id=1)

# Operaciones masivas
alert_ids = [1, 2, 3, 4, 5]
await alert_repo.mark_multiple_as_read(alert_ids)
await alert_repo.resolve_multiple_alerts(alert_ids)

# Limpieza automática
cleaned_count = await alert_repo.cleanup_old_resolved_alerts(days_old=30)
```

#### Validaciones

```python
# Validaciones básicas
exists = await alert_repo.validate_alert_exists(alert_id=1)
employee_exists = await alert_repo.validate_employee_exists(employee_id=1)

# Validaciones de datos
validation_errors = await alert_repo.validate_alert_data(alert_data)

# Reporte de integridad
integrity_report = await alert_repo.get_data_integrity_report()
```

### Mantenimiento del Repositorio

```python
# Estado de salud del repositorio
health_info = await alert_repo.get_repository_health()

# Tareas de mantenimiento
maintenance_results = await alert_repo.perform_maintenance(cleanup_days=30)
```

## Manejo de Errores

El repositorio utiliza un sistema robusto de manejo de errores:

- **SQLAlchemyError**: Errores de base de datos convertidos automáticamente
- **RepositoryError**: Errores específicos del repositorio
- **ValidationError**: Errores de validación de datos
- **Logging estructurado**: Registro detallado de todas las operaciones

```python
from planificador.exceptions.repository_exceptions import RepositoryError

try:
    alert = await alert_repo.create_alert(alert_data)
except RepositoryError as e:
    logger.error(f"Error en repositorio: {e.message}")
    # Manejar error específico
except Exception as e:
    logger.error(f"Error inesperado: {e}")
    # Manejar error general
```

## Compatibilidad

Este módulo mantiene compatibilidad con implementaciones anteriores:

```python
# Nueva implementación (recomendada)
from planificador.repositories.alert import AlertRepositoryFacade

# Implementación anterior (compatible)
from planificador.repositories.alert import AlertRepository
```

## Mejores Prácticas

1. **Usar el Facade**: Siempre usar `AlertRepositoryFacade` como punto de entrada
2. **Manejo de sesiones**: Gestionar correctamente las sesiones de SQLAlchemy
3. **Validaciones**: Usar las validaciones integradas antes de operaciones críticas
4. **Logging**: Aprovechar el logging estructurado para debugging
5. **Mantenimiento**: Ejecutar tareas de mantenimiento periódicamente
6. **Estadísticas**: Usar las estadísticas para monitoreo y análisis

## Rendimiento

- **Consultas optimizadas**: Uso eficiente de SQLAlchemy con eager/lazy loading
- **Operaciones en lote**: Soporte para operaciones masivas
- **Índices de base de datos**: Consultas optimizadas con índices apropiados
- **Caching**: Implementación de cache para consultas frecuentes
- **Async/Await**: Operaciones asíncronas para mejor rendimiento

## Testing

```python
import pytest
from planificador.repositories.alert import AlertRepositoryFacade

@pytest.mark.asyncio
async def test_create_alert(async_session):
    alert_repo = AlertRepositoryFacade(async_session)
    
    alert_data = AlertCreate(
        title="Test Alert",
        type=AlertType.TASK_OVERDUE,
        user_id=1
    )
    
    alert = await alert_repo.create_alert(alert_data)
    assert alert.title == "Test Alert"
    assert alert.type == AlertType.TASK_OVERDUE
```

## Contribución

Para contribuir al repositorio de alertas:

1. Seguir las convenciones de código establecidas
2. Implementar tests para nueva funcionalidad
3. Actualizar documentación según cambios
4. Usar el sistema de excepciones existente
5. Mantener compatibilidad con versiones anteriores

## Versión

**Versión actual**: 2.0.0
**Autor**: AkGroup Development Team
**Última actualización**: 2024