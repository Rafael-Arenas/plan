# Funciones Disponibles en Vacation Repository

**Fecha de actualización:** 2025-08-19

## Módulos y Funciones

### VacationRepository (vacation_repository.py)

#### Operaciones CRUD Básicas (4 funciones)
1. `create_vacation(vacation_data: Dict[str, Any]) -> Vacation` - Crea una nueva vacación con validación completa
2. `update_vacation(vacation_id: int, update_data: Dict[str, Any]) -> Vacation` - Actualiza una vacación existente
4. `delete_vacation(vacation_id: int) -> bool` - Elimina una vacación por ID

#### Consultas de Delegación - Query Builder (12 funciones)
5. `get_by_employee_id(employee_id: int) -> List[Vacation]` - Obtiene todas las vacaciones de un empleado
6. `get_by_status(status: VacationStatus) -> List[Vacation]` - Obtiene vacaciones por estado específico
7. `get_by_type(vacation_type: VacationType) -> List[Vacation]` - Obtiene vacaciones por tipo específico
8. `get_by_date_range(start_date: date, end_date: date) -> List[Vacation]` - Obtiene vacaciones en un rango de fechas
9. `get_by_employee_and_date_range(employee_id: int, start_date: date, end_date: date) -> List[Vacation]` - Obtiene vacaciones de un empleado en un rango de fechas específico
3. `get_vacation_by_id(vacation_id: int) -> Optional[Vacation]` - Obtiene una vacación por su ID con relaciones cargadas
10. `search_vacations(employee_id: Optional[int] = None, start_date: Optional[date] = None, end_date: Optional[date] = None, status: Optional[VacationStatus] = None, vacation_type: Optional[VacationType] = None, limit: int = 100, offset: int = 0) -> List[Vacation]` - Busca vacaciones con múltiples filtros
11. `get_employee_vacations(employee_id: int, year: Optional[int] = None) -> List[Vacation]` - Obtiene vacaciones de un empleado por año
12. `get_pending_approvals(limit: int = 50) -> List[Vacation]` - Obtiene todas las vacaciones pendientes de aprobación
13. `get_overlapping_vacations(start_date: date, end_date: date, employee_id: Optional[int] = None) -> List[Vacation]` - Obtiene vacaciones que se solapan con un período específico
14. `get_current_month_vacations() -> List[Vacation]` - Obtiene vacaciones del mes actual
15. `get_upcoming_vacations(days_ahead: int = 30) -> List[Vacation]` - Obtiene vacaciones próximas en los siguientes días
16. `get_with_relations(vacation_id: int) -> Optional[Vacation]` - Obtiene vacación con todas las relaciones cargadas

#### Consultas de Delegación - Estadísticas (6 funciones)
17. `get_vacation_trends(employee_id: int, months_back: int = 12) -> Dict[str, Any]` - Obtiene tendencias de vacaciones de un empleado
18. `get_employee_vacation_summary(employee_id: int, year: Optional[int] = None) -> Dict[str, Any]` - Obtiene resumen de vacaciones por empleado
19. `get_team_vacation_statistics(team_id: int, year: Optional[int] = None) -> Dict[str, Any]` - Obtiene estadísticas de vacaciones para un equipo
20. `get_vacation_balance_analysis(employee_ids: Optional[List[int]] = None, year: Optional[int] = None) -> List[Dict[str, Any]]` - Analiza balances de vacaciones de empleados
21. `get_vacation_patterns_analysis(start_date: date, end_date: date) -> Dict[str, Any]` - Analiza patrones de uso de vacaciones
22. `get_team_vacation_summary(employee_ids: List[int], start_date: date, end_date: date) -> List[Dict[str, Any]]` - Obtiene resumen de vacaciones de un equipo

#### Consultas de Delegación - Validaciones (2 funciones)
23. `validate_vacation_request(employee_id: int, vacation_type: VacationType, start_date: date, end_date: date, exclude_vacation_id: Optional[int] = None) -> Dict[str, Any]` - Valida una solicitud de vacación completa
24. `get_vacation_conflicts(employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]` - Obtiene información detallada sobre conflictos de vacaciones

#### Métodos de Gestión de Estado (3 funciones)
25. `approve_vacation(vacation_id: int, approved_by: str, notes: Optional[str] = None) -> Optional[Vacation]` - Aprueba una vacación específica
26. `reject_vacation(vacation_id: int, rejected_by: str, reason: Optional[str] = None) -> Optional[Vacation]` - Rechaza una vacación con razón opcional
27. `cancel_vacation(vacation_id: int, cancelled_by: int = None, reason: str = None) -> Vacation` - Cancela una vacación con razón opcional

#### Métodos de Compatibilidad (3 funciones)
28. `calculate_vacation_balance(employee_id: int, year: Optional[int] = None) -> Dict[str, Any]` - Calcula el balance de vacaciones de un empleado
29. `calculate_business_days(start_date: date, end_date: date) -> int` - Calcula días hábiles entre dos fechas
30. `format_vacation_date(vacation: Vacation) -> Dict[str, str]` - Formatea las fechas de una vacación para presentación

---

### VacationQueryBuilder (vacation_query_builder.py)

#### Consultas Básicas (5 funciones)
31. `get_by_employee(employee_id: int) -> List[Vacation]` - Obtiene todas las vacaciones de un empleado
32. `get_by_employee_and_date_range(employee_id: int, start_date: date, end_date: date) -> List[Vacation]` - Obtiene vacaciones de un empleado en un rango de fechas
33. `get_by_date_range(start_date: date, end_date: date) -> List[Vacation]` - Obtiene vacaciones en rango de fechas
34. `get_by_status(status: VacationStatus) -> List[Vacation]` - Obtiene vacaciones por estado
35. `get_by_type(vacation_type: VacationType) -> List[Vacation]` - Obtiene vacaciones por tipo

#### Consultas Especializadas (4 funciones)
36. `search_with_filters(filters: VacationSearchFilter) -> List[Vacation]` - Busca vacaciones aplicando múltiples filtros
37. `get_with_relations(vacation_id: int) -> Optional[Vacation]` - Obtiene vacación con relaciones cargadas
38. `get_pending_approvals(limit: int = 50) -> List[Vacation]` - Obtiene vacaciones pendientes de aprobación
39. `get_overlapping_vacations(employee_id: int, start_date: date, end_date: date, exclude_vacation_id: Optional[int] = None) -> List[Vacation]` - Busca vacaciones que se solapan con un período específico

---

### VacationValidator (vacation_validator.py)

#### Validación de Vacación (2 funciones)
40. `validate_create_data(data: Dict[str, Any]) -> None` - Valida los datos para crear una nueva vacación
41. `validate_update_data(data: Dict[str, Any]) -> None` - Valida los datos para actualizar una vacación

#### Validación de Solicitudes (2 funciones)
42. `validate_vacation_request(employee_id: int, start_date: date, end_date: date, vacation_type: VacationType, exclude_vacation_id: Optional[int] = None) -> Dict[str, Any]` - Valida una solicitud de vacación completa
43. `validate_vacation_id(vacation_id: int) -> None` - Valida el ID de una vacación

#### Validaciones Privadas (8 funciones)
44. `_validate_required_fields_for_create(data: Dict[str, Any]) -> None` - **[PRIVADA]** Valida campos requeridos para crear vacación
45. `_validate_employee_id(employee_id: int) -> None` - **[PRIVADA]** Valida el ID del empleado
46. `_validate_vacation_type(vacation_type) -> None` - **[PRIVADA]** Valida el tipo de vacación
47. `_validate_start_date(start_date) -> None` - **[PRIVADA]** Valida la fecha de inicio de la vacación
48. `_validate_end_date(end_date) -> None` - **[PRIVADA]** Valida la fecha de fin de la vacación
49. `_validate_date_range(start_date: date, end_date: date) -> None` - **[PRIVADA]** Valida rango de fechas y duración máxima
50. `_validate_status(status) -> None` - **[PRIVADA]** Valida el estado de la vacación
51. `_validate_requested_date(requested_date) -> None` - **[PRIVADA]** Valida la fecha de solicitud de la vacación

---

### VacationRelationshipManager (vacation_relationship_manager.py)

#### Gestión de Relaciones (4 funciones)
52. `get_vacation_with_employee(vacation_id: int) -> Optional[Vacation]` - Obtiene vacación con información del empleado
53. `get_vacation_with_all_relations(vacation_id: int) -> Optional[Vacation]` - Obtiene vacación con todas las relaciones cargadas
54. `get_employee_vacations_with_details(employee_id: int, year: Optional[int] = None) -> List[Vacation]` - Obtiene vacaciones de empleado con detalles completos
55. `get_team_vacations_summary(team_id: int, start_date: date, end_date: date) -> Dict[str, Any]` - Genera resumen de vacaciones para un equipo

#### Validación de Existencia (2 funciones)
56. `validate_vacation_exists(vacation_id: int) -> Vacation` - Valida la existencia de una vacación por ID
57. `validate_employee_exists(employee_id: int) -> Employee` - Valida la existencia de un empleado por ID

#### Gestión de Conflictos (2 funciones)
58. `check_vacation_overlap(employee_id: int, start_date: date, end_date: date, exclude_vacation_id: Optional[int] = None) -> bool` - Verifica solapamiento de vacaciones
59. `get_vacation_conflicts(employee_id: int, start_date: date, end_date: date, exclude_vacation_id: Optional[int] = None) -> Dict[str, Any]` - Obtiene información detallada sobre conflictos de vacaciones

---

### VacationStatistics (vacation_statistics.py)

#### Estadísticas por Empleado (2 funciones)
60. `get_vacation_summary_by_employee(employee_id: int, year: int) -> Dict[str, Any]` - Obtiene resumen estadístico de vacaciones por empleado
61. `get_vacation_trends_by_employee(employee_id: int, months: int = 12) -> List[Dict[str, Any]]` - Obtiene tendencias de uso de vacaciones por empleado

#### Estadísticas por Equipo (2 funciones)
62. `get_team_vacation_statistics(employee_ids: List[int], year: int) -> Dict[str, Any]` - Obtiene estadísticas de vacaciones para un equipo
63. `get_team_vacation_summary(employee_ids: List[int], start_date: date, end_date: date) -> Dict[str, Any]` - Obtiene resumen de vacaciones para un equipo en un período específico

#### Análisis Avanzado (2 funciones)
64. `get_vacation_balance_analysis(employee_id: int, reference_date: Optional[date] = None) -> Dict[str, Any]` - Analiza balances de vacaciones de empleados
65. `get_vacation_patterns_analysis(employee_ids: Optional[List[int]] = None, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]` - Analiza patrones de uso de vacaciones en un período

---

**Total de funciones disponibles:** 65

**Distribución por módulos:**
- VacationRepository: 30 funciones
- VacationQueryBuilder: 9 funciones (5 básicas + 4 especializadas)
- VacationValidator: 12 funciones (2 vacación + 2 solicitudes + 8 privadas)
- VacationRelationshipManager: 8 funciones (4 relaciones + 2 validación + 2 conflictos)
- VacationStatistics: 6 funciones (2 empleado + 2 equipo + 2 análisis)

**Categorías principales:**
- **CRUD básico**: 4 funciones (crear, leer, actualizar, eliminar vacaciones)
- **Consultas especializadas**: 28 funciones (por empleado, estado, tipo, fechas y análisis)
- **Gestión de estado**: 3 funciones (aprobar, rechazar, cancelar)
- **Análisis y estadísticas**: 13 funciones (resúmenes, tendencias, balances y patrones)
- **Gestión de relaciones**: 8 funciones (relaciones, validaciones y conflictos)
- **Validación de datos**: 12 funciones (4 públicas + 8 privadas)

**Funcionalidades especiales:**
- **Gestión de estado de vacaciones**: 3 funciones para aprobar, rechazar y cancelar
- **Análisis de conflictos**: 2 funciones para detectar y gestionar solapamientos
- **Validaciones de negocio**: 12 funciones para garantizar integridad de datos
- **Estadísticas avanzadas**: 5 funciones para análisis de tendencias y patrones
- **Gestión de relaciones**: 8 funciones para manejo de entidades relacionadas

**Total de funciones documentadas**: 65