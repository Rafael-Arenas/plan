# Funciones Disponibles en Workload Repository

**Fecha de actualización:** 2025-08-19

## Módulos y Funciones

### WorkloadRepository (workload_repository.py)

#### Operaciones CRUD Básicas (7 funciones)
1. `create(workload_data: Dict[str, Any]) -> Workload` - Crea una nueva carga de trabajo con validación completa
2. `create_workload(workload_data: Dict[str, Any]) -> Workload` - Alias para crear carga de trabajo
4. `update(workload_id: int, update_data: Dict[str, Any]) -> Workload` - Actualiza una carga de trabajo existente
5. `update_workload(workload_id: int, update_data: Dict[str, Any]) -> Workload` - Alias para actualizar carga de trabajo
6. `delete(entity_id: int) -> bool` - Elimina una carga de trabajo por ID
7. `delete_workload(workload_id: int) -> bool` - Alias para eliminar carga de trabajo

#### Consultas de Delegación - Query Builder (12 funciones)
3. `get_workload_by_id(workload_id: int) -> Optional[Workload]` - Obtiene una carga de trabajo por su ID
8. `get_workloads_by_employee(employee_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Workload]` - Obtiene cargas de trabajo de un empleado en rango de fechas
9. `get_by_employee_and_date(employee_id: int, workload_date: date) -> Optional[Workload]` - Obtiene carga de trabajo específica de empleado en fecha
10. `get_workloads_by_date_range(start_date: date, end_date: date) -> List[Workload]` - Obtiene todas las cargas de trabajo en rango de fechas
11. `get_by_date_range(start_date: date, end_date: date) -> List[Workload]` - Alias para obtener cargas por rango de fechas
12. `get_workloads_by_project(project_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Workload]` - Obtiene cargas de trabajo de un proyecto específico
13. `get_overloaded_employees(target_date: date, threshold_hours: float = 8.0) -> List[Dict[str, Any]]` - Identifica empleados con sobrecarga de trabajo
14. `get_underutilized_employees(target_date: date, threshold_hours: float = 4.0) -> List[Dict[str, Any]]` - Identifica empleados con baja utilización
15. `get_team_workloads(team_id: int, start_date: date, end_date: date) -> List[Workload]` - Obtiene cargas de trabajo de un equipo en rango de fechas
16. `get_team_workload(team_id: int, target_date: date) -> List[Dict[str, Any]]` - Obtiene carga de trabajo de equipo en fecha específica
17. `get_weekly_workload(employee_id: int, week_start: date) -> float` - Calcula total de horas trabajadas por empleado en una semana
18. `get_team_workload_summary(team_id: int, target_date: date) -> Dict[str, Any]` - Obtiene resumen de carga de trabajo de un equipo
19. `get_workload_with_employee(workload_id: int) -> Optional[Workload]` - Obtiene carga de trabajo con empleado asociado
20. `get_workload_with_project(workload_id: int) -> Optional[Workload]` - Obtiene carga de trabajo con proyecto asociado
21. `get_workload_with_all_relations(workload_id: int) -> Optional[Workload]` - Obtiene carga de trabajo con todas las relaciones
22. `get_employee_workloads_with_projects(employee_id: int) -> List[Workload]` - Obtiene cargas de empleado con proyectos asociados
23. `get_project_workloads_with_employees(project_id: int) -> List[Workload]` - Obtiene cargas de proyecto con empleados asociados
24. `get_team_workloads_detailed(team_id: int) -> List[Workload]` - Obtiene resumen detallado de cargas de trabajo de equipo

#### Consultas de Delegación - Estadísticas (3 funciones)
25. `get_project_workload_statistics(project_id: int) -> Dict[str, Any]` - Obtiene estadísticas de carga de trabajo de proyecto
26. `get_workload_summary_by_employee(employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]` - Obtiene resumen de carga de trabajo de empleado
27. `get_workload_trends_by_employee(employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]` - Obtiene tendencias de la carga de trabajo de un empleado

#### Consultas de Delegación - Validaciones (1 función)
28. `check_employee_project_consistency(workload_id: int, employee_id: int, project_id: int) -> bool` - Verifica consistencia entre empleado y proyecto asignados

---

### WorkloadQueryBuilder (workload_query_builder.py)

#### Consultas Básicas (5 funciones)
29. `get_by_employee(employee_id: int) -> List[Workload]` - Obtiene todas las cargas de trabajo de un empleado
30. `get_by_employee_and_date(employee_id: int, workload_date: date) -> Optional[Workload]` - Busca carga de trabajo específica por empleado y fecha
31. `get_by_employee_date_range(employee_id: int, start_date: date, end_date: date) -> List[Workload]` - Obtiene cargas de empleado en rango de fechas
32. `get_by_project_and_date(project_id: int, workload_date: date) -> List[Workload]` - Obtiene cargas de proyecto en fecha específica
33. `get_by_date_range(start_date: date, end_date: date) -> List[Workload]` - Obtiene todas las cargas en rango de fechas

#### Consultas Especializadas (6 funciones)
34. `get_overloaded_employees(target_date: date, threshold_hours: float = 8.0) -> List[Workload]` - Obtiene empleados sobrecargados en fecha
35. `get_underutilized_employees(target_date: date, threshold_hours: float = 4.0) -> List[Workload]` - Obtiene empleados subutilizados en fecha
36. `get_with_relations(workload_id: int) -> Optional[Workload]` - Obtiene carga con todas las relaciones cargadas
37. `get_team_workload(team_id: int, target_date: date) -> List[Dict[str, Any]]` - Obtiene carga de trabajo de equipo en fecha específica
38. `get_by_project(project_id: int) -> List[Workload]` - Obtiene todas las cargas de trabajo de un proyecto
39. `get_by_project_date_range(project_id: int, start_date: date, end_date: date) -> List[Workload]` - Obtiene cargas de proyecto en rango de fechas

### WorkloadRelationshipManager (workload_relationship_manager.py)

#### Gestión de Relaciones (4 funciones)
40. `get_workload_with_employee(workload_id: int) -> Optional[Workload]` - Obtiene carga de trabajo con información del empleado
41. `get_workload_with_project(workload_id: int) -> Optional[Workload]` - Obtiene carga de trabajo con información del proyecto
42. `get_workload_with_all_relations(workload_id: int) -> Optional[Workload]` - Obtiene carga de trabajo con todas sus relaciones cargadas
43. `get_employee_workloads_with_projects(employee_id: int, start_date: Optional[date], end_date: Optional[date]) -> List[Workload]` - Obtiene cargas de trabajo de un empleado con información de proyectos
44. `get_project_workloads_with_employees(project_id: int, start_date: Optional[date], end_date: Optional[date]) -> List[Workload]` - Obtiene cargas de trabajo de un proyecto con información de empleados
45. `get_team_workloads_detailed(team_id: int, target_date: date) -> List[Dict[str, Any]]` - Obtiene cargas de trabajo detalladas de un equipo para una fecha específica

#### Validación de Existencia (3 funciones)
46. `validate_workload_exists(workload_id: int) -> Workload` - Valida que una carga de trabajo existe y la retorna
47. `validate_employee_exists(employee_id: int) -> Employee` - Valida que un empleado existe y lo retorna
48. `validate_project_exists(project_id: int) -> Project` - Valida que un proyecto existe y lo retorna

#### Gestión de Conflictos (1 función)
49. `check_workload_uniqueness(employee_id: int, workload_date: date, exclude_id: Optional[int]) -> bool` - Verifica si ya existe una carga de trabajo para un empleado en una fecha específica

### WorkloadStatistics (workload_statistics.py)

#### Estadísticas por Empleado (2 funciones)
50. `get_workload_summary_by_employee(employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]` - Obtiene un resumen estadístico de cargas de trabajo por empleado
51. `get_workload_trends_by_employee(employee_id: int, days: int = 30) -> List[Dict[str, Any]]` - Obtiene tendencias de carga de trabajo por empleado en los últimos días

#### Estadísticas por Proyecto (1 función)
52. `get_project_workload_statistics(project_id: int, start_date: date, end_date: date) -> Dict[str, Any]` - Obtiene estadísticas de carga de trabajo por proyecto
53. `get_team_workload_distribution(team_id: int, target_date: date) -> Dict[str, Any]` - Obtiene la distribución de carga de trabajo de un equipo para una fecha específica

#### Análisis Avanzado (2 funciones)
54. `get_workload_capacity_analysis(start_date: date, end_date: date) -> Dict[str, Any]` - Analiza la capacidad de carga de trabajo general en un período
55. `get_efficiency_rankings(start_date: date, end_date: date, limit: int = 10) -> List[Dict[str, Any]]` - Obtiene un ranking de empleados por eficiencia en un período

### WorkloadValidator (workload_validator.py)

#### Funciones Públicas (6 funciones)
56. `validate_create_data(data: Dict[str, Any]) -> None` - Valida los datos para crear una nueva carga de trabajo
57. `validate_update_data(data: Dict[str, Any], workload_id: int = None) -> None` - Valida los datos para actualizar una carga de trabajo
58. `validate_date_range(start_date: date, end_date: date) -> None` - Valida un rango de fechas
59. `validate_threshold_hours(threshold_hours: float) -> None` - Valida un umbral de horas
60. `validate_team_id(team_id: int) -> None` - Valida el ID del equipo
61. `validate_workload_id(workload_id: int) -> None` - Valida el ID de la carga de trabajo

#### Funciones Privadas (8 funciones)
62. `_validate_required_fields_for_create(data: Dict[str, Any]) -> None` - **[PRIVADA]** Valida que los campos requeridos estén presentes para crear una carga de trabajo
63. `_validate_employee_id(employee_id: int) -> None` - **[PRIVADA]** Valida el ID del empleado
64. `_validate_date(workload_date) -> None` - **[PRIVADA]** Valida la fecha de la carga de trabajo
65. `_validate_actual_hours(actual_hours: float) -> None` - **[PRIVADA]** Valida las horas reales trabajadas
66. `_validate_planned_hours(planned_hours: Optional[float]) -> None` - **[PRIVADA]** Valida las horas planificadas
67. `_validate_efficiency_score(efficiency_score: Optional[float]) -> None` - **[PRIVADA]** Valida el puntaje de eficiencia
68. `_validate_project_id(project_id: Optional[int]) -> None` - **[PRIVADA]** Valida el ID del proyecto
69. `_validate_is_billable(is_billable: Optional[bool]) -> None` - **[PRIVADA]** Valida el campo de facturación

---

**Total de funciones disponibles:** 68

**Distribución por módulos:**
- WorkloadRepository: 28 funciones
- WorkloadQueryBuilder: 11 funciones
- WorkloadRelationshipManager: 10 funciones
- WorkloadStatistics: 6 funciones
- WorkloadValidator: 14 funciones (6 públicas + 8 privadas)

**Categorías principales:**
- **CRUD básico**: 7 funciones (crear, leer, actualizar, eliminar)
- **Consultas especializadas**: 26 funciones (por empleado, proyecto, equipo y análisis)
- **Análisis y estadísticas**: 12 funciones (carga de trabajo, tendencias y métricas avanzadas)
- **Gestión de relaciones y validaciones**: 10 funciones
- **Validación de datos**: 14 funciones (6 públicas + 8 privadas)

**Total de funciones documentadas**: 69