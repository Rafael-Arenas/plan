# Métodos de Dominio de Horarios (Schedule)

## Descripción General

Esta es una selección de métodos de dominio de horarios derivados de las funcionalidades expuestas por el `ScheduleRepositoryFacade`. Estos métodos proporcionan una capa de servicio fundamental para operaciones complejas relacionadas con la gestión de horarios de empleados, siguiendo el patrón establecido en los servicios de dominio existentes.

El servicio de dominio de horarios encapsula la lógica de negocio compleja, coordina operaciones entre múltiples repositorios (empleados, proyectos, equipos, horarios) y proporciona una interfaz unificada para la gestión completa del ciclo de vida de horarios, incluyendo validaciones de conflictos, gestión de confirmaciones y análisis de productividad temporal.

---

## Métodos Disponibles

### 1. Operaciones CRUD Principales (3 métodos)

1.  `create_schedule(schedule_data: ScheduleCreateSchema) -> ScheduleResponseSchema` - Crea un nuevo horario con validaciones completas de negocio y detección de conflictos.
2.  `update_schedule(schedule_id: int, schedule_data: ScheduleUpdateSchema) -> Optional[ScheduleResponseSchema]` - Actualiza un horario existente con validaciones de solapamiento temporal.
3.  `delete_schedule(schedule_id: int) -> bool` - Elimina un horario después de validar dependencias y impacto en la planificación.

### 2. Operaciones de Consulta por Empleado (4 métodos)

4.  `get_employee_schedules(employee_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[ScheduleResponseSchema]` - Obtiene horarios de un empleado en un rango de fechas específico.
5.  `get_employee_schedules_with_details(employee_id: int, include_projects: bool = True, include_teams: bool = True) -> List[ScheduleDetailedResponseSchema]` - Obtiene horarios de un empleado con información detallada de relaciones.
6.  `get_employee_current_week_schedule(employee_id: int) -> WeeklyScheduleResponseSchema` - Obtiene la programación semanal actual del empleado con resumen de horas.
7.  `get_employee_schedule_conflicts(employee_id: int, start_date: date, end_date: date) -> List[ScheduleConflictSchema]` - Detecta y analiza conflictos de horarios para un empleado específico.

### 3. Operaciones de Consulta por Proyecto (3 métodos)

8.  `get_project_schedules(project_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[ScheduleResponseSchema]` - Obtiene todos los horarios asociados a un proyecto específico.
9.  `get_project_team_schedules(project_id: int, include_employee_details: bool = True) -> ProjectTeamScheduleSchema` - Obtiene horarios completos del equipo asignado al proyecto.
10. `get_project_schedule_timeline(project_id: int, start_date: date, end_date: date) -> ProjectScheduleTimelineSchema` - Genera una línea de tiempo visual de horarios del proyecto.

### 4. Operaciones de Consulta por Equipo (2 métodos)

11. `get_team_schedules(team_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[ScheduleResponseSchema]` - Obtiene horarios de todos los miembros de un equipo.
12. `get_team_schedule_coordination(team_id: int, target_date: date) -> TeamScheduleCoordinationSchema` - Analiza la coordinación y disponibilidad del equipo para una fecha específica.

### 5. Operaciones de Búsqueda y Filtrado (3 métodos)

13. `get_schedules_by_date(target_date: date, employee_id: Optional[int] = None) -> List[ScheduleResponseSchema]` - Obtiene horarios para una fecha específica con filtro opcional por empleado.
14. `get_confirmed_schedules(start_date: date, end_date: date, employee_id: Optional[int] = None) -> List[ScheduleResponseSchema]` - Obtiene solo horarios confirmados en un rango de fechas.
15. `search_schedules_advanced(filters: ScheduleAdvancedFilters) -> List[ScheduleResponseSchema]` - Búsqueda avanzada con múltiples filtros complejos y criterios personalizados.

### 6. Operaciones de Gestión de Confirmaciones (3 métodos)

16. `confirm_schedule(schedule_id: int, confirmation_data: ScheduleConfirmationSchema) -> ScheduleResponseSchema` - Confirma un horario con datos adicionales de validación.
17. `bulk_confirm_schedules(schedule_ids: List[int], confirmation_data: BulkConfirmationSchema) -> BulkConfirmationResultSchema` - Confirma múltiples horarios en una operación transaccional.
18. `get_pending_confirmations(employee_id: Optional[int] = None, days_ahead: int = 7) -> List[PendingConfirmationSchema]` - Obtiene horarios pendientes de confirmación con alertas de vencimiento.

### 7. Operaciones de Estadísticas de Horas (4 métodos)

19. `get_employee_hours_summary(employee_id: int, start_date: date, end_date: date) -> EmployeeHoursSummarySchema` - Calcula resumen completo de horas trabajadas por empleado.
20. `get_project_hours_summary(project_id: int, start_date: date, end_date: date) -> ProjectHoursSummarySchema` - Obtiene resumen de horas invertidas en un proyecto específico.
21. `get_team_hours_summary(team_id: int, start_date: date, end_date: date) -> TeamHoursSummarySchema` - Calcula distribución de horas trabajadas por equipo.
22. `get_overtime_analysis(start_date: date, end_date: date, employee_id: Optional[int] = None) -> OvertimeAnalysisSchema` - Analiza patrones de horas extra y sobrecarga laboral.

### 8. Operaciones de Análisis de Productividad (3 métodos)

23. `get_productivity_metrics(start_date: date, end_date: date, employee_id: Optional[int] = None, project_id: Optional[int] = None) -> ProductivityMetricsSchema` - Calcula métricas avanzadas de productividad y eficiencia.
24. `get_utilization_report(start_date: date, end_date: date, group_by: str = "employee") -> List[UtilizationReportSchema]` - Genera reporte de utilización de recursos humanos.
25. `get_schedule_distribution_analysis(start_date: date, end_date: date, distribution_type: str = "daily") -> ScheduleDistributionSchema` - Analiza patrones de distribución temporal de horarios.

### 9. Operaciones de Validación y Reglas de Negocio (4 métodos)

26. `validate_schedule_business_rules(schedule_data: Dict[str, Any], exclude_id: Optional[int] = None) -> ValidationResultSchema` - Valida todas las reglas de negocio para horarios.
27. `validate_schedule_conflicts(employee_id: int, schedule_date: date, start_time: time, end_time: time, exclude_schedule_id: Optional[int] = None) -> ConflictValidationSchema` - Detecta y valida conflictos de horarios con análisis detallado.
28. `validate_team_schedule_coordination(team_id: int, target_date: date) -> TeamCoordinationValidationSchema` - Valida la coordinación de horarios del equipo para proyectos colaborativos.
29. `validate_workload_distribution(employee_id: int, start_date: date, end_date: date) -> WorkloadValidationSchema` - Valida que la distribución de carga de trabajo sea equilibrada y sostenible.

### 10. Operaciones de Diagnóstico y Salud (1 método)

30. `check_service_health() -> Dict[str, Any]` - Verifica el estado de salud del servicio de horarios y sus dependencias.

---

## Resumen por Categorías

| Categoría | Cantidad | Descripción |
|-----------|----------|-------------|
| **CRUD Principales** | 3 | Operaciones básicas de creación, actualización y eliminación con validaciones |
| **Consulta por Empleado** | 4 | Búsquedas y análisis centrados en empleados específicos con detección de conflictos |
| **Consulta por Proyecto** | 3 | Búsquedas y análisis centrados en proyectos específicos con líneas de tiempo |
| **Consulta por Equipo** | 2 | Análisis de coordinación y disponibilidad de equipos completos |
| **Búsqueda y Filtrado** | 3 | Consultas complejas con múltiples criterios y estados de confirmación |
| **Gestión de Confirmaciones** | 3 | Procesos de confirmación individual y masiva con alertas |
| **Estadísticas de Horas** | 4 | Análisis de horas trabajadas, distribución y detección de horas extra |
| **Análisis de Productividad** | 3 | Métricas avanzadas de productividad, utilización y patrones temporales |
| **Validación y Reglas** | 4 | Verificación de reglas de negocio, conflictos y coordinación de equipos |
| **Diagnóstico** | 1 | Monitoreo de salud y configuración del servicio |
| **Total** | **30** | **Métodos propuestos** |

---

## Características Especiales del Dominio

### Gestión de Conflictos Temporales
- **Detección automática**: Identificación de solapamientos de horarios en tiempo real
- **Resolución inteligente**: Sugerencias automáticas para resolver conflictos temporales
- **Validación preventiva**: Verificación antes de crear o modificar horarios

### Análisis de Productividad Temporal
- **Métricas de eficiencia**: Cálculo de productividad por períodos y empleados
- **Patrones de trabajo**: Identificación de tendencias y hábitos laborales
- **Optimización de recursos**: Sugerencias para mejorar la distribución temporal

### Gestión de Confirmaciones
- **Flujo de aprobación**: Proceso estructurado de confirmación de horarios
- **Alertas automáticas**: Notificaciones de horarios pendientes de confirmación
- **Auditoría completa**: Registro de cambios y confirmaciones para trazabilidad

### Coordinación de Equipos
- **Sincronización temporal**: Análisis de disponibilidad conjunta de equipos
- **Planificación colaborativa**: Herramientas para coordinar horarios de proyectos
- **Distribución equilibrada**: Balanceo automático de cargas de trabajo temporales

### Integración Multi-Repositorio
- **Validación cruzada**: Verificación de integridad entre empleados, proyectos, equipos y horarios
- **Sincronización automática**: Mantenimiento de consistencia de datos relacionados
- **Transacciones distribuidas**: Operaciones atómicas que afectan múltiples entidades temporales

### Análisis Estadístico Avanzado
- **Tendencias temporales**: Identificación de patrones estacionales y cíclicos
- **Predicción de carga**: Análisis predictivo para planificación futura
- **Métricas de utilización**: Cálculo de eficiencia y aprovechamiento de recursos humanos