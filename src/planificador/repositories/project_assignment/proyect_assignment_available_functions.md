# Funciones Disponibles en ProjectAssignmentRepositoryFacade

**Fecha de actualización:** 2025-01-24

## Métodos del ProjectAssignmentRepositoryFacade

El `ProjectAssignmentRepositoryFacade` es la interfaz principal para todas las operaciones relacionadas con asignaciones de proyecto. Proporciona acceso unificado a operaciones CRUD, consultas, validaciones, relaciones y estadísticas.

### OPERACIONES CRUD (4 métodos)

1. `create_assignment(assignment_data: ProjectAssignmentCreate) -> ProjectAssignment` - Crea una nueva asignación de proyecto
2. `update_assignment(assignment_id: int, assignment_data: ProjectAssignmentUpdate) -> ProjectAssignment | None` - Actualiza una asignación existente
3. `delete_assignment(assignment_id: int) -> bool` - Elimina una asignación por su ID
4. `get_assignment_by_id(assignment_id: int) -> ProjectAssignment | None` - Obtiene una asignación por su ID

### OPERACIONES DE CONSULTA (8 métodos)

5. `get_all_assignments(limit: int | None = None, offset: int = 0) -> list[ProjectAssignment]` - Obtiene todas las asignaciones con paginación opcional
6. `get_assignments_by_employee(employee_id: int) -> list[ProjectAssignment]` - Obtiene todas las asignaciones de un empleado específico
7. `get_assignments_by_project(project_id: int) -> list[ProjectAssignment]` - Obtiene todas las asignaciones de un proyecto específico
8. `get_active_assignments() -> list[ProjectAssignment]` - Obtiene todas las asignaciones activas
9. `get_assignments_by_date_range(start_date: date, end_date: date) -> list[ProjectAssignment]` - Obtiene asignaciones que se superponen con un rango de fechas
10. `get_assignments_by_role(role: str) -> list[ProjectAssignment]` - Obtiene asignaciones por rol específico
11. `get_assignments_with_filters(...) -> list[ProjectAssignment]` - Obtiene asignaciones aplicando múltiples filtros
12. `get_overlapping_assignments(employee_id: int, start_date: date, end_date: date, exclude_id: int | None = None) -> list[ProjectAssignment]` - Obtiene asignaciones que se superponen para un empleado en un período

### OPERACIONES DE RELACIONES (7 métodos)

13. `get_assignments_with_employee_data(limit: int | None = None, offset: int = 0) -> list[ProjectAssignment]` - Obtiene asignaciones con datos del empleado incluidos
14. `get_assignments_with_project_data(limit: int | None = None, offset: int = 0) -> list[ProjectAssignment]` - Obtiene asignaciones con datos del proyecto incluidos
15. `get_assignments_with_full_data(limit: int | None = None, offset: int = 0) -> list[ProjectAssignment]` - Obtiene asignaciones con datos completos de empleado y proyecto
16. `transfer_employee_assignments(from_employee_id: int, to_employee_id: int, project_id: int | None = None) -> bool` - Transfiere asignaciones de un empleado a otro
17. `reassign_project_assignments(from_project_id: int, to_project_id: int, employee_id: int | None = None) -> bool` - Reasigna asignaciones de un proyecto a otro
18. `get_employee_workload_summary(employee_id: int) -> dict[str, Any]` - Obtiene un resumen de la carga de trabajo de un empleado
19. `get_project_team_summary(project_id: int) -> dict[str, Any]` - Obtiene un resumen del equipo de un proyecto

### OPERACIONES DE ESTADÍSTICAS (12 métodos)

20. `get_total_assignments_count() -> int` - Obtiene el número total de asignaciones
21. `get_active_assignments_count() -> int` - Obtiene el número de asignaciones activas
22. `get_assignments_by_status_count() -> dict[str, int]` - Obtiene el conteo de asignaciones por estado
23. `get_assignments_by_allocation_category_count() -> dict[str, int]` - Obtiene el conteo de asignaciones por categoría de asignación
24. `get_employee_assignment_stats(employee_id: int) -> dict[str, Any]` - Obtiene estadísticas de asignaciones para un empleado específico
25. `get_project_assignment_stats(project_id: int) -> dict[str, Any]` - Obtiene estadísticas de asignaciones para un proyecto específico
26. `get_assignment_duration_stats() -> dict[str, Any]` - Obtiene estadísticas de duración de asignaciones
27. `get_workload_distribution_stats() -> dict[str, Any]` - Obtiene estadísticas de distribución de carga de trabajo
28. `get_assignment_trends(days: int = 30) -> list[dict[str, Any]]` - Obtiene tendencias de asignaciones en un período
29. `get_overlap_statistics() -> dict[str, Any]` - Obtiene estadísticas de superposición de asignaciones
30. `get_role_distribution_stats() -> dict[str, int]` - Obtiene estadísticas de distribución por roles
31. `get_comprehensive_dashboard_metrics() -> dict[str, Any]` - Obtiene métricas completas para el dashboard

### OPERACIONES DE VALIDACIÓN (11 métodos)

32. `validate_assignment_data(assignment_data: dict[str, Any], exclude_id: int | None = None) -> None` - Valida los datos básicos de una asignación
33. `validate_required_fields(assignment_data: dict[str, Any]) -> None` - Valida que los campos requeridos estén presentes
34. `validate_date_range(start_date: date, end_date: date) -> None` - Valida que el rango de fechas sea válido
35. `validate_allocation_percentage(allocation_percentage: float) -> None` - Valida que el porcentaje de asignación sea válido
36. `validate_hours_per_day(hours_per_day: float) -> None` - Valida que las horas por día sean válidas
37. `validate_employee_exists(employee_id: int) -> None` - Valida que el empleado exista
38. `validate_project_exists(project_id: int) -> None` - Valida que el proyecto exista
39. `validate_no_overlapping_assignments(employee_id: int, start_date: date, end_date: date, exclude_id: int | None = None) -> None` - Valida que no haya asignaciones superpuestas
40. `validate_workload_limits(employee_id: int, start_date: date, end_date: date, allocation_percentage: float) -> None` - Valida que no se excedan los límites de carga de trabajo
41. `validate_assignment_deletion(assignment_id: int) -> None` - Valida que una asignación pueda ser eliminada
42. `validate_business_rules(assignment_data: dict[str, Any], exclude_id: int | None = None) -> None` - Valida reglas de negocio específicas

---

## Resumen de Funcionalidades

**Total de métodos públicos:** 42

**Distribución por categorías:**
- **CRUD básico**: 4 métodos (crear, actualizar, eliminar, obtener por ID)
- **Consultas**: 8 métodos (búsquedas y obtención de datos con filtros)
- **Relaciones**: 7 métodos (gestión de relaciones entre asignaciones, empleados y proyectos)
- **Estadísticas**: 12 métodos (análisis y reportes de asignaciones)
- **Validaciones**: 11 métodos (validación de datos y reglas de negocio)

**Características principales:**
- **Interfaz unificada**: Acceso centralizado a todas las operaciones de asignaciones de proyecto
- **Validación integrada**: Métodos con validación automática de datos y reglas de negocio
- **Soporte para paginación**: Múltiples métodos con soporte para paginación
- **Análisis estadístico**: Amplio conjunto de métodos para análisis y reportes
- **Gestión de relaciones**: Manejo completo de relaciones entre asignaciones, empleados y proyectos
- **Control de superposiciones**: Validación y detección de asignaciones superpuestas
- **Dashboard integrado**: Métodos especializados para interfaces de usuario

**Integración con módulos:**
- **CrudOperations**: Operaciones CRUD básicas
- **QueryOperations**: Consultas y búsquedas avanzadas
- **RelationshipOperations**: Gestión de relaciones y transferencias
- **StatisticsOperations**: Análisis estadístico y métricas
- **ValidationOperations**: Validación de datos y reglas de negocio

**Casos de uso principales:**
- Gestión completa del ciclo de vida de asignaciones de proyecto
- Control de carga de trabajo y distribución de recursos
- Análisis de tendencias y patrones de asignación
- Validación de integridad y reglas de negocio
- Generación de reportes y métricas para dashboards
- Transferencia y reasignación de recursos entre proyectos

**Ejemplo de uso básico:**
```python
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.schemas.project_assignment import ProjectAssignmentCreate
from datetime import date

# Inicializar facade
facade = ProjectAssignmentRepositoryFacade(session)

# Crear nueva asignación con validación
assignment_data = ProjectAssignmentCreate(
    employee_id=1, project_id=1, role="Developer",
    start_date=date(2024, 1, 1), end_date=date(2024, 12, 31),
    allocation_percentage=80.0
)

await facade.validate_assignment_data(assignment_data.dict())
new_assignment = await facade.create_assignment(assignment_data)

# Obtener métricas del dashboard
dashboard_metrics = await facade.get_comprehensive_dashboard_metrics()
```