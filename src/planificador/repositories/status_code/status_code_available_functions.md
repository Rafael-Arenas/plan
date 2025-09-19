# Funciones Disponibles en Status Code Repository

**Fecha de actualización:** 2025-01-21
**Arquitectura:** Modular con Facade Pattern

## Arquitectura del Sistema

### StatusCodeRepositoryFacade (status_code_repository_facade.py)

El repositorio utiliza una **arquitectura modular** con el patrón Facade que integra módulos especializados:

- **StatusCodeCRUDModule**: Operaciones CRUD básicas
- **StatusCodeQueryModule**: Consultas y búsquedas avanzadas  
- **StatusCodeValidationModule**: Validaciones y reglas de negocio
- **StatusCodeStatisticsModule**: Análisis estadísticos y métricas

## Funciones por Módulo

### Módulo CRUD (StatusCodeCRUDModule)

#### Operaciones CRUD Básicas (6 funciones)
1. `create_status_code(status_code_data: Dict[str, Any]) -> StatusCode` - Crea un nuevo código de estado con validaciones
2. `get_status_code_by_id(status_code_id: int) -> Optional[StatusCode]` - Obtiene código de estado por ID
3. `get_status_code_by_code(code: str) -> Optional[StatusCode]` - Busca un código de estado por su código único
4. `update_status_code(status_code_id: int, update_data: Dict[str, Any]) -> StatusCode` - Actualiza un código de estado existente
5. `delete_status_code(status_code_id: int) -> bool` - Elimina un código de estado con validaciones
6. `get_all_status_codes() -> List[StatusCode]` - Obtiene todos los códigos de estado

### Módulo Query (StatusCodeQueryModule)

#### Operaciones de Consulta y Búsqueda (5 funciones)
7. `search_status_codes(search_criteria: Dict[str, Any]) -> List[StatusCode]` - Búsqueda avanzada con múltiples criterios
8. `get_status_codes_by_category(category: str) -> List[StatusCode]` - Obtiene códigos por categoría específica
9. `get_active_status_codes() -> List[StatusCode]` - Obtiene todos los códigos de estado activos ordenados
10. `get_status_codes_by_display_order() -> List[StatusCode]` - Obtiene códigos ordenados por orden de visualización
11. `find_status_codes_by_name_pattern(name_pattern: str) -> List[StatusCode]` - Busca códigos por patrón de nombre

### Módulo Validation (StatusCodeValidationModule)

#### Operaciones de Validación (5 funciones)
12. `validate_status_code_uniqueness(code: str, exclude_id: Optional[int] = None) -> bool` - Valida unicidad de código
13. `validate_status_code_name_uniqueness(name: str, exclude_id: Optional[int] = None) -> bool` - Valida unicidad de nombre
14. `validate_status_code_data(status_code_data: Dict[str, Any]) -> Dict[str, Any]` - Validación completa de datos
15. `validate_display_order_conflicts(display_order: int, exclude_id: Optional[int] = None) -> bool` - Valida conflictos de orden
16. `validate_default_status_code_rules(status_code_data: Dict[str, Any]) -> bool` - Valida reglas de códigos por defecto

### Módulo Statistics (StatusCodeStatisticsModule)

#### Operaciones de Estadísticas y Análisis (4 funciones)
17. `get_status_code_usage_statistics() -> Dict[str, Any]` - Obtiene estadísticas de uso completas
18. `get_status_code_distribution() -> Dict[str, Any]` - Obtiene distribución de códigos por categorías
19. `analyze_status_code_performance() -> Dict[str, Any]` - Analiza rendimiento y métricas de códigos
20. `generate_status_code_integrity_report() -> Dict[str, Any]` - Genera reporte de integridad del sistema

### Métodos del Facade (StatusCodeRepositoryFacade)

#### Operaciones de Gestión y Mantenimiento (12 funciones adicionales)
21. `get_billable_status_codes() -> List[StatusCode]` - Obtiene códigos facturables y activos
22. `get_productive_status_codes() -> List[StatusCode]` - Obtiene códigos productivos y activos
23. `get_status_codes_requiring_approval() -> List[StatusCode]` - Obtiene códigos que requieren aprobación
24. `filter_by_criteria(**criteria) -> List[StatusCode]` - Filtrado avanzado con múltiples criterios
25. `get_max_sort_order() -> int` - Obtiene el valor máximo de sort_order
26. `reorder_status_codes(code_order_mapping: Dict[str, int]) -> bool` - Reordena múltiples códigos
27. `search_by_name(search_term: str) -> List[StatusCode]` - Búsqueda simple por nombre
28. `exists(entity_id: int) -> bool` - Verifica existencia por ID
29. `health_check() -> Dict[str, Any]` - Verificación de salud del repositorio
30. `get_available_methods() -> List[str]` - Lista métodos disponibles
31. `validate_database_connection() -> bool` - Valida conexión a base de datos
32. `get_repository_statistics() -> Dict[str, Any]` - Estadísticas del repositorio

---

**Total de funciones disponibles:** 17

**Distribución por categorías:**
- **CRUD básico**: 4 funciones (crear, leer, actualizar, eliminar códigos de estado)
- **Búsqueda específica**: 5 funciones (por código, nombre, estado activo, facturable, productivo)
- **Búsqueda por características**: 1 función (códigos que requieren aprobación)
- **Filtrado avanzado**: 1 función (filtros múltiples con criterios combinados)
- **Gestión de ordenamiento**: 2 funciones (obtener máximo orden y reordenar códigos)
- **Estadísticas y análisis**: 1 función (estadísticas de uso y distribución)
- **Validación**: 1 función (validación de unicidad de códigos)
- **Métodos heredados**: 2 funciones (operaciones básicas del repositorio base)

**Funcionalidades especiales:**
- **Búsqueda por características booleanas**: 4 funciones para filtrar por is_active, is_billable, is_productive, requires_approval
- **Filtrado combinado**: 1 función que permite aplicar múltiples criterios simultáneamente
- **Gestión de ordenamiento**: 2 funciones para mantener el orden de presentación de códigos
- **Validación de integridad**: 1 función para garantizar unicidad de códigos
- **Análisis estadístico**: 1 función para obtener métricas de uso y distribución
- **Búsqueda textual**: 2 funciones para búsqueda por nombre y término general

**Características de los códigos de estado:**
- **is_active**: Indica si el código está activo y disponible para uso
- **is_billable**: Indica si el tiempo registrado con este código es facturable
- **is_productive**: Indica si el tiempo registrado con este código es productivo
- **requires_approval**: Indica si el uso de este código requiere aprobación
- **sort_order**: Orden de presentación en interfaces de usuario
- **code**: Identificador único alfanumérico del código
- **name**: Nombre descriptivo del código de estado
- **description**: Descripción detallada del propósito del código

**Patrones de uso comunes:**
- **Filtrado por estado**: Usar `get_active_status_codes()` para obtener solo códigos disponibles
- **Filtrado por facturación**: Usar `get_billable_status_codes()` para reportes financieros
- **Filtrado por productividad**: Usar `get_productive_status_codes()` para análisis de rendimiento
- **Búsqueda flexible**: Usar `filter_by_criteria()` para combinaciones complejas de filtros
- **Validación de datos**: Usar `validate_code_uniqueness()` antes de crear o actualizar códigos
- **Gestión de orden**: Usar `get_max_sort_order()` y `reorder_status_codes()` para mantener presentación ordenada

**Integración con otras entidades:**
- **Schedule**: Los códigos de estado se asignan a horarios para categorizar el tipo de trabajo
- **Workload**: Los códigos de estado pueden usarse para categorizar cargas de trabajo
- **Project**: Los códigos de estado pueden asociarse con estados específicos de proyectos

**Casos de uso principales:**
1. **Gestión de tiempo**: Categorizar horas trabajadas por tipo de actividad
2. **Facturación**: Distinguir entre tiempo facturable y no facturable
3. **Análisis de productividad**: Identificar tiempo productivo vs. administrativo
4. **Flujos de aprobación**: Gestionar códigos que requieren validación adicional
5. **Reportes y estadísticas**: Generar análisis basados en categorías de estado
6. **Configuración del sistema**: Mantener catálogos ordenados y actualizados

**Total de funciones documentadas**: 17