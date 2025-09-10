# Servicios - Nueva Arquitectura

Este directorio contiene la implementación refactorizada de los servicios siguiendo el patrón Repository y una clara separación de responsabilidades.

## Estructura de Directorios

```
services/
├── domain/                 # Servicios de dominio (lógica de negocio)
│   ├── __init__.py
│   ├── base_domain_service.py
│   └── client_service.py
├── infrastructure/         # Servicios de infraestructura
│   └── __init__.py
├── legacy/                 # Servicios antiguos (referencia)
│   ├── README.md
│   ├── base_service.py
│   ├── client_service.py
│   ├── employee_service.py
│   └── project_service.py
└── README.md              # Este archivo
```

## Arquitectura

### Flujo de Datos

```
UI/API → Domain Services → Repositories → Database
         ↕
    Infrastructure Services
```

### Responsabilidades

#### Domain Services (Servicios de Dominio)
- **Propósito**: Implementar lógica de negocio específica del dominio
- **Responsabilidades**:
  - Validaciones de reglas de negocio
  - Coordinación entre múltiples repositorios
  - Transformaciones de datos
  - Orquestación de transacciones
  - Implementación de casos de uso complejos

#### Infrastructure Services (Servicios de Infraestructura)
- **Propósito**: Manejar aspectos técnicos e infraestructura
- **Responsabilidades**:
  - Envío de emails y notificaciones
  - Almacenamiento de archivos
  - Integración con APIs externas
  - Logging y monitoreo
  - Caché y optimizaciones

## BaseDomainService

Clase base que proporciona funcionalidad común para todos los servicios de dominio.

### Características Principales

#### Operaciones CRUD Básicas
- `get_by_id(id)` - Obtener entidad por ID
- `get_all(limit, offset)` - Obtener todas las entidades con paginación
- `create(data)` - Crear nueva entidad
- `update(id, data)` - Actualizar entidad existente
- `delete(id)` - Eliminar entidad
- `count(criteria)` - Contar entidades

#### Búsquedas Avanzadas
- `find_by_criteria(criteria)` - Búsqueda por criterios personalizados
- `search_by_name(name, exact_match)` - Búsqueda por nombre
- `get_by_code(code)` - Obtener por código único
- `get_active_entities(**filters)` - Obtener entidades activas

#### Validaciones de Unicidad
- `is_name_unique(name, exclude_id)` - Verificar unicidad de nombre
- `is_code_unique(code, exclude_id)` - Verificar unicidad de código

#### Operaciones en Lote
- `bulk_create(entities_data)` - Crear múltiples entidades
- `bulk_update(updates)` - Actualizar múltiples entidades

#### Estadísticas y Agregaciones
- `get_statistics()` - Estadísticas básicas
- `count_by_criteria(criteria)` - Conteo por criterios

### Métodos de Extensión

Cada servicio específico debe implementar estos métodos para personalizar el comportamiento:

```python
# Validaciones de dominio
async def _validate_create_data(self, data: Dict[str, Any]) -> None
async def _validate_update_data(self, entity_id: int, data: Dict[str, Any]) -> None
async def _validate_delete(self, entity: ModelType) -> None

# Transformaciones de datos
async def _transform_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]
async def _transform_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]
```

## ClientService

Implementación específica para la gestión de clientes.

### Características Específicas

#### Métodos de Búsqueda
- `get_by_name(name)` - Obtener cliente por nombre exacto
- `search_clients_by_name(name)` - Búsqueda parcial por nombre
- `get_clients_with_projects()` - Clientes con proyectos asociados
- `get_active_clients()` - Solo clientes activos

#### Validaciones de Negocio
- `validate_client_name_uniqueness(name, exclude_id)` - Validar nombre único
- `validate_client_code_uniqueness(code, exclude_id)` - Validar código único
- Validación de formato de email
- Validación de campos requeridos

#### Gestión de Estado
- `activate_client(client_id)` - Activar cliente
- `deactivate_client(client_id)` - Desactivar cliente (soft delete)

#### Estadísticas Específicas
- `get_client_statistics()` - Estadísticas detalladas de clientes
  - Total de clientes
  - Clientes activos/inactivos
  - Clientes con/sin proyectos
  - Porcentajes y métricas

#### Transformaciones de Datos
- Normalización de nombres (capitalización)
- Normalización de códigos (mayúsculas)
- Normalización de emails (minúsculas)
- Limpieza de espacios en blanco

## ProjectService

Implementación específica para la gestión de proyectos.

### Características Específicas

#### Métodos de Búsqueda
- `get_by_reference(reference)` - Obtener proyecto por referencia
- `get_by_trigram(trigram)` - Obtener proyecto por trigrama
- `search_projects_by_name(name)` - Búsqueda por nombre, referencia o trigrama
- `get_projects_with_assignments()` - Proyectos con asignaciones
- `get_active_projects()` - Solo proyectos activos (planificados o en progreso)
- `get_projects_by_client(client_id)` - Proyectos de un cliente específico
- `get_projects_by_status(status)` - Filtrado por estado
- `get_projects_by_priority(priority)` - Filtrado por prioridad
- `get_projects_by_date_range(start_date, end_date)` - Proyectos en rango de fechas
- `get_overdue_projects()` - Proyectos atrasados

#### Validaciones de Negocio
- `validate_project_reference_uniqueness(reference, exclude_id)` - Validar referencia única
- `validate_project_trigram_uniqueness(trigram, exclude_id)` - Validar trigrama único
- Validación de fechas (inicio < fin)
- Verificación de asignaciones activas antes de eliminar

#### Gestión de Estado
- `activate_project(project_id)` - Cambiar a IN_PROGRESS
- `complete_project(project_id)` - Cambiar a COMPLETED
- `pause_project(project_id)` - Cambiar a ON_HOLD

#### Estadísticas Específicas
- `get_project_statistics(client_id=None)` - Estadísticas detalladas de proyectos
  - Total de proyectos
  - Proyectos por estado
  - Proyectos por prioridad
  - Estadísticas de asignaciones y horas
  - Métricas por cliente (opcional)

#### Transformaciones de Datos
- Normalización de nombres (capitalización)
- Normalización de referencias y trigramas (mayúsculas)
- Limpieza de descripciones
- Validación y ajuste de fechas

## EmployeeService

Implementación específica para la gestión de empleados.

### Características Específicas

#### Métodos de Búsqueda
- `get_by_full_name(full_name)` - Obtener empleado por nombre completo
- `get_by_employee_code(code)` - Obtener empleado por código
- `get_by_email(email)` - Obtener empleado por email
- `search_employees_by_name(name)` - Búsqueda por nombre, apellido o nombre completo
- `get_employees_with_teams()` - Empleados con sus equipos
- `get_employees_with_projects()` - Empleados con proyectos asignados
- `get_active_employees()` - Solo empleados activos
- `get_employees_by_status(status)` - Filtrado por estado
- `get_employees_by_department(department)` - Filtrado por departamento
- `get_employees_by_skills(skills)` - Empleados con habilidades específicas
- `get_available_employees(date)` - Empleados disponibles para una fecha

#### Validaciones de Negocio
- `validate_employee_name_uniqueness(full_name, exclude_id)` - Validar nombre único
- `validate_employee_code_uniqueness(code, exclude_id)` - Validar código único
- `validate_employee_email_uniqueness(email, exclude_id)` - Validar email único
- Validación de formato de email
- Verificación de proyectos activos antes de eliminar

#### Gestión de Estado
- `activate_employee(employee_id)` - Cambiar a ACTIVE
- `deactivate_employee(employee_id)` - Cambiar a INACTIVE
- `set_employee_on_vacation(employee_id)` - Cambiar a ON_VACATION

#### Estadísticas Específicas
- `get_employee_statistics()` - Estadísticas generales de empleados
  - Total de empleados
  - Empleados por estado
  - Empleados por departamento
  - Distribución de carga de trabajo
- `get_employee_workload_statistics(employee_id)` - Carga de trabajo específica
  - Proyectos asignados
  - Horas planificadas vs realizadas
  - Disponibilidad

#### Transformaciones de Datos
- Normalización de nombres y apellidos (capitalización)
- Construcción automática de nombre completo
- Normalización de códigos (mayúsculas)
- Normalización de emails (minúsculas)
- Normalización de departamentos y posiciones
- Limpieza de espacios en blanco

### Ejemplo de Uso

```python
from planificador.database import DatabaseManager
from planificador.database.repositories.client_repository import ClientRepository
from planificador.services.domain.client_service import ClientService

# Configurar dependencias
db_manager = DatabaseManager()
async with db_manager.get_session() as session:
    client_repository = ClientRepository(session)
    client_service = ClientService(client_repository)
    
    # Crear cliente
    client_data = {
        "name": "Tech Solutions S.A.",
        "code": "TECH001",
        "email": "contact@techsolutions.com",
        "contact_person": "María García",
        "phone": "+34 987 654 321",
        "is_active": True
    }
    
    client = await client_service.create(client_data)
    print(f"Cliente creado: {client.name} (ID: {client.id})")
    
    # Buscar clientes
    active_clients = await client_service.get_active_clients()
    search_results = await client_service.search_clients_by_name("Tech")
    
    # Validaciones
    is_unique = await client_service.validate_client_name_uniqueness("Nuevo Cliente")
    
    # Estadísticas
    stats = await client_service.get_client_statistics()
    print(f"Total clientes: {stats['total_count']}")
```

## Ventajas de la Nueva Arquitectura

### 1. Separación Clara de Responsabilidades
- **Repositorios**: Acceso a datos y persistencia
- **Servicios de Dominio**: Lógica de negocio y validaciones
- **Servicios de Infraestructura**: Aspectos técnicos

### 2. Mejor Testabilidad
- Inyección de dependencias facilita mocking
- Servicios pueden probarse independientemente
- Validaciones y transformaciones aisladas

### 3. Reutilización de Código
- `BaseDomainService` proporciona funcionalidad común
- Métodos genéricos reutilizables
- Patrones consistentes entre servicios

### 4. Mantenibilidad
- Código más organizado y predecible
- Fácil localización de lógica específica
- Extensibilidad sin modificar código base

### 5. Flexibilidad
- Fácil intercambio de implementaciones
- Soporte para múltiples fuentes de datos
- Adaptabilidad a cambios de requisitos

## Migración desde Servicios Legacy

Los servicios antiguos se encuentran en el directorio `legacy/` como referencia. La migración implica:

1. **Identificar lógica de negocio** en servicios legacy
2. **Crear nuevo servicio** heredando de `BaseDomainService`
3. **Implementar validaciones específicas** en métodos `_validate_*`
4. **Implementar transformaciones** en métodos `_transform_*`
5. **Agregar métodos específicos** del dominio
6. **Actualizar dependencias** para usar el nuevo servicio

## Servicios Implementados

### ClientService ✅

**Ubicación**: `src/planificador/services/domain/client_service.py`

**Descripción**: Servicio especializado para la gestión completa de clientes con lógica de negocio específica.

**Funcionalidades Implementadas**:
- **Operaciones CRUD avanzadas**:
  - `create()`: Creación con validaciones completas
  - `update()`: Actualización con validaciones de negocio
  - `delete()`: Eliminación con verificación de dependencias
  - `get_by_id()`: Obtención por ID con validaciones

- **Búsquedas especializadas**:
  - `get_by_name()`: Búsqueda por nombre exacto
  - `search_clients_by_name()`: Búsqueda parcial por nombre
  - `get_clients_with_projects()`: Clientes con proyectos asociados
  - `get_active_clients()`: Solo clientes activos
  - `get_clients_created_current_week()`: Clientes creados esta semana
  - `get_clients_created_current_month()`: Clientes creados este mes
  - `get_clients_created_business_days_only()`: Clientes creados en días laborables

- **Validaciones de negocio**:
  - `validate_client_name_uniqueness()`: Validar nombre único
  - `validate_client_code_uniqueness()`: Validar código único
  - Validación de formato de email
  - Validación de campos requeridos
  - Verificación de proyectos activos antes de eliminación

- **Gestión de estado**:
  - `activate_client()`: Activar cliente
  - `deactivate_client()`: Desactivar cliente (soft delete)

- **Análisis y estadísticas**:
  - `get_client_statistics()`: Estadísticas detalladas de clientes
  - `get_client_creation_analysis()`: Análisis de creación con Pendulum
  - Métricas de clientes activos/inactivos
  - Análisis de clientes con/sin proyectos

- **Funcionalidades con Pendulum**:
  - `create_client_with_pendulum_validation()`: Creación con validaciones de fecha
  - `format_client_creation_date()`: Formateo de fechas de creación
  - Análisis temporal de creación de clientes
  - Validación de días laborables para creación

- **Transformaciones de datos**:
  - Normalización de nombres (capitalización)
  - Normalización de códigos (mayúsculas)
  - Normalización de emails (minúsculas)
  - Limpieza de espacios en blanco

### ProjectService ✅

**Ubicación**: `src/planificador/services/domain/project_service.py`

**Descripción**: Servicio especializado para la gestión completa de proyectos con análisis avanzado.

**Funcionalidades Implementadas**:
- **Operaciones CRUD avanzadas**:
  - `create()`: Creación con validaciones de fechas y dependencias
  - `update()`: Actualización con validaciones de estado
  - `delete()`: Eliminación con verificación de asignaciones

- **Búsquedas especializadas**:
  - `get_by_reference()`: Búsqueda por referencia única
  - `get_by_trigram()`: Búsqueda por trigrama
  - `search_projects_by_name()`: Búsqueda por nombre, referencia o trigrama
  - `get_projects_with_assignments()`: Proyectos con asignaciones
  - `get_active_projects()`: Proyectos activos (planificados o en progreso)
  - `get_projects_by_client()`: Proyectos de un cliente específico
  - `get_projects_by_status()`: Filtrado por estado
  - `get_projects_by_priority()`: Filtrado por prioridad
  - `get_projects_by_date_range()`: Proyectos en rango de fechas
  - `get_overdue_projects()`: Proyectos atrasados

- **Funcionalidades con Pendulum**:
  - `get_projects_starting_current_week()`: Proyectos que inician esta semana
  - `get_projects_ending_current_week()`: Proyectos que terminan esta semana
  - `get_projects_starting_current_month()`: Proyectos que inician este mes
  - `get_projects_starting_business_days_only()`: Proyectos iniciados en días laborables
  - `format_project_dates()`: Formateo avanzado de fechas
  - `get_project_duration_analysis()`: Análisis de duración con Pendulum
  - `get_project_timeline_stats()`: Estadísticas de línea de tiempo

- **Validaciones de negocio**:
  - `validate_project_reference_uniqueness()`: Validar referencia única
  - `validate_project_trigram_uniqueness()`: Validar trigrama único
  - Validación de fechas (inicio < fin)
  - Verificación de asignaciones activas antes de eliminar
  - Validación de estados de transición

- **Gestión de estado**:
  - `activate_project()`: Cambiar a IN_PROGRESS
  - `complete_project()`: Cambiar a COMPLETED
  - `pause_project()`: Cambiar a ON_HOLD

- **Análisis y estadísticas**:
  - `get_project_statistics()`: Estadísticas detalladas por cliente
  - Análisis de duración y fechas
  - Métricas de asignaciones y horas
  - Distribución por estado y prioridad

- **Transformaciones de datos**:
  - Normalización de nombres (capitalización)
  - Normalización de referencias y trigramas (mayúsculas)
  - Limpieza de descripciones
  - Validación y ajuste de fechas

### EmployeeService ✅

**Ubicación**: `src/planificador/services/domain/employee_service.py`

**Descripción**: Servicio especializado para la gestión completa de empleados con análisis de disponibilidad.

**Funcionalidades Implementadas**:
- **Operaciones CRUD avanzadas**:
  - `create()`: Creación con validaciones de unicidad
  - `update()`: Actualización con validaciones de negocio
  - `delete()`: Eliminación con verificación de proyectos activos

- **Búsquedas especializadas**:
  - `get_by_full_name()`: Búsqueda por nombre completo
  - `get_by_employee_code()`: Búsqueda por código de empleado
  - `get_by_email()`: Búsqueda por email
  - `search_employees_by_name()`: Búsqueda parcial por nombre
  - `get_employees_with_teams()`: Empleados con equipos
  - `get_employees_with_projects()`: Empleados con proyectos
  - `get_active_employees()`: Solo empleados activos
  - `get_employees_by_status()`: Filtrado por estado
  - `get_employees_by_department()`: Filtrado por departamento
  - `get_employees_by_skills()`: Empleados con habilidades específicas
  - `get_available_employees()`: Empleados disponibles para fecha

- **Funcionalidades con Pendulum**:
  - `get_employees_hired_current_week()`: Empleados contratados esta semana
  - `get_employees_hired_current_month()`: Empleados contratados este mes
  - `get_employees_hired_business_days_only()`: Contratados en días laborables
  - `format_employee_hire_date()`: Formateo de fechas de contratación
  - `get_employee_tenure_stats()`: Estadísticas de antigüedad
  - `get_employees_by_tenure_range()`: Empleados por rango de antigüedad
  - `create_employee_with_pendulum_validation()`: Creación con validaciones de fecha

- **Validaciones de negocio**:
  - `validate_employee_name_uniqueness()`: Validar nombre único
  - `validate_employee_code_uniqueness()`: Validar código único
  - `validate_employee_email_uniqueness()`: Validar email único
  - Validación de formato de email
  - Verificación de proyectos activos antes de eliminar

- **Gestión de estado**:
  - `activate_employee()`: Cambiar a ACTIVE
  - `deactivate_employee()`: Cambiar a INACTIVE
  - `set_employee_on_vacation()`: Cambiar a ON_VACATION

- **Análisis y estadísticas**:
  - `get_employee_statistics()`: Estadísticas generales
  - `get_employee_workload_statistics()`: Carga de trabajo específica
  - Distribución por estado y departamento
  - Análisis de disponibilidad y utilización

- **Transformaciones de datos**:
  - Normalización de nombres y apellidos (capitalización)
  - Construcción automática de nombre completo
  - Normalización de códigos (mayúsculas)
  - Normalización de emails (minúsculas)

### TeamService ✅

**Ubicación**: `src/planificador/services/domain/team_service.py`

**Descripción**: Servicio especializado para la gestión completa de equipos con gestión de membresías.

**Funcionalidades Implementadas**:
- **Operaciones CRUD avanzadas**:
  - `create()`: Creación con validaciones de límites
  - `update()`: Actualización con validaciones de negocio
  - `delete()`: Eliminación con verificación de miembros

- **Búsquedas especializadas**:
  - `get_by_name()`: Búsqueda por nombre exacto
  - `search_teams_by_name()`: Búsqueda parcial por nombre o descripción
  - `get_teams_by_leader()`: Equipos liderados por un empleado
  - `get_teams_by_department()`: Equipos por departamento
  - `get_active_teams()`: Solo equipos activos
  - `get_teams_created_current_week()`: Equipos creados esta semana
  - `get_teams_created_current_month()`: Equipos creados este mes
  - `get_teams_created_business_days_only()`: Creados en días laborables

- **Gestión de relaciones**:
  - `get_team_with_leader()`: Equipo con líder cargado
  - `get_team_with_members()`: Equipo con miembros cargados
  - `get_team_with_all_relations()`: Equipo con todas las relaciones

- **Gestión de membresías**:
  - `get_team_members()`: Obtener miembros del equipo
  - `is_member()`: Verificar membresía de empleado
  - `add_member()`: Añadir miembro al equipo
  - `remove_member()`: Remover miembro del equipo
  - `update_member_role()`: Actualizar rol de miembro

- **Funcionalidades con Pendulum**:
  - `format_team_creation_date()`: Formateo de fechas de creación
  - Análisis temporal de creación de equipos
  - Validación de días laborables

- **Validaciones de negocio**:
  - Unicidad de nombre de equipo
  - Validación de límites de miembros (1-100)
  - Validación de formato de color hexadecimal
  - Verificación de miembros activos antes de eliminación

- **Gestión de estado**:
  - `activate_team()`: Activar equipo
  - `deactivate_team()`: Desactivar equipo

- **Análisis y estadísticas**:
  - `get_team_statistics()`: Estadísticas detalladas del equipo
  - `get_teams_by_department_summary()`: Resumen por departamento
  - Métricas de membresía y liderazgo

- **Transformaciones de datos**:
  - Normalización de nombres y códigos
  - Formateo de descripciones
  - Valores por defecto (color, max_members, is_active)

### AssignmentService ✅

**Ubicación**: `src/planificador/services/domain/assignment_service.py`

**Descripción**: Servicio especializado para la gestión completa de asignaciones de proyectos con análisis de cargas de trabajo.

**Funcionalidades Implementadas**:
- **Operaciones CRUD avanzadas**:
  - `create()`: Creación con validaciones de disponibilidad
  - `update()`: Actualización con validaciones de conflictos
  - `delete()`: Eliminación con verificación de dependencias

- **Búsquedas especializadas**:
  - `get_employee_assignments()`: Asignaciones de un empleado
  - `get_project_assignments()`: Asignaciones de un proyecto
  - `get_assignments_by_date_range()`: Asignaciones en rango de fechas
  - `get_active_assignments()`: Solo asignaciones activas
  - `get_assignments_by_role()`: Filtrado por rol
  - `get_assignments_current_week()`: Asignaciones de la semana actual
  - `get_assignments_current_month()`: Asignaciones del mes actual
  - `get_assignments_business_days_only()`: Asignaciones en días laborables

- **Análisis de cargas de trabajo**:
  - `get_employee_workload()`: Carga de trabajo detallada de empleado
  - `get_available_employees()`: Empleados disponibles para asignación
  - `get_assignment_conflicts()`: Detección de sobreasignaciones
  - `get_project_resource_summary()`: Resumen de recursos del proyecto
  - `get_team_workload_distribution()`: Distribución de carga por equipo
  - `get_overloaded_employees()`: Empleados con sobrecarga

- **Funcionalidades con Pendulum**:
  - `format_assignment_dates()`: Formateo de fechas de asignación
  - `get_assignment_duration_analysis()`: Análisis de duración
  - Cálculo de días laborables en asignaciones
  - Análisis temporal de asignaciones

- **Gestión de asignaciones**:
  - `create_assignment()`: Crear nueva asignación
  - `update_assignment()`: Actualizar asignación existente
  - `deactivate_assignment()`: Desactivar asignación
  - `bulk_assign_employees()`: Asignación masiva
  - `transfer_assignment()`: Transferir asignación entre empleados

- **Validaciones de negocio**:
  - Validación de disponibilidad de empleados
  - Validación de rangos de fechas
  - Validación de porcentajes (0-100%)
  - Validación de horas asignadas (0-24h)
  - Detección de conflictos de horarios
  - Verificación de límites de carga de trabajo

- **Análisis y estadísticas**:
  - `get_assignment_statistics()`: Estadísticas detalladas
  - Cálculo de cargas de trabajo en tiempo real
  - Detección automática de sobreasignaciones
  - Análisis de disponibilidad por fecha
  - Distribución de roles en proyectos
  - Métricas de utilización de recursos

- **Transformaciones de datos**:
  - Normalización de roles y notas
  - Valores por defecto para campos opcionales
  - Validación de integridad de datos
  - Cálculo automático de porcentajes de dedicación

### ScheduleService ✅

**Ubicación**: `src/planificador/services/domain/schedule_service.py`

**Descripción**: Servicio especializado para la gestión completa de horarios y calendarios con análisis temporal avanzado.

**Funcionalidades Implementadas**:
- **Operaciones CRUD avanzadas**:
  - `create()`: Creación con validaciones de conflictos
  - `update()`: Actualización con validación de solapamientos
  - `delete()`: Eliminación con verificación de dependencias

- **Búsquedas especializadas**:
  - `get_employee_schedules()`: Horarios de un empleado
  - `get_project_schedules()`: Horarios de un proyecto
  - `get_team_schedules()`: Horarios de un equipo
  - `get_schedules_by_date_range()`: Horarios en rango de fechas
  - `get_schedules_current_week()`: Horarios de la semana actual
  - `get_schedules_current_month()`: Horarios del mes actual
  - `get_schedules_business_days_only()`: Horarios en días laborables
  - `get_active_schedules()`: Solo horarios activos
  - `get_upcoming_schedules()`: Próximos horarios

- **Análisis de conflictos y disponibilidad**:
  - `check_schedule_conflict()`: Detección de conflictos de horarios
  - `get_employee_availability()`: Disponibilidad de empleado
  - `get_conflicting_schedules()`: Horarios en conflicto
  - `get_available_time_slots()`: Franjas horarias disponibles
  - `validate_schedule_overlap()`: Validación de solapamientos

- **Funcionalidades con Pendulum**:
  - `format_schedule_date()`: Formateo avanzado de fechas
  - `get_next_available_business_day()`: Próximo día laborable disponible
  - `calculate_schedule_duration()`: Cálculo preciso de duración
  - `adjust_to_business_hours()`: Ajuste a horario laboral
  - `get_business_days_schedules()`: Horarios en días laborables
  - `get_schedule_timeline_stats()`: Estadísticas de línea de tiempo

- **Gestión avanzada de horarios**:
  - `create_schedule_with_validation()`: Creación con validaciones completas
  - `update_schedule()`: Actualización con validación de conflictos
  - `adjust_to_business_day()`: Auto-ajuste a días hábiles
  - `bulk_create_schedules()`: Creación masiva de horarios
  - `reschedule_conflicting()`: Reprogramación automática

- **Análisis temporal y estadísticas**:
  - `get_employee_schedule_analysis()`: Análisis detallado por empleado
  - `get_schedule_utilization_stats()`: Estadísticas de utilización
  - `get_peak_hours_analysis()`: Análisis de horas pico
  - `get_schedule_efficiency_metrics()`: Métricas de eficiencia
  - `calculate_total_scheduled_hours()`: Cálculo de horas totales

- **Gestión de disponibilidad y conflictos**:
  - `get_schedule_conflicts()`: Detección automática de conflictos
  - `get_employee_availability()`: Análisis de disponibilidad por empleado
  - `find_next_available_business_day()`: Próximo día hábil disponible
  - `validate_schedule_creation()`: Validación completa antes de creación

- **Creación y gestión avanzada**:
  - `create_schedule()`: Crear horario con validaciones completas
  - `update_schedule()`: Actualizar con validación de conflictos
  - `adjust_to_business_day()`: Auto-ajuste a días hábiles
  - Integración con Pendulum para manejo preciso de fechas

- **Validaciones de negocio**:
  - Verificación de existencia de empleados, proyectos, equipos
  - Validación de rangos de horarios (inicio < fin)
  - Restricciones de fechas (no muy antiguas)
  - Límites de horas diarias (máximo 8 horas)
  - Límites de longitud en campos de texto
  - Protección contra eliminación de horarios antiguos

- **Transformaciones de datos**:
  - Normalización de descripciones y ubicaciones
  - Establecimiento de valores por defecto
  - Cálculo preciso de horas entre tiempos
  - Manejo de horarios que cruzan medianoche
  - Integración con Pendulum para mayor precisión temporal

### WorkloadService ✅

**Ubicación**: `src/planificador/services/domain/workload_service.py`

**Descripción**: Servicio especializado para la gestión completa de cargas de trabajo con análisis avanzado de capacidad, eficiencia y distribución temporal.

**Funcionalidades Implementadas**:
- **Operaciones CRUD avanzadas**:
  - `create()`: Creación con validaciones de capacidad
  - `update()`: Actualización con verificación de límites
  - `delete()`: Eliminación con validación de dependencias

- **Búsquedas especializadas**:
  - `get_employee_workloads()`: Cargas de trabajo de un empleado
  - `get_project_workloads()`: Cargas de trabajo de un proyecto
  - `get_team_workloads()`: Cargas de trabajo de un equipo
  - `get_workloads_by_date_range()`: Cargas en rango de fechas
  - `get_current_week_workloads()`: Cargas de la semana actual
  - `get_workloads_current_month()`: Cargas del mes actual
  - `get_workloads_business_days_only()`: Cargas en días laborables
  - `get_active_workloads()`: Solo cargas activas
  - `get_overloaded_employees()`: Empleados sobrecargados

- **Análisis de capacidad y eficiencia**:
  - `calculate_employee_utilization()`: Cálculo de utilización
  - `get_employee_efficiency_stats()`: Estadísticas de eficiencia
  - `get_workload_trends()`: Tendencias de carga de trabajo
  - `get_workload_distribution_by_weekday()`: Distribución por día
  - `get_team_workload_summary()`: Resumen por equipo
  - `analyze_workload_patterns()`: Análisis de patrones

- **Funcionalidades con Pendulum**:
  - `format_workload_date()`: Formateo avanzado de fechas
  - `calculate_workload_duration()`: Cálculo preciso de duración
  - `get_business_days_workloads()`: Cargas en días laborables
  - `get_workload_timeline_analysis()`: Análisis de línea de tiempo
  - `adjust_workload_to_business_hours()`: Ajuste a horario laboral

- **Gestión avanzada de cargas**:
  - `create_workload_with_validation()`: Creación con validaciones completas
  - `create_workload_with_pendulum_validation()`: Creación con Pendulum
  - `update_workload_with_validation()`: Actualización validada
  - `bulk_create_workloads()`: Creación masiva
  - `redistribute_workload()`: Redistribución automática

- **Análisis estadístico avanzado**:
  - `get_utilization_statistics()`: Estadísticas de utilización organizacional
  - `get_underutilized_employees()`: Empleados subutilizados
  - `get_efficiency_metrics()`: Métricas de eficiencia
  - `get_weekly_distribution()`: Distribución por día de semana
  - `get_peak_hours_analysis()`: Análisis de horas pico
  - `get_capacity_forecasting()`: Pronóstico de capacidad

- **Gestión de equipos y recursos**:
  - `get_team_resource_distribution()`: Distribución de recursos
  - `get_team_capacity_analysis()`: Análisis de capacidad grupal
  - `balance_team_workload()`: Balanceo de carga por equipo
  - `optimize_resource_allocation()`: Optimización de asignación

- **Creación y gestión avanzada**:
  - `create_workload()`: Crear registro con validaciones completas
  - `update_workload()`: Actualizar con recálculo de métricas
  - Integración con Pendulum para manejo preciso de fechas
  - Cálculo automático de métricas de utilización y eficiencia

- **Validaciones de negocio**:
  - Verificación de rangos de horas válidos (0-24)
  - Validación de porcentajes de utilización (0-100%)
  - Límites de longitud en campos de texto
  - Validación de fechas de negocio

- **Transformaciones de datos**:
  - Cálculo automático de utilización y eficiencia
  - Normalización de notas y descripciones
  - Metadatos de fecha con Pendulum
  - Valores por defecto inteligentes

### VacationService ✅

**Ubicación**: `src/planificador/services/domain/vacation_service.py`

**Descripción**: Servicio especializado para la gestión completa del ciclo de vida de vacaciones con análisis avanzado de balances, tendencias y validaciones de negocio.

**Funcionalidades Implementadas**:
- **Operaciones CRUD avanzadas**:
  - `create()`: Creación con validaciones de conflictos y balances
  - `update()`: Actualización con verificación de estados
  - `delete()`: Eliminación con validación de dependencias

- **Búsquedas especializadas**:
  - `get_employee_vacations()`: Vacaciones de un empleado
  - `get_vacations_by_date_range()`: Vacaciones en rango de fechas
  - `get_vacations_by_status()`: Filtrado por estado
  - `get_vacations_by_type()`: Filtrado por tipo
  - `get_current_month_vacations()`: Vacaciones del mes actual
  - `get_business_days_vacations()`: Vacaciones en días laborables
  - `get_pending_approvals()`: Vacaciones pendientes de aprobación
  - `get_approved_vacations()`: Vacaciones aprobadas
  - `get_conflicting_vacations()`: Detección de conflictos

- **Análisis de balances y tendencias**:
  - `get_employee_vacation_balance()`: Balance de vacaciones por empleado
  - `get_vacation_usage_statistics()`: Estadísticas de uso
  - `get_vacation_trends()`: Tendencias de vacaciones
  - `get_team_vacation_summary()`: Resumen por equipo
  - `analyze_vacation_patterns()`: Análisis de patrones
  - `get_vacation_distribution()`: Distribución temporal

- **Funcionalidades con Pendulum**:
  - `format_vacation_date()`: Formateo avanzado de fechas
  - `calculate_vacation_duration()`: Cálculo preciso de duración
  - `get_business_days_between()`: Días laborables entre fechas
  - `validate_vacation_dates()`: Validación de fechas con Pendulum
  - `create_vacation_with_pendulum_validation()`: Creación con validación Pendulum

- **Gestión avanzada del ciclo de vida**:
  - `create_vacation_with_validation()`: Creación con validaciones completas
  - `approve_vacation()`: Aprobación de solicitudes
  - `reject_vacation()`: Rechazo de solicitudes
  - `cancel_vacation()`: Cancelación de vacaciones
  - `update_vacation()`: Actualización con validaciones
  - `bulk_approve_vacations()`: Aprobación masiva
  - `auto_approve_eligible()`: Aprobación automática según criterios

- **Gestión de aprobaciones y estados**:
  - `get_approval_workflow()`: Flujo de aprobación
  - `escalate_approval()`: Escalamiento de aprobaciones
  - `track_approval_history()`: Historial de aprobaciones
  - `notify_stakeholders()`: Notificaciones automáticas
  - `validate_approval_permissions()`: Validación de permisos

- **Análisis avanzado y reportes**:
  - `generate_vacation_report()`: Reportes detallados
  - `forecast_vacation_impact()`: Pronóstico de impacto
  - `optimize_vacation_scheduling()`: Optimización de programación
  - `detect_vacation_abuse()`: Detección de uso indebido
  - `calculate_replacement_costs()`: Cálculo de costos de reemplazo

- **Validaciones y detección de conflictos**:
  - `validate_vacation_request()`: Validación integral de solicitudes
  - `check_vacation_conflicts()`: Detección de conflictos de fechas
  - `check_team_coverage()`: Verificación de cobertura del equipo
  - `validate_vacation_balance()`: Validación de días disponibles

- **Gestión de aprobaciones**:
  - Workflow de aprobación/rechazo estructurado
  - Gestión de estados y transiciones
  - Historial de cambios y comentarios
  - Notificaciones automáticas

- **Análisis estadísticos**:
  - Resúmenes por empleado y equipo
  - Estadísticas de utilización de vacaciones
  - Patrones de solicitud y aprobación
  - Recomendaciones de planificación

- **Integración con Pendulum**:
  - Manejo preciso de fechas y rangos
  - Cálculo de días laborables
  - Formateo de fechas internacionalizado
  - Validación de períodos vacacionales

- **Validaciones de negocio**:
  - Verificación de límites de días anuales
  - Validación de fechas futuras
  - Restricciones de solapamiento
  - Límites de longitud en campos de texto
  - Validación de tipos de vacación

- **Transformaciones de datos**:
  - Normalización de tipos y motivos
  - Cálculo automático de días laborables
  - Enriquecimiento con metadatos de fecha
  - Valores por defecto inteligentes

### AlertService ✅

**Ubicación**: `src/planificador/services/domain/alert_service.py`

**Descripción**: Servicio especializado para la gestión completa de alertas y notificaciones con análisis de tendencias y flujos de trabajo avanzados.

**Funcionalidades Implementadas**:
- **Operaciones CRUD avanzadas**:
  - `create()`: Creación con validaciones de prioridad y tipo
  - `update()`: Actualización con verificación de estados
  - `delete()`: Eliminación con validación de dependencias

- **Búsquedas especializadas**:
  - `get_alerts_by_type()`: Filtrado por tipo de alerta
  - `get_alerts_by_status()`: Filtrado por estado
  - `get_alerts_by_priority()`: Filtrado por prioridad
  - `get_alerts_by_date_range()`: Alertas en rango de fechas
  - `get_current_week_alerts()`: Alertas de la semana actual
  - `get_current_month_alerts()`: Alertas del mes actual
  - `get_business_days_alerts()`: Alertas en días laborables
  - `get_work_hours_alerts()`: Alertas en horario laboral
  - `get_active_alerts()`: Solo alertas activas
  - `get_critical_alerts()`: Alertas críticas
  - `get_unacknowledged_alerts()`: Alertas sin reconocer
  - `get_employee_alerts()`: Alertas de un empleado
  - `get_project_alerts()`: Alertas de un proyecto

- **Análisis de tendencias y estadísticas**:
  - `get_alert_statistics()`: Estadísticas generales
  - `get_alert_trends()`: Tendencias de alertas
  - `get_alert_frequency_analysis()`: Análisis de frecuencia
  - `get_resolution_time_stats()`: Estadísticas de tiempo de resolución
  - `analyze_alert_patterns()`: Análisis de patrones
  - `get_alert_distribution()`: Distribución temporal

- **Funcionalidades con Pendulum**:
  - `format_alert_date()`: Formateo avanzado de fechas
  - `calculate_alert_age()`: Cálculo de antigüedad
  - `count_alerts_by_date_range()`: Conteo en rango de fechas
  - `get_alerts_timeline()`: Línea de tiempo de alertas
  - `validate_alert_timing()`: Validación de tiempos

- **Gestión completa del ciclo de vida**:
  - `create_alert()`: Creación con validaciones completas
  - `acknowledge_alert()`: Reconocimiento de alertas
  - `resolve_alert()`: Resolución de alertas
  - `dismiss_alert()`: Descarte de alertas
  - `update_alert()`: Actualización con validaciones
  - `acknowledge_alerts_bulk()`: Reconocimiento masivo
  - `cleanup_old_alerts()`: Limpieza de alertas antiguas
  - `auto_resolve_expired()`: Resolución automática de alertas expiradas
  - `escalate_unresolved()`: Escalamiento automático de alertas sin resolver

- **Gestión de estados y flujos**:
  - Workflow de estados estructurado (ACTIVE, ACKNOWLEDGED, RESOLVED, DISMISSED)
  - Transiciones de estado validadas
  - Historial de cambios y comentarios
  - Notificaciones automáticas
  - Sistema de escalamiento por tiempo de respuesta
  - Archivado automático de alertas resueltas

- **Análisis y estadísticas avanzadas**:
  - Estadísticas por tipo, estado y prioridad
  - Análisis de tendencias temporales
  - Métricas de tiempo de respuesta
  - Distribución de alertas por empleado/proyecto
  - Patrones de frecuencia y resolución
  - Cálculo de SLA y tiempos de respuesta
  - Análisis predictivo de alertas críticas

- **Validaciones de negocio**:
  - Verificación de tipos de alerta válidos
  - Validación de longitud de mensajes
  - Verificación de campos requeridos
  - Validación de estados de transición
  - Límites de prioridad y severidad

- **Transformaciones de datos**:
  - Normalización de tipos y mensajes
  - Timestamps automáticos con Pendulum
  - Valores por defecto inteligentes
  - Enriquecimiento con metadatos
  - Cálculo automático de métricas

- **Integración con Pendulum**:
  - Manejo preciso de fechas y tiempos
  - Cálculo de rangos temporales
  - Formateo de fechas internacionalizado
  - Análisis de patrones temporales
  - Validación de horarios laborables

## Mejoras Generales Implementadas

### Integración Pendulum Completa ✅
- **Manejo preciso de fechas y horas** en todos los servicios
- **Formateo internacionalizado** con soporte para múltiples idiomas
- **Cálculos de días laborables** y validaciones de horarios de negocio
- **Análisis temporal avanzado** con estadísticas y tendencias
- **Validaciones de fechas robustas** con Pendulum

### Validaciones de Negocio Mejoradas ✅
- **Validaciones específicas por dominio** en cada servicio
- **Verificación de integridad referencial** entre entidades
- **Límites y restricciones de negocio** aplicados consistentemente
- **Validación de estados y transiciones** en flujos de trabajo
- **Protección contra operaciones no válidas** (eliminaciones, modificaciones)

### Análisis y Estadísticas Avanzadas ✅
- **Métricas de rendimiento** y utilización por servicio
- **Análisis de tendencias temporales** con Pendulum
- **Estadísticas de distribución** por equipos, empleados y proyectos
- **Pronósticos y análisis predictivo** en varios dominios
- **Reportes detallados** con múltiples dimensiones de análisis

### Transformaciones de Datos Consistentes ✅
- **Normalización automática** de campos de texto
- **Establecimiento de valores por defecto** inteligentes
- **Enriquecimiento de datos** con metadatos y cálculos
- **Formateo automático** de fechas, horas y métricas
- **Limpieza y validación** de datos de entrada

### Búsquedas Especializadas ✅
- **Filtros avanzados** por múltiples criterios
- **Búsquedas temporales** con integración Pendulum
- **Consultas optimizadas** para casos de uso específicos
- **Soporte para rangos de fechas** y períodos de negocio
- **Búsquedas por estado y tipo** en todos los servicios

## Próximos Pasos

1. **Implementar servicios de dominio restantes**:
   - ✅ `ClientService` para gestión de clientes (Completado)
   - ✅ `ProjectService` para gestión de proyectos (Completado)
   - ✅ `EmployeeService` para gestión de empleados (Completado)
   - ✅ `TeamService` para gestión de equipos (Completado)
   - ✅ `AssignmentService` para gestión de asignaciones (Completado)
   - ✅ `ScheduleService` para gestión de horarios y calendarios (Completado)
   - ✅ `WorkloadService` para análisis detallado de cargas de trabajo (Completado)
   - ✅ `VacationService` para gestión de vacaciones y ausencias (Completado)
   - ✅ `AlertService` para gestión de alertas y notificaciones (Completado)

2. **Crear servicios de infraestructura**:
   - `NotificationService` para gestión de notificaciones y alertas
   - `ReportService` para generación de reportes y análisis
   - `ExportService` para exportación de datos (PDF, Excel, CSV)
   - `EmailService` para envío de notificaciones por correo
   - `FileService` para gestión de archivos y documentos
   - `AuditService` para auditoría y trazabilidad

3. **Implementar servicios de aplicación**:
   - `PlanningService` para lógica de planificación avanzada
   - `ResourceOptimizationService` para optimización de recursos
   - `ConflictResolutionService` para resolución automática de conflictos
   - `CapacityPlanningService` para planificación de capacidad

4. **Desarrollar tests unitarios y de integración**:
   - Tests para `BaseDomainService`
   - Tests para todos los servicios de dominio implementados
   - Tests de integración entre servicios
   - Tests de validaciones de negocio
   - Mocks para repositorios y dependencias externas
   - Coverage mínimo del 80%

5. **Integración con API REST**:
   - Endpoints para cada servicio implementado
   - Documentación automática con OpenAPI/Swagger
   - Validación de entrada con Pydantic
   - Middleware de validación y autenticación
   - Manejo de errores HTTP estructurado

6. **Optimizaciones y mejoras de rendimiento**:
   - Implementar caching con Redis para consultas frecuentes
   - Paginación eficiente para listados grandes
   - Optimización de consultas SQL con índices
   - Lazy loading para relaciones complejas
   - Connection pooling para base de datos
   - Búsqueda full-text avanzada

7. **Monitoreo y observabilidad**:
   - Métricas de rendimiento con Prometheus
   - Logging estructurado con correlación de requests
   - Health checks para servicios
   - Alertas automáticas para errores críticos
   - Dashboards de monitoreo

8. **Documentación y ejemplos**:
   - Documentación completa de API
   - Guías de uso para desarrolladores
   - Ejemplos de implementación práctica
   - Diagramas de arquitectura actualizados
   - Casos de uso documentados

## Consideraciones de Performance

- **Transacciones**: Los servicios manejan transacciones automáticamente
- **Paginación**: Implementada en métodos de consulta
- **Caché**: Puede implementarse en servicios de infraestructura
- **Operaciones en lote**: Optimizadas para grandes volúmenes de datos

## Logging y Monitoreo

Todos los servicios incluyen logging estructurado usando Loguru:
- Operaciones de creación, actualización y eliminación
- Validaciones y errores
- Métricas de performance
- Trazabilidad de operaciones