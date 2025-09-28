# Funciones Disponibles en ProjectRepositoryFacade

**Última actualización:** Enero 2025

## Descripción General

`ProjectRepositoryFacade` es la clase principal que proporciona una interfaz unificada para todas las operaciones relacionadas con proyectos en el sistema. Esta fachada encapsula la lógica de acceso a datos y coordina las operaciones entre diferentes módulos especializados, ofreciendo una API coherente y fácil de usar para la gestión completa de proyectos.

---

## Métodos Disponibles

### 1. Operaciones CRUD (4 métodos)

1. `create_project(project_data: Dict[str, Any]) -> Project` - Crea un nuevo proyecto después de validar los datos de entrada
2. `update_project(project_id: int, updated_data: Dict[str, Any]) -> Optional[Project]` - Actualiza un proyecto existente después de validar los datos
3. `delete_project(project_id: int) -> bool` - Elimina un proyecto por su ID
4. `archive_project(project_id: int) -> Optional[Project]` - Archiva un proyecto después de validar que puede ser archivado

### 2. Operaciones de Consulta (19 métodos)

5. `search_projects(search_term: str, limit: Optional[int] = None) -> List[Project]` - Busca proyectos por término de búsqueda en nombre, referencia y descripción
6. `get_overdue_projects(limit: Optional[int] = None) -> List[Project]` - Obtiene proyectos que están vencidos
7. `get_active_projects(limit: Optional[int] = None) -> List[Project]` - Obtiene proyectos activos
8. `filter_by_date_range(start_date: date, end_date: date, limit: Optional[int] = None) -> List[Project]` - Filtra proyectos por rango de fechas
9. `get_by_id(project_id: int) -> Optional[Project]` - Obtiene un proyecto por su ID único
10. `get_by_reference(reference: str) -> Optional[Project]` - Obtiene un proyecto por su referencia
11. `get_by_trigram(trigram: str) -> Optional[Project]` - Obtiene un proyecto por su trigrama
12. `search_by_name(search_term: str) -> List[Project]` - Busca proyectos por nombre
13. `get_by_client(client_id: int) -> List[Project]` - Obtiene proyectos por cliente
14. `get_by_status(status: ProjectStatus) -> List[Project]` - Obtiene proyectos por estado
15. `get_by_priority(priority: ProjectPriority) -> List[Project]` - Obtiene proyectos por prioridad
16. `get_by_date_range(start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Project]` - Obtiene proyectos en un rango de fechas
17. `get_projects_starting_current_week(**kwargs) -> List[Project]` - Obtiene proyectos que inician en la semana actual
18. `get_projects_ending_current_week(**kwargs) -> List[Project]` - Obtiene proyectos que terminan en la semana actual
19. `get_projects_starting_current_month(**kwargs) -> List[Project]` - Obtiene proyectos que inician en el mes actual
20. `get_projects_starting_business_days_only(start_date: Optional[date] = None, end_date: Optional[date] = None, **kwargs) -> List[Project]` - Obtiene proyectos que inician en días hábiles
21. `get_with_client(project_id: int) -> Optional[Project]` - Obtiene un proyecto con su cliente
22. `get_with_assignments(project_id: int) -> Optional[Project]` - Obtiene un proyecto con sus asignaciones
23. `get_with_full_details(project_id: int) -> Optional[Project]` - Obtiene un proyecto con todos sus detalles

### 3. Operaciones de Estadísticas (9 métodos)

24. `get_status_summary() -> Dict[str, int]` - Calcula un resumen del número de proyectos por estado
25. `get_overdue_projects_summary() -> List[Dict[str, Any]]` - Obtiene un resumen de proyectos vencidos
26. `get_project_performance_stats() -> Dict[str, Any]` - Obtiene estadísticas de rendimiento de proyectos
27. `get_projects_by_status_summary(status: str) -> Dict[str, Any]` - Obtiene un resumen de proyectos por estado específico
28. `get_project_workload_stats() -> Dict[str, Any]` - Obtiene estadísticas de carga de trabajo de proyectos
29. `get_project_duration_stats() -> Dict[str, Any]` - Obtiene estadísticas de duración de proyectos
30. `get_monthly_project_stats(year: int, month: int) -> Dict[str, Any]` - Obtiene estadísticas de proyectos por mes
31. `get_client_project_stats(client_id: int) -> Dict[str, Any]` - Obtiene estadísticas de proyectos por cliente
32. `get_overdue_projects_stats() -> Dict[str, Any]` - Obtiene estadísticas detalladas de proyectos vencidos

### 4. Operaciones de Validación (4 métodos)

33. `validate_project_creation(data: Dict[str, Any]) -> None` - Valida los datos para la creación de un nuevo proyecto
34. `validate_project_update(project_id: int, data: Dict[str, Any]) -> None` - Valida los datos para la actualización de un proyecto
35. `reference_exists(reference: str, exclude_id: Optional[int] = None) -> bool` - Verifica si una referencia de proyecto existe
36. `trigram_exists(trigram: str, exclude_id: Optional[int] = None) -> bool` - Verifica si un trigrama de proyecto existe

---

## Resumen de Funcionalidades

### Total de Métodos Públicos: 36

**Distribución por Categorías:**
- Operaciones CRUD: 4 métodos (11%)
- Operaciones de Consulta: 19 métodos (53%)
- Operaciones de Estadísticas: 9 métodos (25%)
- Operaciones de Validación: 4 métodos (11%)

### Características Principales

- **Gestión Completa de Proyectos**: CRUD completo con validaciones robustas
- **Consultas Avanzadas**: Búsquedas por múltiples criterios de filtrado
- **Análisis Estadístico**: Métricas de rendimiento, duración y carga de trabajo
- **Validación Robusta**: Verificación de integridad de datos y reglas de negocio
- **Gestión de Relaciones**: Manejo integral de asignaciones con clientes y empleados

### Integración con Otros Módulos

- **Client**: Gestión de proyectos por cliente y validación de relaciones
- **Employee**: Asignación y seguimiento de empleados en proyectos
- **Schedule**: Integración con horarios para seguimiento de tiempo
- **Team**: Gestión de proyectos por equipo y asignaciones grupales

### Casos de Uso Principales

- **Gestión de Proyectos**: Creación, actualización y seguimiento del ciclo de vida completo
- **Planificación de Recursos**: Asignación y gestión de empleados y equipos
- **Seguimiento de Rendimiento**: Análisis de duración, carga de trabajo y productividad
- **Gestión de Clientes**: Seguimiento de proyectos por cliente específico
- **Reportes Gerenciales**: Estadísticas y métricas para toma de decisiones
- **Validación de Datos**: Prevención de duplicados y verificación de integridad