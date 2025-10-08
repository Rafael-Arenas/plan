# Métodos de Dominio de Asignaciones de Proyecto

## Descripción General

Esta es una selección de métodos de dominio de asignaciones de proyecto derivados de las funcionalidades expuestas por el `ProjectAssignmentRepositoryFacade`. Estos métodos proporcionan una capa de servicio fundamental para operaciones complejas relacionadas con la gestión de asignaciones de empleados a proyectos, siguiendo el patrón establecido en los servicios de dominio existentes.

El servicio de dominio de asignaciones de proyecto encapsula la lógica de negocio compleja, coordina operaciones entre múltiples repositorios (empleados, proyectos, asignaciones) y proporciona una interfaz unificada para la gestión completa del ciclo de vida de asignaciones, incluyendo validaciones de solapamiento, gestión de cargas de trabajo y análisis de productividad.

---

## Métodos Disponibles

### 1. Operaciones CRUD Principales (4 métodos)

1.  `create_assignment(assignment_data: ProjectAssignmentCreateSchema) -> ProjectAssignmentResponseSchema` - Crea una nueva asignación con validaciones completas de negocio.
2.  `update_assignment(assignment_id: int, assignment_data: ProjectAssignmentUpdateSchema) -> Optional[ProjectAssignmentResponseSchema]` - Actualiza una asignación existente con validaciones de solapamiento.
3.  `delete_assignment(assignment_id: int) -> bool` - Elimina una asignación después de validar dependencias y impacto.
4.  `get_assignment_by_id(assignment_id: int) -> Optional[ProjectAssignmentResponseSchema]` - Obtiene una asignación por su ID único con datos relacionados.

### 2. Operaciones CRUD Especializadas (3 métodos)

5.  `bulk_create_assignments(assignments_data: List[ProjectAssignmentCreateSchema]) -> List[ProjectAssignmentResponseSchema]` - Crea múltiples asignaciones en una operación transaccional con validaciones cruzadas.
6.  `duplicate_assignment(assignment_id: int, new_assignment_data: ProjectAssignmentDuplicateSchema) -> ProjectAssignmentResponseSchema` - Duplica una asignación existente con nuevos parámetros.
7.  `archive_assignment(assignment_id: int, archive_reason: str) -> Optional[ProjectAssignmentResponseSchema]` - Archiva una asignación manteniendo el historial para auditoría.

### 3. Operaciones de Consulta por Empleado (5 métodos)

8.  `get_assignments_by_employee(employee_id: int) -> List[ProjectAssignmentResponseSchema]` - Obtiene todas las asignaciones de un empleado específico.
9.  `get_active_assignments_by_employee(employee_id: int) -> List[ProjectAssignmentResponseSchema]` - Obtiene solo las asignaciones activas de un empleado.
10. `get_employee_workload_summary(employee_id: int) -> EmployeeWorkloadSummarySchema` - Calcula un resumen completo de la carga de trabajo del empleado.
11. `get_employee_assignment_history(employee_id: int, limit: Optional[int] = None) -> List[ProjectAssignmentResponseSchema]` - Obtiene el historial completo de asignaciones de un empleado.
12. `get_employee_current_allocation(employee_id: int) -> EmployeeAllocationSummarySchema` - Calcula la asignación actual total del empleado en porcentaje.

### 4. Operaciones de Consulta por Proyecto (4 métodos)

13. `get_assignments_by_project(project_id: int) -> List[ProjectAssignmentResponseSchema]` - Obtiene todas las asignaciones de un proyecto específico.
14. `get_project_team_summary(project_id: int) -> ProjectTeamSummarySchema` - Obtiene un resumen completo del equipo asignado al proyecto.
15. `get_project_resource_allocation(project_id: int) -> ProjectResourceAllocationSchema` - Calcula la distribución de recursos del proyecto por roles y tiempo.
16. `get_project_assignment_timeline(project_id: int) -> ProjectTimelineSchema` - Genera una línea de tiempo visual de las asignaciones del proyecto.

### 5. Operaciones de Búsqueda y Filtrado (4 métodos)

17. `get_assignments_with_filters(filters: AssignmentAdvancedFilters) -> List[ProjectAssignmentResponseSchema]` - Búsqueda avanzada con múltiples filtros complejos.
18. `get_assignments_by_date_range(start_date: date, end_date: date) -> List[ProjectAssignmentResponseSchema]` - Obtiene asignaciones que se superponen con un rango de fechas.
19. `get_assignments_by_role(role: str) -> List[ProjectAssignmentResponseSchema]` - Obtiene asignaciones filtradas por rol específico.
20. `get_overlapping_assignments(employee_id: int, start_date: date, end_date: date, exclude_id: Optional[int] = None) -> List[ProjectAssignmentResponseSchema]` - Detecta asignaciones superpuestas para validación de conflictos.

### 6. Operaciones de Gestión de Recursos (3 métodos)

21. `transfer_employee_assignments(from_employee_id: int, to_employee_id: int, project_id: Optional[int] = None) -> TransferResultSchema` - Transfiere asignaciones entre empleados con validaciones de capacidad.
22. `reassign_project_assignments(from_project_id: int, to_project_id: int, employee_id: Optional[int] = None) -> ReassignmentResultSchema` - Reasigna empleados entre proyectos manteniendo continuidad.
23. `balance_team_workload(project_id: int, target_allocation: float = 80.0) -> WorkloadBalanceResultSchema` - Equilibra automáticamente la carga de trabajo del equipo del proyecto.

### 7. Operaciones de Estadísticas Básicas (4 métodos)

24. `get_total_assignments_count() -> int` - Obtiene el número total de asignaciones en el sistema.
25. `get_active_assignments_count() -> int` - Obtiene el número de asignaciones actualmente activas.
26. `get_assignments_by_status_count() -> Dict[str, int]` - Calcula la distribución de asignaciones por estado.
27. `get_assignments_by_allocation_category_count() -> Dict[str, int]` - Obtiene la distribución por categorías de asignación.

### 8. Operaciones de Estadísticas Avanzadas (4 métodos)

28. `get_assignment_duration_analytics() -> AssignmentDurationAnalyticsSchema` - Analiza patrones de duración de asignaciones con tendencias.
29. `get_workload_distribution_analytics() -> WorkloadDistributionAnalyticsSchema` - Analiza la distribución de carga de trabajo en la organización.
30. `get_assignment_trends(days: int = 30) -> List[AssignmentTrendDataSchema]` - Obtiene tendencias de asignaciones en un período específico.
31. `get_comprehensive_dashboard_metrics() -> AssignmentDashboardMetricsSchema` - Genera métricas completas para dashboard ejecutivo.

### 9. Operaciones de Validación y Reglas de Negocio (5 métodos)

32. `validate_assignment_business_rules(assignment_data: Dict[str, Any], exclude_id: Optional[int] = None) -> ValidationResultSchema` - Valida todas las reglas de negocio para asignaciones.
33. `validate_no_overlapping_assignments(employee_id: int, start_date: date, end_date: date, exclude_id: Optional[int] = None) -> bool` - Valida que no existan solapamientos de asignaciones.
34. `validate_workload_limits(employee_id: int, start_date: date, end_date: date, allocation_percentage: float) -> bool` - Valida que la carga de trabajo no exceda límites establecidos.
35. `validate_assignment_deletion(assignment_id: int) -> DeletionValidationSchema` - Valida si una asignación puede ser eliminada sin impacto crítico.
36. `validate_employee_availability(employee_id: int, start_date: date, end_date: date) -> EmployeeAvailabilitySchema` - Valida la disponibilidad del empleado para nuevas asignaciones.

### 10. Operaciones de Diagnóstico y Salud (2 métodos)

37. `check_service_health() -> Dict[str, Any]` - Verifica el estado de salud del servicio de asignaciones y sus dependencias.
38. `get_service_configuration_info() -> Dict[str, Any]` - Obtiene información de configuración y estado del servicio.

---

## Resumen por Categorías

| Categoría | Cantidad | Descripción |
|-----------|----------|-------------|
| **CRUD Principales** | 4 | Operaciones básicas de creación, lectura, actualización y eliminación |
| **CRUD Especializadas** | 3 | Operaciones CRUD con lógica de negocio avanzada y transacciones complejas |
| **Consulta por Empleado** | 5 | Búsquedas y análisis centrados en empleados específicos |
| **Consulta por Proyecto** | 4 | Búsquedas y análisis centrados en proyectos específicos |
| **Búsqueda y Filtrado** | 4 | Consultas complejas con múltiples criterios y detección de conflictos |
| **Gestión de Recursos** | 3 | Transferencias, reasignaciones y balanceo de cargas de trabajo |
| **Estadísticas Básicas** | 4 | Métricas y conteos fundamentales del sistema |
| **Estadísticas Avanzadas** | 4 | Análisis avanzados, tendencias y métricas de productividad |
| **Validación y Reglas** | 5 | Verificación de reglas de negocio, límites y disponibilidad |
| **Diagnóstico** | 2 | Monitoreo de salud y configuración del servicio |
| **Total** | **38** | **Métodos propuestos** |

---

## Características Especiales del Dominio

### Gestión de Solapamientos
- **Detección automática**: Identificación de conflictos de asignación en tiempo real
- **Resolución inteligente**: Sugerencias automáticas para resolver solapamientos
- **Validación preventiva**: Verificación antes de crear o modificar asignaciones

### Análisis de Carga de Trabajo
- **Distribución equilibrada**: Algoritmos para balancear cargas entre empleados
- **Límites configurables**: Respeto a límites máximos de asignación por empleado
- **Métricas de productividad**: Análisis de eficiencia y utilización de recursos

### Gestión Temporal Avanzada
- **Períodos flexibles**: Soporte para asignaciones con fechas variables
- **Planificación predictiva**: Análisis de tendencias para planificación futura
- **Historial completo**: Mantenimiento de auditoría completa de cambios

### Integración Multi-Repositorio
- **Validación cruzada**: Verificación de integridad entre empleados, proyectos y asignaciones
- **Sincronización automática**: Mantenimiento de consistencia de datos relacionados
- **Transacciones distribuidas**: Operaciones atómicas que afectan múltiples entidades