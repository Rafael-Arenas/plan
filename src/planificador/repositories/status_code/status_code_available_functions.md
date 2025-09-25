# Funciones Disponibles en StatusCodeRepositoryFacade

**Fecha de actualización:** 2025-01-24

## Métodos del StatusCodeRepositoryFacade

El `StatusCodeRepositoryFacade` es la interfaz principal para todas las operaciones relacionadas con códigos de estado. Proporciona acceso unificado a operaciones CRUD, consultas, validaciones y estadísticas.

### OPERACIONES CRUD (5 métodos)

1. `create_status_code(status_code_data: Dict[str, Any]) -> StatusCode` - Crea un nuevo código de estado
2. `get_status_code_by_id(status_code_id: int) -> Optional[StatusCode]` - Obtiene un código de estado por su ID
3. `get_all_status_codes() -> List[StatusCode]` - Obtiene todos los códigos de estado
4. `update_status_code(status_code_id: int, status_code_data: Dict[str, Any]) -> StatusCode` - Actualiza un código de estado existente
5. `delete_status_code(status_code_id: int) -> bool` - Elimina un código de estado

### OPERACIONES DE CONSULTA (10 métodos)

6. `find_by_code(code: str) -> Optional[StatusCode]` - Busca un código de estado por su código único
7. `find_by_name(name: str) -> Optional[StatusCode]` - Busca un código de estado por su nombre
8. `find_by_text_search(search_text: str) -> List[StatusCode]` - Busca códigos de estado por texto en nombre o descripción
9. `find_active_status_codes() -> List[StatusCode]` - Obtiene todos los códigos de estado activos
10. `find_inactive_status_codes() -> List[StatusCode]` - Obtiene todos los códigos de estado inactivos
11. `find_default_status_codes() -> List[StatusCode]` - Obtiene códigos de estado marcados como predeterminados
12. `find_by_display_order_range(min_order: int, max_order: int) -> List[StatusCode]` - Busca códigos por rango de orden de visualización
13. `find_with_advanced_filters(filters: Dict[str, Any]) -> List[StatusCode]` - Busca códigos con filtros avanzados
14. `get_status_codes_paginated(page: int = 1, page_size: int = 20, filters: Optional[Dict[str, Any]] = None) -> Tuple[List[StatusCode], int]` - Obtiene códigos de estado con paginación
15. `get_ordered_status_codes(order_by: str = "display_order", ascending: bool = True) -> List[StatusCode]` - Obtiene códigos ordenados por criterio específico

### OPERACIONES DE VALIDACIÓN (5 métodos)

16. `validate_unique_code(code: str, exclude_id: Optional[int] = None) -> bool` - Valida que el código sea único
17. `validate_unique_name(name: str, exclude_id: Optional[int] = None) -> bool` - Valida que el nombre sea único
18. `validate_status_code_data(status_code_data: Dict[str, Any]) -> Dict[str, Any]` - Valida datos completos de código de estado
19. `validate_display_order_conflicts(display_order: int, exclude_id: Optional[int] = None) -> bool` - Valida conflictos en orden de visualización
20. `validate_default_status_rules(is_default: bool, exclude_id: Optional[int] = None) -> Dict[str, Any]` - Valida reglas de códigos predeterminados

### OPERACIONES DE ESTADÍSTICAS (6 métodos)

21. `get_status_code_statistics() -> Dict[str, Any]` - Obtiene estadísticas generales de códigos de estado
22. `get_status_distribution_analysis() -> Dict[str, Any]` - Obtiene análisis de distribución de estados
23. `get_display_order_metrics() -> Dict[str, Any]` - Obtiene métricas de orden de visualización
24. `get_usage_performance_metrics() -> Dict[str, Any]` - Obtiene métricas de rendimiento y uso
25. `get_data_integrity_report() -> Dict[str, Any]` - Genera reporte de integridad de datos
26. `get_status_code_health_check() -> Dict[str, Any]` - Realiza verificación de salud del sistema

### OPERACIONES UTILITARIAS (1 método)

27. `health_check() -> Dict[str, Any]` - Verifica el estado de salud del repositorio

### MÉTODOS HEREDADOS DEL FACADE BASE (5 métodos)

28. `get_all(skip: int = 0, limit: int = 100) -> List[StatusCode]` - Obtiene todos los códigos con paginación
29. `exists_by_id(status_code_id: int) -> bool` - Verifica si un código existe por su ID
30. `count_all(filters: Optional[Dict[str, Any]] = None) -> int` - Cuenta todos los códigos con filtros opcionales
31. `find_by_name_base(name: str) -> Optional[StatusCode]` - Busca un código por nombre exacto (método base)
32. `find_by_code_base(code: str) -> Optional[StatusCode]` - Busca un código por código exacto (método base)

### OPERACIONES DE CONSULTA ESPECÍFICAS (8 métodos)

33. `get_status_codes_by_category(category: str) -> List[StatusCode]` - Obtiene códigos por categoría
34. `get_status_codes_by_priority(priority: int) -> List[StatusCode]` - Obtiene códigos por prioridad
35. `search_status_codes_by_criteria(criteria: Dict[str, Any], limit: Optional[int] = None, offset: Optional[int] = None) -> List[StatusCode]` - Busca códigos por criterios específicos
36. `get_status_codes_with_usage_count() -> List[Dict[str, Any]]` - Obtiene códigos con conteo de uso
37. `find_status_codes_by_date_range(start_date: date, end_date: date) -> List[StatusCode]` - Busca códigos por rango de fechas
38. `get_recently_created_status_codes(days: int = 30) -> List[StatusCode]` - Obtiene códigos creados recientemente
39. `get_recently_updated_status_codes(days: int = 30) -> List[StatusCode]` - Obtiene códigos actualizados recientemente
40. `count_status_codes(filters: Optional[Dict[str, Any]] = None) -> int` - Cuenta códigos con filtros opcionales

### OPERACIONES DE VALIDACIÓN ADICIONALES (3 métodos)

41. `validate_business_rules(operation: str, data: Dict[str, Any]) -> Dict[str, Any]` - Valida reglas de negocio específicas
42. `validate_data_consistency() -> Dict[str, Any]` - Valida consistencia general de datos
43. `check_status_code_dependencies(status_code_id: int) -> Dict[str, Any]` - Verifica dependencias de un código

### OPERACIONES ESTADÍSTICAS ADICIONALES (2 métodos)

44. `generate_status_codes_summary_report(include_inactive: bool = False) -> Dict[str, Any]` - Genera reporte resumen completo
45. `get_status_code_trends(start_date: date, end_date: date, granularity: str = "monthly") -> List[Dict[str, Any]]` - Obtiene tendencias de uso de códigos

---

## Resumen de Funcionalidades

**Total de métodos públicos:** 45

**Distribución por categorías:**
- **CRUD básico**: 5 métodos (crear, obtener, actualizar, eliminar)
- **Consultas**: 10 métodos (búsquedas y obtención de datos)
- **Validaciones**: 5 métodos (validación de datos y reglas)
- **Estadísticas**: 6 métodos (análisis y reportes)
- **Utilitarias**: 1 método (verificación de salud)
- **Métodos base**: 5 métodos (heredados del facade base)
- **Consultas específicas**: 8 métodos (búsquedas especializadas)
- **Validaciones adicionales**: 3 métodos (validaciones avanzadas)
- **Estadísticas adicionales**: 2 métodos (reportes y tendencias)

**Características principales:**
- **Interfaz unificada**: Acceso centralizado a todas las operaciones de códigos de estado
- **Validación integrada**: Métodos con validación automática de datos y reglas de negocio
- **Soporte para paginación**: Múltiples métodos con soporte para paginación
- **Análisis estadístico**: Amplio conjunto de métodos para análisis y reportes
- **Búsqueda avanzada**: Múltiples criterios de búsqueda y filtrado
- **Integridad de datos**: Validaciones exhaustivas y verificaciones de consistencia
- **Monitoreo de salud**: Métodos especializados para verificación del sistema

**Integración con módulos:**
- **CrudModule**: Operaciones CRUD básicas
- **QueryModule**: Consultas y búsquedas
- **ValidationModule**: Validación de datos y reglas
- **StatisticsModule**: Análisis y estadísticas

**Casos de uso principales:**
- Gestión completa del ciclo de vida de códigos de estado
- Configuración y mantenimiento de estados del sistema
- Análisis estadístico y generación de reportes
- Validación de integridad y consistencia de datos
- Búsqueda y filtrado avanzado de códigos
- Monitoreo de salud y rendimiento del sistema
- Integración con sistemas de tiempo y planificación