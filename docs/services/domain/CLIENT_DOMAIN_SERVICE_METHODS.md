# Métodos Disponibles en ClientDomainService

**Última actualización:** Enero 2025

## Descripción General

`ClientDomainService` es el servicio de dominio principal para la gestión integral de clientes en el sistema. Implementa lógica de negocio compleja, coordinación entre dominios, análisis avanzado y gestión del ciclo de vida completo de clientes, proporcionando una capa de abstracción de alto nivel que encapsula las reglas de negocio y coordina las operaciones entre diferentes repositorios y servicios.

El servicio integra validaciones de negocio, análisis estadístico, gestión de proyectos, coordinación cross-domain y generación de reportes, ofreciendo una API coherente para todas las operaciones complejas relacionadas con clientes.

---

## Métodos Disponibles

### 1. Operaciones CRUD con Validación y Dependencias (3 métodos)

1. `create_client_with_validation(client_data: ClientCreateSchema, validate_dependencies: bool = True, notify_stakeholders: bool = True) -> ClientResponseSchema` - Crea un nuevo cliente con validaciones de negocio completas y notificación a stakeholders
2. `update_client_with_dependencies(client_id: int, update_data: ClientUpdateSchema, validate_impact: bool = True, cascade_updates: bool = True) -> ClientResponseSchema` - Actualiza un cliente considerando dependencias y propagando cambios en cascada
3. `delete_client_with_cleanup(client_id: int, force_delete: bool = False, cleanup_related_data: bool = True) -> bool` - Elimina un cliente con limpieza completa de datos relacionados y validación de dependencias

### 2. Búsqueda Avanzada y Consultas Complejas (2 métodos)

4. `advanced_client_search(search_criteria: ClientSearchSchema, include_analytics: bool = False, include_relationships: bool = False) -> Dict[str, Any]` - Realiza búsqueda avanzada de clientes con criterios complejos y enriquecimiento opcional
5. `get_clients_by_complex_criteria(criteria: Dict[str, Any], sort_by: Optional[str] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ClientResponseSchema]` - Obtiene clientes usando criterios complejos de filtrado con paginación y ordenamiento

### 3. Gestión de Proyectos y Transferencias (2 métodos)

6. `transfer_projects_between_clients(from_client_id: int, to_client_id: int, project_ids: Optional[List[int]] = None, validate_business_rules: bool = True) -> Dict[str, Any]` - Transfiere proyectos entre clientes con validaciones de negocio y registro de eventos
7. `analyze_client_project_portfolio(client_id: int, analysis_type: str = "comprehensive", date_range: Optional[Tuple[date, date]] = None) -> Dict[str, Any]` - Analiza el portafolio de proyectos de un cliente con diferentes tipos de análisis

### 4. Análisis y Estadísticas de Negocio (3 métodos)

8. `generate_client_business_report(client_id: int, report_type: str = "comprehensive", include_projections: bool = True, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, Any]` - Genera un reporte de negocio completo para un cliente con proyecciones opcionales
9. `get_client_performance_metrics(client_id: int, metric_types: Optional[List[str]] = None, period: str = "monthly", compare_previous: bool = True) -> Dict[str, Any]` - Obtiene métricas de rendimiento detalladas con comparación temporal
10. `generate_client_dashboard_data(client_id: int, dashboard_type: str = "executive", real_time: bool = True) -> Dict[str, Any]` - Genera datos optimizados para dashboard con diferentes vistas especializadas

### 5. Validación y Reglas de Negocio (2 métodos)

11. `validate_complex_business_rules(client_data: Union[ClientCreateSchema, ClientUpdateSchema], operation_type: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]` - Valida reglas de negocio complejas para operaciones de cliente con contexto adicional
12. `check_client_constraints(client_id: int, constraint_types: Optional[List[str]] = None) -> Dict[str, Any]` - Verifica restricciones y limitaciones del cliente con alertas de proximidad a límites

### 6. Coordinación Cross-Domain (2 métodos)

13. `handle_client_lifecycle_event(client_id: int, event_type: str, event_data: Dict[str, Any], propagate_to_domains: bool = True) -> Dict[str, Any]` - Maneja eventos del ciclo de vida del cliente y coordina acciones cross-domain
14. `synchronize_client_data(client_id: int, target_domains: Optional[List[str]] = None, sync_type: str = "full", force_sync: bool = False) -> Dict[str, Any]` - Sincroniza datos del cliente entre diferentes dominios y sistemas con resolución de conflictos

---

## Resumen de Funcionalidades

### Total de Métodos Públicos: 14

**Distribución por Categorías:**
- Operaciones CRUD con Validación y Dependencias: 3 métodos (21%)
- Búsqueda Avanzada y Consultas Complejas: 2 métodos (14%)
- Gestión de Proyectos y Transferencias: 2 métodos (14%)
- Análisis y Estadísticas de Negocio: 3 métodos (21%)
- Validación y Reglas de Negocio: 2 métodos (14%)
- Coordinación Cross-Domain: 2 métodos (14%)

### Características Principales

- **Lógica de Negocio Compleja**: Implementación de reglas de negocio avanzadas con validación contextual
- **Coordinación Cross-Domain**: Sincronización y eventos entre diferentes dominios del sistema
- **Análisis Avanzado**: Generación de reportes, métricas y análisis de portafolio con proyecciones
- **Validación Robusta**: Sistema completo de validación con reglas de negocio configurables
- **Gestión de Dependencias**: Manejo inteligente de dependencias y propagación de cambios
- **Búsqueda Inteligente**: Consultas complejas con enriquecimiento de datos y metadatos
- **API Asíncrona**: Operaciones no bloqueantes optimizadas para alta concurrencia
- **Auditoría Completa**: Registro detallado de operaciones y eventos para compliance

### Reglas de Negocio Configurables

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

### Integración con Otros Módulos

- **ClientRepositoryFacade**: Acceso unificado a datos de clientes con operaciones especializadas
- **Project Domain**: Coordinación para transferencias y análisis de portafolio de proyectos
- **Analytics Engine**: Generación de métricas, reportes y análisis de tendencias
- **Event System**: Manejo de eventos del ciclo de vida y notificaciones cross-domain
- **Validation Framework**: Sistema robusto de validación con esquemas Pydantic
- **Logging System**: Registro estructurado con Loguru para auditoría y debugging
- **Configuration Management**: Reglas de negocio configurables y externalizadas
- **Exception Handling**: Jerarquía de excepciones específicas del dominio cliente

### Casos de Uso Principales

- **Gestión Integral de Clientes**: Ciclo de vida completo con validaciones de negocio avanzadas
- **Análisis de Negocio**: Reportes ejecutivos, métricas de rendimiento y análisis de portafolio
- **Coordinación de Dominios**: Sincronización de datos y eventos entre diferentes módulos
- **Validación Avanzada**: Reglas de negocio complejas con contexto y dependencias
- **Gestión de Proyectos**: Transferencias inteligentes y análisis de portafolio por cliente
- **Dashboard Ejecutivo**: Datos optimizados para diferentes tipos de visualización
- **Búsqueda Empresarial**: Consultas complejas con enriquecimiento de datos y analytics
- **Auditoría y Compliance**: Registro completo de operaciones y eventos para regulaciones

### Tipos de Análisis Disponibles

**Análisis de Portafolio:**
- `comprehensive`: Análisis completo del portafolio con todas las métricas
- `financial`: Enfoque en métricas financieras y rentabilidad
- `timeline`: Análisis temporal de proyectos y tendencias

**Tipos de Dashboard:**
- `executive`: Vista ejecutiva de alto nivel con KPIs estratégicos
- `operational`: Vista operacional detallada para gestión diaria
- `financial`: Vista financiera especializada para análisis económico

**Tipos de Métricas:**
- `financial`: Métricas financieras y de rentabilidad
- `project`: Métricas de proyectos y entregables
- `timeline`: Métricas temporales y de cumplimiento
- `quality`: Métricas de calidad y satisfacción

### Tipos de Sincronización Cross-Domain

- `full`: Sincronización completa de todos los datos del cliente
- `incremental`: Solo cambios desde la última sincronización
- `selective`: Sincronización de campos específicos según configuración

**Dominios de Sincronización:**
- `projects`: Dominio de proyectos y asignaciones
- `employees`: Dominio de empleados y recursos humanos
- `planning`: Dominio de planificación y cronogramas
- `analytics`: Dominio de análisis y métricas

### Eventos del Ciclo de Vida

- `client_created`: Cliente creado con validaciones completas
- `client_activated`: Cliente activado y listo para operaciones
- `client_suspended`: Cliente suspendido temporalmente
- `client_deleted`: Cliente eliminado con limpieza de datos
- `status_changed`: Cambio de estado con validación de transiciones

---

**Ubicación**: `src/planificador/services/domain/client/client_domain_service.py`
**Versión del servicio**: 1.0.0
**Autor**: Planificador Development Team