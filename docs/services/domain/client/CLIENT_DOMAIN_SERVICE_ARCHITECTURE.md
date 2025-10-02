# Arquitectura del ClientDomainService

## Resumen Ejecutivo

El **ClientDomainService** es un servicio de dominio modular que implementa el patrón Facade para unificar todas las operaciones relacionadas con la gestión de clientes. Esta arquitectura proporciona una interfaz cohesiva mientras mantiene la separación de responsabilidades a través de módulos especializados.

## Arquitectura General

### Estructura del Servicio

```
ClientDomainService (Facade Principal)
├── CrudOperations (Operaciones CRUD básicas)
├── QueryOperations (Consultas básicas)
├── AdvancedQueryOperations (Consultas avanzadas)
├── StatisticsOperations (Estadísticas y métricas)
├── RelationshipOperations (Gestión de relaciones)
├── DateOperations (Operaciones de fechas)
├── ValidationOperations (Validaciones de negocio)
└── HealthOperations (Monitoreo y diagnóstico)
```

### Integración con Capas

```
┌─────────────────────────────────────────┐
│           Capa de Presentación          │
│        (UI, API Controllers)            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         ClientDomainService             │
│           (Facade Principal)            │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ CRUD Ops    │  │ Query Ops       │   │
│  └─────────────┘  └─────────────────┘   │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Advanced    │  │ Statistics      │   │
│  │ Query Ops   │  │ Ops             │   │
│  └─────────────┘  └─────────────────┘   │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Validation  │  │ Health Ops      │   │
│  │ Ops         │  │                 │   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       ClientRepositoryFacade            │
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
**Responsabilidad**: Operaciones CRUD básicas con validaciones de negocio.

**Métodos principales**:
- `create_client(client_data: ClientCreate) -> Client`
- `get_client_by_id(client_id: UUID) -> Optional[Client]`
- `update_client(client_id: UUID, client_data: ClientUpdate) -> Optional[Client]`
- `delete_client(client_id: UUID) -> bool`
- `bulk_create_clients(clients_data: List[ClientCreate]) -> List[Client]`

**Características**:
- Validaciones automáticas antes de persistencia
- Manejo transaccional con rollback automático
- Logging estructurado de todas las operaciones
- Integración con sistema de excepciones personalizado

### 2. QueryOperations
**Responsabilidad**: Consultas básicas y búsquedas simples.

**Métodos principales**:
- `get_client_by_name(name: str) -> Optional[Client]`
- `get_client_by_email(email: str) -> Optional[Client]`
- `get_client_by_code(code: str) -> Optional[Client]`
- `get_clients_by_status(is_active: bool) -> List[Client]`
- `search_clients_basic(search_term: str) -> List[Client]`

**Características**:
- Consultas optimizadas con índices apropiados
- Búsquedas case-insensitive
- Filtrado por múltiples criterios
- Resultados ordenados por relevancia

### 3. AdvancedQueryOperations
**Responsabilidad**: Consultas complejas con filtros, ordenamiento y paginación.

**Métodos principales**:
- `search_clients_advanced(filters, sort_by, sort_order, page, page_size) -> Dict`
- `get_clients_paginated(page, page_size, sort_by) -> Dict`
- `search_clients_fuzzy(search_term, threshold) -> List[Client]`
- `filter_clients_by_criteria(criteria) -> List[Client]`

**Características**:
- Paginación eficiente con metadatos
- Filtros dinámicos y composables
- Búsqueda difusa con algoritmos de similitud
- Ordenamiento por múltiples campos

### 4. StatisticsOperations
**Responsabilidad**: Estadísticas, métricas y análisis de datos.

**Métodos principales**:
- `get_client_statistics() -> ClientStatsResponse`
- `count_clients_by_status() -> Dict[str, int]`
- `get_client_growth_statistics(days) -> Dict`
- `get_client_activity_metrics() -> Dict`

**Características**:
- Cálculos agregados optimizados
- Métricas de crecimiento temporal
- Análisis de distribución y tendencias
- Cacheo de estadísticas frecuentes

### 5. ValidationOperations
**Responsabilidad**: Validaciones de datos y reglas de negocio.

**Métodos principales**:
- `validate_client_creation(client_data) -> Dict`
- `validate_client_update(client_id, client_data) -> Dict`
- `validate_business_rules(client_data) -> Dict`
- `validate_email_uniqueness(email, exclude_client_id) -> bool`

**Características**:
- Validaciones síncronas y asíncronas
- Reglas de negocio configurables
- Validación de unicidad en tiempo real
- Mensajes de error contextualizados

### 6. HealthOperations
**Responsabilidad**: Monitoreo, diagnóstico y mantenimiento del servicio.

**Métodos principales**:
- `check_service_health() -> Dict`
- `check_database_connectivity() -> Dict`
- `generate_health_report() -> Dict`
- `diagnose_data_issues() -> Dict`

**Características**:
- Verificaciones de salud automatizadas
- Diagnóstico de problemas de rendimiento
- Métricas de uso de recursos
- Alertas proactivas de problemas

## Patrones de Diseño Implementados

### 1. Facade Pattern
El `ClientDomainService` actúa como un facade que:
- Unifica el acceso a múltiples subsistemas
- Simplifica la interfaz para los clientes
- Oculta la complejidad interna de los módulos
- Proporciona un punto de entrada único

### 2. Strategy Pattern
Cada módulo implementa una estrategia específica:
- Diferentes algoritmos para diferentes tipos de operaciones
- Intercambiabilidad de implementaciones
- Extensibilidad sin modificar código existente

### 3. Dependency Injection
- Inyección de `AsyncSession` en el constructor
- Inyección de `ClientRepositoryFacade` en módulos
- Facilita testing con mocks
- Reduce acoplamiento entre componentes

### 4. Repository Pattern
- Abstracción de la capa de persistencia
- Separación entre lógica de dominio y acceso a datos
- Facilita cambios en el almacenamiento de datos

## Integración con ClientRepositoryFacade

### Arquitectura de Integración

```python
# El ClientDomainService utiliza el ClientRepositoryFacade
class ClientDomainService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository_facade = ClientRepositoryFacade(session)
        
        # Cada módulo recibe el facade del repositorio
        self.crud = CrudOperations(session, self.repository_facade)
        self.query = QueryOperations(session, self.repository_facade)
        # ... otros módulos
```

### Flujo de Datos

```
ClientDomainService
    ↓ (delega operaciones)
Módulos Especializados
    ↓ (usa para persistencia)
ClientRepositoryFacade
    ↓ (delega a módulos internos)
Módulos de Repositorio
    ↓ (ejecuta consultas)
Base de Datos
```

### Beneficios de la Integración

1. **Separación de Responsabilidades**:
   - Dominio: Lógica de negocio y validaciones
   - Repositorio: Persistencia y acceso a datos

2. **Reutilización de Código**:
   - El facade del repositorio se reutiliza en todos los módulos
   - Evita duplicación de lógica de persistencia

3. **Mantenibilidad**:
   - Cambios en persistencia no afectan lógica de dominio
   - Evolución independiente de las capas

4. **Testabilidad**:
   - Fácil mockeo del facade del repositorio
   - Tests unitarios aislados por módulo

## Manejo de Errores y Excepciones

### Jerarquía de Excepciones

```
Exception
├── RepositoryError (errores de persistencia)
├── ValidationError (errores de validación)
├── BusinessRuleError (violaciones de reglas de negocio)
└── DomainError (errores generales del dominio)
```

### Estrategia de Manejo

1. **Captura Específica**: Cada módulo captura excepciones específicas
2. **Transformación**: Convierte excepciones técnicas en excepciones de dominio
3. **Contexto Enriquecido**: Añade información contextual a las excepciones
4. **Logging Estructurado**: Registra errores con contexto completo
5. **Rollback Automático**: Revierte transacciones en caso de error

### Ejemplo de Manejo

```python
try:
    # Lógica de negocio
    result = await self.repository_facade.create_client(client_data)
    return result
except SQLAlchemyError as e:
    self._logger.error(f"Error de base de datos: {e}")
    await self.session.rollback()
    raise RepositoryError(
        message=f"Error creando cliente: {e}",
        operation="create_client",
        entity_type="Client",
        original_error=e
    )
except ValidationError:
    # Re-lanzar errores de validación sin modificar
    raise
except Exception as e:
    self._logger.error(f"Error inesperado: {e}")
    await self.session.rollback()
    raise DomainError(
        message=f"Error inesperado en servicio de dominio: {e}",
        operation="create_client",
        original_error=e
    )
```

## Configuración y Dependencias

### Dependencias Principales

```toml
[tool.poetry.dependencies]
python = "^3.11"
sqlalchemy = "^2.0.0"
loguru = "^0.7.0"
pendulum = "^3.0.0"
pydantic = "^2.0.0"
```

### Configuración del Servicio

```python
# Configuración a través de settings
from planificador.config.config import settings

# El servicio utiliza configuración centralizada
class ClientDomainService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._logger = logger.bind(
            service="ClientDomainService",
            environment=settings.environment
        )
```

## Patrones de Uso Recomendados

### 1. Inicialización del Servicio

```python
async def get_client_service(session: AsyncSession) -> ClientDomainService:
    """Factory function para crear instancia del servicio."""
    return ClientDomainService(session)

# Uso en controladores
async with async_session() as session:
    client_service = await get_client_service(session)
    result = await client_service.create_client(client_data)
    await session.commit()
```

### 2. Manejo de Transacciones

```python
# Patrón recomendado para operaciones transaccionales
async with async_session() as session:
    try:
        client_service = ClientDomainService(session)
        
        # Múltiples operaciones en la misma transacción
        client1 = await client_service.create_client(data1)
        client2 = await client_service.create_client(data2)
        
        # Commit explícito al final
        await session.commit()
        
    except Exception as e:
        # Rollback automático al salir del contexto
        logger.error(f"Error en transacción: {e}")
        raise
```

### 3. Validaciones Previas

```python
# Validar antes de crear
validation_result = await client_service.validate_client_creation(client_data)
if validation_result["is_valid"]:
    client = await client_service.create_client(client_data)
else:
    handle_validation_errors(validation_result["errors"])
```

## Extensibilidad y Evolución

### Añadir Nuevos Módulos

1. **Crear Interface**: Definir contrato en `interfaces/`
2. **Implementar Módulo**: Crear implementación en `modules/`
3. **Integrar en Facade**: Añadir al `ClientDomainService`
4. **Actualizar Exports**: Modificar `__init__.py`

### Ejemplo de Extensión

```python
# 1. Nueva interface
class IReportingOperations(ABC):
    @abstractmethod
    async def generate_client_report(self, client_id: UUID) -> Dict:
        pass

# 2. Implementación
class ReportingOperations(IReportingOperations):
    def __init__(self, session: AsyncSession, repository_facade: ClientRepositoryFacade):
        # Implementación...

# 3. Integración en facade
class ClientDomainService:
    def __init__(self, session: AsyncSession):
        # ... inicialización existente
        self.reporting = ReportingOperations(session, self.repository_facade)
```

### Versionado de API

- **Versionado Semántico**: Major.Minor.Patch
- **Compatibilidad Hacia Atrás**: Mantener métodos deprecated
- **Migración Gradual**: Proporcionar guías de migración
- **Documentación de Cambios**: Changelog detallado

## Métricas y Monitoreo

### Métricas Clave

1. **Performance**:
   - Tiempo de respuesta por operación
   - Throughput de operaciones por segundo
   - Uso de memoria y CPU

2. **Disponibilidad**:
   - Uptime del servicio
   - Tasa de errores por tipo
   - Tiempo de recuperación ante fallos

3. **Negocio**:
   - Número de clientes creados/actualizados
   - Patrones de uso por módulo
   - Tendencias de crecimiento

### Implementación de Monitoreo

```python
# Decorador para métricas automáticas
@monitor_performance
async def create_client(self, client_data: ClientCreate) -> Client:
    # Implementación...
    
# Logging estructurado con métricas
self._logger.info(
    "Cliente creado exitosamente",
    extra={
        "client_id": str(client.id),
        "operation": "create_client",
        "duration_ms": duration,
        "module": "CrudOperations"
    }
)
```

## Conclusiones

El **ClientDomainService** proporciona una arquitectura robusta y escalable para la gestión del dominio cliente, con las siguientes ventajas clave:

1. **Modularidad**: Separación clara de responsabilidades
2. **Extensibilidad**: Fácil adición de nuevas funcionalidades
3. **Mantenibilidad**: Código organizado y bien documentado
4. **Testabilidad**: Componentes aislados y fáciles de probar
5. **Performance**: Operaciones optimizadas y cacheo inteligente
6. **Robustez**: Manejo comprehensivo de errores y excepciones

Esta arquitectura establece las bases para un sistema escalable y mantenible que puede evolucionar con los requisitos del negocio.