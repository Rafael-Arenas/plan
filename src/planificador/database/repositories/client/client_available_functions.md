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
- `create_client_with_pendulum_validation(client_data: dict) -> Client`
- `get_client_by_id(client_id: int) -> Client | None`
- `update_client(client_id: int, update_data: ClientUpdate) -> Client`
- `delete_client(client_id: int) -> bool`

#### Consultas por Identificadores Únicos (2 funciones)
5. `get_by_name(name: str) -> Optional[Client]` - Obtiene un cliente por su nombre
6. `get_by_code(code: str) -> Optional[Client]` - Obtiene un cliente por su código único

#### Consultas por Atributos (7 funciones)
7. `search_by_name(search_term: str) -> List[Client]` - Busca clientes por patrón de nombre
8. `get_active_clients() -> List[Client]` - Obtiene todos los clientes activos
9. `get_with_projects(client_id: int) -> Optional[Client]` - Obtiene un cliente con sus proyectos asignados
10. `get_client_relationship_duration(client_id: int) -> Dict[str, Any]` - Calcula la duración de la relación con un cliente específico
11. `get_clients_with_contact_info(include_inactive: bool = False) -> List[Client]` - Obtiene clientes que tienen información de contacto
12. `get_clients_without_contact_info(include_inactive: bool = False) -> List[Client]` - Obtiene clientes que no tienen información de contacto
13. `get_clients_display_summary(include_inactive: bool = False) -> List[Dict[str, Any]]` - Obtiene resumen formateado de clientes usando propiedades del modelo

#### Consultas Temporales (3 funciones)
14. `get_clients_created_current_week(**kwargs) -> List[Client]` - Obtiene clientes creados en la semana actual
15. `get_clients_created_current_month(**kwargs) -> List[Client]` - Obtiene clientes creados en el mes actual
16. `get_clients_created_business_days_only(start_date: Union[date, str, None] = None, end_date: Union[date, str, None] = None, **kwargs) -> List[Client]` - Obtiene clientes creados en días laborables

#### Validaciones de Unicidad (2 funciones)
17. `name_exists(name: str, exclude_id: Optional[int] = None) -> bool` - Verifica si existe un nombre de cliente
18. `code_exists(code: str, exclude_id: Optional[int] = None) -> bool` - Verifica si existe un código de cliente

#### Estadísticas y Métricas (8 funciones)
19. `get_client_stats(client_id: int) -> Dict[str, Any]` - Obtiene estadísticas de un cliente específico
20. `get_clients_by_relationship_duration(min_years: float = 0.0, max_years: Optional[float] = None, is_active: Optional[bool] = None) -> List[Dict[str, Any]]` - Obtiene clientes por duración de relación
21. `get_client_counts_by_status() -> Dict[str, int]` - Obtiene conteo de clientes por estado
22. `get_client_creation_trends(days: int = 30) -> Dict[str, Any]` - Obtiene tendencias de creación de clientes
23. `get_clients_by_project_count(limit: int = 10) -> List[Dict[str, Any]]` - Obtiene clientes por cantidad de proyectos (con límite)
24. `get_client_activity_summary() -> Dict[str, Any]` - Obtiene resumen de actividad de clientes
25. `get_performance_metrics() -> Dict[str, Any]` - Obtiene métricas de rendimiento del sistema
26. `get_contact_info_statistics() -> Dict[str, Any]` - Obtiene estadísticas sobre información de contacto de clientes

#### Gestión de Relaciones con Proyectos (4 funciones)
27. `get_client_projects(client_id: int, status_filter: Optional[List[str]] = None, include_inactive: bool = False, load_details: bool = False) -> List[Project]` - Obtiene proyectos de un cliente
28. `get_client_project_summary(client_id: int) -> Dict[str, Any]` - Obtiene resumen de proyectos de un cliente
29. `transfer_projects_to_client(source_client_id: int, target_client_id: int, project_ids: Optional[List[int]] = None, validate_transfer: bool = True) -> Dict[str, Any]` - Transfiere proyectos entre clientes
30. `validate_client_project_integrity(client_id: int) -> Dict[str, Any]` - Valida integridad de relaciones cliente-proyecto

---

### ClientQueryBuilder (client_query_builder.py)

#### Consultas Base por Identificadores (2 funciones)
31. `get_by_name(name: str) -> Optional[Client]` - Busca cliente por nombre
32. `get_by_code(code: str) -> Optional[Client]` - Busca cliente por código

#### Consultas por Atributos (5 funciones)
33. `search_by_name(search_term: str) -> List[Client]` - Busca clientes por patrón de nombre
34. `get_active_clients() -> List[Client]` - Obtiene clientes activos
35. `get_with_projects(client_id: int) -> Optional[Client]` - Obtiene cliente con proyectos
36. `find_clients_with_contact_info(include_inactive: bool = False) -> List[Client]` - Busca clientes que tienen información de contacto
37. `find_clients_without_contact_info(include_inactive: bool = False) -> List[Client]` - Busca clientes que no tienen información de contacto

#### Consultas Temporales (3 funciones)
38. `find_clients_created_current_week(**kwargs) -> List[Client]` - Obtiene clientes creados en la semana actual
39. `find_clients_created_current_month(**kwargs) -> List[Client]` - Obtiene clientes creados en el mes actual
40. `find_clients_created_business_days_only(start_date: Union[date, str, None] = None, end_date: Union[date, str, None] = None, **kwargs) -> List[Client]` - Obtiene clientes creados en días laborables

#### Consultas por Criterios Múltiples (1 función)
41. `find_by_criteria(**kwargs) -> List[Client]` - Busca clientes por múltiples criterios

#### Validaciones de Existencia (2 funciones)
42. `name_exists(name: str, exclude_id: Optional[int] = None) -> bool` - Verifica si existe un nombre
43. `code_exists(code: str, exclude_id: Optional[int] = None) -> bool` - Verifica si existe un código

---

### ClientStatistics (client_statistics.py)

#### Estadísticas por Cliente (1 función)
44. `get_client_stats(client_id: int) -> Dict[str, Any]` - Obtiene estadísticas detalladas de un cliente específico

#### Estadísticas por Categorías (1 función)
45. `get_client_counts_by_status() -> Dict[str, int]` - Obtiene conteos de clientes por estado

#### Estadísticas Temporales (1 función)
46. `get_client_creation_trends(days: int = 30, group_by: str = 'day') -> List[Dict[str, Any]]` - Obtiene tendencias de creación de clientes en un período

#### Estadísticas de Relaciones (2 funciones)
47. `get_client_relationship_duration_stats() -> Dict[str, Any]` - Obtiene estadísticas de duración de relaciones con clientes
48. `get_clients_by_relationship_duration(min_years: float = 0.0, max_years: Optional[float] = None, is_active: Optional[bool] = None) -> List[Dict[str, Any]]` - Obtiene clientes por duración de relación

#### Estadísticas por Proyectos (1 función)
49. `get_clients_by_project_count(limit: int = 10) -> List[Dict[str, Any]]` - Obtiene clientes filtrados por cantidad de proyectos (con límite)

#### Estadísticas de Información de Contacto (1 función)
50. `get_contact_info_statistics() -> Dict[str, Any]` - Obtiene estadísticas detalladas sobre información de contacto de clientes

#### Resumen de Actividad (1 función)
51. `get_client_activity_summary() -> Dict[str, Any]` - Obtiene resumen general de actividad de clientes

#### Métricas de Rendimiento (1 función)
52. `get_performance_metrics() -> Dict[str, Any]` - Obtiene métricas de rendimiento del sistema de clientes

---

### ClientRelationshipManager (client_relationship_manager.py)

#### Consultas de Relaciones Básicas (1 función)
46. `get_client_projects(client_id: int, status_filter: Optional[List[str]] = None, include_inactive: bool = False, load_details: bool = False) -> List[Project]` - Obtiene proyectos asociados a un cliente

#### Gestión de Asignaciones (1 función)
47. `assign_project_to_client(project_id: int, client_id: int, validate_constraints: bool = True) -> Project` - Asigna un proyecto a un cliente

#### Gestión de Transferencias (1 función)
48. `transfer_projects_to_client(source_client_id: int, target_client_id: int, project_ids: Optional[List[int]] = None, validate_transfer: bool = True) -> Dict[str, Any]` - Transfiere proyectos entre clientes

#### Resúmenes y Análisis (1 función)
49. `get_client_project_summary(client_id: int) -> Dict[str, Any]` - Obtiene resumen detallado de proyectos de un cliente

#### Validaciones de Integridad (1 función)
50. `validate_client_project_integrity(client_id: int) -> Dict[str, Any]` - Valida la integridad de las relaciones cliente-proyecto

#### Limpieza de Relaciones (1 función)
51. `cleanup_client_relationships(client_id: int, action: str = 'deactivate') -> Dict[str, Any]` - Limpia relaciones antes de eliminación o desactivación

#### Funciones Privadas (4 funciones)
52. `_validate_client_exists(client_id: int) -> None` - **[PRIVADA]** Valida que un cliente existe
53. `_get_client_by_id(client_id: int) -> Optional[Client]` - **[PRIVADA]** Obtiene un cliente por ID
54. `_get_project_by_id(project_id: int) -> Optional[Project]` - **[PRIVADA]** Obtiene un proyecto por ID
55. `_validate_project_assignment(project: Project, client_id: int) -> None` - **[PRIVADA]** Valida asignación de proyecto

---

### ClientValidator (client_validator.py)

#### Validaciones Principales (3 funciones)
56. `validate_client_data(client_data: Dict[str, Any]) -> Dict[str, Any]` - Valida y normaliza datos de cliente
57. `validate_bulk_data(clients_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]` - Valida datos de múltiples clientes
58. `validate_update_data(update_data: Dict[str, Any]) -> Dict[str, Any]` - Valida datos para actualización de cliente

#### Validaciones de Reglas de Negocio (1 función)
59. `validate_creation_business_day(validate_business_day: bool = False) -> None` - Valida creación en días laborables

#### Validaciones Asíncronas de Existencia (3 funciones)
60. `validate_name_exists(name: str, exclude_id: Optional[int] = None) -> bool` - Valida si existe un nombre de cliente
61. `validate_code_exists(code: str, exclude_id: Optional[int] = None) -> bool` - Valida si existe un código de cliente
62. `validate_client_update_data(update_data: Dict[str, Any], client_id: int) -> Dict[str, Any]` - Valida datos de actualización con contexto de cliente

#### Validaciones Internas - Campos Requeridos (1 función)
63. `_validate_required_fields(data: Dict[str, Any]) -> None` - **[PRIVADA]** Valida campos obligatorios

#### Validaciones Internas - Formato de Datos (8 funciones)
64. `_validate_name(name: str) -> str` - **[PRIVADA]** Valida y normaliza nombre del cliente
65. `_validate_code(code: str) -> str` - **[PRIVADA]** Valida y normaliza código del cliente
66. `_validate_description(description: str) -> str` - **[PRIVADA]** Valida descripción del cliente
67. `_validate_contact_info(contact_info: str) -> str` - **[PRIVADA]** Valida información de contacto
68. `_validate_email(email: str) -> str` - **[PRIVADA]** Valida formato del email
69. `_validate_phone(phone: str) -> str` - **[PRIVADA]** Valida formato del teléfono
70. `_validate_is_active(is_active: Any) -> bool` - **[PRIVADA]** Valida estado activo del cliente
71. `_apply_business_rules(data: Dict[str, Any]) -> None` - **[PRIVADA]** Aplica reglas de negocio específicas

---

## Categorías Funcionales

###### Por Tipo de Operación
- **CRUD Básicas**: 4 funciones
- **Consultas**: 25 funciones (agregada `find_by_criteria`)
- **Estadísticas**: 8 funciones
- **Gestión de Relaciones**: 6 funciones (agregadas `assign_project_to_client` y `cleanup_client_relationships`)
- **Validaciones**: 27 funciones

### Por Nivel de Acceso
- **Funciones Públicas**: 56 funciones
- **Funciones Privadas**: 15 funciones

**Total de funciones documentadas**: 71 funciones

---

**Nota**: Las funciones marcadas como **[PRIVADA]** son métodos internos de las clases y no deben ser llamadas directamente desde código externo. Están documentadas para completitud y mantenimiento del código.