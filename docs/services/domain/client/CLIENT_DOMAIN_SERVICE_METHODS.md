# Métodos de Dominio de Cliente (Básicos)

## Descripción General

Esta es una selección de métodos de dominio de cliente más básicos, derivados de las funcionalidades expuestas por el `ClientRepositoryFacade`. Estos métodos proporcionan una capa de servicio fundamental para operaciones comunes.

---

## Métodos Disponibles

### 1. Operaciones CRUD (3 métodos)

1.  `create_client(client_data: ClientCreateSchema) -> ClientResponseSchema` - Crea un nuevo cliente.
2.  `update_client(client_id: int, client_data: ClientUpdateSchema) -> ClientResponseSchema | None` - Actualiza un cliente existente.
3.  `delete_client(client_id: int) -> bool` - Elimina un cliente.

### 2. Operaciones de Consulta Básica (6 métodos)

4.  `get_client_by_id(client_id: int) -> ClientResponseSchema | None` - Obtiene un cliente por su ID.
5.  `get_client_by_name(name: str) -> ClientResponseSchema | None` - Obtiene un cliente por su nombre.
6.  `get_client_by_code(code: str) -> ClientResponseSchema | None` - Obtiene un cliente por su código.
7.  `get_client_by_email(email: str) -> ClientResponseSchema | None` - Obtiene un cliente por su email. 
8.  `get_all_clients(limit: int | None = None, offset: int = 0) -> List[ClientResponseSchema]` - Obtiene todos los clientes con paginación.
9.  `search_clients_by_name(name_pattern: str) -> List[ClientResponseSchema]` - Busca clientes por un patrón de nombre.

### 3. Operaciones de Búsqueda Avanzada (4 métodos)

10. `search_clients_by_text(search_text: str, fields: list[str] | None = None) -> List[ClientResponseSchema]` - Busca clientes por texto en campos específicos.
11. `get_clients_by_filters(filters: dict[str, Any]) -> List[ClientResponseSchema]` - Obtiene clientes aplicando filtros múltiples.
12. `search_clients_fuzzy(search_term: str, similarity_threshold: float = 0.3) -> List[ClientResponseSchema]` - Búsqueda difusa de clientes por similitud de texto con umbral configurable.
13. `count_clients_by_filters(filters: dict[str, Any]) -> int` - Cuenta clientes que coinciden con filtros específicos sin retornar los datos completos.

### 4. Operaciones Estadísticas Básicas (3 métodos)

14. `get_total_client_count() -> int` - Obtiene el número total de clientes.
15. `get_client_counts_by_status() -> Dict[str, int]` - Obtiene el número de clientes por estado.
16. `get_client_creation_trends(days: int = 30) -> List[Dict[str, Any]]` - Obtiene las tendencias de creación de clientes.

### 5. Operaciones de Estadísticas Avanzadas (4 métodos)

17. `get_client_statistics_summary() -> dict[str, Any]` - Obtiene un resumen de estadísticas de clientes.
18. `get_detailed_client_stats(client_id: int) -> dict[str, Any]` - Obtiene estadísticas detalladas para un cliente específico.
19. `get_clients_by_project_count(limit: int = 10) -> list[dict[str, Any]]` - Obtiene los clientes con más proyectos.
20. `get_dashboard_metrics() -> dict[str, Any]` - Obtiene métricas consolidadas para un dashboard.

### 6. Operaciones de Relaciones (2 métodos)

21. `get_projects_for_client(client_id: int) -> List[ProjectSchema]` - Obtiene los proyectos de un cliente.
22. `get_project_count_for_client(client_id: int) -> int` - Obtiene el número de proyectos de un cliente.

### 7. Operaciones de Fechas (2 métodos)

23. `get_clients_created_in_date_range(start_date: date, end_date: date) -> List[ClientResponseSchema]` - Obtiene clientes creados en un rango de fechas.
24. `get_clients_updated_in_date_range(start_date: date, end_date: date) -> List[ClientResponseSchema]` - Obtiene clientes actualizados en un rango de fechas.

### 8. Operaciones de Validación (4 métodos)

25. `validate_client_uniqueness(name: str, code: str, email: str, exclude_id: int | None = None) -> bool` - Valida la unicidad de nombre, código y email.
26. `validate_client_data_integrity(client_data: dict, operation: str = "create") -> bool` - Valida la integridad de los datos del cliente para una operación.
27. `check_client_deletability(client_id: int) -> bool` - Verifica si un cliente puede ser eliminado.
28. `validate_client_business_rules(client_data: dict) -> bool` - Valida las reglas de negocio para los datos de un cliente.

### 9. Operaciones de Diagnóstico y Salud (2 métodos)

29. `check_service_health() -> dict[str, Any]` - Verifica el estado de salud del servicio y sus dependencias.
30. `get_service_info() -> dict[str, Any]` - Obtiene información de configuración y estado del servicio.