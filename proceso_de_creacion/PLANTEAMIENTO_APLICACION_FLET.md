# Planteamiento: Aplicación de Gestión de Planificación de Equipos con Flet

## 1. Análisis del Dominio

### Datos Identificados en el Excel

#### Hoja "Planning" - Estructura Principal (52 columnas identificadas)
**Información de Proyectos (Columnas A-K):**
- Référence projet, TRI-GRAMME, Nom du projet/Centrale
- JOB, CLIENT, Dates d'arrêt
- Personnel, Formation spéciale, Durée
- Auteur MAJ, Date MAJ

**Equipos y Fechas (Columnas AK-AZ):**
- EQUIPE (asignación de equipos)
- Columnas de fechas mensuales: JANVIER 22, FEVRIER 22, etc.

#### Otras Hojas del Excel
- **Légende**: Códigos de estado y colores para visualización
- **Personnel**: Datos detallados de empleados por meses
- **Congés 2022**: Gestión de períodos de vacaciones
- **Charge 2022/2023**: Distribución de cargas de trabajo

### Entidades Principales Identificadas
1. **Cliente** (Client) - Gestión de empresas contratantes
2. **Proyecto** (Project) - Información completa de proyectos
3. **Empleado** (Employee) - Personal con cualificaciones
4. **Equipo** (Team) - Grupos de trabajo especializados
5. **Membresía de Equipo** (TeamMembership) - Relación empleado-equipo
6. **Asignación de Proyecto** (ProjectAssignment) - Relación empleado-proyecto
7. **Planificación** (Schedule) - Horarios diarios
8. **Código de Estado** (StatusCode) - Estados configurables
9. **Vacaciones** (Vacation) - Gestión de ausencias
10. **Carga de Trabajo** (Workload) - Métricas de productividad
11. **Registro de Cambios** (ChangeLog) - Auditoría completa
12. **Alertas** (Alert) - Sistema de notificaciones

## 2. Arquitectura de la Aplicación

### 2.1 Estructura de Módulos
```
src/
├── planificador/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuración con Pydantic
│   │   └── database.py        # Configuración de BD
│   ├── models/
│   │   ├── __init__.py
│   │   ├── client.py         # Modelo Cliente
│   │   ├── project.py        # Modelo Proyecto
│   │   ├── employee.py       # Modelo Empleado
│   │   ├── team.py           # Modelo Equipo
│   │   ├── team_membership.py # Modelo Membresía de Equipo
│   │   ├── project_assignment.py # Modelo Asignación de Proyecto
│   │   ├── schedule.py       # Modelo Planificación
│   │   ├── status_code.py    # Modelo Códigos de Estado
│   │   ├── vacation.py       # Modelo Vacaciones
│   │   ├── workload.py       # Modelo Carga de Trabajo
│   │   ├── change_log.py     # Modelo Registro de Cambios
│   │   └── alert.py          # Modelo Alertas
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py     # Gestión de conexiones
│   │   ├── repositories/     # Patrón Repository
│   │   │   ├── __init__.py
│   │   │   ├── client_repository.py
│   │   │   ├── project_repository.py
│   │   │   ├── employee_repository.py
│   │   │   ├── team_repository.py
│   │   │   ├── team_membership_repository.py
│   │   │   ├── project_assignment_repository.py
│   │   │   ├── schedule_repository.py
│   │   │   ├── status_code_repository.py
│   │   │   ├── vacation_repository.py
│   │   │   ├── workload_repository.py
│   │   │   ├── change_log_repository.py
│   │   │   └── alert_repository.py
│   │   └── migrations/       # Scripts de migración
│   ├── services/
│   │   ├── __init__.py
│   │   ├── client_service.py
│   │   ├── project_service.py
│   │   ├── employee_service.py
│   │   ├── team_service.py
│   │   ├── team_membership_service.py
│   │   ├── project_assignment_service.py
│   │   ├── schedule_service.py
│   │   ├── status_code_service.py
│   │   ├── vacation_service.py
│   │   ├── workload_service.py
│   │   ├── change_log_service.py
│   │   ├── alert_service.py
│   │   ├── validation_service.py # Validaciones de negocio
│   │   ├── conflict_detection_service.py # Detección de conflictos
│   │   └── export_service.py # Exportación de datos
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_app.py       # Aplicación principal Flet
│   │   ├── components/       # Componentes reutilizables
│   │   │   ├── __init__.py
│   │   │   ├── common/       # Componentes comunes
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_card.py
│   │   │   │   ├── data_table.py
│   │   │   │   ├── form_builder.py
│   │   │   │   ├── search_bar.py
│   │   │   │   ├── filter_panel.py
│   │   │   │   ├── pagination.py
│   │   │   │   ├── loading_spinner.py
│   │   │   │   ├── confirmation_dialog.py
│   │   │   │   ├── error_display.py
│   │   │   │   └── success_message.py
│   │   │   ├── navigation/   # Componentes de navegación
│   │   │   │   ├── __init__.py
│   │   │   │   ├── sidebar.py
│   │   │   │   ├── breadcrumb.py
│   │   │   │   ├── tab_navigator.py
│   │   │   │   └── menu_item.py
│   │   │   ├── forms/        # Componentes de formularios
│   │   │   │   ├── __init__.py
│   │   │   │   ├── entity_form_builder.py
│   │   │   │   ├── validation_feedback.py
│   │   │   │   ├── duplicate_detector.py
│   │   │   │   ├── auto_complete.py
│   │   │   │   ├── date_picker.py
│   │   │   │   ├── date_range_picker.py
│   │   │   │   ├── time_picker.py
│   │   │   │   ├── multi_select.py
│   │   │   │   ├── file_upload.py
│   │   │   │   └── form_validator.py
│   │   │   ├── data_display/ # Componentes de visualización
│   │   │   │   ├── __init__.py
│   │   │   │   ├── employee_card.py
│   │   │   │   ├── project_card.py
│   │   │   │   ├── client_card.py
│   │   │   │   ├── team_card.py
│   │   │   │   ├── qualification_badge.py
│   │   │   │   ├── status_badge.py
│   │   │   │   ├── priority_indicator.py
│   │   │   │   ├── availability_indicator.py
│   │   │   │   ├── progress_bar.py
│   │   │   │   └── metric_card.py
│   │   │   ├── scheduling/   # Componentes de planificación
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schedule_grid.py
│   │   │   │   ├── calendar_view.py
│   │   │   │   ├── timeline_view.py
│   │   │   │   ├── gantt_chart.py
│   │   │   │   ├── conflict_detector.py
│   │   │   │   ├── assignment_panel.py
│   │   │   │   ├── workload_chart.py
│   │   │   │   ├── resource_allocator.py
│   │   │   │   └── schedule_optimizer.py
│   │   │   ├── alerts/       # Componentes de alertas
│   │   │   │   ├── __init__.py
│   │   │   │   ├── alert_center.py
│   │   │   │   ├── notification_badge.py
│   │   │   │   ├── alert_panel.py
│   │   │   │   ├── priority_filter.py
│   │   │   │   ├── alert_config_panel.py
│   │   │   │   ├── conflict_resolver.py
│   │   │   │   └── notification_center.py
│   │   │   ├── audit/        # Componentes de auditoría
│   │   │   │   ├── __init__.py
│   │   │   │   ├── audit_viewer.py
│   │   │   │   ├── change_log_viewer.py
│   │   │   │   ├── change_tracker.py
│   │   │   │   ├── audit_search.py
│   │   │   │   ├── rollback_dialog.py
│   │   │   │   └── audit_export.py
│   │   │   ├── reports/      # Componentes de reportes
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chart_builder.py
│   │   │   │   ├── report_generator.py
│   │   │   │   ├── export_dialog.py
│   │   │   │   ├── dashboard_widget.py
│   │   │   │   ├── kpi_card.py
│   │   │   │   ├── trend_chart.py
│   │   │   │   └── data_visualizer.py
│   │   │   └── management/   # Componentes de gestión
│   │   │       ├── __init__.py
│   │   │       ├── team_membership_manager.py
│   │   │       ├── project_assignment_panel.py
│   │   │       ├── vacation_calendar.py
│   │   │       ├── status_legend.py
│   │   │       ├── team_selector.py
│   │   │       ├── client_selector.py
│   │   │       ├── employee_selector.py
│   │   │       └── bulk_operations.py
│   │   └── views/           # Vistas principales
│   │       ├── __init__.py
│   │       ├── main/         # Vistas principales
│   │       │   ├── __init__.py
│   │       │   ├── dashboard.py
│   │       │   ├── home.py
│   │       │   └── welcome.py
│   │       ├── clients/      # Gestión de clientes
│   │       │   ├── __init__.py
│   │       │   ├── client_list.py
│   │       │   ├── client_form.py
│   │       │   ├── client_detail.py
│   │       │   └── client_projects.py
│   │       ├── projects/     # Gestión de proyectos
│   │       │   ├── __init__.py
│   │       │   ├── project_list.py
│   │       │   ├── project_form.py
│   │       │   ├── project_detail.py
│   │       │   ├── project_assignments.py
│   │       │   ├── project_timeline.py
│   │       │   └── project_analytics.py
│   │       ├── employees/    # Gestión de empleados
│   │       │   ├── __init__.py
│   │       │   ├── employee_list.py
│   │       │   ├── employee_form.py
│   │       │   ├── employee_detail.py
│   │       │   ├── employee_schedule.py
│   │       │   ├── employee_assignments.py
│   │       │   ├── employee_qualifications.py
│   │       │   └── employee_history.py
│   │       ├── teams/        # Gestión de equipos
│   │       │   ├── __init__.py
│   │       │   ├── team_list.py
│   │       │   ├── team_form.py
│   │       │   ├── team_detail.py
│   │       │   ├── team_members.py
│   │       │   ├── team_schedule.py
│   │       │   └── team_performance.py
│   │       ├── scheduling/   # Planificación
│   │       │   ├── __init__.py
│   │       │   ├── schedule_calendar.py
│   │       │   ├── schedule_grid.py
│   │       │   ├── schedule_timeline.py
│   │       │   ├── resource_planning.py
│   │       │   ├── conflict_resolution.py
│   │       │   ├── bulk_scheduling.py
│   │       │   └── schedule_optimization.py
│   │       ├── vacations/    # Gestión de vacaciones
│   │       │   ├── __init__.py
│   │       │   ├── vacation_list.py
│   │       │   ├── vacation_form.py
│   │       │   ├── vacation_calendar.py
│   │       │   ├── vacation_approvals.py
│   │       │   ├── vacation_policies.py
│   │       │   └── vacation_analytics.py
│   │       ├── workload/     # Gestión de cargas de trabajo
│   │       │   ├── __init__.py
│   │       │   ├── workload_dashboard.py
│   │       │   ├── workload_analysis.py
│   │       │   ├── capacity_planning.py
│   │       │   ├── utilization_reports.py
│   │       │   └── efficiency_metrics.py
│   │       ├── alerts/       # Centro de alertas
│   │       │   ├── __init__.py
│   │       │   ├── alert_dashboard.py
│   │       │   ├── alert_list.py
│   │       │   ├── alert_configuration.py
│   │       │   ├── notification_center.py
│   │       │   └── conflict_management.py
│   │       ├── audit/        # Auditoría y seguimiento
│   │       │   ├── __init__.py
│   │       │   ├── audit_dashboard.py
│   │       │   ├── change_history.py
│   │       │   ├── audit_search.py
│   │       │   ├── compliance_reports.py
│   │       │   └── rollback_management.py
│   │       ├── reports/      # Reportes y analytics
│   │       │   ├── __init__.py
│   │       │   ├── report_dashboard.py
│   │       │   ├── project_reports.py
│   │       │   ├── employee_reports.py
│   │       │   ├── team_reports.py
│   │       │   ├── client_reports.py
│   │       │   ├── workload_reports.py
│   │       │   ├── efficiency_reports.py
│   │       │   └── custom_reports.py
│   │       ├── configuration/ # Configuración del sistema
│   │       │   ├── __init__.py
│   │       │   ├── system_config.py
│   │       │   ├── status_codes.py
│   │       │   ├── qualifications.py
│   │       │   ├── alert_settings.py
│   │       │   ├── user_preferences.py
│   │       │   └── data_export.py
│   │       └── setup/        # Configuración inicial
│   │           ├── __init__.py
│   │           ├── setup_wizard.py
│   │           ├── initial_config.py
│   │           ├── data_migration.py
│   │           └── system_validation.py
│   └── utils/
│       ├── __init__.py
│       ├── date_utils.py     # Utilidades de fecha
│       ├── validators.py     # Validaciones personalizadas
│       ├── formatters.py     # Formateo de datos
│       ├── constants.py      # Constantes del sistema
│       ├── helpers.py        # Funciones auxiliares
│       ├── excel_utils.py    # Utilidades para Excel
│       ├── color_utils.py    # Utilidades de colores
│       ├── security_utils.py # Utilidades de seguridad
│       └── performance_utils.py # Utilidades de rendimiento
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Configuración de pytest
│   ├── test_models/         # Tests de modelos
│   │   ├── __init__.py
│   │   ├── test_client.py
│   │   ├── test_project.py
│   │   ├── test_employee.py
│   │   ├── test_team.py
│   │   ├── test_schedule.py
│   │   └── test_integrations.py
│   ├── test_services/       # Tests de servicios
│   │   ├── __init__.py
│   │   ├── test_client_service.py
│   │   ├── test_project_service.py
│   │   ├── test_employee_service.py
│   │   ├── test_schedule_service.py
│   │   └── test_validation_service.py
│   ├── test_repositories/   # Tests de repositorios
│   │   ├── __init__.py
│   │   └── test_base_repository.py
│   ├── test_ui/            # Tests de UI
│   │   ├── __init__.py
│   │   ├── test_components.py
│   │   └── test_views.py
│   └── test_utils/         # Tests de utilidades
│       ├── __init__.py
│       ├── test_date_utils.py
│       └── test_validators.py
├── docs/                   # Documentación
│   ├── README.md
│   ├── INSTALLATION.md
│   ├── USER_GUIDE.md
│   ├── API_REFERENCE.md
│   └── DEPLOYMENT.md
├── scripts/               # Scripts de utilidad
│   ├── setup_db.py       # Configuración inicial de BD
│   ├── migrate_data.py    # Migración de datos
│   ├── backup_db.py       # Respaldo de base de datos
│   └── generate_reports.py # Generación de reportes
├── pyproject.toml        # Configuración de Poetry y proyecto
├── poetry.lock           # Lock file de Poetry
├── .env.example          # Ejemplo de variables de entorno
├── .gitignore
├── pytest.ini           # Configuración de pytest
├── alembic.ini          # Configuración de Alembic
└── main.py
```

### 2.2 Tecnologías Principales
- **Poetry**: Gestor de dependencias y entornos virtuales
- **Flet**: Framework UI multiplataforma
- **SQLAlchemy**: ORM para base de datos
- **Pydantic**: Validación de datos y configuración
- **Loguru**: Logging estructurado
- **Alembic**: Migraciones de base de datos
- **Pendulum**: Manejo avanzado de fechas y horas
- **Pytest**: Framework de testing
- **Ruff**: Linting y formateo de código

## 3. Diseño de Base de Datos

### 3.1 Esquema Principal Actualizado

Basado en el análisis detallado del Excel, el esquema incluye las siguientes entidades principales:

#### Entidades Identificadas:
1. **Clientes** - Gestión de empresas contratantes
2. **Proyectos** - Información completa con referencias, trigramas y metadatos
3. **Empleados** - 24 empleados identificados con cualificaciones completas
4. **Equipos** - Gestión de grupos de trabajo especializados
5. **Membresías de Equipo** - Relación empleado-equipo con roles
6. **Asignaciones de Proyecto** - Relación empleado-proyecto con dedicación
7. **Planificación** - Horarios diarios con códigos de estado
8. **Códigos de Estado** - Estados configurables con colores
9. **Vacaciones** - Gestión completa de ausencias con aprobaciones
10. **Cargas de Trabajo** - Métricas de productividad y eficiencia
11. **Registro de Cambios** - Auditoría completa de modificaciones
12. **Alertas** - Sistema inteligente de notificaciones y conflictos

#### Características Principales del Diseño:
- **Normalización completa** con relaciones bien definidas
- **Flexibilidad** para asignaciones múltiples (empleado puede estar en varios equipos/proyectos)
- **Auditoría completa** con timestamps y usuarios responsables
- **Optimización** con índices para consultas frecuentes
- **Validaciones** a nivel de base de datos y aplicación
- **Escalabilidad** para crecimiento futuro

> **Nota**: Para el esquema SQL completo y modelos SQLAlchemy detallados, consultar el documento [`MODELOS_BASE_DATOS.md`](./MODELOS_BASE_DATOS.md)

### 3.2 Relaciones Principales

```
Client (1) -----> (N) Project
Project (1) -----> (N) ProjectAssignment (N) <----- (1) Employee
Employee (1) -----> (N) TeamMembership (N) <----- (1) Team
Employee (1) -----> (N) Schedule
Schedule (N) -----> (1) StatusCode
Schedule (N) -----> (1) Team [opcional]
Schedule (N) -----> (1) Project [opcional]
Employee (1) -----> (N) Vacation
Employee (1) -----> (N) Workload
```

## 4. Funcionalidades Principales

### 4.1 Módulo de Gestión de Datos
- **Entrada manual de datos** con formularios intuitivos
- **Validación en tiempo real** de estructura y formato
- **Gestión manual de empleados** con información completa
- **Creación de proyectos** con referencias y trigramas únicos
- **Validación de datos en tiempo real**
- **Manejo de errores y validaciones inmediatas**
- **Configuración de cualificaciones del personal** (HN1, HN2, etc.)
- **Creación manual de códigos de estado** con colores personalizables
- **Formularios especializados** para cada entidad del sistema

### 4.2 Gestión de Proyectos y Clientes
- **CRUD completo de proyectos** con referencias únicas
- **Gestión de trigramas** y códigos de proyecto
- **Administración de clientes** y contactos
- **Seguimiento de fechas de parada** y mantenimiento
- **Gestión de formación especial** requerida
- **Control de duración** y metadatos de proyectos

### 4.3 Gestión de Empleados
- **CRUD completo de empleados**
- **Búsqueda y filtrado avanzado** por nombre, código, equipo, cualificación
- **Gestión de cualificaciones del personal** (HN1 montadores, HN2 supervisores, etc.)
- **Control de formación especial** y certificaciones requeridas
- **Gestión de asignaciones múltiples** (equipos y proyectos)
- **Historial de cambios** y auditoría completa
- **Gestión de estados** (activo/inactivo/disponible)
- **Seguimiento de disponibilidad** en tiempo real

### 4.4 Planificación Visual Avanzada
- **Vista de calendario interactivo** con códigos de color configurables
- **Sistema de códigos de color** (verde: presencia en sitio, azul: viajando, etc.)
- **Indicadores visuales** para disponibilidad incierta del personal
- **Drag & drop para asignaciones** de empleados con validación
- **Vista por equipos, proyectos y empleados**
- **Códigos de estado configurables** desde hoja "Légende"
- **Filtros múltiples** (fecha, equipo, empleado, proyecto, cliente, cualificación)
- **Detección automática de conflictos** de asignaciones
- **Vista mensual/semanal/diaria** con días laborables y festivos
- **Alertas y notificaciones** cuando falta personal requerido
- **Cálculo automático** de tiempo de intervención y días de preparación

### 4.5 Gestión de Equipos
- **Administración de equipos** con códigos de color
- **Membresías flexibles** (empleado en múltiples equipos)
- **Roles dentro del equipo** (líder, miembro, especialista)
- **Historial de membresías** con fechas de inicio/fin
- **Capacidad máxima** por equipo

### 4.6 Gestión de Vacaciones
- **Solicitud y aprobación** de vacaciones
- **Múltiples tipos** (anuales, enfermedad, personales, maternidad)
- **Vista de conflictos** de planificación
- **Cálculo automático** de días laborables
- **Notificaciones** de vencimientos y aprobaciones
- **Integración** con planificación diaria

### 4.7 Sistema de Auditoría Completa (ChangeLog)
- **Registro automático** de todos los cambios en el sistema
- **Trazabilidad completa** por entidad (empleado, proyecto, equipo, etc.)
- **Información detallada**: qué cambió, valor anterior, valor nuevo
- **Metadatos de auditoría**: usuario, fecha, IP, navegador
- **Historial inmutable** para cumplimiento normativo
- **Búsqueda avanzada** por entidad, usuario, fecha o tipo de cambio
- **Reportes de auditoría** exportables
- **Rollback inteligente** para revertir cambios críticos

### 4.8 Sistema de Alertas Inteligentes (Alert)
- **Detección automática** de conflictos de planificación
- **Alertas de personal insuficiente** por cualificación
- **Notificaciones de sobreasignación** de recursos
- **Advertencias de fechas límite** de proyectos
- **Alertas de validación** y errores de datos
- **Sistema de prioridades**: baja, media, alta, crítica
- **Centro de notificaciones** centralizado
- **Acknowledgment tracking** (quién vio qué alerta)
- **Resolución automática** de alertas cuando se corrige el problema
- **Configuración personalizable** de tipos de alerta

### 4.9 Reportes y Analytics
- **Reportes de carga de trabajo** por empleado/equipo/proyecto
- **Análisis de eficiencia** y utilización por cualificación
- **Métricas de productividad** mensuales y por proyecto
- **Seguimiento de horas** (planificadas vs reales)
- **Reportes de disponibilidad** de personal por cualificación
- **Análisis de alertas** y notificaciones generadas
- **Exportación a Excel/PDF** con formatos personalizables
- **Gráficos de tendencias** y dashboards interactivos
- **Reportes de asignaciones** por proyecto/cliente/cualificación

## 5. Interfaz de Usuario (Flet)

### 5.1 Estructura de Navegación
```
🏠 Inicio
├── 📊 Dashboard Principal
│   ├── 📈 Métricas Generales
│   ├── 🚨 Alertas Activas
│   ├── 📅 Próximos Vencimientos
│   └── 📊 Resumen de Proyectos
├── 🎉 Bienvenida
└── 🏠 Página de Inicio

🏢 Clientes
├── 📝 Lista de Clientes
│   ├── 🔍 Búsqueda y Filtros
│   ├── 📊 Vista de Tarjetas
│   └── 📋 Vista de Tabla
├── ➕ Formulario de Cliente
│   ├── ✅ Validación en Tiempo Real
│   ├── 🔍 Detección de Duplicados
│   └── 💾 Guardado Automático
├── 👁️ Detalle de Cliente
│   ├── 📊 Información General
│   ├── 📈 Métricas del Cliente
│   └── 📋 Historial de Cambios
└── 📁 Proyectos del Cliente
    ├── 📝 Lista de Proyectos Activos
    ├── 📊 Análisis de Rentabilidad
    └── 📈 Tendencias Históricas

📁 Proyectos
├── 📝 Lista de Proyectos
│   ├── 🔍 Búsqueda Avanzada
│   ├── 🏷️ Filtros por Estado
│   ├── 📊 Vista de Tarjetas
│   └── 📋 Vista de Tabla
├── ➕ Formulario de Proyecto
│   ├── 🏢 Selector de Cliente
│   ├── 📅 Planificación de Fechas
│   ├── 💰 Gestión de Presupuesto
│   └── 🎯 Definición de Objetivos
├── 👁️ Detalle de Proyecto
│   ├── 📊 Información General
│   ├── 📈 Progreso del Proyecto
│   ├── 💰 Estado Financiero
│   └── 📋 Documentación
├── 👥 Asignaciones del Proyecto
│   ├── 👤 Empleados Asignados
│   ├── 🏷️ Roles y Responsabilidades
│   ├── ⏱️ Distribución de Tiempo
│   └── 📊 Carga de Trabajo
├── ⏱️ Línea de Tiempo
│   ├── 📅 Hitos del Proyecto
│   ├── 🎯 Entregables
│   ├── ⚠️ Riesgos Identificados
│   └── 📈 Progreso Visual
└── 📊 Análisis del Proyecto
    ├── 📈 Métricas de Rendimiento
    ├── 💰 Análisis Financiero
    ├── ⏱️ Análisis de Tiempo
    └── 🎯 Cumplimiento de Objetivos

👥 Empleados
├── 📝 Lista de Empleados
│   ├── 🔍 Búsqueda por Habilidades
│   ├── 🏷️ Filtros por Departamento
│   ├── 📊 Vista de Tarjetas
│   └── 📋 Vista de Tabla
├── ➕ Formulario de Empleado
│   ├── 👤 Información Personal
│   ├── 🎯 Calificaciones y Habilidades
│   ├── 📞 Información de Contacto
│   └── 💼 Información Laboral
├── 👁️ Detalle de Empleado
│   ├── 📊 Perfil Completo
│   ├── 🎯 Matriz de Habilidades
│   ├── 📈 Métricas de Rendimiento
│   └── 📋 Información de Contacto
├── 📅 Horario del Empleado
│   ├── 📅 Vista Semanal
│   ├── 📅 Vista Mensual
│   ├── ⏱️ Distribución de Tiempo
│   └── 🚨 Conflictos de Horario
├── 📁 Asignaciones del Empleado
│   ├── 📁 Proyectos Activos
│   ├── 👥 Equipos Participantes
│   ├── 🎯 Roles Asignados
│   └── 📊 Carga de Trabajo
├── 🎯 Calificaciones
│   ├── 🏷️ Habilidades Técnicas
│   ├── 🏷️ Habilidades Blandas
│   ├── 📈 Nivel de Competencia
│   └── 📅 Certificaciones
└── 📋 Historial del Empleado
    ├── 📁 Proyectos Anteriores
    ├── 📈 Evolución de Rendimiento
    ├── 🎯 Desarrollo de Habilidades
    └── 📋 Registro de Cambios

👥 Equipos
├── 📝 Lista de Equipos
│   ├── 🔍 Búsqueda por Proyecto
│   ├── 🏷️ Filtros por Estado
│   ├── 📊 Vista de Tarjetas
│   └── 📋 Vista de Tabla
├── ➕ Formulario de Equipo
│   ├── 📁 Asociación con Proyecto
│   ├── 👤 Selección de Líder
│   ├── 🎯 Definición de Objetivos
│   └── 📅 Planificación Temporal
├── 👁️ Detalle de Equipo
│   ├── 📊 Información General
│   ├── 👥 Composición del Equipo
│   ├── 📈 Métricas de Rendimiento
│   └── 🎯 Objetivos y Metas
├── 👥 Miembros del Equipo
│   ├── 👤 Lista de Miembros
│   ├── 🎯 Roles y Responsabilidades
│   ├── ➕ Agregar Miembros
│   └── ➖ Remover Miembros
├── 📅 Horario del Equipo
│   ├── 📅 Vista Consolidada
│   ├── 👥 Disponibilidad de Miembros
│   ├── 🚨 Conflictos de Horario
│   └── 📊 Distribución de Carga
└── 📊 Rendimiento del Equipo
    ├── 📈 Métricas de Productividad
    ├── 🎯 Cumplimiento de Objetivos
    ├── 👥 Colaboración Interna
    └── 📊 Análisis Comparativo

📅 Planificación
├── 📅 Vista Calendario
│   ├── 📅 Vista Mensual
│   ├── 📅 Vista Semanal
│   ├── 📅 Vista Diaria
│   └── 🔍 Filtros Avanzados
├── 📊 Vista de Cuadrícula
│   ├── 👥 Matriz Empleado-Proyecto
│   ├── ⏱️ Distribución Temporal
│   ├── 🎨 Codificación por Colores
│   └── 📊 Indicadores de Carga
├── ⏱️ Vista de Línea de Tiempo
│   ├── 📁 Cronograma de Proyectos
│   ├── 🎯 Hitos Importantes
│   ├── ⚠️ Dependencias Críticas
│   └── 📈 Progreso Visual
├── 🎯 Planificación de Recursos
│   ├── 👥 Disponibilidad de Empleados
│   ├── 🎯 Matching de Habilidades
│   ├── 📊 Optimización de Carga
│   └── 💰 Análisis de Costos
├── ⚠️ Resolución de Conflictos
│   ├── 🚨 Detección Automática
│   ├── 💡 Sugerencias de Resolución
│   ├── 🔄 Reasignación Automática
│   └── 📋 Registro de Conflictos
├── 🔄 Planificación Masiva
│   ├── 📁 Asignación por Proyecto
│   ├── 👥 Asignación por Equipo
│   ├── 📅 Asignación por Período
│   └── 🎯 Asignación por Habilidades
└── 🎯 Optimización de Horarios
    ├── 🤖 Algoritmos de Optimización
    ├── 📊 Análisis de Eficiencia
    ├── 💡 Recomendaciones Inteligentes
    └── 📈 Métricas de Mejora

🏖️ Vacaciones
├── 📝 Lista de Vacaciones
│   ├── 🔍 Búsqueda por Empleado
│   ├── 🏷️ Filtros por Estado
│   ├── 📅 Filtros por Fecha
│   └── 📊 Vista de Calendario
├── ➕ Solicitud de Vacaciones
│   ├── 👤 Selección de Empleado
│   ├── 📅 Selección de Fechas
│   ├── 📝 Motivo de la Solicitud
│   └── 🚨 Validación de Conflictos
├── 📅 Calendario de Vacaciones
│   ├── 📅 Vista Mensual
│   ├── 👥 Vista por Empleado
│   ├── 👥 Vista por Equipo
│   └── 📁 Vista por Proyecto
├── ✅ Aprobaciones de Vacaciones
│   ├── 📋 Solicitudes Pendientes
│   ├── ✅ Proceso de Aprobación
│   ├── ❌ Proceso de Rechazo
│   └── 📧 Notificaciones Automáticas
├── 📋 Políticas de Vacaciones
│   ├── 📅 Días Disponibles
│   ├── 🏷️ Tipos de Vacaciones
│   ├── 📋 Reglas de Aprobación
│   └── 🚨 Restricciones Especiales
└── 📊 Análisis de Vacaciones
    ├── 📈 Tendencias de Uso
    ├── 👥 Análisis por Empleado
    ├── 📅 Análisis Estacional
    └── 📊 Impacto en Proyectos

📊 Carga de Trabajo
├── 📊 Dashboard de Carga
│   ├── 📈 Métricas Generales
│   ├── 🚨 Alertas de Sobrecarga
│   ├── 👥 Vista por Empleado
│   └── 📁 Vista por Proyecto
├── 📈 Análisis de Carga
│   ├── 📊 Distribución Actual
│   ├── 📈 Tendencias Históricas
│   ├── 🎯 Puntos de Saturación
│   └── 💡 Recomendaciones
├── 🎯 Planificación de Capacidad
│   ├── 📅 Proyección Futura
│   ├── 👥 Necesidades de Personal
│   ├── 🎯 Optimización de Recursos
│   └── 💰 Análisis de Costos
├── 📊 Reportes de Utilización
│   ├── 👥 Utilización por Empleado
│   ├── 📁 Utilización por Proyecto
│   ├── 👥 Utilización por Equipo
│   └── 📅 Utilización Temporal
└── 📈 Métricas de Eficiencia
    ├── 🎯 Productividad Individual
    ├── 👥 Productividad de Equipos
    ├── 📁 Eficiencia de Proyectos
    └── 📊 Benchmarking Interno

🚨 Centro de Alertas
├── 📊 Dashboard de Alertas
│   ├── 🚨 Alertas Críticas
│   ├── ⚠️ Alertas de Advertencia
│   ├── ℹ️ Alertas Informativas
│   └── 📈 Tendencias de Alertas
├── 📋 Lista de Alertas
│   ├── 🔍 Búsqueda y Filtros
│   ├── 🏷️ Filtros por Prioridad
│   ├── 📅 Filtros por Fecha
│   └── 👤 Filtros por Responsable
├── ⚙️ Configuración de Alertas
│   ├── 🎯 Reglas de Negocio
│   ├── 🚨 Umbrales de Alerta
│   ├── 📧 Configuración de Notificaciones
│   └── 👥 Asignación de Responsables
├── 🔔 Centro de Notificaciones
│   ├── 📧 Notificaciones por Email
│   ├── 📱 Notificaciones Push
│   ├── 📋 Historial de Notificaciones
│   └── ⚙️ Preferencias de Usuario
└── ⚠️ Gestión de Conflictos
    ├── 🚨 Detección de Conflictos
    ├── 💡 Sugerencias de Resolución
    ├── 🔄 Proceso de Escalación
    └── 📋 Registro de Resoluciones

📊 Auditoría y Seguimiento
├── 📊 Dashboard de Auditoría
│   ├── 📈 Actividad Reciente
│   ├── 👥 Actividad por Usuario
│   ├── 📋 Cambios por Entidad
│   └── 🚨 Eventos Críticos
├── 📋 Historial de Cambios
│   ├── 🔍 Búsqueda Avanzada
│   ├── 📅 Filtros Temporales
│   ├── 👤 Filtros por Usuario
│   └── 📋 Filtros por Entidad
├── 🔍 Búsqueda de Auditoría
│   ├── 🔍 Búsqueda de Texto Completo
│   ├── 🏷️ Búsqueda por Etiquetas
│   ├── 📅 Búsqueda por Rango de Fechas
│   └── 👤 Búsqueda por Actor
├── 📊 Reportes de Cumplimiento
│   ├── 📋 Reportes Regulatorios
│   ├── 🎯 Métricas de Cumplimiento
│   ├── 📈 Tendencias de Cumplimiento
│   └── 🚨 Violaciones Detectadas
└── ↩️ Gestión de Rollback
    ├── 📋 Puntos de Restauración
    ├── ↩️ Proceso de Rollback
    ├── ✅ Validación de Rollback
    └── 📋 Historial de Rollbacks

📊 Reportes y Analytics
├── 📊 Dashboard de Reportes
│   ├── 📈 KPIs Principales
│   ├── 📊 Widgets Personalizables
│   ├── 📅 Métricas en Tiempo Real
│   └── 📈 Tendencias Ejecutivas
├── 📁 Reportes de Proyectos
│   ├── 📊 Estado de Proyectos
│   ├── 💰 Análisis Financiero
│   ├── ⏱️ Análisis de Tiempo
│   └── 🎯 Cumplimiento de Objetivos
├── 👥 Reportes de Empleados
│   ├── 📊 Rendimiento Individual
│   ├── 🎯 Desarrollo de Habilidades
│   ├── 📅 Utilización de Tiempo
│   └── 📈 Evolución Profesional
├── 👥 Reportes de Equipos
│   ├── 📊 Productividad de Equipos
│   ├── 👥 Dinámicas de Colaboración
│   ├── 🎯 Cumplimiento de Metas
│   └── 📈 Evolución del Rendimiento
├── 🏢 Reportes de Clientes
│   ├── 📊 Satisfacción del Cliente
│   ├── 💰 Rentabilidad por Cliente
│   ├── 📈 Crecimiento de Cuenta
│   └── 🎯 Cumplimiento de SLAs
├── 📊 Reportes de Carga de Trabajo
│   ├── 📈 Análisis de Utilización
│   ├── 🚨 Detección de Sobrecargas
│   ├── 🎯 Optimización de Recursos
│   └── 📊 Balanceamiento de Carga
├── 📈 Reportes de Eficiencia
│   ├── 🎯 Métricas de Productividad
│   ├── 💰 Análisis Costo-Beneficio
│   ├── ⏱️ Optimización de Tiempo
│   └── 📊 Benchmarking Competitivo
└── 🛠️ Reportes Personalizados
    ├── 🎨 Constructor de Reportes
    ├── 📊 Plantillas Predefinidas
    ├── 📅 Programación Automática
    └── 📤 Exportación Múltiple

⚙️ Configuración del Sistema
├── 🖥️ Configuración General
│   ├── 🏢 Información de la Empresa
│   ├── 🌐 Configuración Regional
│   ├── 📅 Configuración de Calendario
│   └── 💾 Configuración de Backup
├── 📋 Códigos de Estado
│   ├── 📝 Lista de Estados
│   ├── ➕ Crear Nuevo Estado
│   ├── ✏️ Editar Estados
│   └── 🎨 Configuración Visual
├── 🎯 Gestión de Calificaciones
│   ├── 📝 Lista de Calificaciones
│   ├── ➕ Crear Nueva Calificación
│   ├── 📊 Niveles de Competencia
│   └── 🏷️ Categorización
├── 🚨 Configuración de Alertas
│   ├── 🎯 Reglas de Negocio
│   ├── 🚨 Umbrales Críticos
│   ├── 📧 Plantillas de Notificación
│   └── 👥 Asignación de Responsables
├── 👤 Preferencias de Usuario
│   ├── 🎨 Personalización de UI
│   ├── 🔔 Configuración de Notificaciones
│   ├── 📅 Preferencias de Calendario
│   └── 🌐 Configuración de Idioma
└── 📤 Exportación de Datos
    ├── 📊 Exportación de Reportes
    ├── 💾 Backup de Datos
    ├── 📋 Configuración de Formatos
    └── 📅 Programación de Exportaciones

🛠️ Configuración Inicial
├── 🧙‍♂️ Asistente de Configuración
│   ├── 🏢 Configuración de Empresa
│   ├── 👤 Configuración de Usuarios
│   ├── 📋 Configuración de Estados
│   └── 🎯 Configuración de Calificaciones
├── ⚙️ Configuración Inicial
│   ├── 💾 Configuración de Base de Datos
│   ├── 🔐 Configuración de Seguridad
│   ├── 📧 Configuración de Email
│   └── 🌐 Configuración de Red
├── 📦 Migración de Datos
│   ├── 📤 Importación de Datos
│   ├── 🔄 Transformación de Datos
│   ├── ✅ Validación de Datos
│   └── 📋 Reporte de Migración
└── ✅ Validación del Sistema
    ├── 🧪 Pruebas de Conectividad
    ├── 📊 Validación de Datos
    ├── 🔐 Pruebas de Seguridad
    └── 📋 Reporte de Validación
```

### 5.2 Componentes Clave del Sistema

#### Componentes Comunes
- **BaseCard**: Componente base para todas las tarjetas del sistema
- **DataTable**: Tabla de datos reutilizable con paginación y filtros
- **FormBuilder**: Constructor genérico de formularios
- **SearchBar**: Barra de búsqueda con autocompletado
- **FilterPanel**: Panel de filtros avanzados
- **Pagination**: Componente de paginación estándar
- **LoadingSpinner**: Indicador de carga
- **ConfirmationDialog**: Diálogos de confirmación
- **ErrorDisplay**: Visualización de errores
- **SuccessMessage**: Mensajes de éxito

#### Componentes de Navegación
- **Sidebar**: Barra lateral de navegación principal
- **Breadcrumb**: Navegación de migas de pan
- **TabNavigator**: Navegador de pestañas
- **MenuItem**: Elementos de menú reutilizables

#### Componentes de Formularios
- **EntityFormBuilder**: Constructor dinámico de formularios para cada entidad
- **ValidationFeedback**: Retroalimentación de validación en tiempo real
- **DuplicateDetector**: Detección automática de duplicados
- **AutoComplete**: Campos de autocompletado
- **DatePicker**: Selector de fechas avanzado
- **DateRangePicker**: Selector de rangos de fechas
- **TimePicker**: Selector de tiempo
- **MultiSelect**: Selector múltiple
- **FileUpload**: Carga de archivos
- **FormValidator**: Validador de formularios

#### Componentes de Visualización de Datos
- **EmployeeCard**: Tarjetas de empleados con información completa
- **ProjectCard**: Visualización de información de proyectos
- **ClientCard**: Tarjetas de clientes
- **TeamCard**: Tarjetas de equipos
- **QualificationBadge**: Badges de calificaciones y habilidades
- **StatusBadge**: Indicadores visuales de estado
- **PriorityIndicator**: Indicadores de prioridad
- **AvailabilityIndicator**: Indicadores de disponibilidad
- **ProgressBar**: Barras de progreso
- **MetricCard**: Tarjetas de métricas

#### Componentes de Planificación
- **ScheduleGrid**: Cuadrícula de planificación visual
- **CalendarView**: Vista de calendario
- **TimelineView**: Vista de línea de tiempo
- **GanttChart**: Gráfico de Gantt
- **ConflictDetector**: Detector de conflictos de horario
- **AssignmentPanel**: Panel de asignaciones
- **WorkloadChart**: Gráfico de carga de trabajo
- **ResourceAllocator**: Asignador de recursos
- **ScheduleOptimizer**: Optimizador de horarios

#### Componentes de Alertas
- **AlertCenter**: Centro principal de alertas
- **NotificationBadge**: Badges de notificación
- **AlertPanel**: Panel de alertas
- **PriorityFilter**: Filtro de prioridades
- **AlertConfigPanel**: Panel de configuración de alertas
- **ConflictResolver**: Resolvedor de conflictos
- **NotificationCenter**: Centro de notificaciones

#### Componentes de Auditoría
- **AuditViewer**: Visualizador principal de auditoría
- **ChangeLogViewer**: Visualizador de registro de cambios
- **ChangeTracker**: Rastreador de cambios
- **AuditSearch**: Búsqueda de auditoría
- **RollbackDialog**: Diálogo de rollback
- **AuditExport**: Exportador de auditoría

#### Componentes de Reportes
- **ChartBuilder**: Constructor de gráficos
- **ReportGenerator**: Generador de reportes
- **ExportDialog**: Diálogo de exportación
- **DashboardWidget**: Widgets de dashboard
- **KPICard**: Tarjetas de KPIs
- **TrendChart**: Gráficos de tendencias
- **DataVisualizer**: Visualizador de datos

#### Componentes de Gestión
- **TeamMembershipManager**: Gestor de membresías de equipo
- **ProjectAssignmentPanel**: Panel de asignaciones de proyecto
- **VacationCalendar**: Calendario de vacaciones
- **StatusLegend**: Leyenda de estados
- **TeamSelector**: Selector de equipos
- **ClientSelector**: Selector de clientes
- **EmployeeSelector**: Selector de empleados
- **BulkOperations**: Operaciones masivas

## 6. Implementación por Fases

### Fase 1: Fundación y Configuración Inicial (2-3 semanas)
- Configuración del proyecto y dependencias
- Modelos de base de datos completos (12 entidades)
- Sistema de entrada manual de datos
- Asistente de configuración inicial
- Formularios básicos de entrada
- Validación en tiempo real de datos
- Interfaz básica con Flet y navegación principal
- Sistema básico de auditoría (ChangeLog)

### Fase 2: Gestión de Entidades Básicas (2-3 semanas)
- CRUD de clientes con validaciones
- CRUD de proyectos con trigramas y referencias
- CRUD de empleados con capacidades múltiples
- Gestión de equipos y membresías
- Relaciones entre entidades
- Sistema básico de alertas (Alert)

### Fase 3: Planificación y Asignaciones (3-4 semanas)
- Grilla de planificación multi-vista (empleados, equipos, proyectos)
- Sistema de asignaciones de proyectos
- Detección de conflictos y solapamientos
- Códigos de estado configurables
- Validaciones de disponibilidad

### Fase 4: Gestión Avanzada (2-3 semanas)
- Sistema completo de vacaciones con aprobaciones
- Cálculo automático de cargas de trabajo
- Métricas y KPIs en tiempo real
- Dashboard con alertas y notificaciones
- Centro de alertas completo con prioridades
- Sistema de auditoría avanzado con búsqueda

### Fase 5: Reportes y Analytics (2-3 semanas)
- Reportes de proyectos y clientes
- Análisis de eficiencia de equipos
- Métricas de utilización de recursos
- Exportación avanzada de datos
- Gráficos interactivos

### Fase 6: Optimización y Pulido (1-2 semanas)
- Mejoras de rendimiento con índices optimizados
- Validaciones adicionales y manejo de errores
- Sistema de rollback para cambios críticos
- Configuración avanzada de alertas
- Documentación completa y guías de usuario
- Testing exhaustivo y corrección de bugs

## 7. Consideraciones Técnicas

### 7.1 Arquitectura de Base de Datos
- **12 entidades principales** con relaciones bien definidas
- **Modelo base** con auditoría automática (created_at, updated_at)
- **20+ índices optimizados** específicos para consultas frecuentes:
  - `idx_employee_status`, `idx_employee_full_name`, `idx_employee_active`
  - `idx_project_reference`, `idx_project_trigram`, `idx_project_client`
  - `idx_schedule_employee_date`, `idx_schedule_project_date`
  - `idx_vacation_employee`, `idx_vacation_dates`, `idx_vacation_status`
  - `idx_workload_employee_date`, `idx_workload_week`, `idx_workload_month`
  - `idx_changelog_entity`, `idx_changelog_user_date`
  - `idx_alert_type_priority`, `idx_alert_active`
- **8 restricciones únicas** para integridad de datos:
  - Códigos únicos para clientes, proyectos, empleados, equipos
  - Prevención de duplicados en membresías y asignaciones
  - Un horario por empleado/fecha/proyecto
- **12 enums tipados** para estados, prioridades, roles y tipos

### 7.2 Performance y Optimización
- **Índices compuestos** para consultas multi-campo (employee_id + date)
- **Paginación inteligente** en listas grandes de proyectos y empleados
- **Cache de datos estáticos** (códigos de estado, equipos)
- **Lazy loading** de relaciones para evitar N+1 queries
- **Vistas materializadas** para métricas agregadas

### 7.3 Validaciones y Integridad
- **Validaciones Pydantic** en servicios para entrada de datos
- **Validaciones SQLAlchemy** a nivel de modelo
- **Detección automática** de conflictos de asignación
- **Cálculo automático** de días laborables y cargas de trabajo
- **Triggers de base de datos** para auditoría y consistencia

### 7.4 Seguridad y Auditoría
- **Logging estructurado** con Loguru para todas las operaciones
- **Auditoría completa** de cambios en entidades críticas
- **Validación de permisos** por rol de usuario
- **Sanitización de inputs** para prevenir inyecciones
- **Backup automático** de datos críticos

### 7.5 Escalabilidad y Mantenimiento
- **Arquitectura modular** con separación clara de responsabilidades
- **Patrón Repository** para abstracción de datos
- **Servicios especializados** por dominio (proyectos, empleados, equipos)
- **Configuración externa** con Pydantic Settings
- **Testing automatizado** con pytest y fixtures
- **Migraciones automáticas** con Alembic

### 7.6 Integración y Exportación
- **Entrada manual de datos** con validación robusta
- **Formularios especializados** para cada entidad
- **Detección de duplicados** en tiempo real
- **Validación automática** de integridad de datos
- **Exportación flexible** a múltiples formatos (Excel, PDF, CSV)

## 8. Próximos Pasos

### Inmediatos (Esta semana)
1. **Configurar entorno de desarrollo completo**
   - Instalar todas las dependencias (Flet, SQLAlchemy, Alembic, etc.)
   - Configurar estructura de directorios modular
   - Configurar base de datos SQLite con Alembic
   - Implementar configuración con Pydantic Settings

2. **Implementar modelos de base de datos**
   - Crear los 12 modelos SQLAlchemy identificados (incluyendo ChangeLog y Alert)
   - Configurar relaciones y restricciones
   - Implementar índices optimizados
   - Sistema básico de auditoría (ChangeLog)
   - Sistema básico de alertas (Alert)
   - Crear migraciones iniciales con Alembic

### Corto plazo (2-3 semanas)
1. **Desarrollar sistema de entrada manual de datos**
   - Formularios especializados para cada entidad
   - Validaciones Pydantic para datos ingresados
   - Manejo de errores y validaciones en tiempo real
   - Registro automático de cambios en ChangeLog

2. **Implementar repositorios y servicios**
   - Patrón Repository para cada entidad
   - Servicios especializados por dominio
   - Validaciones de negocio
   - Logging estructurado con Loguru
   - Servicios de auditoría y alertas

3. **Interfaz básica con Flet**
   - Layout principal con navegación
   - Dashboard con métricas principales
   - Vistas básicas de entidades (CRUD)
   - Centro básico de alertas y notificaciones

### Mediano plazo (1-2 meses)
1. **Funcionalidades avanzadas de planificación**
   - Grilla interactiva multi-vista
   - Sistema de asignaciones de proyectos
   - Detección automática de conflictos
   - Gestión completa de vacaciones
   - Alertas inteligentes automáticas

2. **Sistema de reportes y auditoría avanzada**
   - Métricas de proyectos y clientes
   - Análisis de carga de trabajo
   - Gráficos interactivos
   - Exportación avanzada
   - Búsqueda avanzada en auditoría
   - Sistema de rollback para cambios críticos

3. **Optimizaciones y pulido**
   - Performance con vistas materializadas
   - UX/UI mejorada
   - Testing exhaustivo
   - Documentación completa

### Largo plazo (3+ meses)
1. **Funcionalidades empresariales**
   - Sistema de permisos y roles
   - Integración con sistemas externos
   - API REST para integraciones
   - Notificaciones automáticas
   - Configuración avanzada de alertas personalizadas

2. **Escalabilidad y mantenimiento**
   - Migración a PostgreSQL (opcional)
   - Optimizaciones de base de datos
   - Monitoreo y alertas del sistema
   - Análisis predictivo de conflictos
   - Machine learning para optimización automática
   - Backup automático y recuperación

---

*Este planteamiento proporciona una base sólida para desarrollar una aplicación robusta y escalable que maneje eficientemente los datos de planificación de equipos.*