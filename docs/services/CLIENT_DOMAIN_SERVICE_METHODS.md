# ClientDomainService - Métodos Disponibles

## Descripción General

El `ClientDomainService` es el servicio de dominio principal para la gestión integral de clientes. Implementa lógica de negocio compleja, coordinación entre dominios, análisis avanzado y gestión del ciclo de vida completo de clientes.

**Ubicación**: `src/planificador/services/domain/client/client_domain_service.py`

---

## 📋 Índice de Métodos

### [1. Operaciones CRUD con Validación y Dependencias](#operaciones-crud)
- [create_client_with_validation](#create_client_with_validation)
- [update_client_with_dependencies](#update_client_with_dependencies)
- [delete_client_with_cleanup](#delete_client_with_cleanup)

### [2. Búsqueda Avanzada y Consultas Complejas](#búsqueda-avanzada)
- [advanced_client_search](#advanced_client_search)
- [get_clients_by_complex_criteria](#get_clients_by_complex_criteria)

### [3. Gestión de Proyectos y Transferencias](#gestión-de-proyectos)
- [transfer_projects_between_clients](#transfer_projects_between_clients)
- [analyze_client_project_portfolio](#analyze_client_project_portfolio)

### [4. Análisis y Estadísticas de Negocio](#análisis-y-estadísticas)
- [generate_client_business_report](#generate_client_business_report)
- [get_client_performance_metrics](#get_client_performance_metrics)
- [generate_client_dashboard_data](#generate_client_dashboard_data)

### [5. Validación y Reglas de Negocio](#validación-y-reglas)
- [validate_complex_business_rules](#validate_complex_business_rules)
- [check_client_constraints](#check_client_constraints)

### [6. Coordinación Cross-Domain](#coordinación-cross-domain)
- [handle_client_lifecycle_event](#handle_client_lifecycle_event)
- [synchronize_client_data](#synchronize_client_data)

### [7. Métodos Privados de Soporte](#métodos-privados)

---

## Operaciones CRUD

### `create_client_with_validation`

**Descripción**: Crea un nuevo cliente con validaciones de negocio completas.

**Signatura**:
```python
async def create_client_with_validation(
    self,
    client_data: ClientCreateSchema,
    validate_dependencies: bool = True,
    notify_stakeholders: bool = True
) -> ClientResponseSchema
```

**Parámetros**:
- `client_data` (ClientCreateSchema): Datos del cliente a crear
- `validate_dependencies` (bool): Si validar dependencias externas (default: True)
- `notify_stakeholders` (bool): Si notificar a stakeholders (default: True)

**Retorna**: `ClientResponseSchema` - Cliente creado con información completa

**Excepciones**:
- `ClientBusinessRuleViolationError`: Si viola reglas de negocio
- `ClientValidationError`: Si los datos no son válidos
- `ClientDuplicateError`: Si ya existe un cliente similar

**Funcionalidades**:
- ✅ Validación de reglas de negocio antes de la creación
- ✅ Validación de dependencias externas
- ✅ Verificación de duplicados con lógica de negocio
- ✅ Ejecución de acciones post-creación
- ✅ Notificación a stakeholders

---

### `update_client_with_dependencies`

**Descripción**: Actualiza un cliente considerando dependencias y impacto en cascada.

**Signatura**:
```python
async def update_client_with_dependencies(
    self,
    client_id: int,
    update_data: ClientUpdateSchema,
    validate_impact: bool = True,
    cascade_updates: bool = True
) -> ClientResponseSchema
```

**Parámetros**:
- `client_id` (int): ID del cliente a actualizar
- `update_data` (ClientUpdateSchema): Datos de actualización
- `validate_impact` (bool): Si validar impacto en entidades relacionadas (default: True)
- `cascade_updates` (bool): Si propagar cambios a entidades dependientes (default: True)

**Retorna**: `ClientResponseSchema` - Cliente actualizado

**Excepciones**:
- `ClientNotFoundError`: Si el cliente no existe
- `ClientBusinessRuleViolationError`: Si viola reglas de negocio
- `ClientDependencyError`: Si hay conflictos de dependencias

**Funcionalidades**:
- ✅ Validación de reglas de negocio para actualización
- ✅ Validación de impacto en dependencias
- ✅ Propagación de cambios en cascada
- ✅ Comparación con estado anterior

---

### `delete_client_with_cleanup`

**Descripción**: Elimina un cliente con limpieza completa de datos relacionados.

**Signatura**:
```python
async def delete_client_with_cleanup(
    self,
    client_id: int,
    force_delete: bool = False,
    cleanup_related_data: bool = True
) -> bool
```

**Parámetros**:
- `client_id` (int): ID del cliente a eliminar
- `force_delete` (bool): Si forzar eliminación ignorando dependencias (default: False)
- `cleanup_related_data` (bool): Si limpiar datos relacionados (default: True)

**Retorna**: `bool` - True si la eliminación fue exitosa

**Excepciones**:
- `ClientNotFoundError`: Si el cliente no existe
- `ClientDependencyError`: Si tiene dependencias que impiden la eliminación

**Funcionalidades**:
- ✅ Validación de dependencias antes de eliminar
- ✅ Limpieza de datos relacionados
- ✅ Ejecución de acciones post-eliminación
- ✅ Opción de eliminación forzada

---

## Búsqueda Avanzada

### `advanced_client_search`

**Descripción**: Realiza búsqueda avanzada de clientes con criterios complejos.

**Signatura**:
```python
async def advanced_client_search(
    self,
    search_criteria: ClientSearchSchema,
    include_analytics: bool = False,
    include_relationships: bool = False
) -> Dict[str, Any]
```

**Parámetros**:
- `search_criteria` (ClientSearchSchema): Criterios de búsqueda
- `include_analytics` (bool): Si incluir datos analíticos (default: False)
- `include_relationships` (bool): Si incluir datos de relaciones (default: False)

**Retorna**: `Dict[str, Any]` - Resultados de búsqueda con metadatos

**Estructura de Respuesta**:
```python
{
    'clients': List[Dict],           # Clientes encontrados
    'metadata': Dict,                # Metadatos de búsqueda
    'total_count': int,              # Número total de resultados
    'search_criteria': Dict,         # Criterios utilizados
    'timestamp': str                 # Timestamp de la búsqueda
}
```

**Funcionalidades**:
- ✅ Búsqueda con criterios complejos
- ✅ Enriquecimiento opcional con analytics
- ✅ Inclusión opcional de relaciones
- ✅ Generación de metadatos de búsqueda

---

### `get_clients_by_complex_criteria`

**Descripción**: Obtiene clientes usando criterios complejos de filtrado.

**Signatura**:
```python
async def get_clients_by_complex_criteria(
    self,
    criteria: Dict[str, Any],
    sort_by: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[ClientResponseSchema]
```

**Parámetros**:
- `criteria` (Dict[str, Any]): Criterios de filtrado complejos
- `sort_by` (Optional[str]): Campo de ordenamiento
- `limit` (Optional[int]): Límite de resultados
- `offset` (Optional[int]): Desplazamiento de resultados

**Retorna**: `List[ClientResponseSchema]` - Lista de clientes que cumplen los criterios

**Funcionalidades**:
- ✅ Procesamiento de criterios complejos
- ✅ Ordenamiento flexible
- ✅ Paginación de resultados
- ✅ Validación de criterios

---

## Gestión de Proyectos

### `transfer_projects_between_clients`

**Descripción**: Transfiere proyectos entre clientes con validaciones de negocio.

**Signatura**:
```python
async def transfer_projects_between_clients(
    self,
    from_client_id: int,
    to_client_id: int,
    project_ids: Optional[List[int]] = None,
    validate_business_rules: bool = True
) -> Dict[str, Any]
```

**Parámetros**:
- `from_client_id` (int): ID del cliente origen
- `to_client_id` (int): ID del cliente destino
- `project_ids` (Optional[List[int]]): IDs específicos de proyectos (None = todos)
- `validate_business_rules` (bool): Si validar reglas de negocio (default: True)

**Retorna**: `Dict[str, Any]` - Resultado de la transferencia con detalles

**Excepciones**:
- `ClientProjectTransferError`: Si falla la transferencia
- `ClientNotFoundError`: Si algún cliente no existe

**Funcionalidades**:
- ✅ Validación de existencia de clientes
- ✅ Validación de reglas de transferencia
- ✅ Ejecución de transferencia
- ✅ Registro de eventos de transferencia

---

### `analyze_client_project_portfolio`

**Descripción**: Analiza el portafolio de proyectos de un cliente.

**Signatura**:
```python
async def analyze_client_project_portfolio(
    self,
    client_id: int,
    analysis_type: str = "comprehensive",
    date_range: Optional[Tuple[date, date]] = None
) -> Dict[str, Any]
```

**Parámetros**:
- `client_id` (int): ID del cliente
- `analysis_type` (str): Tipo de análisis (comprehensive, financial, timeline) (default: "comprehensive")
- `date_range` (Optional[Tuple[date, date]]): Rango de fechas para el análisis

**Retorna**: `Dict[str, Any]` - Análisis completo del portafolio

**Excepciones**:
- `ClientNotFoundError`: Si el cliente no existe
- `ClientAnalysisError`: Si falla el análisis

**Tipos de Análisis**:
- `comprehensive`: Análisis completo del portafolio
- `financial`: Enfoque en métricas financieras
- `timeline`: Análisis temporal de proyectos

**Funcionalidades**:
- ✅ Obtención de datos del portafolio
- ✅ Análisis según tipo especificado
- ✅ Enriquecimiento con insights de negocio
- ✅ Filtrado por rango de fechas

---

## Análisis y Estadísticas

### `generate_client_business_report`

**Descripción**: Genera un reporte de negocio completo para un cliente.

**Signatura**:
```python
async def generate_client_business_report(
    self,
    client_id: int,
    report_type: str = "comprehensive",
    include_projections: bool = True,
    date_range: Optional[Tuple[date, date]] = None
) -> Dict[str, Any]
```

**Parámetros**:
- `client_id` (int): ID del cliente
- `report_type` (str): Tipo de reporte (default: "comprehensive")
- `include_projections` (bool): Si incluir proyecciones (default: True)
- `date_range` (Optional[Tuple[date, date]]): Rango de fechas para el reporte

**Retorna**: `Dict[str, Any]` - Reporte de negocio completo

**Excepciones**:
- `ClientNotFoundError`: Si el cliente no existe
- `ClientReportGenerationError`: Si falla la generación del reporte

**Funcionalidades**:
- ✅ Recopilación de datos de múltiples fuentes
- ✅ Generación de métricas de negocio
- ✅ Inclusión opcional de proyecciones
- ✅ Análisis de tendencias

---

### `get_client_performance_metrics`

**Descripción**: Obtiene métricas de rendimiento detalladas de un cliente.

**Signatura**:
```python
async def get_client_performance_metrics(
    self,
    client_id: int,
    metric_types: Optional[List[str]] = None,
    period: str = "monthly",
    compare_previous: bool = True
) -> Dict[str, Any]
```

**Parámetros**:
- `client_id` (int): ID del cliente
- `metric_types` (Optional[List[str]]): Tipos específicos de métricas
- `period` (str): Período de análisis (monthly, quarterly, yearly) (default: "monthly")
- `compare_previous` (bool): Si comparar con período anterior (default: True)

**Retorna**: `Dict[str, Any]` - Métricas de rendimiento

**Tipos de Métricas**:
- `financial`: Métricas financieras
- `project`: Métricas de proyectos
- `timeline`: Métricas temporales
- `quality`: Métricas de calidad

**Funcionalidades**:
- ✅ Cálculo de métricas específicas
- ✅ Comparación con períodos anteriores
- ✅ Análisis de tendencias
- ✅ Generación de insights

---

### `generate_client_dashboard_data`

**Descripción**: Genera datos optimizados para dashboard de cliente.

**Signatura**:
```python
async def generate_client_dashboard_data(
    self,
    client_id: int,
    dashboard_type: str = "executive",
    real_time: bool = True
) -> Dict[str, Any]
```

**Parámetros**:
- `client_id` (int): ID del cliente
- `dashboard_type` (str): Tipo de dashboard (executive, operational, financial) (default: "executive")
- `real_time` (bool): Si incluir datos en tiempo real (default: True)

**Retorna**: `Dict[str, Any]` - Datos optimizados para dashboard

**Tipos de Dashboard**:
- `executive`: Vista ejecutiva de alto nivel
- `operational`: Vista operacional detallada
- `financial`: Vista financiera especializada

**Funcionalidades**:
- ✅ Agregación de datos optimizada
- ✅ Cálculo de KPIs clave
- ✅ Datos en tiempo real opcionales
- ✅ Formato optimizado para UI

---

## Validación y Reglas

### `validate_complex_business_rules`

**Descripción**: Valida reglas de negocio complejas para operaciones de cliente.

**Signatura**:
```python
async def validate_complex_business_rules(
    self,
    client_data: Union[ClientCreateSchema, ClientUpdateSchema],
    operation_type: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

**Parámetros**:
- `client_data` (Union[ClientCreateSchema, ClientUpdateSchema]): Datos del cliente
- `operation_type` (str): Tipo de operación (create, update, delete)
- `context` (Optional[Dict[str, Any]]): Contexto adicional para validación

**Retorna**: `Dict[str, Any]` - Resultado de validación con detalles

**Excepciones**:
- `ClientBusinessRuleViolationError`: Si viola alguna regla

**Reglas Validadas**:
- ✅ Longitud de nombres
- ✅ Campos obligatorios
- ✅ Dominios de email permitidos
- ✅ Límites de proyectos por cliente
- ✅ Transiciones de estado válidas

---

### `check_client_constraints`

**Descripción**: Verifica restricciones y limitaciones del cliente.

**Signatura**:
```python
async def check_client_constraints(
    self,
    client_id: int,
    constraint_types: Optional[List[str]] = None
) -> Dict[str, Any]
```

**Parámetros**:
- `client_id` (int): ID del cliente
- `constraint_types` (Optional[List[str]]): Tipos específicos de restricciones a verificar

**Retorna**: `Dict[str, Any]` - Estado de restricciones y limitaciones

**Tipos de Restricciones**:
- `project_limits`: Límites de proyectos
- `resource_allocation`: Asignación de recursos
- `budget_constraints`: Restricciones presupuestarias
- `timeline_constraints`: Restricciones temporales

**Funcionalidades**:
- ✅ Verificación de límites actuales
- ✅ Cálculo de capacidad disponible
- ✅ Alertas de proximidad a límites
- ✅ Recomendaciones de optimización

---

## Coordinación Cross-Domain

### `handle_client_lifecycle_event`

**Descripción**: Maneja eventos del ciclo de vida del cliente y coordina acciones cross-domain.

**Signatura**:
```python
async def handle_client_lifecycle_event(
    self,
    client_id: int,
    event_type: str,
    event_data: Dict[str, Any],
    propagate_to_domains: bool = True
) -> Dict[str, Any]
```

**Parámetros**:
- `client_id` (int): ID del cliente
- `event_type` (str): Tipo de evento del ciclo de vida
- `event_data` (Dict[str, Any]): Datos del evento
- `propagate_to_domains` (bool): Si propagar a otros dominios (default: True)

**Retorna**: `Dict[str, Any]` - Resultado del manejo del evento

**Tipos de Eventos**:
- `client_created`: Cliente creado
- `client_activated`: Cliente activado
- `client_suspended`: Cliente suspendido
- `client_deleted`: Cliente eliminado
- `status_changed`: Cambio de estado

**Funcionalidades**:
- ✅ Procesamiento de eventos del ciclo de vida
- ✅ Coordinación con otros dominios
- ✅ Ejecución de acciones automáticas
- ✅ Registro de eventos para auditoría

---

### `synchronize_client_data`

**Descripción**: Sincroniza datos del cliente entre diferentes dominios y sistemas.

**Signatura**:
```python
async def synchronize_client_data(
    self,
    client_id: int,
    target_domains: Optional[List[str]] = None,
    sync_type: str = "full",
    force_sync: bool = False
) -> Dict[str, Any]
```

**Parámetros**:
- `client_id` (int): ID del cliente
- `target_domains` (Optional[List[str]]): Dominios específicos a sincronizar
- `sync_type` (str): Tipo de sincronización (full, incremental, selective) (default: "full")
- `force_sync` (bool): Si forzar sincronización ignorando timestamps (default: False)

**Retorna**: `Dict[str, Any]` - Resultado de la sincronización

**Tipos de Sincronización**:
- `full`: Sincronización completa de todos los datos
- `incremental`: Solo cambios desde última sincronización
- `selective`: Solo campos específicos

**Dominios de Sincronización**:
- `projects`: Dominio de proyectos
- `employees`: Dominio de empleados
- `planning`: Dominio de planificación
- `analytics`: Dominio de análisis

**Funcionalidades**:
- ✅ Detección de cambios automática
- ✅ Resolución de conflictos
- ✅ Sincronización bidireccional
- ✅ Registro de sincronización para auditoría

---

## Métodos Privados

### Métodos de Validación
- `_validate_business_rules_for_creation()`: Validación para creación
- `_validate_business_rules_for_update()`: Validación para actualización
- `_validate_external_dependencies()`: Validación de dependencias externas
- `_validate_update_impact()`: Validación de impacto de actualización
- `_validate_deletion_dependencies()`: Validación para eliminación
- `_validate_project_transfer_rules()`: Validación de transferencia de proyectos

### Métodos de Procesamiento
- `_check_for_business_duplicates()`: Verificación de duplicados
- `_execute_post_creation_actions()`: Acciones post-creación
- `_execute_cascade_updates()`: Actualizaciones en cascada
- `_cleanup_related_data()`: Limpieza de datos relacionados
- `_execute_post_deletion_actions()`: Acciones post-eliminación

### Métodos de Análisis
- `_get_client_analytics()`: Obtención de analytics
- `_get_client_relationships()`: Obtención de relaciones
- `_generate_search_metadata()`: Generación de metadatos de búsqueda
- `_process_complex_criteria()`: Procesamiento de criterios complejos
- `_get_client_portfolio_data()`: Datos del portafolio
- `_execute_portfolio_analysis()`: Ejecución de análisis de portafolio
- `_enrich_portfolio_analysis()`: Enriquecimiento de análisis

### Métodos de Coordinación
- `_execute_project_transfer()`: Ejecución de transferencia
- `_register_transfer_event()`: Registro de evento de transferencia
- `_collect_business_data()`: Recopilación de datos de negocio
- `_generate_business_metrics()`: Generación de métricas de negocio
- `_calculate_performance_metrics()`: Cálculo de métricas de rendimiento
- `_aggregate_dashboard_data()`: Agregación de datos de dashboard

---

## 🔧 Configuración de Reglas de Negocio

El servicio utiliza las siguientes reglas de negocio configurables:

```python
_business_rules = {
    'min_name_length': 2,                    # Longitud mínima del nombre
    'max_name_length': 100,                  # Longitud máxima del nombre
    'required_fields': ['name', 'email'],    # Campos obligatorios
    'email_domains_allowed': [...],          # Dominios de email permitidos
    'max_projects_per_client': 50,           # Máximo proyectos por cliente
    'client_status_transitions': {           # Transiciones de estado válidas
        'active': ['inactive', 'suspended'],
        'inactive': ['active'],
        'suspended': ['active', 'inactive']
    }
}
```

---

## 📊 Métricas y Logging

Todos los métodos incluyen:
- ✅ **Logging estructurado** con Loguru
- ✅ **Manejo de excepciones** específicas del dominio
- ✅ **Métricas de rendimiento** automáticas
- ✅ **Auditoría de operaciones** completa
- ✅ **Contexto enriquecido** en logs y errores

---

## 🚀 Uso Recomendado

### Ejemplo de Uso Básico
```python
# Inicializar servicio
client_service = ClientDomainService(session)

# Crear cliente con validación completa
client = await client_service.create_client_with_validation(
    client_data=ClientCreateSchema(...),
    validate_dependencies=True,
    notify_stakeholders=True
)

# Búsqueda avanzada
results = await client_service.advanced_client_search(
    search_criteria=ClientSearchSchema(...),
    include_analytics=True,
    include_relationships=True
)

# Generar reporte de negocio
report = await client_service.generate_client_business_report(
    client_id=1,
    report_type="comprehensive",
    include_projections=True
)
```

### Ejemplo de Coordinación Cross-Domain
```python
# Manejar evento del ciclo de vida
await client_service.handle_client_lifecycle_event(
    client_id=1,
    event_type="client_activated",
    event_data={"activation_reason": "contract_signed"},
    propagate_to_domains=True
)

# Sincronizar datos entre dominios
sync_result = await client_service.synchronize_client_data(
    client_id=1,
    target_domains=["projects", "planning"],
    sync_type="incremental"
)
```

---

**Última actualización**: {timestamp}
**Versión del servicio**: 1.0.0
**Autor**: Planificador Development Team