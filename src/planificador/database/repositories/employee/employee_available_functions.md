# Funciones Disponibles en Employee Repository

**Fecha de actualización:** 19 de agosto de 2025

## Módulos y Funciones

### EmployeeRepository (employee_repository.py)

#### Operaciones CRUD Básicas (3 funciones)
1. `create_employee(employee_data: Dict[str, Any]) -> Employee` - Crea un nuevo empleado con validaciones completas
2. `update_employee(employee_id: int, update_data: Dict[str, Any]) -> Optional[Employee]` - Actualiza un empleado existente con validaciones
3. `get_by_id(employee_id: int) -> Optional[Employee]` - Obtiene empleado por ID (heredado de BaseRepository)

#### Consultas por Identificadores Únicos (3 funciones)
4. `get_by_full_name(full_name: str) -> Optional[Employee]` - Obtiene un empleado por su nombre completo
5. `get_by_employee_code(employee_code: str) -> Optional[Employee]` - Obtiene un empleado por su código único
6. `get_by_email(email: str) -> Optional[Employee]` - Obtiene un empleado por su email

#### Consultas por Atributos (6 funciones)
7. `search_by_name(search_term: str) -> List[Employee]` - Busca empleados por patrón de nombre
8. `get_by_status(status: EmployeeStatus) -> List[Employee]` - Obtiene empleados por estado
9. `get_active_employees() -> List[Employee]` - Obtiene todos los empleados activos
10. `get_available_employees(target_date: Optional[date] = None) -> List[Employee]` - Obtiene empleados disponibles en una fecha
11. `get_by_department(department: str) -> List[Employee]` - Obtiene empleados por departamento
12. `get_by_position(position: str) -> List[Employee]` - Obtiene empleados por posición

#### Consultas por Habilidades (1 función)
13. `get_by_skills(skills: List[str]) -> List[Employee]` - Obtiene empleados que tienen habilidades específicas

#### Consultas con Relaciones (6 funciones)
14. `get_with_teams(employee_id: int) -> Optional[Employee]` - Obtiene un empleado con información de equipos
15. `get_with_projects(employee_id: int) -> Optional[Employee]` - Obtiene un empleado con sus proyectos asignados
16. `get_employee_teams(employee_id: int) -> List[Any]` - Obtiene los equipos de un empleado
17. `get_employee_projects(employee_id: int) -> List[Any]` - Obtiene los proyectos de un empleado
18. `get_employee_vacations(employee_id: int) -> List[Any]` - Obtiene las vacaciones de un empleado
19. `get_employee_time_records(employee_id: int) -> List[Any]` - Obtiene los registros de tiempo de un empleado

#### Validaciones de Dependencias (5 funciones)
20. `has_team_memberships(employee_id: int) -> bool` - Verifica si el empleado tiene membresías en equipos
21. `has_project_assignments(employee_id: int) -> bool` - Verifica si el empleado tiene asignaciones de proyecto
22. `has_vacations(employee_id: int) -> bool` - Verifica si el empleado tiene vacaciones registradas
23. `has_time_records(employee_id: int) -> bool` - Verifica si el empleado tiene registros de tiempo
24. `count_dependencies(employee_id: int) -> Dict[str, int]` - Cuenta todas las dependencias del empleado

#### Validaciones de Unicidad (3 funciones)
25. `full_name_exists(full_name: str, exclude_id: Optional[int] = None) -> bool` - Verifica si existe un nombre completo
26. `employee_code_exists(employee_code: str, exclude_id: Optional[int] = None) -> bool` - Verifica si existe un código de empleado
27. `email_exists(email: str, exclude_id: Optional[int] = None) -> bool` - Verifica si existe un email

#### Estadísticas Básicas (10 funciones)
28. `get_employee_workload_stats(employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]` - Obtiene estadísticas de carga de trabajo
29. `get_count_by_status() -> Dict[str, int]` - Obtiene conteo de empleados por estado
30. `get_count_by_department() -> Dict[str, int]` - Obtiene conteo de empleados por departamento
31. `get_count_by_position() -> Dict[str, int]` - Obtiene conteo de empleados por posición
32. `get_salary_statistics() -> Dict[str, Any]` - Obtiene estadísticas salariales
33. `get_hire_date_distribution() -> Dict[str, Any]` - Obtiene distribución de fechas de contratación
34. `get_team_participation_stats() -> Dict[str, Any]` - Obtiene estadísticas de participación en equipos
35. `get_project_participation_stats() -> Dict[str, Any]` - Obtiene estadísticas de participación en proyectos
36. `get_vacation_statistics() -> Dict[str, Any]` - Obtiene estadísticas de vacaciones
37. `get_skills_distribution() -> Dict[str, Any]` - Obtiene distribución de habilidades

#### Estadísticas Avanzadas (1 función)
38. `get_comprehensive_summary() -> Dict[str, Any]` - Obtiene resumen estadístico completo

#### Consultas Temporales (3 funciones)
39. `get_employees_hired_current_week(**kwargs) -> List[Employee]` - Obtiene empleados contratados en la semana actual
40. `get_employees_hired_current_month(**kwargs) -> List[Employee]` - Obtiene empleados contratados en el mes actual
41. `get_employees_hired_business_days_only(start_date: Union[date, str, None] = None, end_date: Union[date, str, None] = None, **kwargs) -> List[Employee]` - Obtiene empleados contratados en días laborables

#### Análisis de Antigüedad (2 funciones)
42. `get_employee_tenure_stats(employee_id: int) -> Dict[str, Any]` - Obtiene estadísticas de antigüedad de un empleado
43. `get_employees_by_tenure_range(min_years: float = 0.0, max_years: Optional[float] = None, status: Optional[EmployeeStatus] = None) -> List[Dict[str, Any]]` - Obtiene empleados por rango de antigüedad

#### Validaciones Avanzadas (1 función)
44. `create_employee_with_pendulum_validation(employee_data: Dict[str, Any], validate_hire_date_business_day: bool = False) -> Employee` - Crea empleado con validaciones de fecha usando Pendulum

#### Formateo de Fechas (1 función)
45. `format_employee_hire_date(employee: Employee, format_type: str = 'default') -> Optional[str]` - Formatea la fecha de contratación para presentación

---

### EmployeeQueryBuilder (employee_query_builder.py)

#### Consultas Base por Identificadores (3 funciones)
46. `get_by_full_name(full_name: str) -> Optional[Employee]` - Busca empleado por nombre completo
47. `get_by_employee_code(employee_code: str) -> Optional[Employee]` - Busca empleado por código
48. `get_by_email(email: str) -> Optional[Employee]` - Busca empleado por email

#### Consultas por Atributos (6 funciones)
49. `search_by_name(search_term: str) -> List[Employee]` - Busca empleados por patrón de nombre
50. `get_by_status(status: EmployeeStatus) -> List[Employee]` - Obtiene empleados por estado
51. `get_active_employees() -> List[Employee]` - Obtiene empleados activos
52. `get_available_employees(target_date: Optional[date] = None) -> List[Employee]` - Obtiene empleados disponibles
53. `get_by_department(department: str) -> List[Employee]` - Obtiene empleados por departamento
54. `get_by_position(position: str) -> List[Employee]` - Obtiene empleados por posición

#### Consultas por Habilidades (1 función)
55. `get_by_skills(skills: List[str]) -> List[Employee]` - Obtiene empleados por habilidades

#### Consultas con Relaciones (2 funciones)
56. `get_with_teams(employee_id: int) -> Optional[Employee]` - Obtiene empleado con equipos
57. `get_with_projects(employee_id: int) -> Optional[Employee]` - Obtiene empleado con proyectos

#### Validaciones de Existencia (3 funciones)
58. `full_name_exists(full_name: str, exclude_id: Optional[int] = None) -> bool` - Verifica existencia de nombre completo
59. `employee_code_exists(employee_code: str, exclude_id: Optional[int] = None) -> bool` - Verifica existencia de código
60. `email_exists(email: str, exclude_id: Optional[int] = None) -> bool` - Verifica existencia de email

---

### EmployeeStatistics (employee_statistics.py)

#### Estadísticas por Categorías (3 funciones)
61. `get_employee_count_by_status() -> Dict[str, int]` - Obtiene conteos por estado
62. `get_employee_count_by_department() -> Dict[str, int]` - Obtiene conteos por departamento
63. `get_employee_count_by_position() -> Dict[str, int]` - Obtiene conteos por posición

#### Estadísticas Financieras (1 función)
64. `get_salary_statistics() -> Dict[str, float]` - Obtiene estadísticas salariales (promedio, mediana, min, max)

#### Estadísticas Temporales (1 función)
65. `get_hire_date_distribution(years: int = 5) -> Dict[str, int]` - Obtiene distribución de contrataciones por año

#### Estadísticas de Participación (2 funciones)
66. `get_team_participation_stats() -> Dict[str, Any]` - Obtiene estadísticas de participación en equipos
67. `get_project_participation_stats() -> Dict[str, Any]` - Obtiene estadísticas de participación en proyectos

#### Estadísticas de Vacaciones (1 función)
68. `get_vacation_statistics(year: Optional[int] = None) -> Dict[str, Any]` - Obtiene estadísticas de vacaciones

#### Estadísticas de Habilidades (1 función)
69. `get_skills_distribution(limit: int = 20) -> Dict[str, int]` - Obtiene distribución de habilidades

#### Estadísticas Específicas de Empleado (1 función)
70. `get_employee_workload_stats(employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]` - Obtiene estadísticas de carga de trabajo de un empleado

#### Resumen Completo (1 función)
71. `get_comprehensive_summary() -> Dict[str, Any]` - Obtiene resumen estadístico completo de todos los empleados

---

### EmployeeRelationshipManager (employee_relationship_manager.py)

#### Consultas de Relaciones Básicas (3 funciones)
72. `get_employee_teams(employee_id: int) -> List[Team]` - Obtiene equipos de un empleado
73. `get_employee_projects(employee_id: int) -> List[Project]` - Obtiene proyectos de un empleado
74. `get_employee_vacations(employee_id: int) -> List[Vacation]` - Obtiene vacaciones de un empleado

#### Consultas de Membresías y Asignaciones (2 funciones)
75. `get_team_memberships(employee_id: int) -> List[TeamMembership]` - Obtiene membresías en equipos
76. `get_project_assignments(employee_id: int) -> List[ProjectAssignment]` - Obtiene asignaciones de proyecto

#### Consultas con Carga de Relaciones (2 funciones)
77. `get_with_teams(employee_id: int) -> Optional[Employee]` - Obtiene empleado con equipos cargados
78. `get_with_projects(employee_id: int) -> Optional[Employee]` - Obtiene empleado con proyectos cargados

#### Validaciones de Membresía (2 funciones)
79. `check_team_membership(employee_id: int, team_id: int) -> bool` - Verifica membresía en equipo específico
80. `check_project_assignment(employee_id: int, project_id: int) -> bool` - Verifica asignación a proyecto específico

#### Consultas Inversas (2 funciones)
81. `get_employees_by_team(team_id: int) -> List[Employee]` - Obtiene empleados de un equipo
82. `get_employees_by_project(project_id: int) -> List[Employee]` - Obtiene empleados de un proyecto

#### Validaciones y Utilidades (4 funciones)
83. `validate_employee_exists(employee_id: int) -> Employee` - Valida y obtiene empleado existente
84. `get_employee_with_all_relations(employee_id: int) -> Optional[Employee]` - Obtiene empleado con todas las relaciones
85. `count_employee_relationships(employee_id: int) -> dict` - Cuenta todas las relaciones del empleado
86. `has_dependencies(employee_id: int) -> bool` - Verifica si el empleado tiene dependencias

---

### EmployeeValidator (employee_validator.py)

#### Validaciones Principales (2 funciones)
87. `validate_create_data(data: Dict[str, Any]) -> None` - Valida datos para crear empleado
88. `validate_update_data(data: Dict[str, Any]) -> None` - Valida datos para actualizar empleado

#### Validaciones Internas - Campos Requeridos (1 función)
89. `_validate_required_fields_for_create(data: Dict[str, Any]) -> None` - **[PRIVADA]** Valida campos obligatorios para creación

#### Validaciones Internas - Formato de Datos (9 funciones)
90. `_validate_employee_code(employee_code: str) -> None` - **[PRIVADA]** Valida formato del código de empleado
91. `_validate_full_name(full_name: str) -> None` - **[PRIVADA]** Valida formato del nombre completo
92. `_validate_first_name(first_name: str) -> None` - **[PRIVADA]** Valida formato del primer nombre
93. `_validate_last_name(last_name: str) -> None` - **[PRIVADA]** Valida formato del apellido
94. `_validate_email(email: str) -> None` - **[PRIVADA]** Valida formato del email
95. `_validate_phone(phone: Optional[str]) -> None` - **[PRIVADA]** Valida formato del teléfono
96. `_validate_department(department: str) -> None` - **[PRIVADA]** Valida formato del departamento
97. `_validate_position(position: str) -> None` - **[PRIVADA]** Valida formato de la posición
98. `_validate_hire_date(hire_date) -> None` - **[PRIVADA]** Valida fecha de contratación

#### Validaciones Internas - Reglas de Negocio (3 funciones)
99. `_validate_salary(salary: Optional[float]) -> None` - **[PRIVADA]** Valida salario
100. `_validate_status(status: EmployeeStatus) -> None` - **[PRIVADA]** Valida estado del empleado
101. `_validate_skills(skills: Optional[List[str]]) -> None` - **[PRIVADA]** Valida lista de habilidades

#### Validaciones Especializadas (3 funciones)
102. `validate_skills_json(skills_json: Optional[str]) -> Optional[List[str]]` - Valida y convierte JSON de habilidades
103. `validate_search_term(search_term: str) -> str` - Valida término de búsqueda
104. `validate_employee_id(employee_id: int) -> None` - Valida ID de empleado

---

**Total de funciones disponibles:** 104

**Distribución por módulos:**
- EmployeeRepository: 45 funciones (3 CRUD + 3 identificadores + 6 atributos + 1 habilidades + 6 relaciones + 5 dependencias + 3 unicidad + 10 estadísticas básicas + 1 estadística avanzada + 3 temporales + 2 antigüedad + 1 validación avanzada + 1 formateo)
- EmployeeQueryBuilder: 15 funciones (3 identificadores + 6 atributos + 1 habilidades + 2 relaciones + 3 validaciones)
- EmployeeStatistics: 11 funciones (3 categorías + 1 financiera + 1 temporal + 2 participación + 1 vacaciones + 1 habilidades + 1 específica + 1 resumen)
- EmployeeRelationshipManager: 15 funciones (3 básicas + 2 membresías + 2 carga + 2 validaciones + 2 inversas + 4 utilidades)
- EmployeeValidator: 18 funciones (2 principales + 1 campos + 9 formato + 3 negocio + 3 especializadas)

**Categorías principales:**
- **CRUD básico**: 3 funciones (crear, leer, actualizar empleados)
- **Consultas especializadas**: 19 funciones (por identificadores, atributos, habilidades y relaciones)
- **Gestión de relaciones**: 15 funciones (equipos, proyectos, vacaciones y asignaciones)
- **Análisis y estadísticas**: 22 funciones (conteos, distribuciones, participación y resúmenes)
- **Validación de datos**: 18 funciones (creación, actualización, formato y reglas de negocio)
- **Construcción de consultas**: 15 funciones (builders SQL para diferentes tipos de búsqueda)
- **Validaciones de dependencias**: 12 funciones (verificación de relaciones y dependencias)

**Funcionalidades especiales:**
- **Gestión de identificadores únicos**: 9 funciones para nombres, códigos y emails
- **Análisis de disponibilidad**: 2 funciones para consultas de empleados disponibles
- **Validaciones de negocio**: 18 funciones para garantizar integridad y coherencia
- **Gestión de relaciones complejas**: 15 funciones para administración de vínculos entre entidades
- **Estadísticas avanzadas**: 11 funciones para análisis de rendimiento y métricas
- **Consultas optimizadas**: 15 funciones de query building para performance
- **Análisis temporal**: 4 funciones para consultas por fechas y antigüedad
- **Gestión de habilidades**: 3 funciones para manejo de skills y competencias

**Integración con otras entidades:**
- **Team**: 6 funciones para gestión de relaciones con equipos
- **Project**: 6 funciones para gestión de asignaciones de proyectos
- **Vacation**: 3 funciones para gestión de vacaciones
- **TeamMembership**: 3 funciones para gestión de membresías
- **ProjectAssignment**: 3 funciones para gestión de asignaciones
- **TimeEntry**: 2 funciones para registros de tiempo (pendiente implementación del modelo)

**Características de validación:**
- **Validaciones de formato**: 9 funciones para email, teléfono, códigos, etc.
- **Validaciones de unicidad**: 6 funciones para evitar duplicados
- **Validaciones de dependencias**: 5 funciones para verificar relaciones
- **Validaciones de negocio**: 4 funciones para reglas específicas del dominio

**Total de funciones documentadas**: 104