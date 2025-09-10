# Documentación de Modelos del Sistema Planificador

**Fecha de creación:** 21 de agosto de 2025  
**Versión:** 1.0  
**Sistema:** Planificador de Recursos Humanos

## Índice

1. [Modelo Base](#modelo-base)
2. [Gestión de Clientes](#gestión-de-clientes)
3. [Gestión de Empleados](#gestión-de-empleados)
4. [Gestión de Proyectos](#gestión-de-proyectos)
5. [Asignaciones y Equipos](#asignaciones-y-equipos)
6. [Planificación y Horarios](#planificación-y-horarios)
7. [Seguimiento y Métricas](#seguimiento-y-métricas)
8. [Sistema de Alertas](#sistema-de-alertas)
9. [Auditoría y Configuración](#auditoría-y-configuración)
10. [Diagrama de Relaciones](#diagrama-de-relaciones)

---

## Modelo Base

### BaseModel

**Archivo:** `base.py`  
**Propósito:** Modelo abstracto base que proporciona campos de auditoría y métodos comunes para todos los modelos del sistema.

#### Campos Principales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | Clave primaria autoincremental |
| `created_at` | DateTime | Fecha y hora de creación del registro |
| `updated_at` | DateTime | Fecha y hora de última actualización |

#### Métodos y Propiedades Destacadas

- `to_dict()`: Convierte el modelo a diccionario
- `update_from_dict()`: Actualiza el modelo desde un diccionario
- `age_in_days`: Días transcurridos desde la creación
- `last_modified_days`: Días desde la última modificación
- `is_recently_created`: Verifica si fue creado recientemente
- `audit_summary`: Resumen de auditoría del registro

---

## Gestión de Clientes

### Client

**Archivo:** `client.py`  
**Propósito:** Gestión de información de clientes y empresas que contratan servicios.

#### Campos Principales

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `name` | String(200) | Nombre del cliente | Obligatorio, único |
| `code` | String(10) | Código identificador del cliente | Único, opcional |
| `contact_person` | String(100) | Persona de contacto | Opcional |
| `email` | String(100) | Correo electrónico | Opcional |
| `phone` | String(20) | Teléfono de contacto | Opcional |
| `is_active` | Boolean | Estado activo/inactivo | Por defecto: True |
| `notes` | Text | Notas adicionales | Opcional |

#### Relaciones

- **projects**: Relación uno-a-muchos con `Project` (cascade delete)

#### Propiedades Destacadas

- `display_name`: Nombre con código si existe
- `has_contact_info`: Verifica si tiene información de contacto
- `contact_summary`: Resumen de información de contacto
- `status_display`: Estado en español

---

## Gestión de Empleados

### Employee

**Archivo:** `employee.py`  
**Propósito:** Gestión completa de información de empleados, incluyendo datos personales, profesionales y de contacto.

#### Enumeraciones

**EmployeeStatus:**
- `ACTIVE`: Activo
- `INACTIVE`: Inactivo
- `ON_LEAVE`: En licencia
- `ON_VACATION`: En vacaciones
- `TERMINATED`: Terminado

#### Campos Principales

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `first_name` | String(50) | Nombre | Obligatorio |
| `last_name` | String(50) | Apellido | Obligatorio |
| `full_name` | String(255) | Nombre completo | Obligatorio, único |
| `employee_code` | String(20) | Código de empleado | Único, opcional |
| `email` | String(100) | Correo electrónico | Único, opcional |
| `phone` | String(20) | Teléfono | Opcional |
| `hire_date` | Date | Fecha de contratación | Opcional |
| `position` | String(100) | Cargo | Opcional |
| `department` | String(100) | Departamento | Opcional |
| `qualification_level` | String(10) | Nivel de calificación | Opcional |
| `qualification_type` | String(50) | Tipo de calificación | Opcional |
| `status` | Enum | Estado del empleado | Por defecto: ACTIVE |
| `skills` | JSON | Habilidades | Opcional |
| `certifications` | JSON | Certificaciones | Opcional |
| `special_training` | JSON | Entrenamiento especial | Opcional |
| `weekly_hours` | Integer | Horas semanales | Por defecto: 40 |
| `hourly_rate` | Numeric(8,2) | Tarifa por hora | Opcional |
| `is_available` | Boolean | Disponibilidad | Por defecto: True |
| `notes` | Text | Notas adicionales | Opcional |

#### Relaciones

- **team_memberships**: Relación uno-a-muchos con `TeamMembership`
- **project_assignments**: Relación uno-a-muchos con `ProjectAssignment`
- **schedules**: Relación uno-a-muchos con `Schedule`
- **vacations**: Relación uno-a-muchos con `Vacation`
- **workloads**: Relación uno-a-muchos con `Workload`

#### Propiedades Destacadas

- `display_name`: Nombre completo dinámico
- `initials`: Iniciales del empleado
- `is_active_status`: Verifica si está activo
- `contact_info`: Información de contacto completa

---

## Gestión de Proyectos

### Project

**Archivo:** `project.py`  
**Propósito:** Gestión completa de proyectos, incluyendo planificación, seguimiento y control.

#### Enumeraciones

**ProjectStatus:**
- `PLANNED`: Planificado
- `IN_PROGRESS`: En progreso
- `ON_HOLD`: En pausa
- `COMPLETED`: Completado
- `CANCELLED`: Cancelado

**ProjectPriority:**
- `LOW`: Baja
- `MEDIUM`: Media
- `HIGH`: Alta
- `CRITICAL`: Crítica

#### Campos Principales

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `reference` | String(50) | Referencia del proyecto | Obligatorio, único |
| `trigram` | String(3) | Trigrama identificador | Obligatorio, único |
| `name` | String(200) | Nombre del proyecto | Obligatorio |
| `job_code` | String(50) | Código de trabajo | Opcional |
| `client_id` | Integer | ID del cliente | Obligatorio (FK) |
| `start_date` | Date | Fecha de inicio | Opcional |
| `end_date` | Date | Fecha de fin | Opcional |
| `shutdown_dates` | Text | Fechas de parada | Opcional |
| `duration_days` | Integer | Duración en días | Opcional |
| `required_personnel` | Text | Personal requerido | Opcional |
| `special_training` | Text | Entrenamiento especial | Opcional |
| `status` | Enum | Estado del proyecto | Por defecto: PLANNED |
| `priority` | Enum | Prioridad | Por defecto: MEDIUM |
| `responsible_person` | String(100) | Persona responsable | Opcional |
| `last_updated_by` | String(100) | Última actualización por | Opcional |
| `details` | Text | Detalles del proyecto | Opcional |
| `comments` | Text | Comentarios | Opcional |
| `notes` | Text | Notas | Opcional |
| `validation_status` | String(50) | Estado de validación | Opcional |
| `approval_status` | String(50) | Estado de aprobación | Opcional |
| `revision_number` | Integer | Número de revisión | Por defecto: 1 |
| `is_archived` | Boolean | Archivado | Por defecto: False |

#### Relaciones

- **client**: Relación muchos-a-uno con `Client`
- **assignments**: Relación uno-a-muchos con `ProjectAssignment`
- **schedules**: Relación uno-a-muchos con `Schedule`
- **workloads**: Relación uno-a-muchos con `Workload`

#### Propiedades Destacadas

- `duration_days_calculated`: Duración calculada entre fechas
- `is_active`: Verifica si está activo
- `status_display`: Estado en español
- `priority_display`: Prioridad en español
- `days_until_start`: Días hasta el inicio
- `progress_percentage`: Porcentaje de progreso

---

## Asignaciones y Equipos

### ProjectAssignment

**Archivo:** `project_assignment.py`  
**Propósito:** Gestión de asignaciones de empleados a proyectos específicos.

#### Campos Principales

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `employee_id` | Integer | ID del empleado | Obligatorio (FK) |
| `project_id` | Integer | ID del proyecto | Obligatorio (FK) |
| `start_date` | Date | Fecha de inicio | Obligatorio |
| `end_date` | Date | Fecha de fin | Opcional |
| `allocated_hours_per_day` | Numeric(4,2) | Horas asignadas por día | Opcional |
| `percentage_allocation` | Numeric(5,2) | Porcentaje de asignación | Opcional |
| `role_in_project` | String(100) | Rol en el proyecto | Opcional |
| `is_active` | Boolean | Estado activo | Por defecto: True |
| `notes` | Text | Notas | Opcional |

#### Relaciones

- **employee**: Relación muchos-a-uno con `Employee`
- **project**: Relación muchos-a-uno con `Project`

#### Propiedades Destacadas

- `duration_days`: Duración de la asignación
- `is_current`: Verifica si está activa actualmente
- `allocation_category`: Categoría de asignación
- `workload_category`: Categoría de carga de trabajo
- `overlaps_with()`: Verifica solapamiento con otra asignación

### Team

**Archivo:** `team.py`  
**Propósito:** Gestión de equipos de trabajo y sus configuraciones.

#### Campos Principales

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `name` | String(100) | Nombre del equipo | Obligatorio, único |
| `code` | String(20) | Código del equipo | Único, opcional |
| `description` | Text | Descripción | Opcional |
| `color_hex` | String(7) | Color en hexadecimal | Por defecto: #3498db |
| `max_members` | Integer | Máximo de miembros | Por defecto: 10 |
| `is_active` | Boolean | Estado activo | Por defecto: True |
| `notes` | Text | Notas | Opcional |

#### Relaciones

- **memberships**: Relación uno-a-muchos con `TeamMembership`
- **schedules**: Relación uno-a-muchos con `Schedule`

#### Propiedades Destacadas

- `display_name`: Nombre con código
- `current_members_count`: Número actual de miembros
- `is_at_capacity`: Verifica si está a capacidad máxima
- `capacity_percentage`: Porcentaje de capacidad utilizada

### TeamMembership

**Archivo:** `team_membership.py`  
**Propósito:** Gestión de membresías de empleados en equipos con roles específicos.

#### Enumeraciones

**MembershipRole:**
- `MEMBER`: Miembro
- `LEAD`: Líder
- `SUPERVISOR`: Supervisor
- `COORDINATOR`: Coordinador

#### Campos Principales

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `employee_id` | Integer | ID del empleado | Obligatorio (FK) |
| `team_id` | Integer | ID del equipo | Obligatorio (FK) |
| `role` | Enum | Rol en el equipo | Por defecto: MEMBER |
| `start_date` | Date | Fecha de inicio | Obligatorio |
| `end_date` | Date | Fecha de fin | Opcional |
| `is_active` | Boolean | Estado activo | Por defecto: True |

#### Relaciones

- **employee**: Relación muchos-a-uno con `Employee`
- **team**: Relación muchos-a-uno con `Team`

#### Propiedades Destacadas

- `duration_days`: Duración de la membresía
- `is_current`: Verifica si está activa
- `role_display`: Rol en español
- `membership_summary`: Resumen de la membresía

---

## Planificación y Horarios

### Schedule

**Archivo:** `schedule.py`  
**Propósito:** Gestión de horarios y planificación diaria/semanal de empleados.

#### Campos Principales

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `employee_id` | Integer | ID del empleado | Obligatorio (FK) |
| `project_id` | Integer | ID del proyecto | Opcional (FK) |
| `team_id` | Integer | ID del equipo | Opcional (FK) |
| `status_code_id` | Integer | ID del código de estado | Opcional (FK) |
| `date` | Date | Fecha del horario | Obligatorio |
| `start_time` | Time | Hora de inicio | Opcional |
| `end_time` | Time | Hora de fin | Opcional |
| `description` | Text | Descripción | Opcional |
| `location` | String(200) | Ubicación | Opcional |
| `is_confirmed` | Boolean | Confirmado | Por defecto: False |
| `notes` | Text | Notas | Opcional |

#### Relaciones

- **employee**: Relación muchos-a-uno con `Employee`
- **project**: Relación muchos-a-uno con `Project`
- **team**: Relación muchos-a-uno con `Team`
- **status_code**: Relación muchos-a-uno con `StatusCode`

#### Propiedades Destacadas

- `hours_worked`: Horas trabajadas calculadas
- `duration_formatted`: Duración formateada
- `time_range_formatted`: Rango de tiempo formateado
- `is_full_day`: Verifica si es evento de día completo
- `assignment_type`: Tipo de asignación
- `is_overlapping_with()`: Verifica solapamiento

### Vacation

**Archivo:** `vacation.py`  
**Propósito:** Gestión de solicitudes y períodos de vacaciones de empleados.

#### Enumeraciones

**VacationType:**
- `ANNUAL`: Vacaciones anuales
- `SICK`: Licencia médica
- `PERSONAL`: Asuntos personales
- `MATERNITY`: Licencia maternal
- `PATERNITY`: Licencia paternal
- `TRAINING`: Entrenamiento
- `OTHER`: Otro

**VacationStatus:**
- `PENDING`: Pendiente
- `APPROVED`: Aprobada
- `REJECTED`: Rechazada
- `CANCELLED`: Cancelada

#### Campos Principales

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `employee_id` | Integer | ID del empleado | Obligatorio (FK) |
| `start_date` | Date | Fecha de inicio | Obligatorio |
| `end_date` | Date | Fecha de fin | Obligatorio |
| `vacation_type` | Enum | Tipo de vacación | Obligatorio |
| `status` | Enum | Estado de la solicitud | Por defecto: PENDING |
| `requested_date` | Date | Fecha de solicitud | Obligatorio |
| `approved_date` | Date | Fecha de aprobación | Opcional |
| `approved_by` | String(100) | Aprobado por | Opcional |
| `reason` | Text | Razón | Opcional |
| `notes` | Text | Notas | Opcional |
| `total_days` | Integer | Total de días | Obligatorio |
| `business_days` | Integer | Días hábiles | Obligatorio |

#### Relaciones

- **employee**: Relación muchos-a-uno con `Employee`

#### Propiedades Destacadas

- `duration_days`: Duración total en días
- `is_approved`: Verifica si está aprobada
- `is_active`: Verifica si está en curso
- `vacation_type_display`: Tipo en español
- `overlaps_with()`: Verifica solapamiento

---

## Seguimiento y Métricas

### Workload

**Archivo:** `workload.py`  
**Propósito:** Seguimiento detallado de carga de trabajo, métricas de productividad y utilización.

#### Campos Principales

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `employee_id` | Integer | ID del empleado | Obligatorio (FK) |
| `project_id` | Integer | ID del proyecto | Opcional (FK) |
| `date` | Date | Fecha | Obligatorio |
| `week_number` | Integer | Número de semana | Obligatorio |
| `month` | Integer | Mes | Obligatorio |
| `year` | Integer | Año | Obligatorio |
| `planned_hours` | Numeric(10,9) | Horas planificadas | Opcional |
| `actual_hours` | Numeric(10,9) | Horas reales | Opcional |
| `utilization_percentage` | Numeric(5,2) | Porcentaje de utilización | Opcional |
| `efficiency_score` | Numeric(5,2) | Puntuación de eficiencia | Opcional |
| `productivity_index` | Numeric(5,2) | Índice de productividad | Opcional |
| `is_billable` | Boolean | Es facturable | Por defecto: False |
| `notes` | Text | Notas | Opcional |

#### Restricciones

- **Unique Constraint**: `employee_id` + `date` (un registro por empleado por día)

#### Relaciones

- **employee**: Relación muchos-a-uno con `Employee`
- **project**: Relación muchos-a-uno con `Project`

#### Propiedades Destacadas

- `hours_variance`: Diferencia entre horas planificadas y reales
- `hours_variance_percentage`: Porcentaje de variación
- `efficiency_category`: Categoría de eficiencia
- `productivity_category`: Categoría de productividad
- `performance_summary`: Resumen de rendimiento

---

## Sistema de Alertas

### Alert

**Archivo:** `alert.py`  
**Propósito:** Sistema de alertas y notificaciones para eventos importantes del sistema.

#### Enumeraciones

**AlertType:**
- `CONFLICT`: Conflicto
- `INSUFFICIENT_PERSONNEL`: Personal insuficiente
- `OVERALLOCATION`: Sobreasignación
- `DEADLINE_WARNING`: Advertencia de fecha límite
- `VALIDATION_ERROR`: Error de validación
- `SYSTEM_ERROR`: Error del sistema
- `APPROVAL_PENDING`: Aprobación pendiente
- `SCHEDULE_CHANGE`: Cambio de horario
- `VACATION_CONFLICT`: Conflicto de vacaciones
- `OTHER`: Otro

**AlertStatus:**
- `NEW`: Nueva
- `READ`: Leída
- `RESOLVED`: Resuelta
- `IGNORED`: Ignorada

#### Campos Principales

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `user_id` | Integer | ID del usuario | Obligatorio (FK) |
| `alert_type` | Enum | Tipo de alerta | Obligatorio |
| `status` | Enum | Estado de la alerta | Por defecto: NEW |
| `title` | String(200) | Título | Obligatorio |
| `message` | Text | Mensaje | Obligatorio |
| `related_entity_type` | String(50) | Tipo de entidad relacionada | Opcional |
| `related_entity_id` | Integer | ID de entidad relacionada | Opcional |
| `is_read` | Boolean | Leída | Por defecto: False |
| `read_at` | DateTime | Fecha de lectura | Opcional |

#### Relaciones

- **user**: Relación muchos-a-uno con `Employee`

#### Propiedades Destacadas

- `type_display`: Tipo en español
- `status_display`: Estado en español
- `requires_attention`: Requiere atención inmediata
- `priority_level`: Nivel de prioridad
- `mark_as_read()`: Marcar como leída
- `mark_as_resolved()`: Marcar como resuelta

---

## Auditoría y Configuración

### StatusCode

**Archivo:** `status_code.py`  
**Propósito:** Códigos de estado configurables para clasificar actividades y horarios.

#### Campos Principales

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `code` | String(20) | Código | Obligatorio, único |
| `name` | String(100) | Nombre | Obligatorio |
| `description` | Text | Descripción | Opcional |
| `color` | String(7) | Color en hexadecimal | Opcional |
| `icon` | String(50) | Icono | Opcional |
| `is_billable` | Boolean | Es facturable | Por defecto: True |
| `is_productive` | Boolean | Es productivo | Por defecto: True |
| `requires_approval` | Boolean | Requiere aprobación | Por defecto: False |
| `is_active` | Boolean | Estado activo | Por defecto: True |
| `sort_order` | Integer | Orden de clasificación | Por defecto: 0 |

#### Relaciones

- **schedules**: Relación uno-a-muchos con `Schedule`

#### Propiedades Destacadas

- `display_name`: Nombre con código
- `is_billable_productive`: Verifica si es facturable y productivo
- `status_category`: Categoría del estado
- `requires_special_handling`: Requiere manejo especial

---

## Diagrama de Relaciones

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   Project   │◀────│  StatusCode │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                     │
                           ▼                     ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Employee   │◀────│  Schedule   │     │    Team     │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                     │
       ▼                   ▼                     ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Workload   │     │ProjectAssign│     │TeamMembership│
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                     │
       ▼                   ▼                     ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Vacation   │     │    Alert    │     │ ChangeLog   │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Relaciones Principales

1. **Client → Project**: Un cliente puede tener múltiples proyectos
2. **Employee → Multiple**: Un empleado puede tener múltiples asignaciones, horarios, vacaciones, etc.
3. **Project → Multiple**: Un proyecto puede tener múltiples asignaciones, horarios y cargas de trabajo
4. **Team → TeamMembership**: Un equipo puede tener múltiples miembros
5. **StatusCode → Schedule**: Los códigos de estado se usan en horarios

---

## Características Técnicas

### Herencia y Estructura

- **Todos los modelos** heredan de `BaseModel`
- **Campos de auditoría** automáticos: `id`, `created_at`, `updated_at`
- **Métodos comunes** disponibles en todos los modelos

### Tipos de Datos Especiales

- **Enumeraciones**: Para estados, tipos y categorías
- **JSON**: Para datos estructurados flexibles (skills, certifications)
- **Numeric**: Para precisión decimal en horas y porcentajes
- **DateTime/Date/Time**: Para manejo temporal preciso

### Restricciones y Validaciones

- **Unique Constraints**: Para evitar duplicados
- **Foreign Keys**: Para integridad referencial
- **Cascade Operations**: Para operaciones en cascada
- **Default Values**: Para valores por defecto apropiados

### Optimizaciones

- **Lazy Loading**: Para relaciones grandes
- **Eager Loading**: Para relaciones frecuentemente accedidas
- **Índices**: En campos de búsqueda frecuente
- **Hybrid Properties**: Para cálculos eficientes

---

**Fin de la documentación**  
**Última actualización:** 21 de agosto de 2025