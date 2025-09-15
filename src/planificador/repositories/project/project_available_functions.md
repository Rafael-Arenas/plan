# Funciones Disponibles en `ProjectRepositoryFacade`

Este documento detalla todos los métodos públicos disponibles en la clase `ProjectRepositoryFacade`, que sirve como punto de entrada unificado para todas las operaciones relacionadas con los proyectos en la base de datos.

## Arquitectura

La fachada delega las operaciones a módulos especializados, cada uno responsable de un área funcional específica:

- **`_crud_operations`**: Operaciones de Creación, Lectura, Actualización y Eliminación (CRUD).
- **`_query_operations`**: Consultas y búsquedas avanzadas con filtros.
- **`_relationship_operations`**: Gestión de relaciones con otras entidades (clientes, asignaciones).
- **`_statistics_operations`**: Cálculos y agregaciones estadísticas.
- **`_validation_operations`**: Validaciones de datos de entrada.

---

## Métodos por Módulo

### 1. Operaciones CRUD (`_crud_operations`)

- `create_project(project_data: Dict[str, Any]) -> Project`
  - Crea un nuevo proyecto después de validar los datos de entrada.

- `update_project(project_id: int, updated_data: Dict[str, Any]) -> Optional[Project]`
  - Actualiza un proyecto existente después de validar los datos.

- `delete_project(project_id: int) -> bool`
  - Elimina un proyecto por su ID.

- `archive_project(project_id: int) -> Optional[Project]`
  - Archiva un proyecto después de validar que puede ser archivado.

### 2. Operaciones de Consulta (`_query_operations`)

#### Métodos de Consulta Base
- `_base_query(include_archived: bool = False)`
  - Crea una consulta base para proyectos, excluyendo los archivados por defecto.

#### Métodos de Carga de Relaciones
- `with_client(query)`
  - Añade la carga de la relación con el cliente.

- `with_assignments(query)`
  - Añade la carga de la relación con las asignaciones.

#### Métodos de Filtrado
- `filter_by_reference(query, reference: str)`
  - Filtra por número de referencia.

- `filter_by_name(query, name: str)`
  - Filtra por nombre (búsqueda parcial).

- `filter_by_dates(start_date: date, end_date: date)`
  - Filtra por rango de fechas.

#### Métodos de Búsqueda y Consulta
- `search_projects(search_term: str, limit: Optional[int] = None) -> List[Project]`
  - Busca proyectos por término de búsqueda en nombre, referencia y descripción.

- `get_overdue_projects(limit: Optional[int] = None) -> List[Project]`
  - Obtiene proyectos que están vencidos.

- `get_active_projects(limit: Optional[int] = None) -> List[Project]`
  - Obtiene proyectos activos.

- `filter_by_date_range(start_date: date, end_date: date, limit: Optional[int] = None) -> List[Project]`
  - Filtra proyectos por rango de fechas.

- `get_by_id(project_id: int) -> Optional[Project]`
  - Obtiene un proyecto por su ID.

- `format_project_dates(project: Project) -> Dict[str, Optional[str]]`
  - Formatea las fechas de un proyecto.

- `get_by_reference(reference: str) -> Optional[Project]`
  - Obtiene un proyecto por su referencia.

- `get_by_trigram(trigram: str) -> Optional[Project]`
  - Obtiene un proyecto por su trigrama.

- `search_by_name(search_term: str) -> List[Project]`
  - Busca proyectos por nombre.

- `get_by_client(client_id: int) -> List[Project]`
  - Obtiene proyectos por cliente.

- `get_by_status(status: ProjectStatus) -> List[Project]`
  - Obtiene proyectos por estado.

- `get_by_priority(priority: ProjectPriority) -> List[Project]`
  - Obtiene proyectos por prioridad.

- `get_by_date_range(start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Project]`
  - Obtiene proyectos en un rango de fechas.

#### Métodos de Consulta por Períodos
- `get_projects_starting_current_week(**kwargs) -> List[Project]`
  - Obtiene proyectos que inician en la semana actual.

- `get_projects_ending_current_week(**kwargs) -> List[Project]`
  - Obtiene proyectos que terminan en la semana actual.

- `get_projects_starting_current_month(**kwargs) -> List[Project]`
  - Obtiene proyectos que inician en el mes actual.

- `get_projects_starting_business_days_only(start_date: Optional[date] = None, end_date: Optional[date] = None, **kwargs) -> List[Project]`
  - Obtiene proyectos que inician en días hábiles.

#### Métodos de Consulta con Relaciones
- `get_with_client(project_id: int) -> Optional[Project]`
  - Obtiene un proyecto con su cliente.

- `get_with_assignments(project_id: int) -> Optional[Project]`
  - Obtiene un proyecto con sus asignaciones.

- `get_with_full_details(project_id: int) -> Optional[Project]`
  - Obtiene un proyecto con todos sus detalles.

### 3. Operaciones de Estadísticas (`_statistics_operations`)

- `get_status_summary() -> Dict[str, int]`
  - Calcula un resumen del número de proyectos por estado.

- `get_overdue_projects_summary() -> List[Dict[str, Any]]`
  - Obtiene un resumen de proyectos vencidos.

- `get_project_performance_stats() -> Dict[str, Any]`
  - Obtiene estadísticas de rendimiento de proyectos.

- `get_projects_by_status_summary(status: str) -> Dict[str, Any]`
  - Obtiene un resumen de proyectos por estado específico.

- `get_project_workload_stats() -> Dict[str, Any]`
  - Obtiene estadísticas de carga de trabajo de proyectos.

- `get_project_duration_stats() -> Dict[str, Any]`
  - Obtiene estadísticas de duración de proyectos.

- `get_monthly_project_stats(year: int, month: int) -> Dict[str, Any]`
  - Obtiene estadísticas de proyectos por mes.

- `get_client_project_stats(client_id: int) -> Dict[str, Any]`
  - Obtiene estadísticas de proyectos por cliente.

- `get_overdue_projects_stats() -> Dict[str, Any]`
  - Obtiene estadísticas detalladas de proyectos vencidos.

### 4. Operaciones de Validación (`_validation_operations`)

- `validate_project_creation(data: Dict[str, Any]) -> None`
  - Valida los datos para la creación de un nuevo proyecto.

- `validate_project_update(project_id: int, data: Dict[str, Any]) -> None`
  - Valida los datos para la actualización de un proyecto.

- `reference_exists(reference: str, exclude_id: Optional[int] = None) -> bool`
  - Verifica si una referencia de proyecto existe.

- `trigram_exists(trigram: str, exclude_id: Optional[int] = None) -> bool`
  - Verifica si un trigrama de proyecto existe.

---

## Resumen de Funcionalidades

El `ProjectRepositoryFacade` proporciona una interfaz unificada y completa para:

- **Gestión CRUD**: Creación, actualización, eliminación y archivado de proyectos
- **Consultas avanzadas**: Búsquedas por múltiples criterios y filtros
- **Análisis estadístico**: Métricas y resúmenes de rendimiento
- **Validación robusta**: Verificación de integridad de datos
- **Optimización de consultas**: Carga eficiente de relaciones

Todos los métodos están completamente documentados y siguen las mejores prácticas de desarrollo asíncrono con SQLAlchemy.