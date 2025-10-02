# Métodos Disponibles en ClientDomainService

**Última actualización:** Enero 2025

## Descripción General

`ClientDomainService` es el servicio de dominio principal para la gestión integral de clientes en el sistema. Implementa lógica de negocio compleja, coordinación entre dominios, análisis avanzado y gestión del ciclo de vida completo de clientes, proporcionando una capa de abstracción de alto nivel que encapsula las reglas de negocio y coordina las operaciones entre diferentes repositorios y servicios.

El servicio integra validaciones de negocio, análisis estadístico, gestión de proyectos, coordinación cross-domain y generación de reportes, ofreciendo una API coherente para todas las operaciones complejas relacionadas con clientes.

---

## Métodos Disponibles

### 1. Operaciones CRUD con Validación y Dependencias (3 métodos)

1. `create_client_with_validation(client_data: ClientCreateSchema, validate_dependencies: bool = True, notify_stakeholders: bool = True) -> ClientResponseSchema` - Crea un nuevo cliente con validaciones de negocio completas y notificación a stakeholders
2. `update_client_with_dependencies(client_id: int, update_data: ClientUpdateSchema, validate_impact: bool = True, cascade_updates: bool = True) -> ClientResponseSchema` - Actualiza un cliente considerando dependencias y propagando cambios en cascada
3. `delete_client_with_cleanup(client_id: int, force_delete: bool = False, cleanup_related_data: bool = True) -> bool` - Elimina un cliente con limpieza completa de datos relacionados y validación de dependencias

### 2. Búsqueda Avanzada y Consultas Complejas (2 métodos)

4. `advanced_client_search(search_criteria: ClientSearchSchema, include_analytics: bool = False, include_relationships: bool = False) -> Dict[str, Any]` - Realiza búsqueda avanzada de clientes con criterios complejos y enriquecimiento opcional
5. `get_clients_by_complex_criteria(criteria: Dict[str, Any], sort_by: Optional[str] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ClientResponseSchema]` - Obtiene clientes usando criterios complejos de filtrado con paginación y ordenamiento

### 3. Gestión de Proyectos y Transferencias (2 métodos)

6. `transfer_projects_between_clients(from_client_id: int, to_client_id: int, project_ids: Optional[List[int]] = None, validate_business_rules: bool = True) -> Dict[str, Any]` - Transfiere proyectos entre clientes con validaciones de negocio y registro de eventos
7. `analyze_client_project_portfolio(client_id: int, analysis_type: str = "comprehensive", date_range: Optional[Tuple[date, date]] = None) -> Dict[str, Any]` - Analiza el portafolio de proyectos de un cliente con diferentes tipos de análisis

### 4. Análisis y Estadísticas de Negocio (13 métodos)

8. `generate_client_business_report(client_id: int, report_type: str = "comprehensive", include_projections: bool = True, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, Any]` - Genera un reporte de negocio completo para un cliente con proyecciones opcionales
9. `get_client_performance_metrics(client_id: int, metric_types: Optional[List[str]] = None, period: str = "monthly", compare_previous: bool = True) -> Dict[str, Any]` - Obtiene métricas de rendimiento detalladas con comparación temporal
10. `generate_client_dashboard_data(client_id: int, dashboard_type: str = "executive", real_time: bool = True) -> Dict[str, Any]` - Genera datos optimizados para dashboard con diferentes vistas especializadas
11. `calculate_client_roi_metrics(client_id: int, calculation_method: str = "comprehensive", include_projections: bool = True) -> Dict[str, Any]` - Calcula métricas de ROI detalladas con diferentes metodologías de cálculo
12. `analyze_client_profitability_trends(client_id: int, period_months: int = 12, include_forecasting: bool = True) -> Dict[str, Any]` - Analiza tendencias de rentabilidad con forecasting avanzado
13. `generate_client_satisfaction_metrics(client_id: int, metric_sources: Optional[List[str]] = None, weighted_scoring: bool = True) -> Dict[str, Any]` - Genera métricas de satisfacción del cliente con scoring ponderado
14. `calculate_client_lifetime_value(client_id: int, prediction_model: str = "advanced", confidence_intervals: bool = True) -> Dict[str, Any]` - Calcula el valor de vida del cliente con modelos predictivos
15. `analyze_client_engagement_patterns(client_id: int, analysis_depth: str = "comprehensive", behavioral_insights: bool = True) -> Dict[str, Any]` - Analiza patrones de engagement con insights comportamentales
16. `generate_client_risk_assessment(client_id: int, risk_categories: Optional[List[str]] = None, mitigation_strategies: bool = True) -> Dict[str, Any]` - Genera evaluación de riesgo integral con estrategias de mitigación
17. `calculate_client_churn_probability(client_id: int, prediction_horizon_months: int = 6, feature_importance: bool = True) -> Dict[str, Any]` - Calcula probabilidad de churn con análisis de importancia de características
18. `analyze_client_market_position(client_id: int, competitive_analysis: bool = True, market_trends: bool = True) -> Dict[str, Any]` - Analiza posición de mercado del cliente con análisis competitivo
19. `generate_client_growth_projections(client_id: int, projection_scenarios: Optional[List[str]] = None, confidence_bands: bool = True) -> Dict[str, Any]` - Genera proyecciones de crecimiento con múltiples escenarios
20. `calculate_client_operational_efficiency(client_id: int, efficiency_metrics: Optional[List[str]] = None, benchmarking: bool = True) -> Dict[str, Any]` - Calcula eficiencia operacional con benchmarking contra estándares de industria

### 5. Validación y Reglas de Negocio (10 métodos)

21. `validate_complex_business_rules(client_data: Union[ClientCreateSchema, ClientUpdateSchema], operation_type: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]` - Valida reglas de negocio complejas para operaciones de cliente con contexto adicional
22. `check_client_constraints(client_id: int, constraint_types: Optional[List[str]] = None) -> Dict[str, Any]` - Verifica restricciones y limitaciones del cliente con alertas de proximidad a límites
23. `validate_client_data_integrity(client_id: int, validation_scope: str = "comprehensive", auto_fix: bool = False) -> Dict[str, Any]` - Valida integridad de datos del cliente con opción de corrección automática
24. `check_client_relationship_consistency(client_id: int, relationship_types: Optional[List[str]] = None, deep_validation: bool = True) -> Dict[str, Any]` - Verifica consistencia de relaciones del cliente con validación profunda
25. `validate_client_business_logic(client_id: int, logic_rules: Optional[List[str]] = None, context_aware: bool = True) -> Dict[str, Any]` - Valida lógica de negocio específica del cliente con contexto
26. `check_client_compliance_status(client_id: int, compliance_frameworks: Optional[List[str]] = None, detailed_report: bool = True) -> Dict[str, Any]` - Verifica estado de compliance del cliente contra frameworks regulatorios
27. `validate_client_financial_constraints(client_id: int, constraint_categories: Optional[List[str]] = None, alert_thresholds: bool = True) -> Dict[str, Any]` - Valida restricciones financieras con alertas de umbral
28. `check_client_operational_limits(client_id: int, limit_types: Optional[List[str]] = None, usage_analytics: bool = True) -> Dict[str, Any]` - Verifica límites operacionales con analytics de uso
29. `validate_client_security_requirements(client_id: int, security_domains: Optional[List[str]] = None, risk_assessment: bool = True) -> Dict[str, Any]` - Valida requerimientos de seguridad con evaluación de riesgo
30. `check_client_audit_readiness(client_id: int, audit_types: Optional[List[str]] = None, compliance_gaps: bool = True) -> Dict[str, Any]` - Verifica preparación para auditoría con identificación de gaps de compliance

### 6. Coordinación Cross-Domain (2 métodos)

31. `handle_client_lifecycle_event(client_id: int, event_type: str, event_data: Dict[str, Any], propagate_to_domains: bool = True) -> Dict[str, Any]` - Maneja eventos del ciclo de vida del cliente y coordina acciones cross-domain
32. `synchronize_client_data(client_id: int, target_domains: Optional[List[str]] = None, sync_type: str = "full", force_sync: bool = False) -> Dict[str, Any]` - Sincroniza datos del cliente entre diferentes dominios y sistemas con resolución de conflictos

### 7. Gestión de Estado y Ciclo de Vida (8 métodos)

33. `activate_client_with_validation(client_id: int, activation_context: Optional[Dict[str, Any]] = None, notify_stakeholders: bool = True) -> Dict[str, Any]` - Activa un cliente con validaciones completas y notificación a stakeholders
34. `suspend_client_with_impact_analysis(client_id: int, suspension_reason: str, impact_assessment: bool = True, preserve_data: bool = True) -> Dict[str, Any]` - Suspende un cliente con análisis de impacto y preservación de datos
35. `reactivate_client_from_suspension(client_id: int, reactivation_context: Optional[Dict[str, Any]] = None, data_validation: bool = True) -> Dict[str, Any]` - Reactiva un cliente desde suspensión con validación de datos
36. `archive_client_with_retention_policy(client_id: int, retention_period_months: int = 84, archive_related_data: bool = True) -> Dict[str, Any]` - Archiva un cliente aplicando políticas de retención de datos
37. `restore_client_from_archive(client_id: int, restoration_scope: str = "full", data_validation: bool = True) -> Dict[str, Any]` - Restaura un cliente desde archivo con validación de integridad
38. `migrate_client_status(client_id: int, target_status: str, migration_context: Optional[Dict[str, Any]] = None, validate_transition: bool = True) -> Dict[str, Any]` - Migra el estado del cliente con validación de transiciones
39. `track_client_lifecycle_history(client_id: int, include_metadata: bool = True, detailed_timeline: bool = True) -> Dict[str, Any]` - Rastrea el historial completo del ciclo de vida del cliente
40. `predict_client_lifecycle_transitions(client_id: int, prediction_horizon_months: int = 12, confidence_scoring: bool = True) -> Dict[str, Any]` - Predice transiciones futuras del ciclo de vida con scoring de confianza

### 8. Consultas Temporales Especializadas (6 métodos)

41. `get_clients_by_creation_period(start_date: date, end_date: date, include_analytics: bool = False, sort_criteria: Optional[str] = None) -> List[ClientResponseSchema]` - Obtiene clientes creados en un período específico con analytics opcionales
42. `get_clients_by_last_activity_range(days_since_activity: int, activity_types: Optional[List[str]] = None, include_engagement_metrics: bool = False) -> List[ClientResponseSchema]` - Obtiene clientes por rango de última actividad con métricas de engagement
43. `get_clients_by_status_change_period(status_from: str, status_to: str, change_period_days: int, include_transition_context: bool = False) -> List[ClientResponseSchema]` - Obtiene clientes por cambios de estado en período específico
44. `get_clients_approaching_milestones(milestone_types: List[str], days_ahead: int = 30, priority_scoring: bool = True) -> List[Dict[str, Any]]` - Obtiene clientes próximos a hitos importantes con scoring de prioridad
45. `get_clients_with_temporal_patterns(pattern_types: List[str], analysis_period_months: int = 6, statistical_significance: bool = True) -> List[Dict[str, Any]]` - Obtiene clientes con patrones temporales específicos con significancia estadística
46. `get_clients_by_seasonal_behavior(season_type: str, behavior_metrics: Optional[List[str]] = None, comparative_analysis: bool = True) -> List[Dict[str, Any]]` - Obtiene clientes por comportamiento estacional con análisis comparativo

### 9. Operaciones de Limpieza y Mantenimiento (5 métodos)

47. `cleanup_inactive_client_data(inactivity_threshold_months: int = 24, data_categories: Optional[List[str]] = None, dry_run: bool = True) -> Dict[str, Any]` - Limpia datos de clientes inactivos con opción de simulación
48. `optimize_client_data_storage(client_id: Optional[int] = None, optimization_strategies: Optional[List[str]] = None, performance_metrics: bool = True) -> Dict[str, Any]` - Optimiza almacenamiento de datos de cliente con métricas de rendimiento
49. `consolidate_duplicate_client_records(similarity_threshold: float = 0.85, auto_merge: bool = False, detailed_analysis: bool = True) -> Dict[str, Any]` - Consolida registros duplicados de clientes con análisis detallado
50. `refresh_client_computed_fields(client_id: Optional[int] = None, field_categories: Optional[List[str]] = None, batch_processing: bool = True) -> Dict[str, Any]` - Refresca campos calculados del cliente con procesamiento en lotes
51. `maintain_client_data_quality(quality_checks: Optional[List[str]] = None, auto_correction: bool = False, quality_scoring: bool = True) -> Dict[str, Any]` - Mantiene calidad de datos de cliente con scoring de calidad

### 10. Análisis de Relaciones y Dependencias (7 métodos)

52. `analyze_client_project_dependencies(client_id: int, dependency_types: Optional[List[str]] = None, impact_analysis: bool = True) -> Dict[str, Any]` - Analiza dependencias de proyectos del cliente con análisis de impacto
53. `map_client_stakeholder_network(client_id: int, network_depth: int = 3, influence_scoring: bool = True) -> Dict[str, Any]` - Mapea la red de stakeholders del cliente con scoring de influencia
54. `analyze_client_vendor_relationships(client_id: int, relationship_metrics: Optional[List[str]] = None, performance_evaluation: bool = True) -> Dict[str, Any]` - Analiza relaciones con proveedores del cliente con evaluación de rendimiento
55. `track_client_interaction_patterns(client_id: int, interaction_types: Optional[List[str]] = None, pattern_recognition: bool = True) -> Dict[str, Any]` - Rastrea patrones de interacción del cliente con reconocimiento de patrones
56. `analyze_client_communication_flow(client_id: int, communication_channels: Optional[List[str]] = None, effectiveness_metrics: bool = True) -> Dict[str, Any]` - Analiza flujo de comunicación del cliente con métricas de efectividad
57. `map_client_decision_hierarchy(client_id: int, hierarchy_levels: Optional[int] = None, decision_influence: bool = True) -> Dict[str, Any]` - Mapea jerarquía de decisiones del cliente con análisis de influencia
58. `analyze_client_collaboration_networks(client_id: int, network_types: Optional[List[str]] = None, collaboration_metrics: bool = True) -> Dict[str, Any]` - Analiza redes de colaboración del cliente con métricas especializadas

### 11. Notificaciones y Alertas (4 métodos)

59. `generate_client_status_alerts(client_id: Optional[int] = None, alert_types: Optional[List[str]] = None, priority_filtering: bool = True) -> List[Dict[str, Any]]` - Genera alertas de estado del cliente con filtrado por prioridad
60. `send_client_milestone_notifications(client_id: int, milestone_types: List[str], notification_channels: Optional[List[str]] = None) -> Dict[str, Any]` - Envía notificaciones de hitos del cliente por múltiples canales
61. `create_client_performance_alerts(client_id: int, performance_thresholds: Dict[str, float], alert_frequency: str = "daily") -> Dict[str, Any]` - Crea alertas de rendimiento del cliente con umbrales configurables
62. `manage_client_escalation_workflows(client_id: int, escalation_triggers: List[str], workflow_automation: bool = True) -> Dict[str, Any]` - Gestiona workflows de escalación del cliente con automatización

### 12. Exportación y Reportes Especializados (6 métodos)

63. `export_client_comprehensive_report(client_id: int, export_format: str = "pdf", include_attachments: bool = True, template_customization: Optional[Dict[str, Any]] = None) -> Dict[str, Any]` - Exporta reporte integral del cliente con personalización de plantilla
64. `generate_client_audit_trail_report(client_id: int, audit_period_months: int = 12, compliance_framework: Optional[str] = None, detailed_evidence: bool = True) -> Dict[str, Any]` - Genera reporte de auditoría del cliente con evidencia detallada
65. `export_client_financial_summary(client_id: int, financial_periods: List[str], comparison_analysis: bool = True, forecast_inclusion: bool = True) -> Dict[str, Any]` - Exporta resumen financiero del cliente con análisis comparativo
66. `generate_client_compliance_report(client_id: int, compliance_standards: List[str], gap_analysis: bool = True, remediation_plan: bool = True) -> Dict[str, Any]` - Genera reporte de compliance del cliente con plan de remediación
67. `export_client_relationship_map(client_id: int, map_format: str = "interactive", relationship_depth: int = 3, visual_analytics: bool = True) -> Dict[str, Any]` - Exporta mapa de relaciones del cliente con analytics visual
68. `generate_client_executive_summary(client_id: int, summary_type: str = "strategic", kpi_focus: Optional[List[str]] = None, executive_insights: bool = True) -> Dict[str, Any]` - Genera resumen ejecutivo del cliente con insights estratégicos

---

## Resumen de Funcionalidades

### Total de Métodos Públicos: 68

**Distribución por Categorías:**
- Operaciones CRUD con Validación y Dependencias: 3 métodos (4%)
- Búsqueda Avanzada y Consultas Complejas: 2 métodos (3%)
- Gestión de Proyectos y Transferencias: 2 métodos (3%)
- Análisis y Estadísticas de Negocio: 13 métodos (19%)
- Validación y Reglas de Negocio: 10 métodos (15%)
- Coordinación Cross-Domain: 2 métodos (3%)
- Gestión de Estado y Ciclo de Vida: 8 métodos (12%)
- Consultas Temporales Especializadas: 6 métodos (9%)
- Operaciones de Limpieza y Mantenimiento: 5 métodos (7%)
- Análisis de Relaciones y Dependencias: 7 métodos (10%)
- Notificaciones y Alertas: 4 métodos (6%)
- Exportación y Reportes Especializados: 6 métodos (9%)

### Características Principales Expandidas

- **Lógica de Negocio Compleja**: Implementación de reglas de negocio avanzadas con validación contextual y compliance
- **Coordinación Cross-Domain**: Sincronización y eventos entre diferentes dominios del sistema con resolución de conflictos
- **Análisis Avanzado**: Generación de reportes, métricas y análisis de portafolio con proyecciones y forecasting
- **Validación Robusta**: Sistema completo de validación con reglas de negocio configurables y auditoría
- **Gestión de Dependencias**: Manejo inteligente de dependencias y propagación de cambios con análisis de impacto
- **Búsqueda Inteligente**: Consultas complejas con enriquecimiento de datos y metadatos temporales
- **API Asíncrona**: Operaciones no bloqueantes optimizadas para alta concurrencia y procesamiento en lotes
- **Auditoría Completa**: Registro detallado de operaciones y eventos para compliance y trazabilidad
- **Gestión del Ciclo de Vida**: Control completo del estado del cliente con transiciones validadas y automatización
- **Analytics Predictivos**: Modelos de machine learning para churn, LTV, y proyecciones de crecimiento
- **Gestión de Calidad de Datos**: Limpieza automática, deduplicación y optimización de almacenamiento
- **Análisis de Relaciones**: Mapeo de redes de stakeholders, dependencias y patrones de colaboración
- **Sistema de Alertas**: Notificaciones inteligentes con escalación automática y múltiples canales
- **Reportes Ejecutivos**: Exportación especializada con plantillas personalizables y analytics visual

### Reglas de Negocio Configurables Expandidas

```python
_business_rules = {
    # Validación básica
    'min_name_length': 2,
    'max_name_length': 100,
    'required_fields': ['name', 'email'],
    'email_domains_allowed': [...],
    
    # Límites operacionales
    'max_projects_per_client': 50,
    'max_stakeholders_per_client': 25,
    'max_concurrent_validations': 10,
    
    # Transiciones de estado
    'client_status_transitions': {
        'active': ['inactive', 'suspended', 'archived'],
        'inactive': ['active', 'archived'],
        'suspended': ['active', 'inactive', 'archived'],
        'archived': ['active']  # Solo con validación especial
    },
    
    # Métricas y umbrales
    'churn_probability_threshold': 0.7,
    'roi_minimum_threshold': 0.15,
    'satisfaction_alert_threshold': 3.0,
    'engagement_decline_threshold': 0.3,
    
    # Retención y archivado
    'default_retention_months': 84,
    'inactivity_threshold_months': 24,
    'archive_notification_days': 30,
    
    # Compliance y auditoría
    'audit_trail_retention_years': 7,
    'compliance_check_frequency_days': 90,
    'security_validation_required': True,
    
    # Performance y optimización
    'batch_processing_size': 100,
    'cache_ttl_minutes': 30,
    'async_operation_timeout_minutes': 15
}
```

### Integración con Otros Módulos Expandida

- **ClientRepositoryFacade**: Acceso unificado a datos de clientes con operaciones especializadas y caching
- **Project Domain**: Coordinación para transferencias y análisis de portafolio de proyectos con dependencias
- **Analytics Engine**: Generación de métricas, reportes y análisis de tendencias con ML/AI
- **Event System**: Manejo de eventos del ciclo de vida y notificaciones cross-domain con workflows
- **Validation Framework**: Sistema robusto de validación con esquemas Pydantic y reglas dinámicas
- **Logging System**: Registro estructurado con Loguru para auditoría y debugging con correlación
- **Configuration Management**: Reglas de negocio configurables y externalizadas con hot-reload
- **Exception Handling**: Jerarquía de excepciones específicas del dominio cliente con contexto
- **Notification Service**: Sistema de alertas multi-canal con escalación automática y templates
- **Security Framework**: Validación de seguridad, compliance y control de acceso granular
- **Data Quality Engine**: Limpieza automática, deduplicación y optimización de datos
- **Reporting Engine**: Generación de reportes con plantillas personalizables y exportación múltiple
- **ML/AI Services**: Modelos predictivos para churn, LTV, forecasting y análisis de patrones
- **Workflow Engine**: Automatización de procesos de negocio y escalación de eventos

### Casos de Uso Principales Expandidos

- **Gestión Integral de Clientes**: Ciclo de vida completo con validaciones de negocio avanzadas y automatización
- **Análisis de Negocio**: Reportes ejecutivos, métricas de rendimiento y análisis de portafolio con IA
- **Coordinación de Dominios**: Sincronización de datos y eventos entre diferentes módulos con resolución de conflictos
- **Validación Avanzada**: Reglas de negocio complejas con contexto, dependencias y compliance
- **Gestión de Proyectos**: Transferencias inteligentes y análisis de portafolio por cliente con impacto
- **Dashboard Ejecutivo**: Datos optimizados para diferentes tipos de visualización con tiempo real
- **Búsqueda Empresarial**: Consultas complejas con enriquecimiento de datos y analytics temporales
- **Auditoría y Compliance**: Registro completo de operaciones y eventos para regulaciones y certificaciones
- **Análisis Predictivo**: Modelos de churn, LTV, growth forecasting y análisis de riesgo
- **Gestión de Calidad**: Limpieza automática de datos, deduplicación y optimización de performance
- **Análisis de Relaciones**: Mapeo de stakeholders, dependencias y redes de colaboración
- **Sistema de Alertas**: Notificaciones proactivas con escalación automática y múltiples canales
- **Reportes Especializados**: Exportación con plantillas personalizables para diferentes audiencias
- **Optimización Operacional**: Automatización de procesos, workflows y mantenimiento de datos

### Tipos de Análisis Disponibles Expandidos

**Análisis de Portafolio:**
- `comprehensive`: Análisis completo del portafolio con todas las métricas y proyecciones
- `financial`: Enfoque en métricas financieras, rentabilidad y ROI con forecasting
- `timeline`: Análisis temporal de proyectos, tendencias y patrones estacionales
- `risk`: Evaluación de riesgo del portafolio con estrategias de mitigación
- `strategic`: Análisis estratégico con posicionamiento de mercado y competencia

**Tipos de Dashboard:**
- `executive`: Vista ejecutiva de alto nivel con KPIs estratégicos y tendencias
- `operational`: Vista operacional detallada para gestión diaria y tácticas
- `financial`: Vista financiera especializada para análisis económico y presupuestario
- `compliance`: Vista de compliance con estado regulatorio y auditoría
- `predictive`: Vista predictiva con forecasting y análisis de tendencias futuras

**Tipos de Métricas:**
- `financial`: Métricas financieras, rentabilidad, ROI y valor de vida del cliente
- `project`: Métricas de proyectos, entregables y performance de ejecución
- `timeline`: Métricas temporales, cumplimiento y análisis de cronogramas
- `quality`: Métricas de calidad, satisfacción del cliente y NPS
- `engagement`: Métricas de engagement, actividad y patrones de uso
- `risk`: Métricas de riesgo, probabilidad de churn y factores de alerta
- `operational`: Métricas operacionales, eficiencia y optimización de procesos

### Tipos de Sincronización Cross-Domain Expandidos

- `full`: Sincronización completa de todos los datos del cliente con validación integral
- `incremental`: Solo cambios desde la última sincronización con delta tracking
- `selective`: Sincronización de campos específicos según configuración y permisos
- `priority`: Sincronización prioritaria de datos críticos con baja latencia
- `batch`: Sincronización en lotes para operaciones masivas con optimización

**Dominios de Sincronización:**
- `projects`: Dominio de proyectos, asignaciones y cronogramas
- `employees`: Dominio de empleados, recursos humanos y competencias
- `planning`: Dominio de planificación, scheduling y resource allocation
- `analytics`: Dominio de análisis, métricas y business intelligence
- `finance`: Dominio financiero, facturación y contabilidad
- `compliance`: Dominio de compliance, auditoría y regulaciones
- `security`: Dominio de seguridad, accesos y permisos

### Eventos del Ciclo de Vida Expandidos

**Eventos de Estado:**
- `client_created`: Cliente creado con validaciones completas y setup inicial
- `client_activated`: Cliente activado y listo para operaciones con notificaciones
- `client_suspended`: Cliente suspendido temporalmente con preservación de datos
- `client_archived`: Cliente archivado con políticas de retención aplicadas
- `client_restored`: Cliente restaurado desde archivo con validación de integridad
- `client_deleted`: Cliente eliminado con limpieza completa de datos relacionados
- `status_changed`: Cambio de estado con validación de transiciones y workflows

**Eventos de Negocio:**
- `milestone_reached`: Hito importante alcanzado con métricas de progreso
- `threshold_exceeded`: Umbral crítico excedido con alertas automáticas
- `compliance_violation`: Violación de compliance detectada con escalación
- `performance_alert`: Alerta de performance con análisis de causas
- `relationship_change`: Cambio en relaciones del cliente con impacto assessment
- `data_quality_issue`: Problema de calidad de datos detectado con corrección
- `security_event`: Evento de seguridad relacionado con el cliente

### Configuración de Alertas y Notificaciones

**Tipos de Alertas:**
- `performance`: Alertas de rendimiento y KPIs críticos
- `compliance`: Alertas de compliance y regulaciones
- `security`: Alertas de seguridad y accesos
- `financial`: Alertas financieras y presupuestarias
- `operational`: Alertas operacionales y de proceso
- `quality`: Alertas de calidad de datos y servicios

**Canales de Notificación:**
- `email`: Notificaciones por correo electrónico con templates
- `sms`: Notificaciones SMS para alertas críticas
- `webhook`: Webhooks para integración con sistemas externos
- `dashboard`: Notificaciones en dashboard con tiempo real
- `mobile`: Notificaciones push para aplicaciones móviles
- `slack`: Integración con Slack para equipos colaborativos

### Tipos de Exportación y Reportes

**Formatos de Exportación:**
- `pdf`: Reportes PDF con diseño profesional y branding
- `excel`: Hojas de cálculo Excel con múltiples pestañas y gráficos
- `csv`: Archivos CSV para análisis de datos y importación
- `json`: Formato JSON para integración con APIs y sistemas
- `xml`: Formato XML para intercambio de datos estructurados
- `interactive`: Dashboards interactivos con drill-down capabilities

**Tipos de Reportes:**
- `executive`: Reportes ejecutivos con resumen estratégico y KPIs
- `operational`: Reportes operacionales detallados para gestión diaria
- `financial`: Reportes financieros con análisis de rentabilidad y costos
- `compliance`: Reportes de compliance con evidencia y documentación
- `audit`: Reportes de auditoría con trail completo y trazabilidad
- `analytical`: Reportes analíticos con insights y recomendaciones

---

**Ubicación**: `src/planificador/services/domain/client/client_domain_service.py`
**Versión del servicio**: 2.0.0
**Autor**: Planificador Development Team
**Última revisión**: Enero 2025