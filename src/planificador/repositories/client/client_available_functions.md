# Funciones Disponibles en ClientRepositoryFacade

**Última actualización:** Enero 2025

## Descripción General

`ClientRepositoryFacade` es la clase principal que proporciona una interfaz unificada para todas las operaciones relacionadas con clientes en el sistema. Esta fachada encapsula la lógica de acceso a datos y coordina las operaciones entre diferentes módulos especializados, ofreciendo una API coherente y fácil de usar para la gestión completa de clientes.

La fachada integra 8 módulos especializados que manejan diferentes aspectos de las operaciones con clientes: consultas avanzadas, operaciones CRUD, gestión de fechas, monitoreo de salud, consultas básicas, gestión de relaciones, análisis estadístico y validación de datos.

---

## Métodos Disponibles

### 1. Operaciones de Consulta Avanzada (5 métodos)

1. `search_clients_by_text(search_text: str, fields: list[str] | None = None, limit: int = 50, offset: int = 0) -> list[Client]` - Busca clientes por texto en campos específicos con paginación
2. `get_clients_by_filters(filters: dict[str, Any], limit: int = 50, offset: int = 0, order_by: str | None = None) -> list[Client]` - Obtiene clientes aplicando filtros múltiples con ordenamiento opcional
3. `get_clients_with_relationships(include_projects: bool = False, include_contacts: bool = False, limit: int = 50, offset: int = 0) -> list[Client]` - Obtiene clientes con sus relaciones cargadas según los parámetros especificados
4. `count_clients_by_filters(filters: dict[str, Any]) -> int` - Cuenta clientes que coinciden con filtros específicos
5. `search_clients_fuzzy(search_term: str, similarity_threshold: float = 0.3) -> list[Client]` - Búsqueda difusa de clientes por similitud de texto con umbral configurable

### 2. Operaciones CRUD (3 métodos)

6. `create_client(client_data: ClientCreate) -> Client` - Crea un nuevo cliente con validación completa de datos
7. `update_client(client_id: int, client_data: ClientUpdate) -> Client | None` - Actualiza un cliente existente con los datos proporcionados
8. `delete_client(client_id: int) -> bool` - Elimina un cliente por su ID único

### 3. Operaciones de Fechas (2 métodos)

9. `get_clients_created_in_date_range(start_date: datetime, end_date: datetime) -> list[Client]` - Obtiene clientes creados dentro del rango de fechas especificado
10. `get_clients_updated_in_date_range(start_date: datetime, end_date: datetime) -> list[Client]` - Obtiene clientes actualizados dentro del rango de fechas especificado

### 4. Operaciones de Salud (2 métodos)

11. `health_check() -> dict[str, Any]` - Verifica el estado de salud de todos los módulos del repositorio
12. `get_module_info() -> dict[str, Any]` - Obtiene información detallada de configuración y estado de todos los módulos

### 5. Operaciones de Consulta (6 métodos)

13. `get_client_by_id(client_id: int) -> Client | None` - Obtiene un cliente por su identificador único
14. `get_client_by_name(name: str) -> Client | None` - Obtiene un cliente por su nombre exacto
15. `get_client_by_code(code: str) -> Client | None` - Obtiene un cliente por su código único
16. `get_client_by_email(email: str) -> Client | None` - Obtiene un cliente por su dirección de email
17. `search_clients_by_name(name_pattern: str) -> list[Client]` - Busca clientes que coincidan con el patrón de nombre proporcionado
18. `get_all_clients(limit: int | None = None, offset: int = 0) -> list[Client]` - Obtiene todos los clientes con paginación opcional

### 6. Operaciones de Relaciones (3 métodos)

19. `transfer_projects_to_client(from_client_id: int, to_client_id: int) -> bool` - Transfiere todos los proyectos de un cliente a otro cliente
20. `get_client_projects(client_id: int) -> list[Any]` - Obtiene todos los proyectos asociados a un cliente específico
21. `get_client_project_count(client_id: int) -> int` - Cuenta el número total de proyectos asociados a un cliente

### 7. Operaciones de Estadísticas (7 métodos)

22. `get_client_statistics() -> dict[str, Any]` - Obtiene estadísticas generales y métricas agregadas de todos los clientes
23. `get_client_counts_by_status() -> dict[str, int]` - Cuenta clientes agrupados por su estado actual
24. `get_client_count() -> int` - Obtiene el número total de clientes registrados en el sistema
25. `get_client_stats_by_id(client_id: int) -> dict[str, Any]` - Obtiene estadísticas detalladas y métricas específicas de un cliente
26. `get_client_creation_trends(days: int = 30, group_by: str = "day") -> list[dict[str, Any]]` - Obtiene tendencias de creación de clientes en un período específico
27. `get_clients_by_project_count(limit: int = 10) -> list[dict[str, Any]]` - Obtiene clientes ordenados por cantidad de proyectos asociados
28. `get_comprehensive_dashboard_metrics() -> dict[str, Any]` - Obtiene métricas completas y consolidadas para dashboard ejecutivo

### 8. Operaciones de Validación (11 métodos)

29. `validate_unique_fields(client_data: dict[str, Any], exclude_id: int | None = None) -> None` - Valida que campos únicos no estén duplicados en la base de datos
30. `validate_email_format(email: str) -> None` - Valida que el formato del email sea correcto según estándares RFC
31. `validate_phone_format(phone: str) -> None` - Valida que el formato del número de teléfono sea válido
32. `validate_required_fields(client_data: dict[str, Any]) -> None` - Valida que todos los campos requeridos estén presentes y no vacíos
33. `validate_field_lengths(client_data: dict[str, Any]) -> None` - Valida que las longitudes de los campos no excedan los límites máximos
34. `validate_client_data(client_data: dict[str, Any], exclude_id: int | None = None, validate_uniqueness: bool = True) -> None` - Ejecuta validación completa de datos de cliente incluyendo reglas de negocio
35. `validate_code_format(code: str) -> None` - Valida que el formato del código de cliente cumpla con las reglas establecidas
36. `validate_business_rules(client_data: dict[str, Any], exclude_id: int | None = None) -> None` - Valida reglas de negocio específicas y restricciones del dominio
37. `validate_client_name_unique(name: str, exclude_id: int | None = None) -> bool` - Verifica que el nombre del cliente sea único en el sistema
38. `validate_client_code_unique(code: str, exclude_id: int | None = None) -> bool` - Verifica que el código del cliente sea único en el sistema
39. `validate_client_deletion(client_id: int) -> bool` - Valida si un cliente puede ser eliminado según las reglas de negocio

---

## Resumen de Funcionalidades

### Total de Métodos Públicos: 39

**Distribución por Categorías:**
- Operaciones de Consulta Avanzada: 5 métodos (13%)
- Operaciones CRUD: 3 métodos (8%)
- Operaciones de Fechas: 2 métodos (5%)
- Operaciones de Salud: 2 métodos (5%)
- Operaciones de Consulta: 6 métodos (15%)
- Operaciones de Relaciones: 3 métodos (8%)
- Operaciones de Estadísticas: 7 métodos (18%)
- Operaciones de Validación: 11 métodos (28%)

### Características Principales

- **Gestión Completa de Clientes**: CRUD completo con validación robusta de datos
- **Consultas Avanzadas**: Búsquedas por múltiples criterios, filtros complejos y búsqueda difusa
- **Validación Exhaustiva**: 11 métodos especializados para garantizar integridad de datos y reglas de negocio
- **Análisis Estadístico**: Métricas completas, tendencias y dashboard ejecutivo para toma de decisiones
- **Gestión de Relaciones**: Operaciones especializadas para manejo de proyectos asociados y transferencias
- **Monitoreo de Salud**: Verificación del estado y configuración de todos los módulos del sistema
- **API Asíncrona**: Operaciones no bloqueantes para mejor rendimiento en aplicaciones concurrentes
- **Búsqueda Flexible**: Soporte para paginación, ordenamiento y filtros múltiples

### Integración con Otros Módulos

- **Project**: Gestión de asignaciones y transferencias de proyectos entre clientes
- **Database**: Integración completa con modelos SQLAlchemy y operaciones transaccionales
- **Validation**: Sistema robusto de validación con esquemas Pydantic (ClientCreate, ClientUpdate)
- **Logging**: Registro estructurado de operaciones con Loguru para auditoría y debugging
- **Statistics**: Análisis de tendencias, métricas de creación y dashboard de gestión
- **Health**: Monitoreo continuo del estado de todos los módulos especializados

### Casos de Uso Principales

- **Gestión de Clientes**: Creación, actualización y seguimiento del ciclo de vida completo de clientes
- **Búsqueda y Filtrado**: Localización de clientes por múltiples criterios con búsqueda difusa
- **Análisis de Negocio**: Estadísticas, tendencias y métricas para reportes gerenciales
- **Validación de Datos**: Prevención de duplicados y verificación de integridad referencial
- **Gestión de Proyectos**: Asignación, transferencia y seguimiento de proyectos por cliente
- **Monitoreo del Sistema**: Verificación de salud y estado de los módulos de repositorio
- **Dashboard Ejecutivo**: Métricas consolidadas para toma de decisiones estratégicas
- **Auditoría y Compliance**: Registro detallado de operaciones para cumplimiento normativo