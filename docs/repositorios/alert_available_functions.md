# Funciones Disponibles en AlertRepositoryFacade

**Última actualización:** Enero 2025

## Descripción General

`AlertRepositoryFacade` es la clase principal que proporciona una interfaz unificada para todas las operaciones relacionadas con alertas en el sistema. Esta fachada encapsula la lógica de acceso a datos y coordina las operaciones entre diferentes módulos especializados, ofreciendo una API coherente y fácil de usar para la gestión completa de alertas.

La fachada integra 5 módulos especializados que manejan diferentes aspectos de las operaciones con alertas: operaciones CRUD, consultas avanzadas, estadísticas y métricas, gestión de estados y validación de datos.

---

## Métodos Disponibles

### 1. Operaciones CRUD (5 métodos)

1. `create_alert(alert_data: Dict[str, Any]) -> Alert` - Crea una nueva alerta con validaciones completas
2. `get_by_id(alert_id: int) -> Optional[Alert]` - Obtiene una alerta por su ID único
3. `get_by_unique_field(field_name: str, field_value: Any) -> Optional[Alert]` - Obtiene una alerta por un campo único específico
4. `update_alert(alert_id: int, update_data: Dict[str, Any]) -> Alert` - Actualiza una alerta existente con validaciones
5. `delete_alert(alert_id: int) -> bool` - Elimina una alerta del sistema

### 2. Operaciones de Consulta por Tipo y Estado (7 métodos)

6. `find_by_type(alert_type: AlertType) -> List[Alert]` - Obtiene alertas por tipo específico
7. `find_by_status(status: AlertStatus) -> List[Alert]` - Obtiene alertas por estado específico
8. `get_active_alerts() -> List[Alert]` - Obtiene todas las alertas activas (NEW y READ)
9. `get_critical_alerts() -> List[Alert]` - Obtiene alertas críticas activas
10. `get_unread_alerts() -> List[Alert]` - Obtiene alertas no leídas (estado NEW)
11. `get_alerts_with_relations() -> List[Alert]` - Obtiene todas las alertas con sus relaciones cargadas
12. `get_with_relations(alert_id: int) -> Optional[Alert]` - Obtiene alerta específica con todas sus relaciones cargadas

### 3. Operaciones de Consulta por Entidades Relacionadas (2 métodos)

13. `find_by_employee(employee_id: int) -> List[Alert]` - Obtiene alertas asociadas a un empleado específico
14. `find_by_project(project_id: int) -> List[Alert]` - Obtiene alertas asociadas a un proyecto específico

### 4. Operaciones de Consulta Temporal (5 métodos)

15. `find_by_date_range(start_date: datetime, end_date: datetime) -> List[Alert]` - Obtiene alertas en un rango de fechas específico
16. `get_old_resolved_alerts(days_old: int = 30) -> List[Alert]` - Obtiene alertas resueltas antiguas para limpieza
17. `get_current_week_alerts() -> List[Alert]` - Obtiene alertas de la semana actual
18. `get_current_month_alerts() -> List[Alert]` - Obtiene alertas del mes actual
19. `count_alerts_by_date_range(start_date: datetime, end_date: datetime) -> int` - Cuenta alertas en un rango de fechas

### 5. Operaciones de Consulta Avanzada (2 métodos)

20. `get_all_with_filters(filters: Dict[str, Any]) -> List[Alert]` - Obtiene alertas con filtros dinámicos aplicados
21. `bulk_create_alerts(alerts_data: List[Dict[str, Any]]) -> List[Alert]` - Crea múltiples alertas en lote con validaciones

### 6. Gestión de Estados de Alertas (12 métodos)

22. `acknowledge_alert(alert_id: int, acknowledged_by: str) -> Alert` - Marca una alerta como reconocida (READ)
23. `resolve_alert(alert_id: int, resolved_by: str, resolution_notes: Optional[str] = None) -> Alert` - Marca una alerta como resuelta
24. `dismiss_alert(alert_id: int, dismissed_by: str, dismissal_reason: Optional[str] = None) -> Alert` - Descarta una alerta (IGNORED)
25. `bulk_acknowledge_alerts(alert_ids: List[int], acknowledged_by: str) -> List[Alert]` - Reconoce múltiples alertas en lote
26. `bulk_resolve_alerts(alert_ids: List[int], resolved_by: str, resolution_notes: Optional[str] = None) -> List[Alert]` - Resuelve múltiples alertas en lote
27. `cleanup_old_alerts(days_old: int = 90) -> int` - Limpia alertas antiguas resueltas o descartadas
28. `get_valid_state_transitions(current_status: AlertStatus) -> List[AlertStatus]` - Obtiene transiciones de estado válidas
29. `can_transition_to_state(current_status: AlertStatus, target_status: AlertStatus) -> bool` - Verifica si se puede transicionar a un estado
30. `mark_as_read(alert_id: int) -> Alert` - Marca una alerta como leída
31. `mark_as_resolved(alert_id: int) -> Alert` - Marca una alerta como resuelta
32. `mark_as_ignored(alert_id: int) -> Alert` - Marca una alerta como ignorada
33. `reactivate_alert(alert_id: int) -> Alert` - Reactiva una alerta previamente resuelta o ignorada

### 7. Operaciones de Estado en Lote (6 métodos)

34. `mark_multiple_as_read(alert_ids: List[int]) -> List[Alert]` - Marca múltiples alertas como leídas
35. `mark_all_as_read_for_employee(employee_id: int) -> int` - Marca todas las alertas de un empleado como leídas
36. `resolve_multiple_alerts(alert_ids: List[int]) -> List[Alert]` - Resuelve múltiples alertas en una operación
37. `cleanup_old_resolved_alerts(days_old: int = 30) -> int` - Limpia alertas resueltas antiguas específicamente
38. `get_state_transition_summary() -> Dict[str, Any]` - Obtiene resumen de transiciones de estado del sistema
39. `format_alert_created_at(alert: Alert, format_str: str = 'YYYY-MM-DD HH:mm:ss') -> str` - Formatea la fecha de creación de una alerta

### 8. Estadísticas y Métricas Básicas (8 métodos)

40. `get_alert_statistics(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]` - Obtiene estadísticas generales de alertas
41. `get_alert_counts_by_status() -> Dict[str, int]` - Obtiene conteo de alertas por estado
42. `get_alert_counts_by_type() -> Dict[str, int]` - Obtiene conteo de alertas por tipo
43. `get_alert_trends(days: int = 30, group_by: str = 'day') -> List[Dict[str, Any]]` - Obtiene tendencias de alertas en período específico
44. `get_alert_response_time_stats() -> Dict[str, float]` - Calcula estadísticas de tiempo de respuesta
45. `get_alerts_by_employee_stats(limit: int = 10) -> List[Dict[str, Any]]` - Obtiene estadísticas de alertas por empleado
46. `get_alerts_by_project_stats(limit: int = 10) -> List[Dict[str, Any]]` - Obtiene estadísticas de alertas por proyecto
47. `get_critical_alerts_summary() -> Dict[str, Any]` - Obtiene resumen de alertas críticas

### 9. Estadísticas y Métricas Avanzadas (8 métodos)

48. `get_performance_metrics() -> Dict[str, Any]` - Obtiene métricas de rendimiento del sistema de alertas
49. `count_total_alerts() -> int` - Cuenta el total de alertas en el sistema
50. `count_by_status(status: AlertStatus) -> int` - Cuenta alertas por estado específico
51. `count_by_type(alert_type: AlertType) -> int` - Cuenta alertas por tipo específico
52. `count_unread_alerts() -> int` - Cuenta alertas no leídas en el sistema
53. `count_critical_alerts() -> int` - Cuenta alertas críticas activas
54. `count_by_employee(employee_id: int) -> int` - Cuenta alertas por empleado específico
55. `get_employee_alert_summary(employee_id: int) -> Dict[str, Any]` - Obtiene resumen de alertas por empleado

### 10. Estadísticas Temporales (4 métodos)

56. `get_daily_alert_counts(days: int = 30) -> Dict[str, int]` - Obtiene conteos diarios de alertas
57. `get_weekly_statistics() -> Dict[str, Any]` - Obtiene estadísticas semanales consolidadas
58. `get_monthly_statistics() -> Dict[str, Any]` - Obtiene estadísticas mensuales consolidadas
59. `get_comprehensive_statistics() -> Dict[str, Any]` - Obtiene estadísticas comprehensivas del sistema

### 11. Validaciones de Datos (10 métodos)

60. `validate_alert_data(alert_data: Dict[str, Any]) -> Dict[str, Any]` - Valida y normaliza datos de alerta
61. `validate_bulk_data(alerts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]` - Valida datos de múltiples alertas
62. `validate_update_data(update_data: Dict[str, Any]) -> Dict[str, Any]` - Valida datos para actualización de alerta
63. `validate_alert_exists(alert_id: int) -> bool` - Valida que una alerta existe en el sistema
64. `validate_employee_exists(employee_id: int) -> bool` - Valida que un empleado existe en el sistema
65. `validate_project_exists(project_id: int) -> bool` - Valida que un proyecto existe en el sistema
66. `validate_alert_consistency(alert_id: int) -> List[str]` - Valida la consistencia de una alerta específica
67. `validate_duplicate_alert(title: str, user_id: int, type_alert: AlertType) -> bool` - Valida si existe una alerta duplicada
68. `validate_alert_limit_per_user(user_id: int, limit: int = 50) -> bool` - Valida el límite de alertas por usuario
69. `validate_critical_alert_escalation(alert_id: int, hours_threshold: int = 24) -> bool` - Valida si una alerta crítica necesita escalación

### 12. Validaciones Avanzadas y Reportes (2 métodos)

70. `validate_multiple_alerts(alert_ids: List[int]) -> Dict[int, List[str]]` - Valida múltiples alertas y retorna errores por ID
71. `get_data_integrity_report() -> Dict[str, Any]` - Obtiene reporte de integridad de datos del sistema

### 13. Utilidades y Salud del Sistema (1 método)

72. `get_repository_health() -> Dict[str, Any]` - Obtiene el estado de salud completo del repositorio

---

## Resumen de Funcionalidades

### Total de Métodos Públicos: 72

**Distribución por Categorías:**
- Operaciones CRUD: 5 métodos (7%)
- Operaciones de Consulta por Tipo y Estado: 7 métodos (10%)
- Operaciones de Consulta por Entidades Relacionadas: 2 métodos (3%)
- Operaciones de Consulta Temporal: 5 métodos (7%)
- Operaciones de Consulta Avanzada: 2 métodos (3%)
- Gestión de Estados de Alertas: 12 métodos (17%)
- Operaciones de Estado en Lote: 6 métodos (8%)
- Estadísticas y Métricas Básicas: 8 métodos (11%)
- Estadísticas y Métricas Avanzadas: 8 métodos (11%)
- Estadísticas Temporales: 4 métodos (6%)
- Validaciones de Datos: 10 métodos (14%)
- Validaciones Avanzadas y Reportes: 2 métodos (3%)
- Utilidades y Salud del Sistema: 1 método (1%)

### Características Principales

- **Gestión Completa de Alertas**: CRUD completo con validación robusta de datos y reglas de negocio
- **Sistema de Estados Avanzado**: Gestión completa del ciclo de vida de alertas con transiciones validadas
- **Consultas Especializadas**: Búsquedas por múltiples criterios, filtros temporales y entidades relacionadas
- **Validación Exhaustiva**: 12 métodos especializados para garantizar integridad de datos y consistencia
- **Análisis Estadístico Completo**: Métricas detalladas, tendencias temporales y dashboard ejecutivo
- **Operaciones en Lote**: Procesamiento eficiente de múltiples alertas simultáneamente
- **Monitoreo de Salud**: Verificación del estado y rendimiento del sistema de alertas
- **API Asíncrona**: Operaciones no bloqueantes para mejor rendimiento en aplicaciones concurrentes
- **Gestión de Fechas Avanzada**: Integración con Pendulum para manejo robusto de fechas y zonas horarias
- **Limpieza Automática**: Herramientas para mantenimiento y limpieza de alertas antiguas

### Integración con Otros Módulos

- **Employee**: Gestión de alertas por empleado y estadísticas de asignación
- **Project**: Asociación de alertas con proyectos específicos y seguimiento
- **Database**: Integración completa con modelos SQLAlchemy y operaciones transaccionales
- **Validation**: Sistema robusto de validación con esquemas Pydantic (AlertCreate, AlertUpdate, AlertSearchFilter)
- **Logging**: Registro estructurado de operaciones con Loguru para auditoría y debugging
- **Statistics**: Análisis de tendencias, métricas de rendimiento y dashboard de gestión
- **State Management**: Control completo del ciclo de vida y transiciones de estado de alertas

### Casos de Uso Principales

- **Sistema de Notificaciones**: Creación, gestión y seguimiento de alertas del sistema
- **Monitoreo de Proyectos**: Alertas relacionadas con el estado y progreso de proyectos
- **Gestión de Empleados**: Notificaciones y alertas específicas por empleado
- **Análisis de Rendimiento**: Estadísticas y métricas para evaluación del sistema
- **Dashboard Ejecutivo**: Métricas consolidadas para toma de decisiones estratégicas
- **Mantenimiento del Sistema**: Limpieza automática y validación de integridad de datos
- **Auditoría y Compliance**: Registro detallado de operaciones para cumplimiento normativo
- **Escalación de Incidentes**: Gestión de alertas críticas y procesos de escalación
- **Reportes Gerenciales**: Análisis de tendencias y estadísticas para reportes ejecutivos
- **Gestión de Estados**: Control completo del flujo de trabajo de alertas desde creación hasta resolución