# Arquitectura del ProjectDomainService

## Resumen Ejecutivo

El **ProjectDomainService** es un servicio de dominio modular que implementa el patrón Facade para unificar todas las operaciones relacionadas con la gestión de proyectos. Esta arquitectura proporciona una interfaz cohesiva mientras mantiene la separación de responsabilidades a través de módulos especializados, integrando funcionalidades avanzadas de planificación, seguimiento y análisis de proyectos.

## Arquitectura General

### Estructura del Servicio

```
ProjectDomainService (Facade Principal)
├── CrudOperations (Operaciones CRUD básicas)
├── SpecializedCrudOperations (CRUD especializado)
├── QueryOperations (Consultas básicas)
├── AdvancedQueryOperations (Consultas avanzadas)
├── DatePlanningOperations (Fechas y planificación)
├── RelationshipOperations (Gestión de relaciones)
├── BasicStatisticsOperations (Estadísticas básicas)
├── AdvancedStatisticsOperations (Estadísticas avanzadas)
├── ValidationOperations (Validaciones de negocio)
└── DiagnosticOperations (Monitoreo y diagnóstico)
```

### Integración con Capas

```
┌─────────────────────────────────────────┐
│           Capa de Presentación          │
│        (UI, API Controllers)            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         ProjectDomainService            │
│           (Facade Principal)            │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ CRUD Ops    │  │ Specialized     │   │
│  │             │  │ CRUD Ops       │   │
│  └─────────────┘  └─────────────────┘   │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Query Ops   │  │ Advanced        │   │
│  │             │  │ Query Ops       │   │
│  └─────────────┘  └─────────────────┘   │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Date &      │  │ Relationship    │   │
│  │ Planning    │  │ Ops             │   │
│  └─────────────┘  └─────────────────┘   │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Basic Stats │  │ Advanced Stats  │   │
│  │ Ops         │  │ Ops             │   │
│  └─────────────┘  └─────────────────┘   │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Validation  │  │ Diagnostic      │   │
│  │ Ops         │  │ Ops             │   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       ProjectRepositoryFacade           │
│         (Capa de Persistencia)          │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            Base de Datos                │
│             (SQLite)                    │
└─────────────────────────────────────────┘
```

## Módulos Especializados

### 1. CrudOperations
**Responsabilidad**: Operaciones CRUD básicas con validaciones de negocio específicas de proyectos.

**Métodos principales**:
- `create_project(project_data: ProjectCreate) -> Project`
- `get_project_by_id(project_id: UUID) -> Optional[Project]`
- `update_project(project_id: UUID, project_data: ProjectUpdate) -> Optional[Project]`
- `delete_project(project_id: UUID) -> bool`
- `get_all_projects(skip: int, limit: int) -> List[Project]`

**Características**:
- Validaciones automáticas de fechas de inicio y fin
- Verificación de códigos únicos de proyecto
- Manejo transaccional con rollback automático
- Logging estructurado de todas las operaciones
- Integración con sistema de excepciones personalizado

### 2. SpecializedCrudOperations
**Responsabilidad**: Operaciones CRUD especializadas para casos de uso específicos de proyectos.

**Métodos principales**:
- `bulk_create_projects(projects_data: List[ProjectCreate]) -> List[Project]`
- `bulk_update_projects(updates: List[ProjectBulkUpdate]) -> List[Project]`
- `soft_delete_project(project_id: UUID) -> bool`
- `restore_project(project_id: UUID) -> Optional[Project]`
- `archive_project(project_id: UUID) -> bool`
- `clone_project(project_id: UUID, new_data: ProjectClone) -> Project`

**Características**:
- Operaciones masivas optimizadas
- Soft delete con posibilidad de restauración
- Clonación de proyectos con configuración personalizable
- Archivado automático de proyectos completados
- Manejo de estados de proyecto complejos

### 3. QueryOperations
**Responsabilidad**: Consultas básicas y búsquedas simples de proyectos.

**Métodos principales**:
- `get_project_by_name(name: str) -> Optional[Project]`
- `get_project_by_code(code: str) -> Optional[Project]`
- `get_projects_by_status(status: ProjectStatus) -> List[Project]`
- `get_projects_by_client(client_id: UUID) -> List[Project]`
- `search_projects_basic(search_term: str) -> List[Project]`

**Características**:
- Consultas optimizadas con índices apropiados
- Búsquedas case-insensitive por nombre y descripción
- Filtrado por estado, cliente y fechas
- Resultados ordenados por relevancia y fecha de creación
- Soporte para búsqueda por código de proyecto

### 4. AdvancedQueryOperations
**Responsabilidad**: Consultas complejas con filtros avanzados, ordenamiento y paginación.

**Métodos principales**:
- `search_projects_advanced(filters, sort_by, sort_order, page, page_size) -> Dict`
- `get_projects_paginated(page, page_size, sort_by) -> Dict`
- `search_projects_fuzzy(search_term, threshold) -> List[Project]`
- `filter_projects_by_criteria(criteria) -> List[Project]`
- `get_projects_with_assignments() -> List[Project]`
- `get_projects_full_details() -> List[Project]`

**Características**:
- Paginación eficiente con metadatos completos
- Filtros dinámicos y composables por múltiples criterios
- Búsqueda difusa con algoritmos de similitud
- Ordenamiento por múltiples campos (fecha, prioridad, estado)
- Carga eager de relaciones para evitar N+1 queries
- Filtros por rango de fechas y duración

### 5. DatePlanningOperations
**Responsabilidad**: Operaciones especializadas en fechas, planificación y cronogramas.

**Métodos principales**:
- `get_projects_by_date_range(start_date, end_date) -> List[Project]`
- `get_overdue_projects() -> List[Project]`
- `get_projects_ending_soon(days: int) -> List[Project]`
- `calculate_project_duration(project_id: UUID) -> Dict`
- `get_project_timeline(project_id: UUID) -> Dict`
- `update_project_dates(project_id: UUID, dates: ProjectDates) -> Optional[Project]`

**Características**:
- Cálculos automáticos de duración y progreso
- Detección de proyectos en riesgo por fechas
- Análisis de cronogramas y dependencias
- Gestión de zonas horarias con Pendulum
- Alertas automáticas de vencimientos
- Optimización de calendarios de proyecto

### 6. RelationshipOperations
**Responsabilidad**: Gestión de relaciones entre proyectos y otras entidades.

**Métodos principales**:
- `get_projects_by_employee(employee_id: UUID) -> List[Project]`
- `assign_employee_to_project(project_id: UUID, employee_id: UUID) -> bool`
- `remove_employee_from_project(project_id: UUID, employee_id: UUID) -> bool`
- `get_project_team(project_id: UUID) -> List[Employee]`
- `get_client_projects_summary(client_id: UUID) -> Dict`

**Características**:
- Gestión completa de asignaciones de empleados
- Análisis de carga de trabajo por empleado
- Resúmenes de proyectos por cliente
- Validación de conflictos de asignación
- Historial de cambios en asignaciones
- Métricas de colaboración en equipo

### 7. BasicStatisticsOperations
**Responsabilidad**: Estadísticas básicas y métricas fundamentales de proyectos.

**Métodos principales**:
- `get_project_count() -> int`
- `get_projects_by_status_count() -> Dict[str, int]`
- `get_active_projects_count() -> int`
- `get_completed_projects_count() -> int`
- `get_project_completion_rate() -> float`

**Características**:
- Conteos básicos optimizados
- Métricas de estado y progreso
- Tasas de finalización y éxito
- Estadísticas de distribución por estado
- Cacheo de métricas frecuentes
- Actualizaciones en tiempo real

### 8. AdvancedStatisticsOperations
**Responsabilidad**: Estadísticas avanzadas, análisis de tendencias y métricas de rendimiento.

**Métodos principales**:
- `get_project_performance_stats() -> Dict`
- `get_monthly_project_stats(months: int) -> Dict`
- `get_client_project_stats() -> Dict`
- `get_overdue_projects_summary() -> Dict`
- `get_project_duration_analysis() -> Dict`
- `get_employee_project_workload() -> Dict`

**Características**:
- Análisis de rendimiento y productividad
- Tendencias temporales y estacionales
- Métricas de eficiencia por cliente y empleado
- Análisis predictivo de retrasos
- Dashboards de KPIs ejecutivos
- Reportes de utilización de recursos

### 9. ValidationOperations
**Responsabilidad**: Validaciones de datos y reglas de negocio específicas de proyectos.

**Métodos principales**:
- `validate_project_creation(project_data) -> Dict`
- `validate_project_update(project_id, project_data) -> Dict`
- `validate_project_dates(start_date, end_date) -> Dict`
- `validate_project_code_uniqueness(code, exclude_project_id) -> bool`
- `validate_project_assignment(project_id, employee_id) -> Dict`

**Características**:
- Validaciones síncronas y asíncronas
- Reglas de negocio configurables para proyectos
- Validación de fechas y cronogramas
- Verificación de unicidad de códigos
- Validación de capacidad de empleados
- Mensajes de error contextualizados y específicos

### 10. DiagnosticOperations
**Responsabilidad**: Monitoreo, diagnóstico y mantenimiento del servicio de proyectos.

**Métodos principales**:
- `check_service_health() -> Dict`
- `check_database_connectivity() -> Dict`
- `generate_health_report() -> Dict`
- `diagnose_project_data_issues() -> Dict`
- `check_project_integrity() -> Dict`

**Características**:
- Verificaciones de salud automatizadas
- Diagnóstico de problemas de rendimiento
- Validación de integridad de datos de proyectos
- Métricas de uso de recursos
- Alertas proactivas de problemas
- Reportes de estado del sistema

## Patrones de Diseño Implementados

### 1. Facade Pattern
El `ProjectDomainService` actúa como un facade que:
- Unifica el acceso a múltiples subsistemas de gestión de proyectos
- Simplifica la interfaz para los clientes del servicio
- Oculta la complejidad interna de los módulos especializados
- Proporciona un punto de entrada único para todas las operaciones

### 2. Strategy Pattern
Cada módulo implementa una estrategia específica:
- Diferentes algoritmos para diferentes tipos de operaciones de proyecto
- Intercambiabilidad de implementaciones según el contexto
- Extensibilidad sin modificar código existente
- Especialización por dominio funcional

### 3. Dependency Injection
- Inyección de `AsyncSession` en el constructor
- Inyección de `ProjectRepositoryFacade` en módulos
- Facilita testing con mocks y stubs
- Reduce acoplamiento entre componentes
- Permite configuración flexible de dependencias

### 4. Repository Pattern
- Abstracción completa de la capa de persistencia
- Separación entre lógica de dominio y acceso a datos
- Facilita cambios en el almacenamiento de datos
- Permite testing independiente de la base de datos

### 5. Command Pattern
- Encapsulación de operaciones complejas de proyecto
- Soporte para undo/redo en operaciones críticas
- Logging y auditoría de comandos ejecutados
- Procesamiento asíncrono de operaciones pesadas

## Integración con ProjectRepositoryFacade

### Arquitectura de Integración

```python
# El ProjectDomainService utiliza el ProjectRepositoryFacade
class ProjectDomainService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository_facade = ProjectRepositoryFacade(session)
        
        # Cada módulo recibe el facade del repositorio
        self.crud = CrudOperations(session, self.repository_facade)
        self.specialized_crud = SpecializedCrudOperations(session, self.repository_facade)
        self.query = QueryOperations(session, self.repository_facade)
        self.advanced_query = AdvancedQueryOperations(session, self.repository_facade)
        self.date_planning = DatePlanningOperations(session, self.repository_facade)
        self.relationship = RelationshipOperations(session, self.repository_facade)
        self.basic_stats = BasicStatisticsOperations(session, self.repository_facade)
        self.advanced_stats = AdvancedStatisticsOperations(session, self.repository_facade)
        self.validation = ValidationOperations(session, self.repository_facade)
        self.diagnostic = DiagnosticOperations(session, self.repository_facade)
```

### Flujo de Datos

```
ProjectDomainService
    ↓ (delega operaciones especializadas)
Módulos Especializados
    ↓ (usa para persistencia y consultas)
ProjectRepositoryFacade
    ↓ (delega a módulos internos especializados)
Módulos de Repositorio (CRUD, Query, Stats, etc.)
    ↓ (ejecuta consultas optimizadas)
Base de Datos (SQLite con índices optimizados)
```

### Beneficios de la Integración

1. **Separación de Responsabilidades**:
   - Dominio: Lógica de negocio, validaciones y orquestación
   - Repositorio: Persistencia, consultas optimizadas y acceso a datos

2. **Reutilización de Código**:
   - El facade del repositorio se reutiliza en todos los módulos
   - Evita duplicación de lógica de persistencia
   - Componentes especializados reutilizables

3. **Mantenibilidad**:
   - Cambios en persistencia no afectan lógica de dominio
   - Evolución independiente de las capas
   - Módulos cohesivos y bajo acoplamiento

4. **Testabilidad**:
   - Fácil mockeo del facade del repositorio
   - Tests unitarios aislados por módulo
   - Cobertura completa de casos de uso

5. **Performance**:
   - Consultas optimizadas en el repositorio
   - Cacheo inteligente de operaciones frecuentes
   - Lazy loading y eager loading según necesidad

## Manejo de Errores y Excepciones

### Jerarquía de Excepciones Específicas

```
Exception
├── RepositoryError (errores de persistencia)
├── ValidationError (errores de validación de proyectos)
├── BusinessRuleError (violaciones de reglas de negocio)
├── ProjectNotFoundError (proyecto no encontrado)
├── ProjectCodeDuplicateError (código duplicado)
├── ProjectDateValidationError (fechas inválidas)
├── ProjectAssignmentError (errores de asignación)
└── DomainError (errores generales del dominio)
```

### Estrategia de Manejo Especializada

1. **Captura Específica**: Cada módulo captura excepciones específicas de su dominio
2. **Transformación Contextual**: Convierte excepciones técnicas en excepciones de dominio de proyectos
3. **Contexto Enriquecido**: Añade información específica de proyectos (ID, código, estado)
4. **Logging Estructurado**: Registra errores con contexto completo de proyecto
5. **Rollback Automático**: Revierte transacciones en caso de error
6. **Notificaciones**: Alertas automáticas para errores críticos

### Ejemplo de Manejo Especializado

```python
try:
    # Lógica de negocio específica de proyectos
    result = await self.repository_facade.create_project(project_data)
    return result
except SQLAlchemyError as e:
    self._logger.error(f"Error de base de datos en proyecto: {e}")
    await self.session.rollback()
    raise RepositoryError(
        message=f"Error creando proyecto: {e}",
        operation="create_project",
        entity_type="Project",
        entity_id=project_data.get("code"),
        original_error=e
    )
except ValidationError:
    # Re-lanzar errores de validación sin modificar
    raise
except IntegrityError as e:
    # Manejo específico para códigos duplicados
    if "project_code" in str(e):
        raise ProjectCodeDuplicateError(
            message=f"El código de proyecto '{project_data.code}' ya existe",
            project_code=project_data.code
        )
    raise
except Exception as e:
    self._logger.error(f"Error inesperado en proyecto: {e}")
    await self.session.rollback()
    raise DomainError(
        message=f"Error inesperado en servicio de dominio de proyectos: {e}",
        operation="create_project",
        original_error=e
    )
```

## Configuración y Dependencias

### Dependencias Principales

```toml
[tool.poetry.dependencies]
python = "^3.13"
sqlalchemy = "^2.0.0"
loguru = "^0.7.0"
pendulum = "^3.0.0"
pydantic = "^2.0.0"
pathlib = "^1.0.0"  # Para manejo de archivos de proyecto
```

### Configuración del Servicio

```python
# Configuración a través de settings
from planificador.config.config import settings

# El servicio utiliza configuración centralizada
class ProjectDomainService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._logger = logger.bind(
            service="ProjectDomainService",
            environment=settings.environment,
            version=settings.app_version
        )
        
        # Configuración específica de proyectos
        self.max_project_duration_days = settings.max_project_duration_days
        self.default_project_status = settings.default_project_status
        self.enable_project_notifications = settings.enable_project_notifications
```

## Patrones de Uso Recomendados

### 1. Inicialización del Servicio

```python
async def get_project_service(session: AsyncSession) -> ProjectDomainService:
    """Factory function para crear instancia del servicio de proyectos."""
    return ProjectDomainService(session)

# Uso en controladores
async with async_session() as session:
    project_service = await get_project_service(session)
    result = await project_service.create_project(project_data)
    await session.commit()
```

### 2. Manejo de Transacciones Complejas

```python
# Patrón recomendado para operaciones transaccionales de proyectos
async with async_session() as session:
    try:
        project_service = ProjectDomainService(session)
        
        # Múltiples operaciones en la misma transacción
        project = await project_service.create_project(project_data)
        await project_service.assign_employee_to_project(project.id, employee_id)
        await project_service.update_project_dates(project.id, dates_data)
        
        # Commit explícito al final
        await session.commit()
        
    except Exception as e:
        # Rollback automático al salir del contexto
        logger.error(f"Error en transacción de proyecto: {e}")
        raise
```

### 3. Validaciones Previas Especializadas

```python
# Validar antes de crear proyecto
validation_result = await project_service.validate_project_creation(project_data)
if validation_result["is_valid"]:
    # Validar fechas específicamente
    date_validation = await project_service.validate_project_dates(
        project_data.start_date, 
        project_data.end_date
    )
    if date_validation["is_valid"]:
        project = await project_service.create_project(project_data)
    else:
        handle_date_validation_errors(date_validation["errors"])
else:
    handle_validation_errors(validation_result["errors"])
```

### 4. Operaciones de Búsqueda Avanzada

```python
# Búsqueda avanzada con múltiples criterios
search_criteria = {
    "status": ["active", "in_progress"],
    "client_id": client_id,
    "date_range": {
        "start": start_date,
        "end": end_date
    },
    "assigned_employee": employee_id
}

results = await project_service.filter_projects_by_criteria(search_criteria)
```

## Extensibilidad y Evolución

### Añadir Nuevos Módulos Especializados

1. **Crear Interface**: Definir contrato en `interfaces/project/`
2. **Implementar Módulo**: Crear implementación en `modules/project/`
3. **Integrar en Facade**: Añadir al `ProjectDomainService`
4. **Actualizar Exports**: Modificar `__init__.py`
5. **Documentar**: Actualizar documentación de arquitectura

### Ejemplo de Extensión: Módulo de Reportes

```python
# 1. Nueva interface
class IProjectReportingOperations(ABC):
    @abstractmethod
    async def generate_project_report(self, project_id: UUID) -> Dict:
        pass
    
    @abstractmethod
    async def generate_client_projects_report(self, client_id: UUID) -> Dict:
        pass

# 2. Implementación
class ProjectReportingOperations(IProjectReportingOperations):
    def __init__(self, session: AsyncSession, repository_facade: ProjectRepositoryFacade):
        self.session = session
        self.repository_facade = repository_facade
        self._logger = logger.bind(module="ProjectReportingOperations")

    async def generate_project_report(self, project_id: UUID) -> Dict:
        # Implementación específica de reportes de proyecto
        pass

# 3. Integración en facade
class ProjectDomainService:
    def __init__(self, session: AsyncSession):
        # ... inicialización existente
        self.reporting = ProjectReportingOperations(session, self.repository_facade)
```

### Versionado de API

- **Versionado Semántico**: Major.Minor.Patch
- **Compatibilidad Hacia Atrás**: Mantener métodos deprecated con warnings
- **Migración Gradual**: Proporcionar guías de migración detalladas
- **Documentación de Cambios**: Changelog detallado con ejemplos
- **Testing de Compatibilidad**: Suite de tests para versiones anteriores

## Métricas y Monitoreo Específicas

### Métricas Clave de Proyectos

1. **Performance**:
   - Tiempo de respuesta por operación de proyecto
   - Throughput de creación/actualización de proyectos
   - Uso de memoria para operaciones complejas
   - Tiempo de consultas de estadísticas avanzadas

2. **Disponibilidad**:
   - Uptime del servicio de proyectos
   - Tasa de errores por tipo de operación
   - Tiempo de recuperación ante fallos
   - Disponibilidad de funciones críticas

3. **Negocio**:
   - Número de proyectos creados/actualizados por período
   - Patrones de uso por módulo especializado
   - Tendencias de crecimiento de proyectos
   - Métricas de finalización y éxito
   - Análisis de retrasos y sobrecostos

### Implementación de Monitoreo Especializado

```python
# Decorador para métricas automáticas de proyectos
@monitor_project_performance
async def create_project(self, project_data: ProjectCreate) -> Project:
    # Implementación...
    
# Logging estructurado con métricas específicas
self._logger.info(
    "Proyecto creado exitosamente",
    extra={
        "project_id": str(project.id),
        "project_code": project.code,
        "client_id": str(project.client_id),
        "operation": "create_project",
        "duration_ms": duration,
        "module": "CrudOperations",
        "project_status": project.status,
        "estimated_duration_days": project.estimated_duration_days
    }
)

# Métricas de negocio específicas
await self._record_business_metric(
    metric_name="project_created",
    value=1,
    tags={
        "client_id": str(project.client_id),
        "project_type": project.type,
        "priority": project.priority
    }
)
```

### Dashboard de Métricas

```python
# Métricas para dashboard ejecutivo
class ProjectMetricsDashboard:
    async def get_executive_metrics(self) -> Dict:
        return {
            "total_projects": await self.basic_stats.get_project_count(),
            "active_projects": await self.basic_stats.get_active_projects_count(),
            "completion_rate": await self.basic_stats.get_project_completion_rate(),
            "overdue_projects": len(await self.date_planning.get_overdue_projects()),
            "monthly_trends": await self.advanced_stats.get_monthly_project_stats(12),
            "performance_metrics": await self.advanced_stats.get_project_performance_stats()
        }
```

## Integración con Otros Servicios

### ClientDomainService
- Validación de existencia de clientes
- Obtención de información de clientes para proyectos
- Sincronización de datos de cliente

### EmployeeDomainService
- Gestión de asignaciones de empleados
- Validación de disponibilidad de empleados
- Análisis de carga de trabajo

### Ejemplo de Integración

```python
class ProjectDomainService:
    def __init__(self, session: AsyncSession):
        # ... inicialización base
        self.client_service = None  # Inyectado externamente
        self.employee_service = None  # Inyectado externamente
    
    async def create_project_with_validations(self, project_data: ProjectCreate) -> Project:
        # Validar cliente existe
        if self.client_service:
            client = await self.client_service.get_client_by_id(project_data.client_id)
            if not client:
                raise ValidationError("Cliente no encontrado")
        
        # Crear proyecto
        project = await self.create_project(project_data)
        
        # Asignar empleados si se especifican
        if project_data.assigned_employees and self.employee_service:
            for employee_id in project_data.assigned_employees:
                await self.assign_employee_to_project(project.id, employee_id)
        
        return project
```

## Conclusiones

El **ProjectDomainService** proporciona una arquitectura robusta, escalable y especializada para la gestión completa del dominio de proyectos, con las siguientes ventajas clave:

1. **Modularidad Especializada**: Separación clara de responsabilidades por funcionalidad específica de proyectos
2. **Extensibilidad Avanzada**: Fácil adición de nuevas funcionalidades especializadas
3. **Mantenibilidad Superior**: Código organizado, bien documentado y fácil de mantener
4. **Testabilidad Completa**: Componentes aislados y fáciles de probar unitariamente
5. **Performance Optimizada**: Operaciones optimizadas, cacheo inteligente y consultas eficientes
6. **Robustez Empresarial**: Manejo comprehensivo de errores, logging estructurado y monitoreo
7. **Integración Fluida**: Coordinación efectiva con otros servicios de dominio
8. **Escalabilidad Horizontal**: Arquitectura preparada para crecimiento y alta demanda

Esta arquitectura establece las bases para un sistema de gestión de proyectos escalable, mantenible y robusto que puede evolucionar con los requisitos complejos del negocio, proporcionando una base sólida para funcionalidades avanzadas de planificación, seguimiento y análisis de proyectos.