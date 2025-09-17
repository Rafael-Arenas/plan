# Funciones Disponibles en Team Repository

**Fecha de actualización:** 2025-08-19

## Módulos y Funciones

### CrudTeamRepository (crud_repository.py)

#### Operaciones CRUD Básicas (3 funciones)
1. `create_team(team_data: Dict[str, Any]) -> Team` - Crea un nuevo equipo con validaciones
2. `update_team(team_id: int, update_data: Dict[str, Any]) -> Optional[Team]` - Actualiza un equipo con validaciones
4. `delete_team(team_id: int) -> bool` - Elimina un equipo (heredado de BaseRepository)

#### Consultas de Delegación - Query Builder (8 funciones)
5. `search_by_name(search_term: str) -> List[Team]` - Busca equipos por término en el nombre (búsqueda parcial)
6. `search_by_code(search_term: str) -> List[Team]` - Busca equipos por término en el código (búsqueda parcial)
7. `search_by_description(search_term: str) -> List[Team]` - Busca equipos por término en la descripción
8. `get_active_teams() -> List[Team]` - Obtiene todos los equipos activos
3. `get_by_name(name: str) -> Optional[Team]` - Obtiene un equipo por su nombre exacto
9. `get_by_department(department: str) -> List[Team]` - Obtiene equipos por departamento
10. `get_by_leader(leader_id: int) -> List[Team]` - Obtiene equipos liderados por un empleado específico
11. `get_teams_by_size_range(min_size: int, max_size: int) -> List[Team]` - Obtiene equipos cuyo número de miembros esté dentro del rango especificado
12. `get_by_id(team_id: int) -> Optional[Team]` - Obtiene equipo por ID (heredado de BaseRepository)

#### Consultas de Delegación - Estadísticas (3 funciones)
13. `get_team_stats(team_id: int) -> Dict[str, Any]` - Obtiene estadísticas de un equipo específico
14. `get_teams_by_department_summary() -> Dict[str, int]` - Obtiene un resumen de equipos agrupados por departamento
15. `get_team_activity_stats(team_id: int) -> Dict[str, Any]` - Calcula estadísticas de actividad de un equipo usando Pendulum

#### Consultas de Delegación - Relaciones (3 funciones)
16. `get_with_leader(team_id: int) -> Optional[Team]` - Obtiene un equipo con información del líder cargada
17. `get_with_members(team_id: int) -> Optional[Team]` - Obtiene un equipo con información de miembros cargada
18. `get_with_all_relations(team_id: int) -> Optional[Team]` - Obtiene un equipo con todas las relaciones cargadas

#### Consultas de Delegación - Validaciones (2 funciones)
19. `name_exists(name: str, exclude_id: Optional[int] = None) -> bool` - Verifica si existe un equipo con el nombre dado
20. `code_exists(code: str, exclude_id: Optional[int] = None) -> bool` - Verifica si existe un equipo con el código dado

#### Métodos de Compatibilidad (10 funciones)
21. `get_team_members(team_id: int, active_only: bool = True) -> List[Employee]` - Obtiene los miembros de un equipo
22. `is_member(team_id: int, employee_id: int, active_only: bool = True) -> bool` - Verifica si un empleado es miembro de un equipo
23. `add_member(team_id: int, employee_id: int, role: Optional[MembershipRole] = None, start_date: Optional[date] = None) -> TeamMembership` - Añade un miembro a un equipo
24. `remove_member(team_id: int, employee_id: int, end_date: Optional[date] = None) -> bool` - Remueve un miembro de un equipo
25. `update_member_role(team_id: int, employee_id: int, new_role: MembershipRole) -> bool` - Actualiza el rol de un miembro en el equipo
26. `get_teams_created_current_week(**kwargs) -> List[Team]` - Obtiene equipos creados en la semana actual usando Pendulum
27. `get_teams_created_current_month(**kwargs) -> List[Team]` - Obtiene equipos creados en el mes actual usando Pendulum
28. `get_teams_created_business_days_only(start_date: Union[date, str, None] = None, end_date: Union[date, str, None] = None, **kwargs) -> List[Team]` - Obtiene equipos creados solo en días laborables
29. `get_teams_by_age_range(min_days: int = 0, max_days: Optional[int] = None, department: Optional[str] = None, active_only: bool = True) -> List[Dict[str, Any]]` - Obtiene equipos por rango de edad usando Pendulum
30. `create_team_with_pendulum_validation(team_data: Dict[str, Any], validate_creation_business_day: bool = False) -> Team` - Crea un equipo con validaciones avanzadas usando Pendulum
31. `get_team_membership_duration_stats(team_id: int, employee_id: int) -> Dict[str, Any]` - Calcula estadísticas de duración de membresía usando Pendulum
32. `format_team_created_at(team: Team) -> Optional[str]` - Formatea la fecha de creación del equipo
33. `get_all() -> List[Team]` - Obtiene todos los equipos (heredado de BaseRepository)

---

### TeamQueryBuilder (team_query_builder.py)

#### Consultas Básicas (5 funciones)
34. `build_base_query() -> select` - Construye la consulta base para equipos
35. `build_active_teams_query() -> select` - Construye consulta para equipos activos
36. `build_by_name_query(name: str) -> select` - Construye consulta para buscar equipo por nombre exacto
37. `build_search_by_name_query(search_term: str) -> select` - Construye consulta para búsqueda parcial por nombre
38. `search_by_description(search_term: str) -> select` - Construye consulta para búsqueda por descripción

#### Consultas por Relaciones (5 funciones)
39. `build_by_leader_query(leader_id: int) -> select` - Construye consulta para equipos por líder
40. `build_by_department_query(department: str) -> select` - Construye consulta para equipos por departamento
41. `build_with_leader_query(team_id: int) -> select` - Construye consulta para equipo con líder cargado
42. `build_with_members_query(team_id: int) -> select` - Construye consulta para equipo con miembros cargados
43. `build_with_all_relations_query(team_id: int) -> select` - Construye consulta para equipo con todas las relaciones

#### Consultas de Membresías (3 funciones)
44. `build_membership_query(team_id: int, employee_id: int, active_only: bool = True) -> select` - Construye consulta para verificar membresía
45. `build_teams_by_size_query(min_size: int, max_size: int) -> select` - Construye consulta para equipos por tamaño
46. `build_teams_by_member_query(employee_id: int) -> select` - Construye consulta para equipos de un miembro

#### Consultas de Análisis (4 funciones)
47. `build_team_size_stats_query() -> select` - Construye consulta para estadísticas de tamaño de equipos
48. `build_departments_query() -> select` - Construye consulta para obtener departamentos únicos
49. `build_teams_without_leader_query() -> select` - Construye consulta para equipos sin líder
50. `build_teams_by_role_query(role: MembershipRole) -> select` - Construye consulta para equipos por rol de membresía

#### Métodos de Compatibilidad (3 funciones)
51. `get_teams_by_size_range(min_size: int, max_size: int) -> select` - Alias para build_teams_by_size_query
52. `get_active_teams() -> select` - Alias para build_active_teams_query
53. `get_by_name(name: str) -> select` - Alias para build_by_name_query

---

### TeamValidator (team_validator.py)

#### Validación de Equipo (2 funciones)
54. `validate_team_data(team_data: Dict[str, Any]) -> Dict[str, Any]` - Valida datos completos de un equipo
55. `validate_team_name_uniqueness(name: str, exclude_id: Optional[int] = None) -> bool` - Valida unicidad del nombre del equipo

#### Validación de Membresía (2 funciones)
56. `validate_membership_data(membership_data: Dict[str, Any]) -> Dict[str, Any]` - Valida datos de membresía de equipo
57. `validate_membership_uniqueness(team_id: int, employee_id: int) -> bool` - Valida unicidad de membresía

#### Validación de Reglas de Negocio (2 funciones)
58. `validate_leader_assignment(team_id: int, leader_id: int) -> bool` - Valida asignación de líder a equipo
59. `validate_role_change(current_role: str, new_role: str) -> bool` - Valida cambio de rol de miembro

#### Validación de Consistencia (1 función)
60. `validate_team_deletion(team_id: int) -> bool` - Valida que un equipo puede ser eliminado

#### Métodos de Compatibilidad (1 función)
61. `validate_unique_name(name: str, exclude_id: Optional[int] = None) -> bool` - Alias para validate_team_name_uniqueness

---

### TeamRelationshipManager (team_relationship_manager.py)

#### Gestión de Membresías (4 funciones)
62. `add_member(team_id: int, employee_id: int, role: str = MembershipRole.MEMBER.value, start_date: Optional[date] = None) -> TeamMembership` - Añade un miembro al equipo
63. `remove_member(team_id: int, employee_id: int) -> bool` - Remueve un miembro del equipo
64. `update_member_role(team_id: int, employee_id: int, new_role: str) -> bool` - Actualiza el rol de un miembro
65. `get_active_membership(team_id: int, employee_id: int) -> Optional[TeamMembership]` - Obtiene la membresía activa de un empleado en un equipo

#### Gestión de Liderazgo (2 funciones)
66. `assign_leader(team_id: int, leader_id: int) -> bool` - Asigna un líder al equipo
67. `remove_leader(team_id: int) -> bool` - Remueve el líder del equipo

#### Consultas de Relaciones (3 funciones)
68. `get_teams_by_member(employee_id: int) -> List[Team]` - Obtiene equipos donde el empleado es miembro
69. `get_team_members(team_id: int, active_only: bool = True) -> List[Employee]` - Obtiene miembros de un equipo
70. `get_members_by_role(team_id: int, role: MembershipRole) -> List[Employee]` - Obtiene miembros de un equipo por rol específico

---

### TeamStatistics (team_statistics.py)

#### Estadísticas Básicas (3 funciones)
71. `get_team_count_stats() -> Dict[str, int]` - Obtiene conteo de equipos (totales, activos, con/sin líder)
72. `get_team_size_distribution() -> Dict[str, Any]` - Obtiene distribución de tamaños por equipo
73. `get_department_stats() -> Dict[str, Any]` - Obtiene estadísticas por departamento

#### Estadísticas de Membresías (3 funciones)
74. `get_membership_stats() -> Dict[str, Any]` - Obtiene conteo de membresías (totales, activas, distribución por rol)
75. `get_employee_team_participation(employee_id: int) -> Dict[str, Any]` - Obtiene participación de empleados en equipos
76. `get_membership_trends(start_date: date, end_date: date) -> Dict[str, Any]` - Obtiene tendencias de membresías en un período

#### Métricas Avanzadas (2 funciones)
77. `get_team_efficiency_metrics(team_id: int) -> Dict[str, Any]` - Obtiene métricas de eficiencia de equipos
78. `_categorize_team_size(size: int) -> str` - **[PRIVADA]** Categoriza el tamaño de un equipo

#### Reportes (1 función)
79. `get_summary_report() -> Dict[str, Any]` - Obtiene reporte resumen completo de estadísticas de equipos

---

**Total de funciones disponibles:** 79

**Distribución por módulos:**
- TeamRepository: 33 funciones
- TeamQueryBuilder: 20 funciones (5 básicas + 5 relaciones + 3 membresías + 4 análisis + 3 compatibilidad)
- TeamValidator: 8 funciones (2 equipo + 2 membresía + 2 reglas + 1 consistencia + 1 compatibilidad)
- TeamRelationshipManager: 9 funciones (4 membresías + 2 liderazgo + 3 consultas)
- TeamStatistics: 9 funciones

**Categorías principales:**
- **CRUD básico**: 8 funciones (crear, leer, actualizar, eliminar equipos y membresías)
- **Consultas especializadas**: 34 funciones (por nombre, departamento, líder, miembros, análisis)
- **Gestión de relaciones**: 9 funciones (membresías, liderazgo, consultas de relaciones)
- **Análisis y estadísticas**: 17 funciones (conteos, distribuciones, tendencias, métricas y estadísticas adicionales)
- **Validación de datos**: 8 funciones (equipos, membresías, reglas de negocio y consistencia)

**Funcionalidades especiales:**
- **Integración con Pendulum**: 6 funciones para manejo avanzado de fechas y tiempo
- **Análisis de actividad**: 3 funciones para estadísticas de actividad y duración
- **Validaciones de negocio**: 8 funciones para garantizar integridad de datos
- **Gestión de membresías**: 9 funciones para administración de miembros y liderazgo
- **Consultas especializadas**: 34 funciones para búsquedas avanzadas y análisis

**Total de funciones documentadas**: 79