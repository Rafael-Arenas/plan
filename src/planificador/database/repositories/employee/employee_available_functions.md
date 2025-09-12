# Funciones Disponibles en `EmployeeRepositoryFacade`

Este documento detalla todos los métodos públicos disponibles en la clase `EmployeeRepositoryFacade`, que sirve como punto de entrada unificado para todas las operaciones relacionadas con los empleados en la base de datos.

## Arquitectura

La fachada delega las operaciones a módulos especializados, cada uno responsable de un área funcional específica:

- **`_crud`**: Operaciones de Creación, Lectura, Actualización y Eliminación (CRUD).
- **`_dates`**: Operaciones complejas relacionadas con fechas (contratación, antigüedad).
- **`_queries`**: Consultas y búsquedas avanzadas.
- **`_relationships`**: Gestión de relaciones con otras entidades (equipos, proyectos).
- **`_statistics`**: Cálculos y agregaciones estadísticas.
- **`_validation`**: Validaciones de datos de entrada.

---

## Métodos por Módulo

### 1. Operaciones CRUD (`_crud`)

- `create_employee(employee_data: Dict[str, Any]) -> Employee`
  - Crea un nuevo empleado en la base de datos.

- `update_employee(employee_id: int, update_data: Dict[str, Any]) -> Optional[Employee]`
  - Actualiza los datos de un empleado existente.

- `delete_employee(employee_id: int) -> bool`
  - Elimina un empleado de la base de datos.

### 2. Operaciones de Fechas (`_dates`)

- `get_employees_hired_current_week(**kwargs) -> List[Employee]`
  - Obtiene los empleados contratados en la semana actual.

- `get_employees_hired_current_month(**kwargs) -> List[Employee]`
  - Obtiene los empleados contratados en el mes actual.

- `get_employees_hired_business_days_only(start_date, end_date, **kwargs) -> List[Employee]`
  - Obtiene empleados contratados únicamente en días laborables dentro de un rango.

- `get_by_hire_date_range(start_date: date, end_date: date, **kwargs) -> List[Employee]`
  - Obtiene empleados por rango de fecha de contratación.

- `get_employee_tenure_stats(employee_id: int) -> Dict[str, Any]`
  - Calcula estadísticas de antigüedad para un empleado específico.

- `get_employees_by_tenure_range(min_years, max_years, status) -> List[Dict[str, Any]]`
  - Obtiene empleados según un rango de años de antigüedad.

- `create_employee_with_date_validation(employee_data, validate_hire_date_business_day) -> Employee`
  - Crea un empleado aplicando validaciones avanzadas sobre la fecha de contratación.

- `format_employee_hire_date(employee: Employee, format_type: str) -> Optional[str]`
  - Formatea la fecha de contratación de un empleado a un formato legible.

### 3. Operaciones de Consulta (`_queries`)

- `get_by_id(employee_id: int) -> Optional[Employee]`
  - Obtiene un empleado por su ID.

- `get_all(skip: int = 0, limit: int = 100) -> List[Employee]`
  - Obtiene una lista paginada de todos los empleados.

- `employee_exists(employee_id: int) -> bool`
  - Verifica si un empleado existe por su ID.

- `count() -> int`
  - Devuelve el número total de empleados.

- `search_by_name(name: str, **kwargs) -> List[Employee]`
  - Busca empleados por su nombre.

- `get_by_email(email: str) -> Optional[Employee]`
  - Obtiene un empleado por su dirección de correo electrónico.

- `get_by_status(status: EmployeeStatus, **kwargs) -> List[Employee]`
  - Obtiene empleados filtrando por su estado (activo, inactivo, etc.).

- `get_available_employees(**kwargs) -> List[Employee]`
  - Obtiene empleados con estado "disponible".

- `search_by_skills(skills: Union[str, List[str]], **kwargs) -> List[Employee]`
  - Busca empleados que posean ciertas habilidades.

- `get_by_department(department: str, **kwargs) -> List[Employee]`
  - Obtiene empleados de un departamento específico.

- `get_by_position(position: str, **kwargs) -> List[Employee]`
  - Obtiene empleados con una posición o cargo específico.

- `get_by_salary_range(min_salary: float, max_salary: float, **kwargs) -> List[Employee]`
  - Obtiene empleados cuyo salario se encuentra en un rango determinado.

- `advanced_search(filters: Dict[str, Any], **kwargs) -> List[Employee]`
  - Realiza una búsqueda avanzada con múltiples filtros combinados.

- `get_by_full_name(full_name: str) -> Optional[Employee]`
  - Obtiene un empleado por su nombre completo.

- `get_by_employee_code(employee_code: str) -> Optional[Employee]`
  - Obtiene un empleado por su código único.

- `get_active_employees() -> List[Employee]`
  - Obtiene todos los empleados con estado "activo".

- `get_with_teams(employee_id: int) -> Optional[Employee]`
  - Obtiene un empleado y carga sus relaciones con equipos.

- `get_with_projects(employee_id: int) -> Optional[Employee]`
  - Obtiene un empleado y carga sus relaciones con proyectos.

- `full_name_exists(full_name: str, exclude_id: Optional[int]) -> bool`
  - Verifica si ya existe un empleado con el mismo nombre completo.

- `employee_code_exists(employee_code: str, exclude_id: Optional[int]) -> bool`
  - Verifica si ya existe un empleado con el mismo código.

- `email_exists(email: str, exclude_id: Optional[int]) -> bool`
  - Verifica si ya existe un empleado con el mismo correo electrónico.

### 4. Operaciones de Relaciones (`_relationships`)

- `get_employee_teams(employee_id: int) -> List[Dict[str, Any]]`
  - Obtiene los equipos a los que pertenece un empleado.

- `get_employee_projects(employee_id: int) -> List[Dict[str, Any]]`
  - Obtiene los proyectos en los que un empleado está asignado.

- `get_employee_vacations(employee_id: int) -> List[Dict[str, Any]]`
  - Obtiene el historial de vacaciones de un empleado.

- `get_team_memberships(employee_id: int) -> List[Dict[str, Any]]`
  - Obtiene las membresías de equipo de un empleado.

- `get_project_assignments(employee_id: int) -> List[Dict[str, Any]]`
  - Obtiene las asignaciones a proyectos de un empleado.

- `check_team_membership(employee_id: int, team_id: int) -> bool`
  - Verifica si un empleado es miembro de un equipo específico.

- `check_project_assignment(employee_id: int, project_id: int) -> bool`
  - Verifica si un empleado está asignado a un proyecto específico.

- `get_employees_by_team(team_id: int) -> List[Employee]`
  - Obtiene todos los empleados de un equipo.

- `get_employees_by_project(project_id: int) -> List[Employee]`
  - Obtiene todos los empleados de un proyecto.

- `validate_employee_exists(employee_id: int) -> Employee`
  - Valida que un empleado existe y lo devuelve; si no, lanza una excepción.

- `get_employee_with_all_relations(employee_id: int) -> Optional[Employee]`
  - Obtiene un empleado con todas sus relaciones (equipos, proyectos, etc.) cargadas.

- `count_employee_relationships(employee_id: int) -> Dict[str, int]`
  - Cuenta el número de relaciones (equipos, proyectos) de un empleado.

- `has_dependencies(employee_id: int) -> bool`
  - Verifica si un empleado tiene dependencias que impidan su eliminación.

### 5. Operaciones de Estadísticas (`_statistics`)

- `get_employee_count_by_status() -> Dict[str, int]`
  - Devuelve el número de empleados por cada estado.

- `get_employee_count_by_department() -> Dict[str, int]`
  - Devuelve el número de empleados por cada departamento.

- `get_employee_count_by_position() -> Dict[str, int]`
  - Devuelve el número de empleados por cada posición.

- `get_salary_statistics() -> Dict[str, float]`
  - Calcula estadísticas sobre los salarios (mínimo, máximo, promedio).

- `get_hire_date_distribution(period: str) -> Dict[str, int]`
  - Devuelve la distribución de contrataciones por período (mes, año).

- `get_team_participation_stats() -> Dict[str, Any]`
  - Genera estadísticas sobre la participación de empleados en equipos.

- `get_project_participation_stats() -> Dict[str, Any]`
  - Genera estadísticas sobre la participación de empleados en proyectos.

- `get_vacation_statistics(year: Optional[int]) -> Dict[str, Any]`
  - Calcula estadísticas sobre las vacaciones solicitadas.

- `get_skills_distribution(limit: int) -> Dict[str, int]`
  - Devuelve la distribución de las habilidades más comunes entre los empleados.

- `get_employee_workload_stats(employee_id, start_date, end_date) -> Dict[str, Any]`
  - Calcula estadísticas de carga de trabajo para un empleado en un período.

- `get_comprehensive_summary() -> Dict[str, Any]`
  - Genera un resumen completo que combina múltiples estadísticas clave.

### 6. Operaciones de Validación (`_validation`)

- `validate_create_data(data: Dict[str, Any]) -> None`
  - Valida los datos de entrada antes de crear un empleado.

- `validate_update_data(data: Dict[str, Any]) -> None`
  - Valida los datos de entrada antes de actualizar un empleado.

- `validate_skills_json(skills_json: Optional[str]) -> Optional[List[str]]`
  - Valida que el campo de habilidades (JSON) sea correcto y lo convierte a una lista.

- `validate_search_term(search_term: str) -> str`
  - Valida y sanea un término de búsqueda.

- `validate_employee_id(employee_id: int) -> None`
  - Valida que el ID de un empleado tenga un formato válido.