# Funciones Disponibles en WorkloadRepositoryFacade

**Fecha de actualización:** 2025-01-24

## Métodos del WorkloadRepositoryFacade

El `WorkloadRepositoryFacade` es la interfaz principal para todas las operaciones relacionadas con cargas de trabajo. Proporciona acceso unificado a operaciones CRUD, consultas, validaciones, relaciones y estadísticas.

### OPERACIONES CRUD (9 métodos)

1. `create_workload(workload_data: Dict[str, Any]) -> Workload` - Crea una nueva carga de trabajo
2. `update_workload(workload_id: int, workload_data: Dict[str, Any]) -> Workload` - Actualiza una carga de trabajo existente
3. `delete_workload(workload_id: int) -> bool` - Elimina una carga de trabajo
4. `get_workload_by_id(workload_id: int) -> Optional[Workload]` - Obtiene una carga de trabajo por ID
5. `get_by_unique_field(field_name: str, field_value: Any) -> Optional[Workload]` - Obtiene una carga de trabajo por campo único
6. `add_workload(workload_data: Dict[str, Any]) -> Workload` - Alias para create_workload
7. `find_workload_by_id(workload_id: int) -> Optional[Workload]` - Alias para get_workload_by_id
8. `modify_workload(workload_id: int, workload_data: Dict[str, Any]) -> Workload` - Alias para update_workload
9. `remove_workload(workload_id: int) -> bool` - Alias para delete_workload

### OPERACIONES DE CONSULTA (9 métodos)

10. `get_workloads_by_employee(employee_id: int, active_only: bool = True) -> List[Workload]` - Obtiene cargas de trabajo por empleado
11. `get_workloads_by_project(project_id: int, active_only: bool = True) -> List[Workload]` - Obtiene cargas de trabajo por proyecto
12. `get_workloads_by_date_range(start_date: date, end_date: date, employee_id: Optional[int] = None) -> List[Workload]` - Obtiene cargas de trabajo por rango de fechas
13. `get_workloads_by_status(status: str, employee_id: Optional[int] = None) -> List[Workload]` - Obtiene cargas de trabajo por estado
14. `search_workloads_by_criteria(criteria: Dict[str, Any], limit: Optional[int] = None, offset: Optional[int] = None) -> List[Workload]` - Busca cargas de trabajo por criterios específicos
15. `get_workloads_with_pagination(page: int = 1, page_size: int = 20, filters: Optional[Dict[str, Any]] = None) -> Tuple[List[Workload], int]` - Obtiene cargas de trabajo con paginación
16. `count_workloads(filters: Optional[Dict[str, Any]] = None) -> int` - Cuenta cargas de trabajo con filtros opcionales
17. `find_workloads_by_employee(employee_id: int, active_only: bool = True) -> List[Workload]` - Alias para get_workloads_by_employee
18. `find_workloads_by_project(project_id: int, active_only: bool = True) -> List[Workload]` - Alias para get_workloads_by_project

### OPERACIONES DE VALIDACIÓN (8 métodos)

19. `validate_workload_data(workload_data: Dict[str, Any]) -> Dict[str, Any]` - Valida datos de carga de trabajo
20. `validate_workload_hours(employee_id: int, hours: float, work_date: date) -> Dict[str, Any]` - Valida horas de trabajo
21. `validate_workload_status(status: str) -> Dict[str, Any]` - Valida estado de carga de trabajo
22. `validate_workload_description(description: str) -> Dict[str, Any]` - Valida descripción de carga de trabajo
23. `validate_workload_date_range(start_date: date, end_date: date) -> Dict[str, Any]` - Valida rango de fechas
24. `check_workload_duplicates(employee_id: int, project_id: int, work_date: date, exclude_workload_id: Optional[int] = None) -> Dict[str, Any]` - Verifica duplicados de carga de trabajo
25. `validate_employee_daily_hours(employee_id: int, work_date: date, additional_hours: float, exclude_workload_id: Optional[int] = None) -> Dict[str, Any]` - Valida horas diarias del empleado
26. `validate_data_consistency() -> Dict[str, Any]` - Valida consistencia de datos

### OPERACIONES DE RELACIONES (7 métodos)

27. `get_workload_with_employee_details(workload_id: int) -> Optional[Dict[str, Any]]` - Obtiene carga de trabajo con detalles del empleado
28. `get_workload_with_project_details(workload_id: int) -> Optional[Dict[str, Any]]` - Obtiene carga de trabajo con detalles del proyecto
29. `get_workloads_with_relationships(workload_ids: Optional[List[int]] = None, include_employee: bool = True, include_project: bool = True) -> List[Dict[str, Any]]` - Obtiene cargas de trabajo con relaciones
30. `validate_employee_exists(employee_id: int) -> bool` - Valida que el empleado existe
31. `validate_project_exists(project_id: int) -> bool` - Valida que el proyecto existe
32. `get_employee_project_associations(employee_id: int) -> List[Dict[str, Any]]` - Obtiene asociaciones empleado-proyecto
33. `analyze_workload_dependencies(workload_id: int) -> Dict[str, Any]` - Analiza dependencias de carga de trabajo

### OPERACIONES DE ESTADÍSTICAS (6 métodos)

34. `get_employee_workload_statistics(employee_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]` - Obtiene estadísticas de carga de trabajo por empleado
35. `get_project_workload_statistics(project_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]` - Obtiene estadísticas de carga de trabajo por proyecto
36. `get_team_workload_statistics(team_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]` - Obtiene estadísticas de carga de trabajo por equipo
37. `get_workload_trends_analysis(start_date: date, end_date: date, granularity: str = "weekly") -> List[Dict[str, Any]]` - Obtiene análisis de tendencias de carga de trabajo
38. `get_workload_distribution_analysis(analysis_type: str = "by_employee", start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]` - Obtiene análisis de distribución de carga de trabajo
39. `calculate_productivity_metrics(employee_id: Optional[int] = None, project_id: Optional[int] = None, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]` - Calcula métricas de productividad

### OPERACIONES COMPUESTAS Y AVANZADAS (3 métodos)

40. `create_workload_with_validation(workload_data: Dict[str, Any]) -> Dict[str, Any]` - Crea carga de trabajo con validación completa
41. `get_workload_dashboard_data(employee_id: Optional[int] = None, project_id: Optional[int] = None, team_id: Optional[int] = None, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]` - Obtiene datos para dashboard de cargas de trabajo
42. `bulk_workload_operation(operation: str, workload_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]` - Ejecuta operaciones masivas en cargas de trabajo

---

## Resumen de Funcionalidades

**Total de métodos públicos:** 42

**Distribución por categorías:**
- **CRUD básico**: 9 métodos (crear, actualizar, eliminar, obtener, con aliases)
- **Consultas**: 9 métodos (búsquedas y obtención de datos con filtros)
- **Validaciones**: 8 métodos (validación de datos, duplicados y reglas de negocio)
- **Relaciones**: 7 métodos (gestión de relaciones con empleados y proyectos)
- **Estadísticas**: 6 métodos (análisis, tendencias y métricas)
- **Operaciones compuestas**: 3 métodos (operaciones complejas y masivas)

**Características principales:**
- **Interfaz unificada**: Acceso centralizado a todas las operaciones de cargas de trabajo
- **Validación integrada**: Métodos con validación automática de datos y reglas de negocio
- **Soporte para paginación**: Múltiples métodos con soporte para paginación y filtros
- **Análisis estadístico**: Conjunto completo de métodos para análisis y reportes
- **Gestión de relaciones**: Manejo completo de relaciones con empleados y proyectos
- **Operaciones masivas**: Soporte para procesamiento en lote
- **Dashboard integrado**: Métodos especializados para interfaces de usuario
- **Aliases de compatibilidad**: Métodos alternativos para facilitar la migración

**Integración con módulos:**
- **WorkloadCrudModule**: Operaciones CRUD básicas
- **WorkloadQueryModule**: Consultas y búsquedas avanzadas
- **WorkloadValidationModule**: Validación de datos y reglas de negocio
- **WorkloadRelationshipModule**: Gestión de relaciones con otras entidades
- **WorkloadStatisticsModule**: Análisis estadístico y métricas

**Casos de uso principales:**
- Gestión completa del ciclo de vida de cargas de trabajo
- Seguimiento y análisis de productividad de empleados
- Planificación y asignación de recursos en proyectos
- Validación de integridad de datos y reglas de negocio
- Generación de reportes y análisis estadísticos
- Operaciones masivas y procesamiento en lote
- Integración con interfaces de usuario (dashboards)
- Análisis de tendencias y distribución de cargas de trabajo

**Validaciones específicas:**
- **Duplicados**: Prevención de cargas de trabajo duplicadas por empleado/proyecto/fecha
- **Horas diarias**: Validación de límites de horas de trabajo por día
- **Consistencia de datos**: Verificación de integridad referencial
- **Existencia de entidades**: Validación de empleados y proyectos relacionados
- **Reglas de negocio**: Aplicación de reglas específicas del dominio

**Capacidades de análisis:**
- **Estadísticas por empleado**: Métricas individuales de productividad
- **Estadísticas por proyecto**: Análisis de recursos asignados a proyectos
- **Estadísticas por equipo**: Métricas agregadas de equipos de trabajo
- **Análisis de tendencias**: Evolución temporal de cargas de trabajo
- **Distribución de cargas**: Análisis de distribución por diferentes criterios
- **Métricas de productividad**: Cálculos avanzados de eficiencia y rendimiento