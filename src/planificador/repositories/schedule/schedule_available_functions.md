# Funciones Disponibles en `ScheduleRepositoryFacade`

Este documento detalla todos los métodos públicos disponibles en la clase `ScheduleRepositoryFacade`, que sirve como punto de entrada unificado para todas las operaciones relacionadas con los horarios en la base de datos.

## Arquitectura

La fachada delega las operaciones a módulos especializados, cada uno responsable de un área funcional específica:

- **`crud_module`**: Operaciones de Creación, Lectura, Actualización y Eliminación (CRUD).
- **`query_module`**: Consultas y búsquedas avanzadas con filtros.
- **`relationship_module`**: Gestión de relaciones con otras entidades (empleados, proyectos, equipos).
- **`statistics_module`**: Cálculos y agregaciones estadísticas.
- **`validation_module`**: Validaciones de datos de entrada.

---

## Métodos por Módulo

### 1. Operaciones CRUD (`crud_module`)

- `create_schedule(schedule_data: Dict[str, Any]) -> Schedule`
  - Crea un nuevo horario después de validar los datos de entrada.

- `update_schedule(schedule_id: int, schedule_data: Dict[str, Any]) -> Schedule`
  - Actualiza un horario existente después de validar los datos.

- `delete_schedule(schedule_id: int) -> bool`
  - Elimina un horario por su ID.

### 2. Operaciones de Consulta (`query_module`)

#### Métodos de Consulta Base

- `get_schedule_by_id(schedule_id: int) -> Optional[Schedule]`
  - Obtiene un horario por su ID.

- `get_schedules_by_employee(employee_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Schedule]`
  - Obtiene horarios de un empleado en un rango de fechas opcional.

- `get_schedules_by_date(target_date: date, employee_id: Optional[int] = None) -> List[Schedule]`
  - Obtiene horarios para una fecha específica, opcionalmente filtrados por empleado.

- `get_schedules_by_project(project_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Schedule]`
  - Obtiene horarios asociados a un proyecto en un rango de fechas opcional.

- `get_schedules_by_team(team_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Schedule]`
  - Obtiene horarios asociados a un equipo en un rango de fechas opcional.

#### Métodos de Consulta Avanzada

- `get_confirmed_schedules(start_date: date, end_date: date, employee_id: Optional[int] = None) -> List[Schedule]`
  - Obtiene horarios confirmados en un rango de fechas, opcionalmente filtrados por empleado.

- `search_schedules(filters: Dict[str, Any], limit: Optional[int] = None, offset: Optional[int] = None) -> List[Schedule]`
  - Busca horarios con filtros personalizados, con paginación opcional.

- `count_schedules(filters: Optional[Dict[str, Any]] = None) -> int`
  - Cuenta el número de horarios que coinciden con los filtros especificados.

### 3. Operaciones de Relaciones (`relationship_module`)

#### Gestión de Relaciones con Empleados

- `get_employee_schedules_with_details(employee_id: int, include_projects: bool = True, include_teams: bool = True, include_status_codes: bool = True) -> List[Schedule]`
  - Obtiene horarios de un empleado con detalles de relaciones opcionales.

- `get_employees_with_schedules_in_period(start_date: date, end_date: date) -> List[Tuple[Employee, List[Schedule]]]`
  - Obtiene empleados con sus horarios en un período específico.

- `get_employee_schedules_in_period(employee_id: int, start_date: date, end_date: date) -> List[Schedule]`
  - Obtiene horarios de un empleado en un período específico.

#### Gestión de Relaciones con Proyectos

- `get_project_schedules_with_details(project_id: int, include_employees: bool = True, include_teams: bool = True, include_status_codes: bool = True) -> List[Schedule]`
  - Obtiene horarios de un proyecto con detalles de relaciones opcionales.

- `get_projects_with_schedules_in_period(start_date: date, end_date: date) -> List[Tuple[Project, List[Schedule]]]`
  - Obtiene proyectos con sus horarios en un período específico.

- `get_project_schedules_in_period(project_id: int, start_date: date, end_date: date) -> List[Schedule]`
  - Obtiene horarios de un proyecto en un período específico.

#### Gestión de Relaciones con Equipos

- `get_team_schedules_with_details(team_id: int, include_employees: bool = True, include_projects: bool = True, include_status_codes: bool = True) -> List[Schedule]`
  - Obtiene horarios de un equipo con detalles de relaciones opcionales.

#### Operaciones de Asignación

- `assign_schedule_to_project(schedule_id: int, project_id: int) -> Schedule`
  - Asigna un horario a un proyecto específico.

- `assign_schedule_to_team(schedule_id: int, team_id: int) -> Schedule`
  - Asigna un horario a un equipo específico.

- `remove_schedule_from_project(schedule_id: int) -> Schedule`
  - Remueve la asignación de un horario de un proyecto.

- `remove_schedule_from_team(schedule_id: int) -> Schedule`
  - Remueve la asignación de un horario de un equipo.

#### Operaciones de Resumen y Validación de Relaciones

- `get_schedule_relationships_summary(schedule_id: int) -> Dict[str, Any]`
  - Obtiene un resumen completo de las relaciones de un horario.

- `validate_project_assignment(schedule_id: int, project_id: int) -> bool`
  - Valida si un horario puede ser asignado a un proyecto específico.

- `validate_team_assignment(schedule_id: int, team_id: int) -> bool`
  - Valida si un horario puede ser asignado a un equipo específico.

### 4. Operaciones de Estadísticas (`statistics_module`)

#### Resúmenes de Horas

- `get_employee_hours_summary(employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]`
  - Obtiene resumen de horas trabajadas por empleado en un período.

- `get_project_hours_summary(project_id: int, start_date: date, end_date: date) -> Dict[str, Any]`
  - Obtiene resumen de horas por proyecto en un período.

- `get_team_hours_summary(team_id: int, start_date: date, end_date: date) -> Dict[str, Any]`
  - Obtiene resumen de horas por equipo en un período.

#### Métricas y Análisis

- `get_schedule_counts_by_status(start_date: date, end_date: date, employee_id: Optional[int] = None) -> Dict[str, int]`
  - Obtiene conteo de horarios agrupados por estado en un período.

- `get_productivity_metrics(start_date: date, end_date: date, employee_id: Optional[int] = None, project_id: Optional[int] = None) -> Dict[str, Any]`
  - Obtiene métricas de productividad con filtros opcionales.

- `get_utilization_report(start_date: date, end_date: date, group_by: str = "employee") -> List[Dict[str, Any]]`
  - Obtiene reporte de utilización agrupado por criterio especificado.

- `get_confirmation_statistics(start_date: date, end_date: date) -> Dict[str, Any]`
  - Obtiene estadísticas de confirmación de horarios en un período.

- `get_overtime_analysis(start_date: date, end_date: date, employee_id: Optional[int] = None) -> Dict[str, Any]`
  - Obtiene análisis de horas extra con filtro opcional por empleado.

#### Reportes y Distribuciones

- `get_schedule_distribution(start_date: date, end_date: date, distribution_type: str = "daily") -> List[Dict[str, Any]]`
  - Obtiene distribución de horarios por tipo especificado (diario, semanal, etc.).

- `get_top_performers(start_date: date, end_date: date, metric: str = "hours", limit: int = 10) -> List[Dict[str, Any]]`
  - Obtiene los mejores desempeños según la métrica especificada.

### 5. Operaciones de Validación (`validation_module`)

#### Validaciones de Datos

- `validate_schedule_data(schedule_data: Dict[str, Any]) -> bool`
  - Valida la integridad y formato de los datos de un horario.

- `validate_schedule_id(schedule_id: int) -> bool`
  - Valida que un ID de horario sea válido y exista en la base de datos.

#### Validaciones de Rangos

- `validate_date_range(start_date: date, end_date: date) -> bool`
  - Valida que un rango de fechas sea lógicamente correcto.

- `validate_time_range(start_time: time, end_time: time) -> bool`
  - Valida que un rango de horas sea lógicamente correcto.

#### Validaciones de Conflictos y Asignaciones

- `validate_schedule_conflicts(employee_id: int, schedule_date: date, start_time: time, end_time: time, exclude_schedule_id: Optional[int] = None) -> bool`
  - Valida que no existan conflictos de horarios para un empleado en una fecha y hora específica.

- `validate_project_assignment(employee_id: int, project_id: int) -> bool`
  - Valida que un empleado esté autorizado para trabajar en un proyecto específico.

- `validate_team_membership(employee_id: int, team_id: int) -> bool`
  - Valida que un empleado pertenezca a un equipo específico.

- `validate_search_filters(filters: Dict[str, Any]) -> bool`
  - Valida que los filtros de búsqueda tengan el formato y valores correctos.

---

## Métodos de Conveniencia y Operaciones Compuestas

### Operaciones Avanzadas

- `get_complete_schedule_info(schedule_id: int) -> Optional[Dict[str, Any]]`
  - Obtiene información completa de un horario incluyendo todas sus relaciones y detalles.

- `create_schedule_with_validation(schedule_data: Dict[str, Any]) -> Dict[str, Any]`
  - Crea un horario con validación completa de datos y conflictos.

- `update_schedule_with_validation(schedule_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]`
  - Actualiza un horario con validación completa de datos y conflictos.

---

## Resumen de Funcionalidades

El `ScheduleRepositoryFacade` proporciona una interfaz unificada y completa para:

- **Gestión CRUD**: Creación, actualización y eliminación de horarios
- **Consultas avanzadas**: Búsquedas por empleado, proyecto, equipo, fecha y filtros personalizados
- **Gestión de relaciones**: Manejo completo de asignaciones entre horarios, empleados, proyectos y equipos
- **Análisis estadístico**: Métricas de productividad, utilización, horas extra y rendimiento
- **Validación robusta**: Verificación de conflictos, integridad de datos y reglas de negocio
- **Operaciones compuestas**: Métodos de conveniencia que combinan múltiples operaciones

Todos los métodos están completamente documentados y siguen las mejores prácticas de desarrollo asíncrono con SQLAlchemy, proporcionando manejo robusto de errores y logging estructurado.