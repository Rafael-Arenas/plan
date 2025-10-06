# Métodos de Dominio de Proyecto

## Descripción General

Esta es una selección de métodos de dominio de proyecto derivados de las funcionalidades expuestas por el `ProjectRepositoryFacade`. Estos métodos proporcionan una capa de servicio fundamental para operaciones comunes relacionadas con la gestión de proyectos, siguiendo el patrón establecido en los servicios de dominio existentes.

El servicio de dominio de proyectos encapsula la lógica de negocio compleja, coordina operaciones entre múltiples repositorios y proporciona una interfaz unificada para la gestión completa del ciclo de vida de proyectos.

---

## Métodos Disponibles

### 1. Operaciones CRUD Principales (5 métodos)

1.  `create_project(project_data: ProjectCreateSchema) -> ProjectResponseSchema` - Crea un nuevo proyecto con validaciones de negocio.
2.  `get_project_by_id(project_id: int) -> Optional[ProjectResponseSchema]` - Obtiene un proyecto por su ID único.
3.  `update_project(project_id: int, project_data: ProjectUpdateSchema) -> Optional[ProjectResponseSchema]` - Actualiza un proyecto existente con validaciones.
4.  `delete_project(project_id: int) -> bool` - Elimina un proyecto después de validar dependencias.
5.  `archive_project(project_id: int) -> Optional[ProjectResponseSchema]` - Archiva un proyecto validando que puede ser archivado.

### 2. Operaciones CRUD Especializadas (4 métodos)

6.  `create_project_with_assignments(project_data: ProjectCreateSchema, assignments: List[ProjectAssignmentSchema]) -> ProjectResponseSchema` - Crea un proyecto con asignaciones iniciales de empleados.
7.  `bulk_create_projects(projects_data: List[ProjectCreateSchema]) -> List[ProjectResponseSchema]` - Crea múltiples proyectos en una sola operación transaccional.
8.  `duplicate_project(project_id: int, new_project_data: ProjectDuplicateSchema) -> ProjectResponseSchema` - Duplica un proyecto existente con nuevos datos.
9.  `restore_archived_project(project_id: int) -> Optional[ProjectResponseSchema]` - Restaura un proyecto archivado validando su estado.

### 3. Operaciones de Consulta Básica (6 métodos)

10. `get_project_by_reference(reference: str) -> Optional[ProjectResponseSchema]` - Obtiene un proyecto por su referencia única.
11. `get_project_by_trigram(trigram: str) -> Optional[ProjectResponseSchema]` - Obtiene un proyecto por su trigrama.
12. `search_projects_by_name(search_term: str) -> List[ProjectResponseSchema]` - Busca proyectos por nombre usando coincidencia parcial.
13. `get_projects_by_client(client_id: int) -> List[ProjectResponseSchema]` - Obtiene todos los proyectos de un cliente específico.
14. `get_projects_by_status(status: ProjectStatus) -> List[ProjectResponseSchema]` - Obtiene proyectos filtrados por estado.
15. `get_projects_by_priority(priority: ProjectPriority) -> List[ProjectResponseSchema]` - Obtiene proyectos filtrados por prioridad.

### 4. Operaciones de Búsqueda Avanzada (4 métodos)

16. `advanced_project_search(filters: ProjectAdvancedFilters) -> List[ProjectResponseSchema]` - Búsqueda avanzada con múltiples filtros complejos.
17. `search_projects_full_text(search_term: str, limit: Optional[int] = None) -> List[ProjectResponseSchema]` - Búsqueda de texto completo en nombre, referencia y descripción.
18. `get_overdue_projects(limit: Optional[int] = None) -> List[ProjectResponseSchema]` - Obtiene proyectos que están vencidos con análisis de impacto.
19. `get_active_projects_with_workload(limit: Optional[int] = None) -> List[ProjectWithWorkloadSchema]` - Obtiene proyectos activos con información de carga de trabajo.

### 5. Operaciones de Fechas y Planificación (5 métodos)

20. `get_projects_by_date_range(start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[ProjectResponseSchema]` - Obtiene proyectos en un rango de fechas específico.
21. `get_projects_starting_current_week() -> List[ProjectResponseSchema]` - Obtiene proyectos que inician en la semana actual.
22. `get_projects_ending_current_week() -> List[ProjectResponseSchema]` - Obtiene proyectos que terminan en la semana actual.
23. `get_projects_starting_current_month() -> List[ProjectResponseSchema]` - Obtiene proyectos que inician en el mes actual.
24. `get_projects_starting_business_days_only(start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[ProjectResponseSchema]` - Obtiene proyectos que inician en días hábiles únicamente.

### 6. Operaciones de Relaciones y Detalles (3 métodos)

25. `get_project_with_client_details(project_id: int) -> Optional[ProjectWithClientSchema]` - Obtiene un proyecto con información completa del cliente.
26. `get_project_with_assignments(project_id: int) -> Optional[ProjectWithAssignmentsSchema]` - Obtiene un proyecto con todas sus asignaciones de empleados.
27. `get_project_with_full_details(project_id: int) -> Optional[ProjectFullDetailsSchema]` - Obtiene un proyecto con todos sus detalles relacionados (cliente, asignaciones, workloads).

### 7. Operaciones de Estadísticas Básicas (4 métodos)

28. `get_project_status_summary() -> Dict[str, int]` - Calcula un resumen del número de proyectos por estado.
29. `get_overdue_projects_summary() -> List[Dict[str, Any]]` - Obtiene un resumen detallado de proyectos vencidos con métricas.
30. `get_project_performance_stats() -> Dict[str, Any]` - Obtiene estadísticas de rendimiento general de proyectos.
31. `get_projects_by_status_summary(status: str) -> Dict[str, Any]` - Obtiene un resumen de proyectos por estado específico con análisis.

### 8. Operaciones de Estadísticas Avanzadas (4 métodos)

32. `get_project_workload_statistics() -> Dict[str, Any]` - Obtiene estadísticas detalladas de carga de trabajo de proyectos.
33. `get_project_duration_analytics() -> Dict[str, Any]` - Obtiene análisis de duración de proyectos con tendencias.
34. `get_monthly_project_analytics(year: int, month: int) -> Dict[str, Any]` - Obtiene análisis completo de proyectos por mes específico.
35. `get_client_project_analytics(client_id: int) -> Dict[str, Any]` - Obtiene análisis detallado de proyectos por cliente.

### 9. Operaciones de Validación (3 métodos)

36. `validate_project_business_rules(project_data: Dict[str, Any]) -> ValidationResult` - Valida las reglas de negocio para datos de proyecto.
37. `validate_project_reference_uniqueness(reference: str, exclude_id: Optional[int] = None) -> bool` - Valida la unicidad de la referencia del proyecto.
38. `validate_project_trigram_uniqueness(trigram: str, exclude_id: Optional[int] = None) -> bool` - Valida la unicidad del trigrama del proyecto.

### 10. Operaciones de Diagnóstico y Salud (2 métodos)

39. `check_service_health() -> Dict[str, Any]` - Verifica el estado de salud del servicio de proyectos y sus dependencias.
40. `get_service_configuration_info() -> Dict[str, Any]` - Obtiene información de configuración y estado del servicio.

---

## Resumen por Categorías

| Categoría | Cantidad | Descripción |
|-----------|----------|-------------|
| **CRUD Principales** | 5 | Operaciones básicas de creación, lectura, actualización y eliminación |
| **CRUD Especializadas** | 4 | Operaciones CRUD con lógica de negocio avanzada |
| **Consulta Básica** | 6 | Búsquedas y filtros simples por criterios específicos |
| **Búsqueda Avanzada** | 4 | Consultas complejas con múltiples criterios y análisis |
| **Fechas y Planificación** | 5 | Gestión de períodos, fechas y planificación temporal |
| **Relaciones y Detalles** | 3 | Manejo de relaciones con clientes, empleados y asignaciones |
| **Estadísticas Básicas** | 4 | Métricas y resúmenes estadísticos fundamentales |
| **Estadísticas Avanzadas** | 4 | Análisis avanzados y tendencias de datos |
| **Validación** | 3 | Verificación de reglas de negocio e integridad |
| **Diagnóstico** | 2 | Monitoreo de salud y configuración del servicio |
| **Total** | **40** | **Métodos propuestos** |

---

## Características Técnicas

### Schemas Utilizados
- **ProjectCreateSchema**: Esquema para creación de proyectos
- **ProjectUpdateSchema**: Esquema para actualización de proyectos
- **ProjectResponseSchema**: Esquema para respuestas de proyectos
- **ProjectDuplicateSchema**: Esquema para duplicación de proyectos
- **ProjectAdvancedFilters**: Esquema para filtros avanzados de búsqueda
- **ProjectWithClientSchema**: Esquema para proyectos con información de cliente
- **ProjectWithAssignmentsSchema**: Esquema para proyectos con asignaciones
- **ProjectFullDetailsSchema**: Esquema para proyectos con detalles completos
- **ProjectWithWorkloadSchema**: Esquema para proyectos con información de carga de trabajo
- **ProjectAssignmentSchema**: Esquema para asignaciones de proyectos
- **ValidationResult**: Esquema para resultados de validación
- **ProjectStatus**: Enum para estados de proyectos
- **ProjectPriority**: Enum para prioridades de proyectos

### Patrones Implementados
- **Domain Service Pattern**: Encapsula lógica de negocio compleja
- **Facade Pattern**: Unifica acceso a múltiples módulos especializados
- **Repository Pattern**: Abstrae el acceso a datos
- **Async/Await**: Operaciones asíncronas optimizadas
- **Validation Pattern**: Validaciones robustas de reglas de negocio
- **Analytics Pattern**: Análisis y métricas avanzadas

### Integración con Otros Servicios
- **ClientDomainService**: Para validación y análisis de relaciones cliente-proyecto
- **EmployeeDomainService**: Para gestión de asignaciones y recursos
- **PlanningDomainService**: Para coordinación de planificación temporal
- **ResourceManagementService**: Para optimización de recursos y cargas de trabajo
- **AnalyticsDomainService**: Para métricas avanzadas y reportes gerenciales

### Casos de Uso Principales
- **Gestión Completa de Proyectos**: Ciclo de vida completo desde creación hasta archivo
- **Planificación de Recursos**: Asignación optimizada de empleados y equipos
- **Seguimiento de Rendimiento**: Análisis de duración, productividad y cumplimiento
- **Gestión de Clientes**: Seguimiento de proyectos por cliente con análisis de rentabilidad
- **Reportes Gerenciales**: Estadísticas y métricas para toma de decisiones estratégicas
- **Validación de Integridad**: Prevención de duplicados y verificación de reglas de negocio
- **Análisis Predictivo**: Tendencias y proyecciones basadas en datos históricos