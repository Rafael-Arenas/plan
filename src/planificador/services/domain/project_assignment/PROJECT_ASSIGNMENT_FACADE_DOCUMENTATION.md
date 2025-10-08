# Documentación del Servicio de Dominio de Asignaciones de Proyecto

## Resumen Ejecutivo

El **ProjectAssignmentDomainService** es la implementación principal del patrón Facade para el dominio de asignaciones de proyecto. Proporciona una interfaz unificada y simplificada que encapsula la complejidad de 8 módulos especializados, ofreciendo más de 50 métodos organizados en 6 categorías funcionales principales.

## Arquitectura del Patrón Facade

### Principios Implementados

1. **Interfaz Unificada**: Un solo punto de acceso para todas las operaciones del dominio
2. **Encapsulación de Complejidad**: Los clientes no necesitan conocer la estructura interna
3. **Desacoplamiento**: Reduce las dependencias entre el cliente y los subsistemas
4. **Simplificación**: API consistente y fácil de usar
5. **Coordinación**: Manejo centralizado de transacciones y errores

### Estructura Modular

```
ProjectAssignmentDomainService (Facade Principal)
├── CrudOperations (Operaciones CRUD)
├── EmployeeQueries (Consultas de Empleados)
├── ProjectQueries (Consultas de Proyectos)
├── SearchOperations (Búsqueda y Filtrado)
├── ResourceManagement (Gestión de Recursos)
├── StatisticsOperations (Estadísticas y Análisis)
├── ValidationOperations (Validación y Reglas)
└── DiagnosticOperations (Diagnóstico y Salud)
```

## Categorías Funcionales

### 1. Operaciones CRUD Principales

**Propósito**: Gestión básica del ciclo de vida de asignaciones

#### Métodos Principales

- **`create_assignment(assignment_data)`**
  - **Descripción**: Crea una nueva asignación de proyecto
  - **Validaciones**: Reglas de negocio, conflictos, restricciones de carga
  - **Retorna**: `ProjectAssignmentResponse`
  - **Excepciones**: `ValidationError`, `RepositoryError`

- **`update_assignment(assignment_id, update_data)`**
  - **Descripción**: Actualiza una asignación existente
  - **Validaciones**: Integridad de actualización, cambios permitidos
  - **Retorna**: `ProjectAssignmentResponse`
  - **Excepciones**: `ValidationError`, `RepositoryError`

- **`delete_assignment(assignment_id)`**
  - **Descripción**: Elimina una asignación
  - **Validaciones**: Reglas de eliminación, dependencias
  - **Retorna**: `bool`
  - **Excepciones**: `ValidationError`, `RepositoryError`

- **`get_assignment_by_id(assignment_id)`**
  - **Descripción**: Obtiene una asignación por ID
  - **Retorna**: `Optional[ProjectAssignmentResponse]`
  - **Excepciones**: `RepositoryError`

#### Métodos Especializados

- **`bulk_create_assignments(assignments_data)`**
  - **Descripción**: Creación en lote con validación transaccional
  - **Optimización**: Procesamiento eficiente de múltiples registros
  - **Retorna**: `List[ProjectAssignmentResponse]`

- **`duplicate_assignment(assignment_id, modifications)`**
  - **Descripción**: Duplicación inteligente con modificaciones opcionales
  - **Características**: Preserva relaciones, aplica modificaciones
  - **Retorna**: `ProjectAssignmentResponse`

- **`archive_assignment(assignment_id)`**
  - **Descripción**: Archivado suave manteniendo historial
  - **Características**: Preserva integridad referencial
  - **Retorna**: `ProjectAssignmentResponse`

### 2. Consultas Centradas en Empleados

**Propósito**: Análisis y consultas desde la perspectiva del empleado

#### Métodos de Consulta

- **`get_all_employee_assignments(employee_id, include_archived)`**
  - **Descripción**: Todas las asignaciones de un empleado
  - **Filtros**: Incluir/excluir archivadas
  - **Retorna**: `List[ProjectAssignmentResponse]`

- **`get_active_employee_assignments(employee_id)`**
  - **Descripción**: Solo asignaciones activas del empleado
  - **Optimización**: Consulta filtrada por estado
  - **Retorna**: `List[ProjectAssignmentResponse]`

- **`get_employee_workload_summary(employee_id, analysis_period)`**
  - **Descripción**: Resumen completo de carga de trabajo
  - **Métricas**: Porcentaje total, horas diarias, distribución por proyecto
  - **Análisis**: Capacidad disponible, recomendaciones
  - **Retorna**: `Dict[str, Any]` con métricas detalladas

- **`get_employee_assignment_history(employee_id, limit)`**
  - **Descripción**: Historial cronológico de asignaciones
  - **Características**: Ordenado por fecha, limitado opcionalmente
  - **Retorna**: `List[Dict[str, Any]]`

- **`get_employee_current_allocation(employee_id)`**
  - **Descripción**: Estado actual de asignación del empleado
  - **Información**: Proyectos activos, carga total, disponibilidad
  - **Retorna**: `Dict[str, Any]`

### 3. Consultas Centradas en Proyectos

**Propósito**: Análisis y consultas desde la perspectiva del proyecto

#### Métodos de Consulta

- **`get_all_project_assignments(project_id, include_archived)`**
  - **Descripción**: Todas las asignaciones de un proyecto
  - **Filtros**: Incluir/excluir archivadas
  - **Retorna**: `List[ProjectAssignmentResponse]`

- **`get_project_team_summary(project_id)`**
  - **Descripción**: Resumen completo del equipo del proyecto
  - **Métricas**: Tamaño del equipo, distribución de roles, experiencia
  - **Análisis**: Fortalezas, gaps, recomendaciones
  - **Retorna**: `Dict[str, Any]`

- **`get_project_resource_allocation(project_id)`**
  - **Descripción**: Análisis de asignación de recursos
  - **Información**: Distribución por empleado, utilización, eficiencia
  - **Retorna**: `Dict[str, Any]`

- **`get_project_assignment_timeline(project_id)`**
  - **Descripción**: Línea de tiempo visual del proyecto
  - **Características**: Cronología, hitos, superposiciones
  - **Retorna**: `Dict[str, Any]`

### 4. Operaciones de Búsqueda y Filtrado

**Propósito**: Búsqueda avanzada y filtrado complejo

#### Métodos de Búsqueda

- **`get_assignments_with_filters(filters)`**
  - **Descripción**: Búsqueda avanzada con filtros complejos
  - **Filtros**: Estado, fechas, empleado, proyecto, rol, porcentaje
  - **Características**: Combinación AND/OR, rangos, patrones
  - **Retorna**: `List[ProjectAssignmentResponse]`

- **`get_assignments_by_date_range(start_date, end_date)`**
  - **Descripción**: Asignaciones que se superponen con un rango de fechas
  - **Lógica**: Detección inteligente de superposiciones
  - **Retorna**: `List[ProjectAssignmentResponse]`

- **`get_assignments_by_role(role)`**
  - **Descripción**: Filtrado por rol específico
  - **Características**: Búsqueda exacta o por patrón
  - **Retorna**: `List[ProjectAssignmentResponse]`

- **`get_overlapping_assignments(employee_id, start_date, end_date, exclude_assignment_id)`**
  - **Descripción**: Detección de conflictos temporales
  - **Análisis**: Superposiciones, conflictos de carga, recomendaciones
  - **Retorna**: `List[Dict[str, Any]]` con detalles de conflictos

### 5. Gestión de Recursos

**Propósito**: Optimización y balanceo de recursos

#### Métodos de Optimización

- **`optimize_resource_allocation(project_id)`**
  - **Descripción**: Optimización automática de recursos del proyecto
  - **Algoritmos**: Balanceo de carga, maximización de eficiencia
  - **Análisis**: Situación actual, plan optimizado, impacto esperado
  - **Retorna**: `Dict[str, Any]` con plan de optimización

- **`calculate_team_capacity(team_member_ids, period_start, period_end)`**
  - **Descripción**: Cálculo de capacidad del equipo
  - **Métricas**: Capacidad total, utilizada, disponible por miembro
  - **Análisis**: Distribución, cuellos de botella, recomendaciones
  - **Retorna**: `Dict[str, Any]` con análisis de capacidad

- **`balance_workload_across_team(project_id)`**
  - **Descripción**: Balanceo de carga dentro del equipo
  - **Estrategias**: Redistribución equitativa, consideración de habilidades
  - **Resultado**: Plan de balanceo, transferencias sugeridas
  - **Retorna**: `Dict[str, Any]` con plan de balanceo

### 6. Estadísticas y Análisis

**Propósito**: Análisis estadístico y métricas de rendimiento

#### Métodos Estadísticos Básicos

- **`get_assignment_count_by_status(filters)`**
  - **Descripción**: Conteo de asignaciones por estado
  - **Filtros**: Opcionales para segmentación
  - **Retorna**: `Dict[str, int]`

- **`get_assignment_distribution_by_role(filters)`**
  - **Descripción**: Distribución de asignaciones por rol
  - **Métricas**: Conteo, porcentajes, tendencias
  - **Retorna**: `Dict[str, Any]`

- **`get_average_allocation_metrics(filters)`**
  - **Descripción**: Métricas promedio de asignación
  - **Cálculos**: Porcentaje promedio, horas diarias, duración
  - **Retorna**: `Dict[str, float]`

- **`get_assignment_duration_statistics(filters)`**
  - **Descripción**: Estadísticas de duración de asignaciones
  - **Métricas**: Promedio, mediana, percentiles, distribución
  - **Retorna**: `Dict[str, Any]`

#### Métodos de Análisis Avanzado

- **`analyze_assignment_trends(period_months, granularity)`**
  - **Descripción**: Análisis de tendencias temporales
  - **Características**: Múltiples granularidades, detección de patrones
  - **Métricas**: Crecimiento, estacionalidad, proyecciones
  - **Retorna**: `Dict[str, Any]` con análisis de tendencias

- **`calculate_resource_utilization_metrics(analysis_period)`**
  - **Descripción**: Métricas de utilización de recursos
  - **Análisis**: Eficiencia, subutilización, sobreasignación
  - **Retorna**: `Dict[str, Any]`

- **`get_project_performance_metrics(project_ids)`**
  - **Descripción**: Métricas de rendimiento de proyectos
  - **KPIs**: Eficiencia del equipo, cumplimiento de plazos, calidad
  - **Retorna**: `Dict[str, Any]`

- **`generate_predictive_insights(prediction_horizon_months)`**
  - **Descripción**: Insights predictivos basados en datos históricos
  - **Algoritmos**: Análisis de tendencias, proyecciones, recomendaciones
  - **Retorna**: `Dict[str, Any]` con predicciones

### 7. Validación y Reglas de Negocio

**Propósito**: Validación integral y aplicación de reglas de negocio

#### Métodos de Validación

- **`validate_assignment_business_rules(assignment_data)`**
  - **Descripción**: Validación completa de reglas de negocio
  - **Validaciones**: Datos básicos, fechas, asignación, entidades relacionadas
  - **Retorna**: `Dict[str, Any]` con resultado de validación

- **`check_workload_constraints(employee_id, additional_allocation, period_start, period_end)`**
  - **Descripción**: Verificación de restricciones de carga de trabajo
  - **Análisis**: Carga actual, proyectada, límites, recomendaciones
  - **Retorna**: `Dict[str, Any]` con análisis de restricciones

- **`validate_date_consistency(start_date, end_date)`**
  - **Descripción**: Validación de consistencia temporal
  - **Verificaciones**: Orden lógico, días laborables, restricciones
  - **Retorna**: `Dict[str, Any]`

- **`check_assignment_conflicts(assignment_data, exclude_assignment_id)`**
  - **Descripción**: Detección de conflictos con asignaciones existentes
  - **Análisis**: Conflictos temporales, de carga, de rol, de proyecto
  - **Retorna**: `Dict[str, Any]` con detalles de conflictos

- **`validate_assignment_update_integrity(assignment_id, update_data)`**
  - **Descripción**: Validación de integridad para actualizaciones
  - **Verificaciones**: Campos actualizables, impacto, consistencia
  - **Retorna**: `Dict[str, Any]`

### 8. Diagnóstico y Salud del Sistema

**Propósito**: Monitoreo de salud y diagnóstico del sistema

#### Métodos de Diagnóstico

- **`get_system_health_status(include_performance_metrics, include_data_quality_checks)`**
  - **Descripción**: Estado completo de salud del sistema
  - **Verificaciones**: Componentes básicos, calidad de datos, rendimiento
  - **Métricas**: Tiempo de respuesta, integridad, disponibilidad
  - **Retorna**: `Dict[str, Any]` con estado de salud

- **`run_data_integrity_audit(fix_issues, audit_scope)`**
  - **Descripción**: Auditoría completa de integridad de datos
  - **Verificaciones**: Integridad de asignaciones, relaciones, reglas de negocio
  - **Características**: Corrección automática opcional, alcance configurable
  - **Retorna**: `Dict[str, Any]` con resultados de auditoría

## Métodos de Utilidad y Coordinación

### Métodos del Servicio

- **`get_service_statistics()`**
  - **Descripción**: Estadísticas generales del servicio
  - **Información**: Métricas básicas, distribución de estados, salud del sistema
  - **Retorna**: `Dict[str, Any]`

- **`validate_service_integrity()`**
  - **Descripción**: Validación completa de integridad del servicio
  - **Verificaciones**: Módulos cargados, integración con repositorio, integridad de datos
  - **Retorna**: `Dict[str, Any]` con resultado de validación

## Características Técnicas

### Manejo de Errores

- **Jerarquía de Excepciones**: `ValidationError`, `RepositoryError`
- **Logging Estructurado**: Loguru con contexto enriquecido
- **Rollback Automático**: En operaciones transaccionales
- **Preservación de Errores**: Cadena de errores originales

### Performance y Optimización

- **Operaciones Asíncronas**: Todos los métodos son async/await
- **Lazy Loading**: Carga de datos bajo demanda
- **Caching Inteligente**: En consultas frecuentes
- **Batch Processing**: Para operaciones en lote

### Validación de Datos

- **Pydantic Schemas**: Validación automática de entrada
- **Type Hints Completos**: Tipado estático completo
- **Validación de Negocio**: Reglas específicas del dominio
- **Sanitización**: Limpieza automática de datos

### Logging y Trazabilidad

- **Logging Estructurado**: Contexto enriquecido por operación
- **Trazabilidad Completa**: Seguimiento de operaciones complejas
- **Métricas de Performance**: Tiempo de ejecución y recursos
- **Auditoría**: Registro de cambios y accesos

## Patrones de Uso

### Inicialización del Servicio

```python
from planificador.services.domain.project_assignment import (
    ProjectAssignmentDomainService,
    ProjectAssignmentRepositoryFacade
)

# Inicializar repositorio facade
repository_facade = ProjectAssignmentRepositoryFacade(session)

# Inicializar servicio de dominio
domain_service = ProjectAssignmentDomainService(repository_facade)
```

### Operaciones CRUD Básicas

```python
# Crear asignación
assignment_data = ProjectAssignmentCreate(...)
new_assignment = await domain_service.create_assignment(assignment_data)

# Obtener asignación
assignment = await domain_service.get_assignment_by_id(assignment_id)

# Actualizar asignación
update_data = ProjectAssignmentUpdate(...)
updated_assignment = await domain_service.update_assignment(assignment_id, update_data)

# Eliminar asignación
success = await domain_service.delete_assignment(assignment_id)
```

### Consultas Avanzadas

```python
# Carga de trabajo del empleado
workload = await domain_service.get_employee_workload_summary(employee_id)

# Equipo del proyecto
team_summary = await domain_service.get_project_team_summary(project_id)

# Búsqueda con filtros
filters = ProjectAssignmentFilter(...)
results = await domain_service.get_assignments_with_filters(filters)
```

### Análisis y Optimización

```python
# Optimizar recursos
optimization_plan = await domain_service.optimize_resource_allocation(project_id)

# Estadísticas de tendencias
trends = await domain_service.analyze_assignment_trends(period_months=12)

# Diagnóstico del sistema
health_status = await domain_service.get_system_health_status()
```

## Beneficios del Patrón Facade

### Para Desarrolladores

1. **API Simplificada**: Una sola clase para todas las operaciones
2. **Documentación Centralizada**: Toda la funcionalidad en un lugar
3. **Consistencia**: Patrones uniformes en todos los métodos
4. **Mantenibilidad**: Cambios internos no afectan a los clientes

### Para el Sistema

1. **Desacoplamiento**: Clientes independientes de la implementación interna
2. **Flexibilidad**: Fácil modificación de la lógica interna
3. **Reutilización**: Módulos especializados reutilizables
4. **Testabilidad**: Cada módulo es testeable independientemente

### Para el Negocio

1. **Funcionalidad Rica**: Más de 50 métodos especializados
2. **Análisis Avanzado**: Insights profundos sobre asignaciones
3. **Optimización Automática**: Mejora continua de recursos
4. **Validación Robusta**: Prevención proactiva de errores

## Conclusión

El **ProjectAssignmentDomainService** representa una implementación completa y robusta del patrón Facade, proporcionando una interfaz unificada para un dominio complejo. Con 8 módulos especializados, más de 50 métodos organizados en 6 categorías funcionales, y características avanzadas como optimización de recursos, análisis predictivo y diagnóstico automático, este servicio establece un estándar de excelencia para la arquitectura de servicios de dominio en el proyecto Planificador.