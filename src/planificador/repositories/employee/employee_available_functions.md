# Funciones Disponibles en EmployeeRepositoryFacade

**Última actualización:** Enero 2025

## Descripción General

`EmployeeRepositoryFacade` es la clase principal que proporciona una interfaz unificada para todas las operaciones relacionadas con empleados en el sistema. Esta fachada encapsula la lógica de acceso a datos y coordina las operaciones entre diferentes módulos especializados, ofreciendo una API coherente y fácil de usar para la gestión completa de empleados.

---

## Métodos Disponibles

### 1. Operaciones CRUD (4 métodos)

1. `create_employee(employee_data: Dict[str, Any]) -> Employee` - Crea un nuevo empleado después de validar los datos de entrada
2. `update_employee(employee_id: int, update_data: Dict[str, Any]) -> Optional[Employee]` - Actualiza los datos de un empleado existente
3. `delete_employee(employee_id: int) -> bool` - Elimina un empleado de la base de datos
4. `get_by_unique_field(field_name: str, value: Any) -> Optional[Employee]` - Obtiene un empleado por un campo único específico

### 2. Operaciones de Fechas (8 métodos)

5. `get_employees_hired_current_week(**kwargs) -> List[Employee]` - Obtiene los empleados contratados en la semana actual
6. `get_employees_hired_current_month(**kwargs) -> List[Employee]` - Obtiene los empleados contratados en el mes actual
7. `get_employees_hired_business_days_only(start_date, end_date, **kwargs) -> List[Employee]` - Obtiene empleados contratados únicamente en días laborables dentro de un rango
8. `get_by_hire_date_range(start_date: date, end_date: date, **kwargs) -> List[Employee]` - Obtiene empleados por rango de fecha de contratación
9. `get_employee_tenure_stats(employee_id: int) -> Dict[str, Any]` - Calcula estadísticas de antigüedad para un empleado específico
10. `get_employees_by_tenure_range(min_years, max_years, status) -> List[Dict[str, Any]]` - Obtiene empleados según un rango de años de antigüedad
11. `create_employee_with_date_validation(employee_data, validate_hire_date_business_day) -> Employee` - Crea un empleado aplicando validaciones avanzadas sobre la fecha de contratación
12. `format_employee_hire_date(employee: Employee, format_type: str) -> Optional[str]` - Formatea la fecha de contratación de un empleado a un formato legible

### 3. Operaciones de Consulta (22 métodos)

13. `get_by_id(employee_id: int) -> Optional[Employee]` - Obtiene un empleado por su ID único
14. `get_all(skip: int = 0, limit: int = 100) -> List[Employee]` - Obtiene una lista paginada de todos los empleados
15. `employee_exists(employee_id: int) -> bool` - Verifica si un empleado existe por su ID
16. `count() -> int` - Devuelve el número total de empleados
17. `search_by_name(name: str, **kwargs) -> List[Employee]` - Busca empleados por su nombre
18. `get_by_email(email: str) -> Optional[Employee]` - Obtiene un empleado por su dirección de correo electrónico
19. `get_by_status(status: EmployeeStatus, **kwargs) -> List[Employee]` - Obtiene empleados filtrando por su estado (activo, inactivo, etc.)
20. `get_available_employees(**kwargs) -> List[Employee]` - Obtiene empleados con estado "disponible"
21. `search_by_skills(skills: Union[str, List[str]], **kwargs) -> List[Employee]` - Busca empleados que posean ciertas habilidades
22. `get_by_department(department: str, **kwargs) -> List[Employee]` - Obtiene empleados de un departamento específico
23. `get_by_position(position: str, **kwargs) -> List[Employee]` - Obtiene empleados con una posición o cargo específico
24. `get_by_salary_range(min_salary: float, max_salary: float, **kwargs) -> List[Employee]` - Obtiene empleados cuyo salario se encuentra en un rango determinado
25. `advanced_search(filters: Dict[str, Any], **kwargs) -> List[Employee]` - Realiza una búsqueda avanzada con múltiples filtros combinados
26. `get_by_full_name(full_name: str) -> Optional[Employee]` - Obtiene un empleado por su nombre completo
27. `get_by_employee_code(employee_code: str) -> Optional[Employee]` - Obtiene un empleado por su código único
28. `get_active_employees() -> List[Employee]` - Obtiene todos los empleados con estado "activo"
29. `get_with_teams(employee_id: int) -> Optional[Employee]` - Obtiene un empleado y carga sus relaciones con equipos
30. `get_with_projects(employee_id: int) -> Optional[Employee]` - Obtiene un empleado y carga sus relaciones con proyectos
31. `full_name_exists(full_name: str, exclude_id: Optional[int]) -> bool` - Verifica si ya existe un empleado con el mismo nombre completo
32. `employee_code_exists(employee_code: str, exclude_id: Optional[int]) -> bool` - Verifica si ya existe un empleado con el mismo código
33. `email_exists(email: str, exclude_id: Optional[int]) -> bool` - Verifica si ya existe un empleado con el mismo correo electrónico
34. `count() -> int` - Devuelve el número total de empleados registrados

### 4. Operaciones de Relaciones (14 métodos)

35. `get_employee_teams(employee_id: int) -> List[Dict[str, Any]]` - Obtiene los equipos a los que pertenece un empleado
36. `get_employee_projects(employee_id: int) -> List[Dict[str, Any]]` - Obtiene los proyectos en los que un empleado está asignado
37. `get_employee_vacations(employee_id: int) -> List[Dict[str, Any]]` - Obtiene el historial de vacaciones de un empleado
38. `get_team_memberships(employee_id: int) -> List[Dict[str, Any]]` - Obtiene las membresías de equipo de un empleado
39. `get_project_assignments(employee_id: int) -> List[Dict[str, Any]]` - Obtiene las asignaciones a proyectos de un empleado
40. `check_team_membership(employee_id: int, team_id: int) -> bool` - Verifica si un empleado es miembro de un equipo específico
41. `check_project_assignment(employee_id: int, project_id: int) -> bool` - Verifica si un empleado está asignado a un proyecto específico
42. `get_employees_by_team(team_id: int) -> List[Employee]` - Obtiene todos los empleados de un equipo
43. `get_employees_by_project(project_id: int) -> List[Employee]` - Obtiene todos los empleados de un proyecto
44. `validate_employee_exists(employee_id: int) -> Employee` - Valida que un empleado existe y lo devuelve; si no, lanza una excepción
45. `get_employee_with_all_relations(employee_id: int) -> Optional[Employee]` - Obtiene un empleado con todas sus relaciones (equipos, proyectos, etc.) cargadas
46. `count_employee_relationships(employee_id: int) -> Dict[str, int]` - Cuenta el número de relaciones (equipos, proyectos) de un empleado
47. `has_dependencies(employee_id: int) -> bool` - Verifica si un empleado tiene dependencias que impidan su eliminación

### 5. Operaciones de Estadísticas (11 métodos)

48. `get_employee_count_by_status() -> Dict[str, int]` - Devuelve el número de empleados por cada estado
49. `get_employee_count_by_department() -> Dict[str, int]` - Devuelve el número de empleados por cada departamento
50. `get_employee_count_by_position() -> Dict[str, int]` - Devuelve el número de empleados por cada posición
51. `get_salary_statistics() -> Dict[str, float]` - Calcula estadísticas sobre los salarios (mínimo, máximo, promedio)
52. `get_hire_date_distribution(period: str) -> Dict[str, int]` - Devuelve la distribución de contrataciones por período (mes, año)
53. `get_team_participation_stats() -> Dict[str, Any]` - Genera estadísticas sobre la participación de empleados en equipos
54. `get_project_participation_stats() -> Dict[str, Any]` - Genera estadísticas sobre la participación de empleados en proyectos
55. `get_vacation_statistics(year: Optional[int]) -> Dict[str, Any]` - Calcula estadísticas sobre las vacaciones solicitadas
56. `get_skills_distribution(limit: int) -> Dict[str, int]` - Devuelve la distribución de las habilidades más comunes entre los empleados
57. `get_employee_workload_stats(employee_id, start_date, end_date) -> Dict[str, Any]` - Calcula estadísticas de carga de trabajo para un empleado en un período
58. `get_comprehensive_summary() -> Dict[str, Any]` - Genera un resumen completo que combina múltiples estadísticas clave

### 6. Operaciones de Validación (5 métodos)

59. `validate_create_data(data: Dict[str, Any]) -> None` - Valida los datos de entrada antes de crear un empleado
60. `validate_update_data(data: Dict[str, Any]) -> None` - Valida los datos de entrada antes de actualizar un empleado
61. `validate_skills_json(skills_json: Optional[str]) -> Optional[List[str]]` - Valida que el campo de habilidades (JSON) sea correcto y lo convierte a una lista
62. `validate_search_term(search_term: str) -> str` - Valida y sanea un término de búsqueda
63. `validate_employee_id(employee_id: int) -> None` - Valida que el ID de un empleado tenga un formato válido

---

## Resumen de Funcionalidades

### Total de Métodos Públicos: 63

**Distribución por Categorías:**
- Operaciones CRUD: 4 métodos (6%)
- Operaciones de Fechas: 8 métodos (13%)
- Operaciones de Consulta: 22 métodos (35%)
- Operaciones de Relaciones: 14 métodos (22%)
- Operaciones de Estadísticas: 11 métodos (17%)
- Operaciones de Validación: 5 métodos (8%)

### Características Principales

- **Gestión Completa de Empleados**: CRUD completo con validaciones robustas
- **Consultas Avanzadas**: Búsquedas por múltiples criterios de filtrado (nombre, email, departamento, posición, habilidades, salario)
- **Gestión de Fechas**: Operaciones especializadas para fechas de contratación, antigüedad y períodos específicos
- **Análisis de Relaciones**: Gestión integral de asignaciones con equipos, proyectos y vacaciones
- **Análisis Estadístico**: Métricas de distribución, participación y carga de trabajo
- **Validación Robusta**: Verificación de integridad de datos y reglas de negocio

### Integración con Otros Módulos

- **Team**: Gestión de membresías y asignaciones de empleados en equipos
- **Project**: Asignación y seguimiento de empleados en proyectos
- **Vacation**: Gestión del historial de vacaciones de empleados
- **Schedule**: Integración con horarios para seguimiento de tiempo y disponibilidad

### Casos de Uso Principales

- **Gestión de Empleados**: Creación, actualización y seguimiento del ciclo de vida completo
- **Búsqueda y Filtrado**: Localización de empleados por múltiples criterios
- **Planificación de Recursos**: Asignación y gestión de empleados en equipos y proyectos
- **Análisis de Antigüedad**: Seguimiento de fechas de contratación y cálculo de antigüedad
- **Seguimiento de Relaciones**: Análisis de participación en equipos y proyectos
- **Reportes Gerenciales**: Estadísticas y métricas para toma de decisiones
- **Validación de Datos**: Prevención de duplicados y verificación de integridad