# Funciones Disponibles en TeamRepositoryFacade

**Fecha de actualización:** 2025-01-24

## Métodos del TeamRepositoryFacade

El `TeamRepositoryFacade` es la interfaz principal para todas las operaciones relacionadas con equipos. Proporciona acceso unificado a operaciones CRUD, consultas, validaciones, relaciones y estadísticas.

### OPERACIONES CRUD (3 métodos)

1. `create_team(team_data: Dict[str, Any]) -> Team` - Crea un nuevo equipo
2. `update_team(team_id: int, team_data: Dict[str, Any]) -> Team` - Actualiza un equipo existente
3. `delete_team(team_id: int) -> bool` - Elimina un equipo

### OPERACIONES DE CONSULTA (8 métodos)

4. `get_team_by_id(team_id: int) -> Optional[Team]` - Obtiene un equipo por su ID
5. `get_team_by_name(name: str) -> Optional[Team]` - Obtiene un equipo por su nombre
6. `get_teams_by_department(department: str, active_only: bool = True) -> List[Team]` - Obtiene equipos por departamento
7. `get_active_teams() -> List[Team]` - Obtiene todos los equipos activos
8. `get_inactive_teams() -> List[Team]` - Obtiene todos los equipos inactivos
9. `search_teams_by_criteria(criteria: Dict[str, Any], limit: Optional[int] = None, offset: Optional[int] = None) -> List[Team]` - Busca equipos por criterios específicos
10. `get_teams_with_pagination(page: int = 1, page_size: int = 20, filters: Optional[Dict[str, Any]] = None) -> Tuple[List[Team], int]` - Obtiene equipos con paginación
11. `count_teams(filters: Optional[Dict[str, Any]] = None) -> int` - Cuenta equipos con filtros opcionales

### MÉTODOS HEREDADOS DEL FACADE BASE (5 métodos)

12. `get_all(skip: int = 0, limit: int = 100) -> List[Team]` - Obtiene todos los equipos con paginación
13. `exists_by_id(team_id: int) -> bool` - Verifica si un equipo existe por su ID
14. `count_all(filters: Optional[Dict[str, Any]] = None) -> int` - Cuenta todos los equipos con filtros opcionales
15. `find_by_name(name: str) -> Optional[Team]` - Busca un equipo por nombre exacto
16. `find_by_code(code: str) -> Optional[Team]` - Busca un equipo por código exacto

### OPERACIONES DE BÚSQUEDA AVANZADA (1 método)

17. `search_teams(search_term: str, skip: int = 0, limit: int = 100) -> List[Team]` - Busca equipos por término de búsqueda con paginación

### OPERACIONES DE RELACIONES - GESTIÓN DE MIEMBROS (8 métodos)

18. `add_team_member(team_id: int, employee_id: int, role: str, is_leader: bool = False, start_date: Optional[date] = None) -> TeamMembership` - Añade un miembro al equipo
19. `remove_team_member(team_id: int, employee_id: int, end_date: Optional[date] = None) -> bool` - Remueve un miembro del equipo
20. `assign_team_leader(team_id: int, employee_id: int) -> TeamMembership` - Asigna un líder al equipo
21. `get_team_members(team_id: int, active_only: bool = True, include_details: bool = False) -> List[TeamMembership]` - Obtiene miembros de un equipo
22. `get_team_leader(team_id: int) -> Optional[TeamMembership]` - Obtiene el líder de un equipo
23. `get_employee_teams(employee_id: int, active_only: bool = True, include_details: bool = False) -> List[TeamMembership]` - Obtiene equipos de un empleado
24. `get_teams_with_members_details(team_ids: Optional[List[int]] = None, active_only: bool = True) -> List[Dict[str, Any]]` - Obtiene equipos con detalles de miembros
25. `update_member_role(team_id: int, employee_id: int, new_role: str) -> TeamMembership` - Actualiza el rol de un miembro

### OPERACIONES DE ESTADÍSTICAS (10 métodos)

26. `count_total_teams(active_only: bool = True) -> int` - Cuenta el total de equipos
27. `get_team_size_distribution() -> Dict[str, int]` - Obtiene distribución de tamaños de equipos
28. `get_membership_trends(start_date: date, end_date: date, granularity: str = "monthly") -> List[Dict[str, Any]]` - Obtiene tendencias de membresías
29. `get_leadership_statistics() -> Dict[str, Any]` - Obtiene estadísticas de liderazgo
30. `get_department_team_distribution() -> Dict[str, int]` - Obtiene distribución de equipos por departamento
31. `get_average_team_size(department: Optional[str] = None) -> float` - Obtiene el tamaño promedio de equipos
32. `get_teams_without_leader() -> List[Team]` - Obtiene equipos sin líder
33. `get_most_active_employees_in_teams(limit: int = 10) -> List[Dict[str, Any]]` - Obtiene empleados más activos en equipos
34. `get_team_creation_trends(start_date: date, end_date: date, granularity: str = "monthly") -> List[Dict[str, Any]]` - Obtiene tendencias de creación de equipos
35. `generate_teams_summary_report(include_inactive: bool = False) -> Dict[str, Any]` - Genera reporte resumen de equipos

### OPERACIONES DE VALIDACIÓN (5 métodos)

36. `validate_team_data(team_data: Dict[str, Any]) -> Dict[str, Any]` - Valida datos de equipo
37. `validate_membership_data(membership_data: Dict[str, Any]) -> Dict[str, Any]` - Valida datos de membresía
38. `check_membership_conflicts(employee_id: int, team_id: int) -> Dict[str, Any]` - Verifica conflictos de membresía
39. `validate_business_rules(operation: str, data: Dict[str, Any]) -> Dict[str, Any]` - Valida reglas de negocio
40. `validate_data_consistency() -> Dict[str, Any]` - Valida consistencia de datos

### OPERACIONES COMPUESTAS Y AVANZADAS (4 métodos)

41. `get_complete_team_info(team_id: int) -> Optional[Dict[str, Any]]` - Obtiene información completa de un equipo
42. `create_team_with_validation(team_data: Dict[str, Any]) -> Dict[str, Any]` - Crea equipo con validación completa
43. `add_team_member_with_validation(team_id: int, employee_id: int, role: str, is_leader: bool = False, start_date: Optional[date] = None) -> Dict[str, Any]` - Añade miembro con validación completa
44. `get_team_dashboard_data(team_id: Optional[int] = None, department: Optional[str] = None) -> Dict[str, Any]` - Obtiene datos para dashboard de equipos

### OPERACIONES MASIVAS (1 método)

45. `bulk_team_operation(operation: str, team_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]` - Ejecuta operaciones masivas en equipos

---

## Resumen de Funcionalidades

**Total de métodos públicos:** 45

**Distribución por categorías:**
- **CRUD básico**: 3 métodos (crear, actualizar, eliminar)
- **Consultas**: 8 métodos (búsquedas y obtención de datos)
- **Métodos base**: 5 métodos (heredados del facade base)
- **Búsqueda avanzada**: 1 método (búsqueda con términos)
- **Gestión de relaciones**: 8 métodos (miembros y liderazgo)
- **Estadísticas**: 10 métodos (análisis y reportes)
- **Validaciones**: 5 métodos (validación de datos y reglas)
- **Operaciones compuestas**: 4 métodos (operaciones complejas)
- **Operaciones masivas**: 1 método (procesamiento en lote)

**Características principales:**
- **Interfaz unificada**: Acceso centralizado a todas las operaciones de equipos
- **Validación integrada**: Métodos con validación automática de datos y reglas de negocio
- **Soporte para paginación**: Múltiples métodos con soporte para paginación
- **Análisis estadístico**: Amplio conjunto de métodos para análisis y reportes
- **Gestión de relaciones**: Manejo completo de membresías y liderazgo
- **Operaciones masivas**: Soporte para procesamiento en lote
- **Dashboard integrado**: Métodos especializados para interfaces de usuario

**Integración con módulos:**
- **CrudModule**: Operaciones CRUD básicas
- **QueryModule**: Consultas y búsquedas
- **ValidationModule**: Validación de datos y reglas
- **RelationshipModule**: Gestión de relaciones
- **StatisticsModule**: Análisis y estadísticas

**Casos de uso principales:**
- Gestión completa del ciclo de vida de equipos
- Administración de membresías y liderazgo
- Análisis estadístico y generación de reportes
- Validación de integridad de datos
- Operaciones masivas y procesamiento en lote
- Integración con interfaces de usuario (dashboards)