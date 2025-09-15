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

- `_base_query(include_archived: bool = False)`
  - Crea una consulta base para proyectos, excluyendo los archivados por defecto.

- `with_client(query)`
  - Añade la carga de la relación con el cliente.

- `with_assignments(query)`
  - Añade la carga de la relación con las asignaciones.

- `with_full_details(query)`
  - Añade la carga de todas las relaciones principales.

- `filter_by_reference(query, reference: str)`
  - Filtra por número de referencia.

- `filter_by_trigram(query, trigram: str)`
  - Filtra por trigrama del proyecto.

- `filter_by_name(query, name: str)`
  - Filtra por nombre (búsqueda parcial).

- `filter_by_client(query, client_id: int)`
  - Filtra por ID de cliente.

- `filter_by_status(query, status: str)`
  - Filtra por estado del proyecto.

- `filter_by_priority(query, priority: str)`
  - Filtra por prioridad del proyecto.

- `filter_by_date_range(query, start_date, end_date)`
  - Filtra por rango de fechas.

### 3. Operaciones de Relaciones (`_relationship_operations`)

- `with_client_relationship(query)`
  - Añade la carga de la relación con el cliente usando relationship operations.

- `with_assignments_relationship(query)`
  - Añade la carga de la relación con las asignaciones usando relationship operations.

- `with_full_details_relationship(query)`
  - Añade la carga de todas las relaciones principales usando relationship operations.

### 4. Operaciones de Estadísticas (`_statistics_operations`)

- `get_status_summary() -> Dict[str, int]`
  - Calcula un resumen del número de proyectos por estado.

- `get_overdue_projects_summary() -> List[Dict[str, Any]]`
  - Obtiene un resumen de proyectos vencidos.

### 5. Operaciones de Validación (`_validation_operations`)

- `validate_project_creation(data: Dict[str, Any]) -> None`
  - Valida los datos para la creación de un nuevo proyecto.

- `validate_project_update(project_id: int, data: Dict[str, Any]) -> None`
  - Valida los datos para la actualización de un proyecto.