# Funciones Disponibles en Client Repository

## Resumen
Este documento enumera todas las funciones públicas disponibles en el sistema de repositorios de cliente del Planificador. El sistema está organizado en módulos especializados que siguen principios de arquitectura limpia y separación de responsabilidades.

## Arquitectura del Sistema

### Punto de Entrada Principal
- **ClientRepositoryFacade**: Interfaz unificada que coordina todas las operaciones
- **Módulos Especializados**: Cada uno maneja un aspecto específico del dominio
- **Interfaces Abstractas**: Definen contratos para inyección de dependencias

---

## 1. ClientRepositoryFacade (client_repository_facade.py)
**Punto de entrada principal del sistema - 67 métodos públicos**

### CRUD Operations (5 métodos)
- `create_client(client_data: ClientCreate) -> Client`
- `create_client_with_date_validation(client_data: dict) -> Client`
- `get_client_by_id(client_id: int) -> Client | None`
- `update_client(client_id: int, update_data: ClientUpdate) -> Client`
- `delete_client(client_id: int) -> bool`

#### Consultas por Identificadores Únicos (2 funciones)
- `get_by_name(name: str) -> Optional[Client]` - Obtiene un cliente por su nombre
- `get_by_code(code: str) -> Optional[Client]` - Obtiene un cliente por su código único

#### Consultas por Atributos (7 funciones)
- `search_by_name(search_term: str) -> List[Client]` - Busca clientes por patrón de nombre
- `get_active_clients() -> List[Client]` - Obtiene todos los clientes activos
- `get_with_projects(client_id: int) -> Optional[Client]` - Obtiene un cliente con sus proyectos asignados
- `get_client_relationship_duration(client_id: int) -> Dict[str, Any]` - Calcula la duración de la relación con un cliente específico
- `get_clients_with_contact_info(include_inactive: bool = False) -> List[Client]` - Obtiene clientes que tienen información de contacto
- `get_clients_without_contact_info(include_inactive: bool = False) -> List[Client]` - Obtiene clientes que no tienen información de contacto
- `get_clients_display_summary(include_inactive: bool = False) -> List[Dict[str, Any]]` - Obtiene resumen formateado de clientes usando propiedades del modelo

#### Consultas Temporales (3 funciones)
- `get_clients_created_current_week(**kwargs) -> List[Client]` - Obtiene clientes creados en la semana actual
- `get_clients_created_current_month(**kwargs) -> List[Client]` - Obtiene clientes creados en el mes actual
- `get_clients_created_business_days_only(start_date: Union[date, str, None] = None, end_date: Union[date, str, None] = None, **kwargs) -> List[Client]` - Obtiene clientes creados en días laborables

#### Validaciones de Unicidad (2 funciones)
- `name_exists(name: str, exclude_id: Optional[int] = None) -> bool` - Verifica si existe un nombre de cliente
- `code_exists(code: str, exclude_id: Optional[int] = None) -> bool` - Verifica si existe un código de cliente

#### Estadísticas y Métricas (28 funciones)
- `get_client_stats(client_id: int) -> Dict[str, Any]` - Obtiene estadísticas de un cliente específico
- `get_clients_by_relationship_duration(min_years: float = 0.0, max_years: Optional[float] = None, is_active: Optional[bool] = None) -> List[Dict[str, Any]]` - Obtiene clientes por duración de relación
- `get_client_counts_by_status() -> Dict[str, int]` - Obtiene conteo de clientes por estado
- `get_client_creation_trends(days: int = 30) -> Dict[str, Any]` - Obtiene tendencias de creación de clientes
- `get_clients_by_project_count(limit: int = 10) -> List[Dict[str, Any]]` - Obtiene clientes por cantidad de proyectos (con límite)
- `get_client_activity_summary() -> Dict[str, Any]` - Obtiene resumen de actividad de clientes
- `get_performance_metrics() -> Dict[str, Any]` - Obtiene métricas de rendimiento del sistema
- `get_contact_info_statistics() -> Dict[str, Any]` - Obtiene estadísticas sobre información de contacto de clientes
- `get_client_segmentation_analysis()`
- `get_client_value_analysis()`
- `get_client_retention_analysis()`
- `get_comprehensive_dashboard_metrics()`
- `get_client_count()`
- `get_active_client_count()`
- `get_clients_by_creation_date()`
- `get_client_distribution_by_status()`
- `get_top_clients_by_projects()`
- `calculate_client_metrics()`
- `get_monthly_client_growth()`
- `get_total_clients_count()`
- `get_active_clients_count()`
- `get_inactive_clients_count()`
- `get_clients_created_this_month()`
- `get_clients_created_this_year()`
- `get_average_clients_per_month()`
- `calculate_growth_rate()`
- `get_monthly_client_creation_stats()`
- `generate_comprehensive_stats()`
- `get_top_clients_by_activity()`
- `validate_date_range()`
- `export_stats_to_dict()`

#### Gestión de Relaciones con Proyectos (6 funciones)
- `get_client_projects(client_id: int, status_filter: Optional[List[str]] = None, include_inactive: bool = False, load_details: bool = False) -> List[Project]` - Obtiene proyectos de un cliente
- `get_client_project_summary(client_id: int) -> Dict[str, Any]` - Obtiene resumen de proyectos de un cliente
- `transfer_projects_to_client(source_client_id: int, target_client_id: int, project_ids: Optional[List[int]] = None, validate_transfer: bool = True) -> Dict[str, Any]` - Transfiere proyectos entre clientes
- `validate_client_project_integrity(client_id: int) -> Dict[str, Any]` - Valida integridad de relaciones cliente-proyecto
- `assign_project_to_client(project_id: int, client_id: int, validate_constraints: bool = True) -> Project`
- `cleanup_client_relationships(client_id: int, action: str = 'deactivate') -> Dict[str, Any]`

#### Validaciones (7 funciones)
- `validate_client_data(client_data: Dict[str, Any]) -> Dict[str, Any]`
- `validate_bulk_data(clients_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]`
- `validate_update_data(update_data: Dict[str, Any]) -> Dict[str, Any]`
- `validate_creation_business_day(validate_business_day: bool = False) -> None`
- `validate_name_exists(name: str, exclude_id: Optional[int] = None) -> bool`
- `validate_code_exists(code: str, exclude_id: Optional[int] = None) -> bool`
- `validate_client_update_data(update_data: Dict[str, Any], client_id: int) -> Dict[str, Any]`

---

### ClientQueryBuilder (client_query_builder.py)

#### Consultas Base por Identificadores (2 funciones)
- `get_by_name(name: str) -> Optional[Client]`
- `get_by_code(code: str) -> Optional[Client]`

#### Consultas por Atributos (5 funciones)
- `search_by_name(search_term: str) -> List[Client]`
- `get_active_clients() -> List[Client]`
- `get_with_projects(client_id: int) -> Optional[Client]`
- `find_clients_with_contact_info(include_inactive: bool = False) -> List[Client]`
- `find_clients_without_contact_info(include_inactive: bool = False) -> List[Client]`

#### Consultas Temporales (3 funciones)
- `find_clients_created_current_week(**kwargs) -> List[Client]`
- `find_clients_created_current_month(**kwargs) -> List[Client]`
- `find_clients_created_business_days_only(start_date: Union[date, str, None] = None, end_date: Union[date, str, None] = None, **kwargs) -> List[Client]`

#### Consultas por Criterios Múltiples (1 función)
- `find_by_criteria(**kwargs) -> List[Client]`

#### Validaciones de Existencia (2 funciones)
- `name_exists(name: str, exclude_id: Optional[int] = None) -> bool`
- `code_exists(code: str, exclude_id: Optional[int] = None) -> bool`

---

### ClientStatistics (client_statistics.py)

#### Estadísticas (28 funciones)
- `get_client_stats(client_id: int) -> Dict[str, Any]`
- `get_client_counts_by_status() -> Dict[str, int]`
- `get_client_creation_trends(days: int = 30, group_by: str = 'day') -> List[Dict[str, Any]]`
- `get_client_relationship_duration_stats() -> Dict[str, Any]`
- `get_clients_by_relationship_duration(min_years: float = 0.0, max_years: Optional[float] = None, is_active: Optional[bool] = None) -> List[Dict[str, Any]]`
- `get_clients_by_project_count(limit: int = 10) -> List[Dict[str, Any]]`
- `get_contact_info_statistics() -> Dict[str, Any]`
- `get_client_activity_summary() -> Dict[str, Any]`
- `get_client_segmentation_analysis()`
- `get_client_value_analysis()`
- `get_client_retention_analysis()`
- `get_comprehensive_dashboard_metrics()`
- `get_performance_metrics()`
- `get_client_count()`
- `get_active_client_count()`
- `get_clients_by_creation_date()`
- `get_client_distribution_by_status()`
- `get_top_clients_by_projects()`
- `calculate_client_metrics()`
- `get_monthly_client_growth()`
- `get_total_clients_count()`
- `get_active_clients_count()`
- `get_inactive_clients_count()`
- `get_clients_created_this_month()`
- `get_clients_created_this_year()`
- `get_average_clients_per_month()`
- `calculate_growth_rate()`
- `get_monthly_client_creation_stats()`
- `generate_comprehensive_stats()`
- `get_top_clients_by_activity()`
- `validate_date_range()`
- `export_stats_to_dict()`

---

### ClientRelationshipManager (client_relationship_manager.py)

#### Gestión de Relaciones (6 funciones)
- `get_client_projects(client_id: int, status_filter: Optional[List[str]] = None, include_inactive: bool = False, load_details: bool = False) -> List[Project]`
- `assign_project_to_client(project_id: int, client_id: int, validate_constraints: bool = True) -> Project`
- `transfer_projects_to_client(source_client_id: int, target_client_id: int, project_ids: Optional[List[int]] = None, validate_transfer: bool = True) -> Dict[str, Any]`
- `get_client_project_summary(client_id: int) -> Dict[str, Any]`
- `validate_client_project_integrity(client_id: int) -> Dict[str, Any]`
- `cleanup_client_relationships(client_id: int, action: str = 'deactivate') -> Dict[str, Any]`

---

### ClientValidator (client_validator.py)

#### Validaciones (7 funciones)
- `validate_client_data(client_data: Dict[str, Any]) -> Dict[str, Any]`
- `validate_bulk_data(clients_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]`
- `validate_update_data(update_data: Dict[str, Any]) -> Dict[str, Any]`
- `validate_creation_business_day(validate_business_day: bool = False) -> None`
- `validate_name_exists(name: str, exclude_id: Optional[int] = None) -> bool`
- `validate_code_exists(code: str, exclude_id: Optional[int] = None) -> bool`
- `validate_client_update_data(update_data: Dict[str, Any], client_id: int) -> Dict[str, Any]`

---

## Resumen de Funciones por Módulo

Este documento cataloga las funciones públicas disponibles en los módulos de repositorio de clientes, agrupadas por su funcionalidad principal. Cada módulo tiene un propósito específico, desde la gestión de datos básicos hasta análisis estadísticos complejos.

- **`ClientRepositoryFacade`**: 21 funciones para operaciones CRUD, consultas y gestión de relaciones.
- **`ClientQueryBuilder`**: 15 funciones para construir consultas dinámicas y complejas.
- **`ClientStatistics`**: 28 funciones para análisis estadísticos y métricas de negocio.
- **`ClientRelationshipManager`**: 6 funciones para gestionar las relaciones entre clientes y proyectos.
- **`ClientValidator`**: 7 funciones para la validación de datos y reglas de negocio.

---

**Nota**: Las funciones marcadas como **[PRIVADA]** son métodos internos de las clases y no deben ser llamadas directamente desde código externo. Están documentadas para completitud y mantenimiento del código.