# Funciones Disponibles en Alert Repository

**Fecha de actualización:** 19 de agosto de 2025

## Módulos y Funciones

### AlertRepository (alert_repository.py)

#### Operaciones CRUD Básicas (5 funciones)
1. `create_alert(alert_data: Dict[str, Any]) -> Alert` - Crea una nueva alerta con validaciones completas
2. `update_alert(alert_id: int, update_data: Dict[str, Any]) -> Alert` - Actualiza una alerta existente con validaciones
3. `bulk_create_alerts(alerts_data: List[Dict[str, Any]]) -> List[Alert]` - Crea múltiples alertas en lote con validaciones
4. `get_by_id(alert_id: int) -> Optional[Alert]` - Obtiene alerta por ID (heredado de BaseRepository)
5. `delete_alert(alert_id: int) -> bool` - Elimina una alerta del sistema

#### Consultas por Tipo y Estado (7 funciones)
6. `find_by_type(alert_type: AlertType) -> List[Alert]` - Obtiene alertas por tipo específico
7. `find_by_status(status: AlertStatus) -> List[Alert]` - Obtiene alertas por estado específico
8. `get_active_alerts() -> List[Alert]` - Obtiene todas las alertas activas (NEW y READ)
9. `get_critical_alerts() -> List[Alert]` - Obtiene alertas críticas activas
10. `get_unread_alerts() -> List[Alert]` - Obtiene alertas no leídas (estado NEW)
11. `get_alerts_with_relations() -> List[Alert]` - Obtiene todas las alertas con sus relaciones cargadas
12. `get_with_relations(alert_id: int) -> Optional[Alert]` - Obtiene alerta específica con todas sus relaciones cargadas

#### Consultas por Entidades Relacionadas (2 funciones)
11. `find_by_employee(employee_id: int) -> List[Alert]` - Obtiene alertas asociadas a un empleado específico
12. `find_by_project(project_id: int) -> List[Alert]` - Obtiene alertas asociadas a un proyecto específico

#### Consultas Temporales (2 funciones)
13. `find_by_date_range(start_date: datetime, end_date: datetime) -> List[Alert]` - Obtiene alertas en un rango de fechas
14. `get_old_resolved_alerts(days_old: int = 30) -> List[Alert]` - Obtiene alertas resueltas antiguas para limpieza

#### Gestión de Estados de Alertas (3 funciones)
15. `acknowledge_alert(alert_id: int, acknowledged_by: str) -> Alert` - Marca una alerta como reconocida (READ)
16. `resolve_alert(alert_id: int, resolved_by: str, resolution_notes: Optional[str] = None) -> Alert` - Marca una alerta como resuelta
17. `dismiss_alert(alert_id: int, dismissed_by: str, dismissal_reason: Optional[str] = None) -> Alert` - Descarta una alerta (IGNORED)

#### Operaciones en Lote (2 funciones)
18. `bulk_acknowledge_alerts(alert_ids: List[int], acknowledged_by: str) -> List[Alert]` - Reconoce múltiples alertas en lote
19. `bulk_resolve_alerts(alert_ids: List[int], resolved_by: str, resolution_notes: Optional[str] = None) -> List[Alert]` - Resuelve múltiples alertas en lote

#### Limpieza y Mantenimiento (1 función)
20. `cleanup_old_alerts(days_old: int = 90) -> int` - Limpia alertas antiguas resueltas o descartadas

#### Funciones de Utilidad (8 funciones)
21. `get_valid_state_transitions(current_status: AlertStatus) -> List[AlertStatus]` - Obtiene transiciones de estado válidas
22. `can_transition_to_state(current_status: AlertStatus, target_status: AlertStatus) -> bool` - Verifica si se puede transicionar a un estado
23. `get_current_week_alerts() -> List[Alert]` - Obtiene alertas de la semana actual
24. `get_current_month_alerts() -> List[Alert]` - Obtiene alertas del mes actual
25. `count_alerts_by_date_range(start_date: datetime, end_date: datetime) -> int` - Cuenta alertas en un rango de fechas
26. `format_alert_created_at(alert: Alert, format_str: str = 'YYYY-MM-DD HH:mm:ss') -> str` - Formatea la fecha de creación de una alerta
27. `get_alert_statistics(start_date=None, end_date=None) -> Dict[str, Any]` - Obtiene estadísticas generales de alertas
28. `get_all_with_filters(filters: Dict[str, Any]) -> List[Alert]` - Obtiene alertas con filtros dinámicos

#### Métodos Alias para Compatibilidad (6 funciones)
29. `get_by_employee(user_id: int) -> List[Alert]` - Alias para query_builder.get_by_employee
30. `get_by_status(status: AlertStatus) -> List[Alert]` - Alias para query_builder.get_by_status
31. `get_by_type(alert_type: AlertType) -> List[Alert]` - Alias para query_builder.get_by_alert_type
32. `get_by_date_range(start_date, end_date) -> List[Alert]` - Alias para query_builder.get_by_date_range
33. `find_by_employee(user_id: int) -> List[Alert]` - Delega a query_builder.get_by_employee
34. `find_by_type(alert_type: AlertType) -> List[Alert]` - Delega a query_builder.get_by_alert_type

#### Estadísticas y Métricas (8 funciones)
35. `get_alert_counts_by_status() -> Dict[str, int]` - Obtiene conteo de alertas por estado
36. `get_alert_counts_by_type() -> Dict[str, int]` - Obtiene conteo de alertas por tipo
37. `get_alert_trends(days: int = 30, group_by: str = 'day') -> List[Dict[str, Any]]` - Obtiene tendencias de alertas en período específico
38. `get_alert_response_time_stats() -> Dict[str, float]` - Calcula estadísticas de tiempo de respuesta
39. `get_alerts_by_employee_stats(limit: int = 10) -> List[Dict[str, Any]]` - Obtiene estadísticas de alertas por empleado
40. `get_alerts_by_project_stats(limit: int = 10) -> List[Dict[str, Any]]` - Obtiene estadísticas de alertas por proyecto
41. `get_critical_alerts_summary() -> Dict[str, Any]` - Obtiene resumen de alertas críticas
42. `get_performance_metrics() -> Dict[str, Any]` - Obtiene métricas de rendimiento del sistema de alertas

---

### AlertQueryBuilder (alert_query_builder.py)

#### Consultas Base por Tipo y Estado (4 funciones)
43. `get_by_type(alert_type: AlertType) -> List[Alert]` - Busca alertas por tipo específico
44. `get_by_alert_type(alert_type: AlertType) -> List[Alert]` - Busca alertas por tipo (método alternativo)
45. `get_by_status(status: AlertStatus) -> List[Alert]` - Busca alertas por estado específico
46. `get_active_alerts() -> List[Alert]` - Obtiene alertas activas (NEW y READ)

#### Consultas por Entidades Relacionadas (2 funciones)
47. `get_by_employee(employee_id: int) -> List[Alert]` - Obtiene alertas de un empleado específico
48. `get_by_project(project_id: int) -> List[Alert]` - Obtiene alertas de un proyecto específico

#### Consultas Temporales (1 función)
49. `get_by_date_range(start_date: datetime, end_date: datetime) -> List[Alert]` - Obtiene alertas en rango de fechas

#### Consultas Especializadas (4 funciones)
50. `get_critical_alerts() -> List[Alert]` - Obtiene alertas críticas activas
51. `get_unacknowledged_alerts() -> List[Alert]` - Obtiene alertas no reconocidas
52. `get_with_relations(alert_id: int) -> Optional[Alert]` - Obtiene alerta con relaciones cargadas
53. `get_all_with_filters(**filters) -> List[Alert]` - Obtiene alertas con filtros dinámicos

#### Consultas de Limpieza (2 funciones)
54. `get_old_resolved_alerts(days_old: int = 30) -> List[Alert]` - Obtiene alertas resueltas antiguas
55. `cleanup_old_alerts(days_old: int = 90) -> int` - Limpia alertas antiguas resueltas o descartadas

---

### AlertStateManager (alert_state_manager.py)

#### Gestión de Transiciones de Estado (2 funciones)
56. `get_valid_transitions(current_status: AlertStatus) -> List[AlertStatus]` - Obtiene transiciones válidas desde un estado
57. `can_transition_to(current_status: AlertStatus, target_status: AlertStatus) -> bool` - Verifica si una transición es válida

#### Operaciones de Cambio de Estado (3 funciones)
58. `acknowledge_alert(alert_id: int, acknowledged_by: str) -> Alert` - Marca alerta como reconocida (READ)
59. `resolve_alert(alert_id: int, resolved_by: str, resolution_notes: Optional[str] = None) -> Alert` - Marca alerta como resuelta
60. `dismiss_alert(alert_id: int, dismissed_by: str, dismissal_reason: Optional[str] = None) -> Alert` - Descarta una alerta (IGNORED)

#### Operaciones en Lote (2 funciones)
61. `bulk_acknowledge_alerts(alert_ids: List[int], acknowledged_by: str) -> List[Alert]` - Reconoce múltiples alertas
62. `bulk_resolve_alerts(alert_ids: List[int], resolved_by: str, resolution_notes: Optional[str] = None) -> List[Alert]` - Resuelve múltiples alertas

#### Funciones Privadas (2 funciones)
63. `_validate_state_transition(current_status: AlertStatus, new_status: AlertStatus) -> bool` - **[PRIVADA]** Valida transición de estado
64. `_get_alert_by_id(alert_id: int) -> Alert` - **[PRIVADA]** Obtiene alerta por ID

---

### AlertStatistics (alert_statistics.py)

#### Estadísticas por Categorías (2 funciones)
65. `get_alert_counts_by_status() -> Dict[str, int]` - Obtiene conteo de alertas por estado
66. `get_alert_counts_by_type() -> Dict[str, int]` - Obtiene conteo de alertas por tipo

#### Estadísticas Temporales (1 función)
67. `get_alert_trends(days: int = 30, group_by: str = 'day') -> List[Dict[str, Any]]` - Obtiene tendencias de alertas en período

#### Estadísticas de Rendimiento (1 función)
68. `get_alert_response_time_stats() -> Dict[str, float]` - Calcula estadísticas de tiempo de respuesta

#### Estadísticas por Entidades (2 funciones)
69. `get_alerts_by_employee_stats(limit: int = 10) -> List[Dict[str, Any]]` - Obtiene estadísticas por empleado
70. `get_alerts_by_project_stats(limit: int = 10) -> List[Dict[str, Any]]` - Obtiene estadísticas por proyecto

#### Resúmenes Especializados (1 función)
71. `get_critical_alerts_summary() -> Dict[str, Any]` - Obtiene resumen de alertas críticas

#### Métricas de Rendimiento (1 función)
72. `get_performance_metrics() -> Dict[str, Any]` - Obtiene métricas de rendimiento del sistema

---

### AlertValidator (alert_validator.py)

#### Validaciones Principales (3 funciones)
73. `validate_alert_data(alert_data: Dict[str, Any]) -> Dict[str, Any]` - Valida y normaliza datos de alerta
74. `validate_bulk_data(alerts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]` - Valida datos de múltiples alertas
75. `validate_update_data(update_data: Dict[str, Any]) -> Dict[str, Any]` - Valida datos para actualización de alerta

#### Validaciones Internas - Campos Requeridos (1 función)
76. `_validate_required_fields(data: Dict[str, Any]) -> None` - **[PRIVADA]** Valida campos obligatorios

#### Validaciones Internas - Formato de Datos (6 funciones)
77. `_validate_title(title: str) -> str` - **[PRIVADA]** Valida y normaliza título de la alerta
78. `_validate_message(message: str) -> str` - **[PRIVADA]** Valida y normaliza mensaje de la alerta
79. `_validate_alert_type(alert_type: Any) -> AlertType` - **[PRIVADA]** Valida tipo de alerta
80. `_validate_priority(priority: Any) -> int` - **[PRIVADA]** Valida prioridad de la alerta
81. `_validate_status(status: Any) -> AlertStatus` - **[PRIVADA]** Valida estado de la alerta
82. `_validate_relationship_ids(data: Dict[str, Any]) -> None` - **[PRIVADA]** Valida IDs de relaciones

#### Validaciones Internas - Reglas de Negocio (2 funciones)
83. `_validate_dates(data: Dict[str, Any]) -> None` - **[PRIVADA]** Valida fechas en los datos
84. `_apply_business_rules(data: Dict[str, Any]) -> None` - **[PRIVADA]** Aplica reglas de negocio específicas

---

## Categorías Funcionales

### Por Tipo de Operación
- **CRUD Básicas**: 4 funciones
- **Consultas**: 23 funciones
- **Gestión de Estados**: 8 funciones
- **Estadísticas**: 8 funciones
- **Validaciones**: 12 funciones
- **Operaciones en Lote**: 4 funciones
- **Gestión de Transiciones**: 2 funciones
- **Funciones de Utilidad**: 7 funciones

### Por Nivel de Acceso
- **Funciones Públicas**: 71 funciones
- **Funciones Privadas**: 12 funciones

**Total de funciones documentadas**: 84 funciones

---

**Nota**: Las funciones marcadas como **[PRIVADA]** son métodos internos de las clases y no deben ser llamadas directamente desde código externo. Están documentadas para completitud y mantenimiento del código.