# Funciones Disponibles en `ClientRepositoryFacade`

Este documento detalla todos los métodos públicos disponibles en la clase `ClientRepositoryFacade`, clasificados por el módulo especializado al que delegan su operación.

---

## Módulo de Operaciones CRUD (`_crud_operations`)

Funciones dedicadas a la creación, actualización y eliminación de registros de clientes.

- **`create_client(client_data: ClientCreate) -> Client`**
  - Crea un nuevo cliente a partir de los datos proporcionados.

- **`update_client(client_id: int, client_data: ClientUpdate) -> Client | None`**
  - Actualiza los datos de un cliente existente, identificado por su ID.

- **`delete_client(client_id: int) -> bool`**
  - Elimina un cliente de forma segura por su ID.

---

## Módulo de Consultas (`_query_operations`)

Métodos para realizar búsquedas y recuperaciones de datos de clientes con filtros comunes.

- **`get_client_by_id(client_id: int) -> Client | None`**
  - Obtiene un cliente por su ID.

- **`get_client_by_name(name: str) -> Client | None`**
  - Busca un cliente por su nombre exacto.

- **`get_client_by_code(code: str) -> Client | None`**
  - Recupera un cliente utilizando su código único.

- **`get_client_by_email(email: str) -> Client | None`**
  - Encuentra un cliente por su dirección de correo electrónico.

- **`search_clients_by_name(name_pattern: str) -> list[Client]`**
  - Realiza una búsqueda de clientes cuyos nombres coincidan con un patrón.

- **`get_all_clients(limit: int | None = None, offset: int = 0) -> list[Client]`**
  - Obtiene una lista de todos los clientes, con soporte para paginación.

---

## Módulo de Consultas Avanzadas (`_advanced_query_operations`)

Operaciones de búsqueda complejas que combinan múltiples criterios y relaciones.

- **`search_clients_by_text(search_text: str, fields: list[str] | None = None, limit: int = 50, offset: int = 0) -> list[Client]`**
  - Busca clientes por un texto en campos específicos.

- **`get_clients_by_filters(filters: dict[str, Any], limit: int = 50, offset: int = 0, order_by: str | None = None) -> list[Client]`**
  - Obtiene clientes aplicando un conjunto de filtros dinámicos.

- **`get_clients_with_relationships(include_projects: bool = False, include_contacts: bool = False, limit: int = 50, offset: int = 0) -> list[Client]`**
  - Carga clientes junto con sus relaciones (proyectos, contactos).

- **`count_clients_by_filters(filters: dict[str, Any]) -> int`**
  - Cuenta el número de clientes que coinciden con los filtros.

- **`search_clients_fuzzy(search_term: str, similarity_threshold: float = 0.3) -> list[Client]`**
  - Realiza una búsqueda difusa por término de búsqueda y umbral de similitud.

---

## Módulo de Operaciones de Fechas (`_date_operations`)

Funciones especializadas en filtrar clientes según rangos de fechas.

- **`get_clients_created_in_date_range(start_date: datetime, end_date: datetime) -> list[Client]`**
  - Obtiene clientes creados dentro de un intervalo de fechas.

- **`get_clients_updated_in_date_range(start_date: datetime, end_date: datetime) -> list[Client]`**
  - Recupera clientes que fueron actualizados en un rango de fechas.

---

## Módulo de Relaciones (`_relationship_operations`)

Gestiona las conexiones entre clientes y otras entidades, como proyectos.

- **`transfer_projects_to_client(from_client_id: int, to_client_id: int) -> bool`**
  - Transfiere todos los proyectos de un cliente a otro.

- **`get_client_projects(client_id: int) -> list[Any]`**
  - Obtiene la lista de proyectos asociados a un cliente.

- **`get_client_project_count(client_id: int) -> int`**
  - Cuenta cuántos proyectos tiene asignados un cliente.

---

## Módulo de Estadísticas (`_statistics_operations`)

Cálculos y métricas sobre los datos de los clientes.

- **`get_client_statistics() -> dict[str, Any]`**
  - Obtiene un resumen de estadísticas generales de clientes.

- **`get_client_counts_by_status() -> dict[str, int]`**
  - Devuelve el número de clientes agrupados por su estado.

- **`get_client_count() -> int`**
  - Obtiene el número total de clientes registrados.

- **`get_client_stats_by_id(client_id: int) -> dict[str, Any]`**
  - Recupera estadísticas detalladas para un cliente específico.

- **`get_client_creation_trends(days: int = 30, group_by: str = "day") -> list[dict[str, Any]]`**
  - Analiza las tendencias de creación de clientes en un período.

- **`get_clients_by_project_count(limit: int = 10) -> list[dict[str, Any]]`**
  - Obtiene un ranking de clientes según su número de proyectos.

- **`get_comprehensive_dashboard_metrics() -> dict[str, Any]`**
  - Genera un conjunto completo de métricas para un panel de control.

---

## Módulo de Validación (`_validation_operations`)

Reglas de negocio y validaciones de integridad de datos para la entidad cliente.

- **`validate_unique_fields(client_data: dict[str, Any], exclude_id: int | None = None) -> None`**
  - Valida que los campos únicos (como email o código) no estén duplicados.

- **`validate_email_format(email: str) -> None`**
  - Verifica que el formato del correo electrónico sea válido.

- **`validate_phone_format(phone: str) -> None`**
  - Comprueba que el formato del número de teléfono sea correcto.

- **`validate_required_fields(client_data: dict[str, Any]) -> None`**
  - Asegura que todos los campos obligatorios estén presentes.

- **`validate_field_lengths(client_data: dict[str, Any]) -> None`**
  - Valida que los datos no excedan la longitud máxima permitida.

- **`validate_client_data(client_data: dict[str, Any], exclude_id: int | None = None, validate_uniqueness: bool = True) -> None`**
  - Ejecuta un conjunto completo de validaciones sobre los datos del cliente.

- **`validate_code_format(code: str) -> None`**
  - Valida que el código de cliente cumpla con el formato esperado.

- **`validate_business_rules(client_data: dict[str, Any], exclude_id: int | None = None) -> None`**
  - Aplica reglas de negocio específicas del dominio del cliente.

- **`validate_client_name_unique(name: str, exclude_id: int | None = None) -> bool`**
  - Confirma que el nombre del cliente no esté ya en uso.

- **`validate_client_code_unique(code: str, exclude_id: int | None = None) -> bool`**
  - Verifica que el código del cliente sea único en el sistema.

- **`validate_client_deletion(client_id: int) -> bool`**
  - Comprueba si un cliente puede ser eliminado según las reglas de negocio.

---

## Módulo de Salud del Repositorio (`_health_operations`)

Operaciones para monitorear el estado y la configuración de los módulos del repositorio.

- **`health_check() -> dict[str, Any]`**
  - Realiza una comprobación del estado de todos los módulos internos.

- **`get_module_info() -> dict[str, Any]`**
  - Obtiene información detallada sobre la configuración de cada módulo.