# Funciones Disponibles en `ClientRepositoryFacade`

Este documento detalla todos los métodos públicos disponibles en la clase `ClientRepositoryFacade`, que sirve como punto de entrada unificado para todas las operaciones relacionadas con los clientes en la base de datos.

## Arquitectura

La fachada delega las operaciones a módulos especializados, cada uno responsable de un área funcional específica:

- **`_crud_operations`**: Operaciones de Creación, Lectura, Actualización y Eliminación (CRUD).
- **`_query_operations`**: Consultas y búsquedas básicas.
- **`_advanced_query_operations`**: Consultas y búsquedas avanzadas.
- **`_relationship_operations`**: Gestión de relaciones con otras entidades.
- **`_statistics_operations`**: Cálculos y agregaciones estadísticas.
- **`_validation_operations`**: Validaciones de datos de entrada.
- **`_date_operations`**: Operaciones relacionadas con fechas.
- **`_health_operations`**: Verificación de salud del repositorio.

---

## Métodos por Módulo

### 1. Operaciones CRUD (`_crud_operations`)
- `create_client(client_data: ClientCreate) -> Client` - Crea un nuevo cliente con validación completa.
- `update_client(client_id: int, client_data: ClientUpdate) -> Client | None` - Actualiza un cliente existente.
- `delete_client(client_id: int) -> bool` - Elimina un cliente por ID.

### 2. Operaciones de Consulta (`_query_operations`)
- `get_client_by_id(client_id: int) -> Client | None` - Obtiene un cliente por su ID único.
- `get_client_by_name(name: str) -> Client | None` - Obtiene un cliente por su nombre exacto.
- `get_client_by_code(code: str) -> Client | None` - Obtiene un cliente por su código único.
- `get_client_by_email(email: str) -> Client | None` - Obtiene un cliente por su email.
- `search_clients_by_name(name_pattern: str) -> list[Client]` - Busca clientes por patrón de nombre.
- `get_all_clients(limit: int | None = None, offset: int = 0) -> list[Client]` - Obtiene todos los clientes con paginación.

### 3. Operaciones de Consulta Avanzada (`_advanced_query_operations`)
- `search_clients_by_text(search_text: str, fields: list[str] | None = None, limit: int = 50, offset: int = 0) -> list[Client]` - Busca clientes por texto en campos específicos.
- `get_clients_by_filters(filters: dict[str, Any], limit: int = 50, offset: int = 0, order_by: str | None = None) -> list[Client]` - Obtiene clientes aplicando filtros múltiples.
- `get_clients_with_relationships(include_projects: bool = False, include_contacts: bool = False, limit: int = 50, offset: int = 0) -> list[Client]` - Obtiene clientes con sus relaciones cargadas.
- `count_clients_by_filters(filters: dict[str, Any]) -> int` - Cuenta clientes que coinciden con filtros específicos.
- `search_clients_fuzzy(search_term: str, similarity_threshold: float = 0.3) -> list[Client]` - Búsqueda difusa de clientes por similitud de texto.

### 4. Operaciones de Relaciones (`_relationship_operations`)
- `transfer_projects_to_client(from_client_id: int, to_client_id: int) -> bool` - Transfiere proyectos de un cliente a otro.
- `get_client_projects(client_id: int) -> list[Any]` - Obtiene todos los proyectos asociados a un cliente.
- `get_client_project_count(client_id: int) -> int` - Cuenta los proyectos de un cliente específico.

### 5. Operaciones de Estadísticas (`_statistics_operations`)
- `get_client_statistics() -> dict[str, Any]` - Obtiene estadísticas generales de clientes.
- `get_client_counts_by_status() -> dict[str, int]` - Cuenta clientes agrupados por estado.
- `get_client_count() -> int` - Obtiene el número total de clientes.
- `get_client_stats_by_id(client_id: int) -> dict[str, Any]` - Obtiene estadísticas específicas de un cliente.
- `get_client_creation_trends(days: int = 30, group_by: str = "day") -> list[dict[str, Any]]` - Obtiene tendencias de creación de clientes.
- `get_clients_by_project_count(limit: int = 10) -> list[dict[str, Any]]` - Obtiene clientes ordenados por cantidad de proyectos.
- `get_comprehensive_dashboard_metrics() -> dict[str, Any]` - Obtiene métricas completas para dashboard.

### 6. Operaciones de Validación (`_validation_operations`)
- `validate_unique_fields(client_data: dict[str, Any], exclude_id: int | None = None) -> None` - Valida que campos únicos no estén duplicados.
- `validate_email_format(email: str) -> None` - Valida el formato de email.
- `validate_phone_format(phone: str) -> None` - Valida el formato de teléfono.
- `validate_required_fields(client_data: dict[str, Any]) -> None` - Valida que campos requeridos estén presentes.
- `validate_field_lengths(client_data: dict[str, Any]) -> None` - Valida longitudes máximas de campos.
- `validate_client_data(client_data: dict[str, Any], exclude_id: int | None = None, validate_uniqueness: bool = True) -> None` - Validación completa de datos de cliente.
- `validate_code_format(code: str) -> None` - Valida el formato del código de cliente.
- `validate_business_rules(client_data: dict[str, Any], exclude_id: int | None = None) -> None` - Valida reglas de negocio específicas.
- `validate_client_name_unique(name: str, exclude_id: int | None = None) -> bool` - Verifica unicidad del nombre de cliente.
- `validate_client_code_unique(code: str, exclude_id: int | None = None) -> bool` - Verifica unicidad del código de cliente.
- `validate_client_deletion(client_id: int) -> bool` - Valida si un cliente puede ser eliminado.

### 7. Operaciones de Fechas (`_date_operations`)
- `get_clients_created_in_date_range(start_date: datetime, end_date: datetime) -> list[Client]` - Obtiene clientes creados en un rango de fechas.
- `get_clients_updated_in_date_range(start_date: datetime, end_date: datetime) -> list[Client]` - Obtiene clientes actualizados en un rango de fechas.

### 8. Operaciones de Salud (`_health_operations`)
- `health_check() -> dict[str, Any]` - Verifica el estado de salud de todos los módulos del repositorio.
- `get_module_info() -> dict[str, Any]` - Obtiene información detallada de todos los módulos.