# Funciones Disponibles en VacationRepositoryFacade

**Fecha de actualización:** 2025-01-24

## Métodos del VacationRepositoryFacade

El `VacationRepositoryFacade` es la interfaz principal para todas las operaciones relacionadas con la gestión de vacaciones de empleados. Proporciona acceso unificado a operaciones CRUD, consultas, validaciones, relaciones y estadísticas.

### OPERACIONES CRUD (5 métodos)

1. `create_vacation(vacation_data: Dict[str, Any]) -> Vacation` - Crea una nueva vacación
2. `update_vacation(vacation_id: int, vacation_data: Dict[str, Any]) -> Vacation` - Actualiza una vacación existente
3. `delete_vacation(vacation_id: int) -> bool` - Elimina una vacación
4. `get_vacation_by_id(vacation_id: int) -> Optional[Vacation]` - Obtiene una vacación por su ID
5. `get_by_unique_field(field_name: str, field_value: Any) -> Optional[Vacation]` - Obtiene una vacación por un campo único

### OPERACIONES DE CONSULTA (7 métodos)

6. `get_vacations_by_employee(employee_id: int, active_only: bool = True) -> List[Vacation]` - Obtiene vacaciones por empleado
7. `get_vacations_by_date_range(start_date: date, end_date: date, employee_id: Optional[int] = None) -> List[Vacation]` - Obtiene vacaciones por rango de fechas
8. `get_vacations_by_status(status: str, employee_id: Optional[int] = None) -> List[Vacation]` - Obtiene vacaciones por estado
9. `get_vacations_by_type(vacation_type: str, employee_id: Optional[int] = None) -> List[Vacation]` - Obtiene vacaciones por tipo
10. `search_vacations_by_criteria(criteria: Dict[str, Any], limit: Optional[int] = None, offset: Optional[int] = None) -> List[Vacation]` - Busca vacaciones por criterios específicos
11. `get_vacations_with_pagination(page: int = 1, page_size: int = 20, filters: Optional[Dict[str, Any]] = None) -> Tuple[List[Vacation], int]` - Obtiene vacaciones con paginación
12. `count_vacations(filters: Optional[Dict[str, Any]] = None) -> int` - Cuenta vacaciones con filtros opcionales

### OPERACIONES DE VALIDACIÓN (6 métodos)

13. `validate_vacation_data(vacation_data: Dict[str, Any]) -> Dict[str, Any]` - Valida datos de vacación
14. `validate_vacation_request(employee_id: int, start_date: date, end_date: date, vacation_type: str) -> Dict[str, Any]` - Valida una solicitud de vacación
15. `validate_vacation_id(vacation_id: int) -> Dict[str, Any]` - Valida que un ID de vacación existe
16. `check_vacation_conflicts(employee_id: int, start_date: date, end_date: date, exclude_vacation_id: Optional[int] = None) -> Dict[str, Any]` - Verifica conflictos de vacaciones
17. `validate_business_rules(operation: str, data: Dict[str, Any]) -> Dict[str, Any]` - Valida reglas de negocio
18. `validate_data_consistency() -> Dict[str, Any]` - Valida consistencia de datos

### OPERACIONES DE RELACIONES (5 métodos)

19. `get_vacation_with_employee_details(vacation_id: int) -> Optional[Dict[str, Any]]` - Obtiene vacación con detalles del empleado
20. `validate_employee_exists(employee_id: int) -> bool` - Valida que un empleado existe
21. `get_overlapping_vacations(employee_id: int, start_date: date, end_date: date, exclude_vacation_id: Optional[int] = None) -> List[Vacation]` - Obtiene vacaciones que se solapan
22. `get_vacations_with_relationships(vacation_ids: Optional[List[int]] = None, include_employee: bool = True) -> List[Dict[str, Any]]` - Obtiene vacaciones con relaciones cargadas
23. `get_employee_vacation_summary(employee_id: int, year: Optional[int] = None) -> Dict[str, Any]` - Obtiene resumen de vacaciones del empleado

### OPERACIONES DE ESTADÍSTICAS (5 métodos)

24. `get_employee_vacation_statistics(employee_id: int, year: Optional[int] = None) -> Dict[str, Any]` - Obtiene estadísticas de vacaciones del empleado
25. `get_team_vacation_balance(team_id: int, year: Optional[int] = None) -> Dict[str, Any]` - Obtiene balance de vacaciones del equipo
26. `get_vacation_trends(start_date: date, end_date: date, granularity: str = "monthly") -> List[Dict[str, Any]]` - Obtiene tendencias de vacaciones
27. `get_vacation_patterns_analysis(employee_id: Optional[int] = None, team_id: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]` - Obtiene análisis de patrones de vacaciones
28. `generate_vacation_summary_report(year: Optional[int] = None, include_projections: bool = False) -> Dict[str, Any]` - Genera reporte resumen de vacaciones

### OPERACIONES COMPUESTAS Y AVANZADAS (3 métodos)

29. `create_vacation_with_validation(vacation_data: Dict[str, Any]) -> Dict[str, Any]` - Crea vacación con validación completa
30. `get_vacation_dashboard_data(employee_id: Optional[int] = None, team_id: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]` - Obtiene datos completos para dashboard de vacaciones
31. `bulk_vacation_operation(operation: str, vacation_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]` - Realiza operaciones en lote sobre vacaciones

---

## Resumen de Funcionalidades

**Total de métodos públicos:** 31

**Distribución por categorías:**
- **CRUD básico**: 5 métodos (crear, actualizar, eliminar, obtener por ID y campo único)
- **Consultas**: 7 métodos (búsquedas por empleado, fechas, estado, tipo, con paginación)
- **Validaciones**: 6 métodos (validación de datos, solicitudes, conflictos y reglas de negocio)
- **Relaciones**: 5 métodos (gestión de relaciones con empleados y solapamientos)
- **Estadísticas**: 5 métodos (análisis, tendencias, patrones y reportes)
- **Operaciones compuestas**: 3 métodos (operaciones complejas y masivas)

**Características principales:**
- **Interfaz unificada**: Acceso centralizado a todas las operaciones de vacaciones
- **Validación integrada**: Métodos con validación automática de datos y reglas de negocio
- **Gestión de conflictos**: Detección automática de solapamientos y conflictos de fechas
- **Análisis estadístico**: Conjunto completo de métodos para análisis y reportes
- **Soporte para paginación**: Múltiples métodos con soporte para paginación y filtros
- **Dashboard integrado**: Métodos especializados para interfaces de usuario
- **Operaciones masivas**: Soporte para procesamiento en lote
- **Gestión de relaciones**: Manejo completo de relaciones con empleados

**Integración con módulos:**
- **VacationCrudModule**: Operaciones CRUD básicas
- **VacationQueryModule**: Consultas y búsquedas avanzadas
- **VacationValidationModule**: Validación de datos y reglas de negocio
- **VacationRelationshipModule**: Gestión de relaciones con otras entidades
- **VacationStatisticsModule**: Análisis estadístico y métricas

**Casos de uso principales:**
- Gestión completa del ciclo de vida de vacaciones
- Planificación y aprobación de solicitudes de vacaciones
- Prevención de conflictos y solapamientos
- Seguimiento de balances y días disponibles
- Análisis de patrones de uso de vacaciones
- Generación de reportes y estadísticas
- Operaciones masivas y procesamiento en lote
- Integración con interfaces de usuario (dashboards)

**Validaciones específicas:**
- **Conflictos de fechas**: Prevención de vacaciones solapadas para el mismo empleado
- **Reglas de negocio**: Validación de políticas específicas de la empresa
- **Consistencia de datos**: Verificación de integridad referencial
- **Existencia de empleados**: Validación de empleados relacionados
- **Solicitudes válidas**: Verificación de datos de solicitud completos y correctos

**Capacidades de análisis:**
- **Estadísticas por empleado**: Métricas individuales de uso de vacaciones
- **Balance por equipo**: Análisis de días disponibles y utilizados por equipo
- **Tendencias temporales**: Evolución del uso de vacaciones en el tiempo
- **Análisis de patrones**: Identificación de patrones de comportamiento
- **Reportes de resumen**: Informes completos con proyecciones opcionales

**Tipos de vacaciones soportados:**
- **Vacaciones anuales**: Días de vacaciones regulares
- **Días personales**: Días libres por asuntos personales
- **Licencias médicas**: Ausencias por motivos de salud
- **Permisos especiales**: Licencias por eventos específicos
- **Días compensatorios**: Días libres por trabajo extra

**Funcionalidades de dashboard:**
- **Resumen ejecutivo**: Vista general del estado de vacaciones
- **Estadísticas detalladas**: Métricas específicas por empleado o equipo
- **Tendencias visuales**: Datos preparados para gráficos y visualizaciones
- **Patrones de uso**: Análisis de comportamiento y preferencias
- **Vacaciones recientes**: Historial de actividad reciente

**Operaciones en lote:**
- **Creación masiva**: Procesamiento de múltiples solicitudes simultáneamente
- **Actualización en lote**: Modificación de múltiples vacaciones
- **Eliminación masiva**: Cancelación de múltiples vacaciones
- **Validación individual**: Cada operación se valida independientemente
- **Manejo de errores**: Reporte detallado de éxitos y fallos por elemento