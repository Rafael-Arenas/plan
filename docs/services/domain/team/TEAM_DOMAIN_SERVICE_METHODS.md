# Métodos de Dominio de Equipos (Team)

## Descripción General

Esta es una selección de métodos de dominio de equipos derivados de las funcionalidades expuestas por el `TeamRepositoryFacade`. Estos métodos proporcionan una capa de servicio fundamental para operaciones complejas relacionadas con la gestión de equipos y membresías, siguiendo el patrón establecido en los servicios de dominio existentes.

El servicio de dominio de equipos encapsula la lógica de negocio compleja, coordina operaciones entre múltiples repositorios (empleados, proyectos, equipos, membresías) y proporciona una interfaz unificada para la gestión completa del ciclo de vida de equipos, incluyendo validaciones de capacidad, gestión de roles y análisis de productividad colaborativa.

---

## Métodos Disponibles

### 1. Operaciones CRUD Principales (6 métodos)

1.  `create_team(team_data: TeamCreateSchema, validate_business_rules: bool = True) -> TeamSchema` - Crea un nuevo equipo con validación completa de datos de negocio y verificación de capacidad organizacional.
2.  `get_team_by_id(team_id: int, include_members: bool = False) -> Optional[TeamSchema]` - Obtiene un equipo específico por su identificador único con opción de incluir información detallada de miembros.
3.  `update_team(team_id: int, update_data: TeamUpdateSchema, validate_changes: bool = True) -> TeamSchema` - Actualiza la información de un equipo existente con validación de cambios y verificación de impacto.
4.  `delete_team(team_id: int, force_delete: bool = False) -> bool` - Elimina un equipo del sistema después de validar dependencias y transferir responsabilidades activas.
5.  `get_all_teams(page: int = 1, page_size: int = 50, include_inactive: bool = False) -> PaginatedResponse[TeamSchema]` - Obtiene todos los equipos del sistema con paginación y filtros de estado.
6.  `bulk_create_teams(teams_data: List[TeamCreateSchema], validate_all: bool = True) -> List[TeamSchema]` - Crea múltiples equipos en una operación transaccional con validación masiva.

### 2. Operaciones de Consulta por Criterios Básicos (4 métodos)

7.  `find_teams_by_name(name_pattern: str, exact_match: bool = False) -> List[TeamSchema]` - Busca equipos por nombre con coincidencia parcial o exacta y análisis de relevancia.
8.  `get_teams_by_status(status: TeamStatus, include_details: bool = False) -> List[TeamSchema]` - Obtiene equipos filtrados por su estado actual con información adicional opcional.
9.  `get_teams_by_department(department_id: int, include_members: bool = False) -> List[TeamSchema]` - Obtiene equipos asociados a un departamento específico con detalles de membresía.
10. `search_teams_advanced(search_criteria: TeamSearchCriteria, sort_by: str = "name", sort_order: str = "asc") -> List[TeamSchema]` - Búsqueda avanzada con múltiples criterios complejos y ordenamiento personalizado.

### 3. Operaciones de Consulta por Relaciones (4 métodos)

11. `find_teams_by_leader(leader_id: int, include_team_details: bool = True) -> List[TeamSchema]` - Encuentra equipos liderados por un empleado específico con análisis de liderazgo.
12. `find_teams_by_project(project_id: int, active_only: bool = True) -> List[TeamSchema]` - Encuentra equipos asignados a un proyecto específico con filtros de estado.
13. `find_teams_by_skill_set(required_skills: List[str], match_all: bool = False) -> List[TeamSchema]` - Encuentra equipos que poseen un conjunto específico de habilidades con análisis de competencias.
14. `find_teams_by_date_range(start_date: pendulum.DateTime, end_date: pendulum.DateTime, include_inactive: bool = False) -> List[TeamSchema]` - Encuentra equipos creados en un rango de fechas específico con filtros temporales.

### 4. Operaciones de Gestión de Membresías (4 métodos)

15. `add_team_member(team_id: int, employee_id: int, role: TeamRole, validate_capacity: bool = True) -> TeamMembershipSchema` - Agrega un nuevo miembro a un equipo con validación de roles y capacidad organizacional.
16. `remove_team_member(team_id: int, employee_id: int, transfer_responsibilities: bool = True) -> bool` - Remueve un miembro de un equipo con validación de dependencias y transferencia de responsabilidades.
17. `update_member_role(team_id: int, employee_id: int, new_role: TeamRole, validate_permissions: bool = True) -> TeamMembershipSchema` - Actualiza el rol de un miembro dentro del equipo con verificación de permisos.
18. `get_team_members(team_id: int, active_only: bool = True, include_employee_details: bool = False) -> List[TeamMembershipSchema]` - Obtiene todos los miembros de un equipo con sus roles y detalles opcionales.

### 5. Operaciones de Estadísticas Básicas (4 métodos)

19. `get_team_member_count(team_id: int, active_only: bool = True) -> int` - Obtiene el número total de miembros de un equipo con filtros de estado.
20. `get_teams_count_by_status(include_details: bool = False) -> Dict[TeamStatus, int]` - Obtiene el conteo de equipos agrupados por estado con información adicional.
21. `get_average_team_size(active_teams_only: bool = True, exclude_empty: bool = True) -> float` - Calcula el tamaño promedio de los equipos en el sistema con filtros de análisis.
22. `get_team_creation_trends(period: str = "month", months_back: int = 12) -> List[TeamCreationTrend]` - Obtiene tendencias de creación de equipos por período con análisis temporal.

### 6. Operaciones de Análisis de Productividad (4 métodos)

23. `get_team_performance_metrics(team_id: int, metric_types: List[str], date_range: Optional[DateRange] = None) -> TeamPerformanceMetrics` - Calcula métricas avanzadas de rendimiento de un equipo específico con análisis multidimensional.
24. `get_teams_productivity_analysis(analysis_period: str = "quarter", include_comparisons: bool = True) -> ProductivityAnalysis` - Analiza la productividad de todos los equipos con comparaciones y benchmarking.
25. `get_team_collaboration_metrics(team_ids: Optional[List[int]] = None, collaboration_types: List[str]) -> CollaborationMetrics` - Obtiene métricas de colaboración entre equipos con análisis de sinergia.
26. `generate_teams_summary_report(report_format: str = "detailed", include_charts: bool = False, export_format: str = "json") -> TeamsSummaryReport` - Genera un reporte resumen completo de todos los equipos con visualizaciones opcionales.

### 7. Operaciones de Validación y Reglas de Negocio (2 métodos)

27. `validate_team_data(team_data: TeamSchema, validation_rules: List[str]) -> ValidationResult` - Valida la integridad y consistencia de los datos de un equipo con reglas personalizables.
28. `validate_team_business_rules(team_id: int, business_context: BusinessContext) -> BusinessRuleValidationResult` - Valida que un equipo cumple con las reglas de negocio específicas del contexto organizacional.

### 8. Operaciones de Fecha y Diagnóstico (2 métodos)

29. `get_teams_by_creation_date(creation_date: pendulum.DateTime, date_tolerance: int = 0) -> List[TeamSchema]` - Obtiene equipos filtrados por fecha de creación con tolerancia configurable.
30. `check_service_health() -> Dict[str, Any]` - Verifica el estado de salud del servicio de equipos y sus dependencias críticas.

---

## Resumen por Categorías

| Categoría | Cantidad | Descripción |
|-----------|----------|-------------|
| **CRUD Principales** | 6 | Operaciones básicas de creación, lectura, actualización y eliminación con validaciones |
| **Consulta por Criterios** | 4 | Búsquedas básicas y avanzadas con múltiples filtros y criterios de ordenamiento |
| **Consulta por Relaciones** | 4 | Búsquedas basadas en relaciones con empleados, proyectos y habilidades específicas |
| **Gestión de Membresías** | 4 | Administración completa de miembros del equipo con roles y responsabilidades |
| **Estadísticas Básicas** | 4 | Análisis cuantitativos de equipos, conteos y tendencias temporales |
| **Análisis de Productividad** | 4 | Métricas avanzadas de rendimiento, colaboración y reportes ejecutivos |
| **Validación y Reglas** | 2 | Verificación de integridad de datos y cumplimiento de reglas de negocio |
| **Fecha y Diagnóstico** | 2 | Filtros temporales y monitoreo de salud del servicio |
| **Total** | **30** | **Métodos propuestos** |

---

## Características Especiales del Dominio

### Gestión Avanzada de Membresías
- **Roles dinámicos**: Asignación y modificación de roles con validación de permisos
- **Capacidad organizacional**: Verificación automática de límites de equipo y carga de trabajo
- **Transferencia de responsabilidades**: Proceso automatizado para cambios de membresía

### Análisis de Productividad Colaborativa
- **Métricas de sinergia**: Cálculo de efectividad de colaboración entre miembros
- **Benchmarking de equipos**: Comparación de rendimiento entre equipos similares
- **Análisis predictivo**: Identificación de tendencias de productividad y áreas de mejora

### Validación de Reglas de Negocio
- **Contexto organizacional**: Aplicación de reglas específicas según estructura empresarial
- **Integridad referencial**: Verificación automática de consistencia de datos relacionados
- **Cumplimiento normativo**: Validación de políticas internas y regulaciones externas

### Gestión de Habilidades y Competencias
- **Mapeo de competencias**: Identificación automática de habilidades del equipo
- **Análisis de gaps**: Detección de brechas de habilidades y recomendaciones
- **Optimización de asignaciones**: Sugerencias para formación de equipos óptimos

### Integración Multi-Repositorio
- **Sincronización de empleados**: Coordinación automática con repositorio de empleados
- **Vinculación de proyectos**: Integración seamless con gestión de proyectos
- **Consistencia de datos**: Mantenimiento automático de integridad referencial

### Análisis Temporal y Tendencias
- **Evolución de equipos**: Seguimiento de cambios organizacionales a lo largo del tiempo
- **Patrones estacionales**: Identificación de tendencias cíclicas en formación de equipos
- **Predicción de necesidades**: Análisis predictivo para planificación de recursos humanos

### Reportes Ejecutivos y Visualización
- **Dashboards interactivos**: Generación de reportes visuales para toma de decisiones
- **Exportación múltiple**: Soporte para diversos formatos de exportación (JSON, Excel, PDF)
- **Alertas automáticas**: Notificaciones proactivas sobre cambios críticos en equipos

### Seguridad y Auditoría
- **Trazabilidad completa**: Registro detallado de todos los cambios en equipos y membresías
- **Control de acceso**: Verificación de permisos para operaciones sensibles
- **Auditoría de cumplimiento**: Logs estructurados para auditorías internas y externas

### Performance y Escalabilidad
- **Operaciones en lote**: Procesamiento eficiente de múltiples equipos simultáneamente
- **Cache inteligente**: Optimización de consultas frecuentes con invalidación automática
- **Consultas asíncronas**: Operaciones no bloqueantes para mejor experiencia de usuario

### Integración con Sistemas Externos
- **APIs RESTful**: Interfaces estándar para integración con sistemas de terceros
- **Webhooks**: Notificaciones automáticas de cambios para sistemas dependientes
- **Sincronización bidireccional**: Capacidad de importar y exportar datos de equipos