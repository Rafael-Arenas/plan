# Funciones Disponibles en ScheduleRepositoryFacade

**Última actualización:** Enero 2025

## Descripción General

`ScheduleRepositoryFacade` es la clase principal que proporciona una interfaz unificada para todas las operaciones relacionadas con horarios en el sistema. Esta fachada encapsula la lógica de acceso a datos y coordina las operaciones entre diferentes módulos especializados, ofreciendo una API coherente y fácil de usar para la gestión completa de horarios.

---

## Métodos Disponibles

### 1. Operaciones CRUD (3 métodos)

1. `create_schedule(schedule_data: Dict[str, Any]) -> Schedule` - Crea un nuevo horario en el sistema
2. `update_schedule(schedule_id: int, schedule_data: Dict[str, Any]) -> Schedule` - Actualiza un horario existente
3. `delete_schedule(schedule_id: int) -> bool` - Elimina un horario del sistema

### 2. Operaciones de Consulta (8 métodos)

4. `get_schedule_by_id(schedule_id: int) -> Optional[Schedule]` - Obtiene un horario por su ID único
5. `get_schedules_by_employee(employee_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Schedule]` - Obtiene horarios de un empleado específico
6. `get_schedules_by_date(target_date: date, employee_id: Optional[int] = None) -> List[Schedule]` - Obtiene horarios para una fecha específica
7. `get_schedules_by_project(project_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Schedule]` - Obtiene horarios asociados a un proyecto
8. `get_schedules_by_team(team_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Schedule]` - Obtiene horarios de un equipo específico
9. `get_confirmed_schedules(start_date: date, end_date: date, employee_id: Optional[int] = None) -> List[Schedule]` - Obtiene horarios confirmados en un período
10. `search_schedules(filters: Dict[str, Any], limit: Optional[int] = None, offset: Optional[int] = None) -> List[Schedule]` - Busca horarios con filtros personalizados
11. `count_schedules(filters: Optional[Dict[str, Any]] = None) -> int` - Cuenta horarios que coinciden con filtros específicos

### 3. Operaciones de Relaciones (14 métodos)

12. `get_employee_schedules_with_details(employee_id: int, include_projects: bool = True, include_teams: bool = True, include_status_codes: bool = True) -> List[Schedule]` - Obtiene horarios de empleado con detalles completos
13. `get_employees_with_schedules_in_period(start_date: date, end_date: date) -> List[Tuple[Employee, List[Schedule]]]` - Obtiene empleados con sus horarios en un período
14. `get_employee_schedules_in_period(employee_id: int, start_date: date, end_date: date) -> List[Schedule]` - Obtiene horarios de empleado en período específico
15. `get_project_schedules_with_details(project_id: int, include_employees: bool = True, include_teams: bool = True, include_status_codes: bool = True) -> List[Schedule]` - Obtiene horarios de proyecto con detalles completos
16. `get_projects_with_schedules_in_period(start_date: date, end_date: date) -> List[Tuple[Project, List[Schedule]]]` - Obtiene proyectos con sus horarios en un período
17. `get_project_schedules_in_period(project_id: int, start_date: date, end_date: date) -> List[Schedule]` - Obtiene horarios de proyecto en período específico
18. `get_team_schedules_with_details(team_id: int, include_employees: bool = True, include_projects: bool = True, include_status_codes: bool = True) -> List[Schedule]` - Obtiene horarios de equipo con detalles completos
19. `assign_schedule_to_project(schedule_id: int, project_id: int) -> Schedule` - Asigna un horario a un proyecto específico
20. `assign_schedule_to_team(schedule_id: int, team_id: int) -> Schedule` - Asigna un horario a un equipo específico
21. `remove_schedule_from_project(schedule_id: int) -> Schedule` - Remueve asignación de horario de un proyecto
22. `remove_schedule_from_team(schedule_id: int) -> Schedule` - Remueve asignación de horario de un equipo
23. `get_schedule_relationships_summary(schedule_id: int) -> Dict[str, Any]` - Obtiene resumen de relaciones de un horario
24. `validate_project_assignment(schedule_id: int, project_id: int) -> bool` - Valida asignación de horario a proyecto
25. `validate_team_assignment(schedule_id: int, team_id: int) -> bool` - Valida asignación de horario a equipo

### 4. Operaciones de Estadísticas (10 métodos)

26. `get_employee_hours_summary(employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]` - Obtiene resumen de horas trabajadas por empleado
27. `get_project_hours_summary(project_id: int, start_date: date, end_date: date) -> Dict[str, Any]` - Obtiene resumen de horas por proyecto
28. `get_team_hours_summary(team_id: int, start_date: date, end_date: date) -> Dict[str, Any]` - Obtiene resumen de horas por equipo
29. `get_schedule_counts_by_status(start_date: date, end_date: date, employee_id: Optional[int] = None) -> Dict[str, int]` - Obtiene conteo de horarios por estado
30. `get_productivity_metrics(start_date: date, end_date: date, employee_id: Optional[int] = None, project_id: Optional[int] = None) -> Dict[str, Any]` - Obtiene métricas de productividad
31. `get_utilization_report(start_date: date, end_date: date, group_by: str = "employee") -> List[Dict[str, Any]]` - Obtiene reporte de utilización de recursos
32. `get_confirmation_statistics(start_date: date, end_date: date) -> Dict[str, Any]` - Obtiene estadísticas de confirmación de horarios
33. `get_overtime_analysis(start_date: date, end_date: date, employee_id: Optional[int] = None) -> Dict[str, Any]` - Obtiene análisis de horas extra
34. `get_schedule_distribution(start_date: date, end_date: date, distribution_type: str = "daily") -> List[Dict[str, Any]]` - Obtiene distribución de horarios por período
35. `get_top_performers(start_date: date, end_date: date, metric: str = "hours", limit: int = 10) -> List[Dict[str, Any]]` - Obtiene empleados con mejor rendimiento

### 5. Operaciones de Validación (8 métodos)

36. `validate_schedule_data(schedule_data: Dict[str, Any]) -> bool` - Valida integridad de datos de horario
37. `validate_schedule_id(schedule_id: int) -> bool` - Valida existencia de ID de horario
38. `validate_employee_id(employee_id: int) -> bool` - Valida existencia de ID de empleado
39. `validate_date_range(start_date: date, end_date: date) -> bool` - Valida coherencia de rango de fechas
40. `validate_time_range(start_time: time, end_time: time) -> bool` - Valida coherencia de rango de horas
41. `validate_schedule_conflicts(employee_id: int, schedule_date: date, start_time: time, end_time: time, exclude_schedule_id: Optional[int] = None) -> bool` - Valida conflictos de horarios
42. `validate_team_membership(employee_id: int, team_id: int) -> bool` - Valida pertenencia de empleado a equipo
43. `validate_search_filters(filters: Dict[str, Any]) -> bool` - Valida formato de filtros de búsqueda

### 6. Operaciones Compuestas y Avanzadas (6 métodos)

44. `get_complete_schedule_info(schedule_id: int) -> Optional[Dict[str, Any]]` - Obtiene información completa de horario con todas las relaciones
45. `create_schedule_with_validation(schedule_data: Dict[str, Any]) -> Dict[str, Any]` - Crea horario con validación completa de datos y conflictos
46. `update_schedule_with_validation(schedule_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]` - Actualiza horario con validación completa
47. `get_employee_schedule_summary(employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]` - Obtiene resumen completo de horarios de empleado
48. `bulk_schedule_operation(operation: str, schedule_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]` - Realiza operaciones en lote sobre múltiples horarios
49. `create_validated_schedule(schedule_data: Dict[str, Any]) -> Schedule` - Crea horario con validación exhaustiva de reglas de negocio

---

## Resumen de Funcionalidades

### Total de Métodos Públicos: 49

**Distribución por Categorías:**
- Operaciones CRUD: 3 métodos (6%)
- Operaciones de Consulta: 8 métodos (16%)
- Operaciones de Relaciones: 14 métodos (29%)
- Operaciones de Estadísticas: 10 métodos (20%)
- Operaciones de Validación: 8 métodos (16%)
- Operaciones Compuestas: 6 métodos (12%)

### Características Principales

- **Gestión Completa de Horarios**: CRUD completo con validaciones robustas
- **Consultas Avanzadas**: Búsquedas por empleado, proyecto, equipo, fecha y filtros personalizados
- **Gestión de Relaciones**: Manejo integral de asignaciones entre horarios, empleados, proyectos y equipos
- **Análisis Estadístico**: Métricas de productividad, utilización, horas extra y rendimiento
- **Validación Robusta**: Verificación de conflictos, integridad de datos y reglas de negocio
- **Operaciones Compuestas**: Métodos de conveniencia que combinan múltiples operaciones

### Integración con Otros Módulos

- **Employee**: Gestión de horarios por empleado y validación de pertenencia
- **Project**: Asignación y seguimiento de horarios por proyecto
- **Team**: Gestión de horarios por equipo y validación de membresía
- **StatusCode**: Integración con estados de horarios para seguimiento y reportes

### Casos de Uso Principales

- **Planificación de Recursos**: Asignación y gestión de horarios de trabajo
- **Seguimiento de Productividad**: Análisis de horas trabajadas y rendimiento
- **Gestión de Proyectos**: Seguimiento de tiempo dedicado a proyectos específicos
- **Análisis de Equipos**: Evaluación de rendimiento y utilización por equipos
- **Reportes Gerenciales**: Estadísticas y métricas para toma de decisiones
- **Validación de Conflictos**: Prevención de solapamientos y conflictos de horarios