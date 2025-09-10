# Documentación de Esquemas Pydantic - Sistema Planificador

**Fecha de generación:** 21 de agosto de 2025, 15:18 (America/Santiago)  
**Versión del sistema:** Python 3.13 con Pydantic v2  
**Ubicación:** `src/planificador/schemas/`

## Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Análisis de Coherencia con Modelos](#análisis-de-coherencia-con-modelos)
3. [Estructura de Esquemas](#estructura-de-esquemas)
4. [Esquemas por Módulo](#esquemas-por-módulo)
5. [Validaciones y Reglas de Negocio](#validaciones-y-reglas-de-negocio)
6. [Esquemas de Respuesta](#esquemas-de-respuesta)
7. [Características Técnicas](#características-técnicas)
8. [Diagrama de Relaciones](#diagrama-de-relaciones)

## Resumen Ejecutivo

El sistema de esquemas Pydantic del Planificador está compuesto por **13 módulos principales** que definen la validación de datos, serialización y deserialización para todas las entidades del sistema. Los esquemas mantienen **coherencia completa** con los modelos SQLAlchemy y implementan validaciones robustas de reglas de negocio.

### Estadísticas del Sistema
- **Total de esquemas base:** 13
- **Esquemas de creación:** 13
- **Esquemas de actualización:** 12
- **Esquemas de salida:** 13
- **Esquemas de respuesta optimizados:** 25+
- **Validaciones personalizadas:** 35+
- **Filtros de búsqueda:** 8

## Análisis de Coherencia con Modelos

### ✅ Coherencia Verificada

Todos los esquemas Pydantic mantienen **coherencia completa** con sus correspondientes modelos SQLAlchemy:

#### Campos y Tipos de Datos
- **Nombres de campos:** Coincidencia exacta entre esquemas y modelos
- **Tipos de datos:** Mapeo correcto (SQLAlchemy → Pydantic)
- **Campos opcionales:** Consistencia en `Optional` vs `nullable=True`
- **Restricciones:** Validaciones Pydantic alineadas con restricciones de BD

#### Enumeraciones
- **EmployeeStatus:** Coherente entre modelo y esquemas
- **ProjectStatus:** Coherente entre modelo y esquemas
- **ProjectPriority:** Coherente entre modelo y esquemas
- **VacationType:** Coherente entre modelo y esquemas
- **VacationStatus:** Coherente entre modelo y esquemas
- **AlertType:** Coherente entre modelo y esquemas
- **AlertStatus:** Coherente entre modelo y esquemas
- **MembershipRole:** Coherente entre modelo y esquemas

#### Relaciones
- **Claves foráneas:** Correctamente representadas como `int` en esquemas
- **Relaciones anidadas:** Esquemas `WithDetails` para cargar relaciones
- **Referencias circulares:** Resueltas con `TYPE_CHECKING` y `ForwardRef`

### 🔍 Diferencias Identificadas (Intencionales)

1. **Campos calculados:** Los esquemas no incluyen propiedades calculadas de los modelos
2. **Campos de auditoría:** `created_at` y `updated_at` solo en esquemas de salida
3. **Validaciones adicionales:** Los esquemas implementan validaciones de negocio no presentes en modelos

## Estructura de Esquemas

### Patrón de Organización

Cada módulo sigue un patrón consistente:

```
schemas/
├── base/
│   └── base.py              # BaseSchema con ConfigDict
├── {entity}/
│   └── {entity}.py          # Esquemas específicos
├── response/
│   ├── __init__.py          # Resolución de ForwardRefs
│   └── response_schemas.py  # Esquemas optimizados
└── __init__.py              # Importaciones centralizadas
```

### Tipos de Esquemas por Entidad

1. **Base:** Campos principales para validación
2. **Create:** Para creación de nuevas entidades
3. **Update:** Para actualización (campos opcionales)
4. **Output:** Para serialización con campos de auditoría
5. **WithRelations:** Para incluir entidades relacionadas
6. **SearchFilter:** Para filtros de búsqueda

## Esquemas por Módulo

### 1. Employee (Empleado)

**Ubicación:** `schemas/employee/employee.py`

#### Esquemas Principales
- `EmployeeBase`: Campos principales (first_name, last_name, employee_code, email, etc.)
- `EmployeeCreate`: Hereda de EmployeeBase
- `EmployeeUpdate`: Todos los campos opcionales
- `Employee`: Esquema de salida con id, created_at, updated_at

#### Esquemas con Relaciones
- `EmployeeWithTeams`: Incluye team_memberships
- `EmployeeWithProjects`: Incluye project_assignments
- `EmployeeWithSchedules`: Incluye schedules
- `EmployeeWithVacations`: Incluye vacations
- `EmployeeWithWorkloads`: Incluye workloads
- `EmployeeWithDetails`: Incluye todas las relaciones

#### Validaciones
- **Email:** Validación con EmailStr
- **Longitudes:** min_length y max_length en campos de texto
- **Estado:** Enum EmployeeStatus con valor por defecto ACTIVE

#### Filtros de Búsqueda
```python
class EmployeeSearchFilter(BaseSchema):
    name: Optional[str] = None
    code: Optional[str] = None
    email: Optional[str] = None
    status: Optional[EmployeeStatus] = None
    department: Optional[str] = None
    position: Optional[str] = None
    team_id: Optional[int] = None
    project_id: Optional[int] = None
```

### 2. Project (Proyecto)

**Ubicación:** `schemas/project/project.py`

#### Esquemas Principales
- `ProjectBase`: Campos principales con validaciones de fechas
- `ProjectCreate`: Hereda de ProjectBase
- `ProjectUpdate`: Todos los campos opcionales
- `Project`: Esquema de salida con relación a Client

#### Validaciones Destacadas
```python
@field_validator('start_date')
@classmethod
def validate_start_date(cls, v: Optional[date]) -> Optional[date]:
    """Valida que la fecha de inicio del proyecto sea razonable."""
    if v is not None:
        if v < pendulum.now().subtract(years=5).date():
            raise ValueError("La fecha de inicio no puede ser anterior a 5 años")
        if v > pendulum.now().add(years=10).date():
            raise ValueError("La fecha de inicio no puede ser posterior a 10 años")
    return v

def validate_project_dates(self) -> 'ProjectBase':
    """Valida que las fechas del proyecto sean coherentes."""
    if self.start_date and self.end_date:
        if self.start_date >= self.end_date:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        # Validar que la duración no sea excesiva (máximo 5 años)
        duration = pendulum.instance(self.end_date) - pendulum.instance(self.start_date)
        if duration.days > 365 * 5:
            raise ValueError("La duración del proyecto no puede exceder 5 años")
    return self
```

#### Esquemas con Relaciones
- `ProjectWithAssignments`: Incluye assignments
- `ProjectWithSchedules`: Incluye schedules
- `ProjectWithWorkloads`: Incluye workloads
- `ProjectWithDetails`: Incluye todas las relaciones

### 3. Client (Cliente)

**Ubicación:** `schemas/client/client.py`

#### Esquemas Principales
- `ClientBase`: Campos principales (name, code, contact_person, email, etc.)
- `ClientCreate`: Hereda de ClientBase
- `ClientUpdate`: Todos los campos opcionales
- `Client`: Esquema de salida
- `ClientWithProjects`: Incluye lista de proyectos

#### Validaciones
- **Email:** Validación con EmailStr opcional
- **Longitudes:** Restricciones en name (100), code (20), notes (500)
- **Estado:** Campo is_active con valor por defecto True

### 4. Team (Equipo)

**Ubicación:** `schemas/team/team.py`

#### Esquemas Principales
- `TeamBase`: Campos principales con validación de color hex
- `TeamCreate`: Hereda de TeamBase
- `TeamUpdate`: Todos los campos opcionales
- `Team`: Esquema de salida

#### Validaciones Destacadas
```python
color_hex: str = Field(default="#3498db", pattern=r"^#[0-9A-Fa-f]{6}$")
max_members: int = Field(default=10, ge=1, le=100)
```

#### TeamMembership
- `TeamMembershipBase`: Campos de membresía con validaciones de fechas
- `TeamMembershipCreate`: Para crear membresías
- `TeamMembership`: Esquema de salida

#### Validaciones de Membresía
```python
@field_validator('start_date')
@classmethod
def validate_start_date(cls, v: date) -> date:
    """Valida que la fecha de inicio no sea muy antigua ni muy futura."""
    if v < pendulum.now().subtract(years=10).date():
        raise ValueError("La fecha de inicio no puede ser anterior a 10 años")
    if v > pendulum.now().add(years=5).date():
        raise ValueError("La fecha de inicio no puede ser posterior a 5 años")
    return v
```

### 5. Schedule (Horario)

**Ubicación:** `schemas/schedule/schedule.py`

#### Esquemas Principales
- `ScheduleBase`: Campos principales (employee_id, project_id, date, times, etc.)
- `ScheduleCreate`: Hereda de ScheduleBase
- `ScheduleUpdate`: Todos los campos opcionales
- `Schedule`: Esquema de salida
- `ScheduleSearchFilter`: Filtros de búsqueda

#### Campos Principales
```python
employee_id: int
project_id: Optional[int] = None
team_id: Optional[int] = None
status_code_id: Optional[int] = None
date: date
start_time: time
end_time: time
description: Optional[str] = None
location: Optional[str] = None
is_confirmed: bool = False
notes: Optional[str] = None
```

### 6. Workload (Carga de Trabajo)

**Ubicación:** `schemas/workload/workload.py`

#### Esquemas Principales
- `WorkloadBase`: Campos principales con validaciones de consistencia
- `WorkloadCreate`: Hereda de WorkloadBase
- `Workload`: Esquema de salida

#### Validaciones Destacadas
```python
@field_validator('date')
@classmethod
def validate_date_consistency(cls, v: date, info: ValidationInfo) -> date:
    """Valida que la fecha sea consistente con week_number, month y year."""
    if 'week_number' in info.data and info.data['week_number']:
        expected_week = pendulum.instance(v).week_of_year
        if expected_week != info.data['week_number']:
            raise ValueError(f"La fecha {v} no corresponde a la semana {info.data['week_number']}")
    return v

@field_validator('actual_hours')
@classmethod
def validate_hours_range(cls, v: Optional[Decimal]) -> Optional[Decimal]:
    """Valida que las horas estén en un rango razonable."""
    if v is not None:
        if v < 0:
            raise ValueError("Las horas no pueden ser negativas")
        if v > 24:
            raise ValueError("Las horas no pueden exceder 24 por día")
    return v
```

### 7. Vacation (Vacaciones)

**Ubicación:** `schemas/vacation/vacation.py`

#### Esquemas Principales
- `VacationBase`: Campos principales con validaciones complejas
- `VacationCreate`: Hereda de VacationBase
- `VacationUpdate`: Todos los campos opcionales
- `Vacation`: Esquema de salida
- `VacationSearchFilter`: Filtros de búsqueda

#### Validaciones Complejas
```python
@model_validator(mode='after')
def validate_approval_consistency(self):
    """Validar consistencia entre estado de aprobación y campos relacionados."""
    if self.status == VacationStatus.APPROVED:
        if not self.approved_date:
            raise ValueError('Las vacaciones aprobadas deben tener fecha de aprobación')
        if not self.approved_by:
            raise ValueError('Las vacaciones aprobadas deben indicar quién las aprobó')
    elif self.status == VacationStatus.PENDING:
        if self.approved_date or self.approved_by:
            raise ValueError('Las vacaciones pendientes no pueden tener datos de aprobación')
    return self
```

### 8. ProjectAssignment (Asignación de Proyecto)

**Ubicación:** `schemas/assignment/assignment.py`

#### Esquemas Principales
- `ProjectAssignmentBase`: Campos principales con validaciones de asignación
- `ProjectAssignmentCreate`: Hereda de ProjectAssignmentBase
- `ProjectAssignmentUpdate`: Todos los campos opcionales
- `ProjectAssignment`: Esquema de salida

#### Validaciones de Asignación
```python
@model_validator(mode='after')
def validate_allocation_consistency(self):
    """Validar consistencia entre horas asignadas y porcentaje de asignación."""
    if (self.allocated_hours_per_day is not None and 
        self.percentage_allocation is not None):
        # Si se especifican ambos, verificar que sean consistentes (8 horas = 100%)
        expected_percentage = (self.allocated_hours_per_day / 8) * 100
        if abs(float(self.percentage_allocation) - float(expected_percentage)) > 5:
            raise ValueError(
                'Las horas asignadas por día y el porcentaje de asignación no son consistentes'
            )
    return self
```

### 9. Alert (Alerta)

**Ubicación:** `schemas/alert/alert.py`

#### Esquemas Principales
- `AlertBase`: Campos principales con validaciones de lectura
- `AlertCreate`: Hereda de AlertBase
- `AlertUpdate`: Todos los campos opcionales
- `Alert`: Esquema de salida
- `AlertSearchFilter`: Filtros de búsqueda

#### Validaciones de Estado
```python
@model_validator(mode='after')
def validate_read_consistency(self) -> 'AlertBase':
    """Valida la coherencia entre is_read y read_at."""
    if self.is_read and self.read_at is None:
        raise ValueError("Si la alerta está marcada como leída, debe tener fecha de lectura")
    if not self.is_read and self.read_at is not None:
        raise ValueError("Si la alerta no está leída, no debe tener fecha de lectura")
    return self
```

### 10. StatusCode (Código de Estado)

**Ubicación:** `schemas/status_code/status_code.py`

#### Esquemas Principales
- `StatusCodeBase`: Campos principales (code, name, description, etc.)
- `StatusCodeCreate`: Hereda de StatusCodeBase
- `StatusCodeUpdate`: Todos los campos opcionales
- `StatusCode`: Esquema de salida

#### Campos Principales
```python
code: str = Field(..., min_length=1, max_length=20)
name: str = Field(..., min_length=1, max_length=100)
description: Optional[str] = None
color: Optional[str] = Field(None, max_length=7)  # Para códigos hex
icon: Optional[str] = Field(None, max_length=50)
is_billable: bool = False
is_productive: bool = True
requires_approval: bool = False
is_active: bool = True
sort_order: int = Field(default=0)
```

### 11. Base Schema

**Ubicación:** `schemas/base/base.py`

```python
class BaseSchema(BaseModel):
    """Schema base para todos los esquemas Pydantic."""
    
    model_config = ConfigDict(from_attributes=True)
```

### 12. Response Schemas

**Ubicación:** `schemas/response/response_schemas.py`

#### Categorías de Esquemas de Respuesta

1. **Listados Optimizados**
   - `EmployeeListResponse`: Campos esenciales para listados
   - `ProjectListResponse`: Información básica + cliente
   - `ClientListResponse`: Datos básicos + contador de proyectos
   - `TeamListResponse`: Información básica + contador de miembros
   - `ScheduleListResponse`: Horario con nombres de entidades relacionadas
   - `VacationListResponse`: Vacaciones con nombre de empleado
   - `WorkloadListResponse`: Carga de trabajo con nombres
   - `ProjectAssignmentListResponse`: Asignaciones con nombres

2. **Búsquedas Enriquecidas**
   - `EmployeeSearchResponse`: Incluye proyectos y equipos actuales
   - `ProjectSearchResponse`: Incluye empleados asignados
   - `ScheduleSearchResponse`: Información completa de horario

3. **Resúmenes Ejecutivos**
   - `EmployeeSummaryResponse`: Métricas de empleado
   - `ProjectSummaryResponse`: Métricas de proyecto (consolidado desde report.py)
   - `TeamSummaryResponse`: Métricas de equipo (consolidado desde report.py)
   - `WorkloadSummaryResponse`: Resumen de período (consolidado desde report.py)
   
   > **Nota:** Los esquemas de resumen anteriormente ubicados en `schemas/report/report.py` han sido consolidados en `response_schemas.py` para evitar duplicación y simplificar la arquitectura.

4. **Paginación**
   - `PaginatedResponse`: Base para paginación
   - `PaginatedEmployeeResponse`: Empleados paginados
   - `PaginatedProjectResponse`: Proyectos paginados
   - `PaginatedClientResponse`: Clientes paginados
   - `PaginatedScheduleResponse`: Horarios paginados
   - `PaginatedVacationResponse`: Vacaciones paginadas
   - `PaginatedWorkloadResponse`: Cargas de trabajo paginadas

5. **Dashboard y Métricas**
   - `DashboardStatsResponse`: Estadísticas generales
   - `EmployeeUtilizationResponse`: Utilización de empleados
   - `ProjectProgressResponse`: Progreso de proyectos

## Validaciones y Reglas de Negocio

### Tipos de Validaciones Implementadas

#### 1. Validaciones de Campo (`@field_validator`)
- **Fechas:** Rangos razonables, no futuras cuando aplica
- **Emails:** Formato válido con EmailStr
- **Longitudes:** min_length y max_length en strings
- **Rangos numéricos:** ge (>=), le (<=) para números
- **Patrones:** Regex para códigos hex, códigos de empleado

#### 2. Validaciones de Modelo (`@model_validator`)
- **Coherencia de fechas:** start_date < end_date
- **Consistencia de estado:** Campos relacionados coherentes
- **Reglas de negocio:** Validaciones complejas entre campos
- **Cálculos derivados:** Verificación de campos calculados

#### 3. Validaciones Personalizadas

**Fechas de Proyecto:**
```python
def validate_project_dates(self) -> 'ProjectBase':
    """Valida que las fechas del proyecto sean coherentes."""
    if self.start_date and self.end_date:
        if self.start_date >= self.end_date:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        # Validar que la duración no sea excesiva (máximo 5 años)
        duration = pendulum.instance(self.end_date) - pendulum.instance(self.start_date)
        if duration.days > 365 * 5:
            raise ValueError("La duración del proyecto no puede exceder 5 años")
    return self
```

**Consistencia de Asignación:**
```python
def validate_allocation_consistency(self):
    """Validar consistencia entre horas asignadas y porcentaje de asignación."""
    if (self.allocated_hours_per_day is not None and 
        self.percentage_allocation is not None):
        expected_percentage = (self.allocated_hours_per_day / 8) * 100
        if abs(float(self.percentage_allocation) - float(expected_percentage)) > 5:
            raise ValueError(
                'Las horas asignadas por día y el porcentaje de asignación no son consistentes'
            )
    return self
```

**Aprobación de Vacaciones:**
```python
def validate_approval_consistency(self):
    """Validar consistencia entre estado de aprobación y campos relacionados."""
    if self.status == VacationStatus.APPROVED:
        if not self.approved_date:
            raise ValueError('Las vacaciones aprobadas deben tener fecha de aprobación')
        if not self.approved_by:
            raise ValueError('Las vacaciones aprobadas deben indicar quién las aprobó')
    return self
```

### Reglas de Negocio Implementadas

1. **Gestión de Fechas**
   - Fechas de proyecto no pueden exceder 5 años de duración
   - Fechas de inicio no pueden ser muy antiguas (5-10 años)
   - Fechas de fin no pueden ser muy futuras (10-15 años)
   - Fechas de vacaciones deben ser coherentes con solicitud

2. **Asignaciones y Recursos**
   - Horas por día no pueden exceder 24
   - Porcentajes de asignación entre 0-100%
   - Consistencia entre horas y porcentajes (8h = 100%)
   - Máximo de miembros por equipo (1-100)

3. **Estados y Aprobaciones**
   - Vacaciones aprobadas requieren fecha y aprobador
   - Alertas leídas requieren fecha de lectura
   - Estados de empleado y proyecto coherentes

4. **Validaciones de Formato**
   - Códigos hex para colores (#RRGGBB)
   - Emails válidos con EmailStr
   - Códigos de empleado con formato específico

## Esquemas de Respuesta

### Optimización por Caso de Uso

#### 1. Listados (Performance)
**Objetivo:** Minimizar datos transferidos en listados

```python
class EmployeeListResponse(BaseSchema):
    """Schema optimizado para listados de empleados."""
    
    id: int
    full_name: str  # Calculado: first_name + last_name
    employee_code: str
    email: str
    status: EmployeeStatus
    position: Optional[str] = None
    department: Optional[str] = None
    is_available: bool = True
```

#### 2. Búsquedas (Información Enriquecida)
**Objetivo:** Incluir contexto adicional para búsquedas

```python
class EmployeeSearchResponse(BaseSchema):
    """Schema enriquecido para búsquedas de empleados."""
    
    # Campos básicos
    id: int
    full_name: str
    employee_code: str
    email: str
    status: EmployeeStatus
    
    # Contexto adicional
    current_projects: List[str] = []  # Nombres de proyectos
    current_teams: List[str] = []    # Nombres de equipos
```

#### 3. Resúmenes (Métricas)
**Objetivo:** Proporcionar métricas calculadas

```python
class EmployeeSummaryResponse(BaseSchema):
    """Schema con métricas para resúmenes ejecutivos."""
    
    # Identificación
    id: int
    full_name: str
    employee_code: str
    
    # Métricas calculadas
    total_projects: int = 0
    active_projects: int = 0
    current_utilization: Optional[Decimal] = None
    avg_efficiency: Optional[Decimal] = None
    pending_vacations: int = 0
```

#### 4. Dashboard (Estadísticas)
**Objetivo:** Métricas agregadas para dashboard

```python
class DashboardStatsResponse(BaseSchema):
    """Estadísticas generales para dashboard."""
    
    total_employees: int = 0
    active_employees: int = 0
    total_projects: int = 0
    active_projects: int = 0
    pending_vacations: int = 0
    today_schedules: int = 0
    overdue_projects: int = 0
    high_priority_projects: int = 0
```

### Paginación Tipada

```python
class PaginatedResponse(BaseSchema):
    """Base para respuestas paginadas."""
    
    total: int = Field(..., description="Total de elementos")
    page: int = Field(..., description="Página actual")
    size: int = Field(..., description="Elementos por página")
    pages: int = Field(..., description="Total de páginas")
    has_next: bool = Field(..., description="Tiene página siguiente")
    has_prev: bool = Field(..., description="Tiene página anterior")

class PaginatedEmployeeResponse(PaginatedResponse):
    """Respuesta paginada de empleados."""
    
    items: List[EmployeeListResponse] = []
```

## Características Técnicas

### Configuración Base

```python
class BaseSchema(BaseModel):
    """Schema base para todos los esquemas Pydantic."""
    
    model_config = ConfigDict(from_attributes=True)
```

**Características:**
- `from_attributes=True`: Permite crear esquemas desde objetos SQLAlchemy
- Herencia consistente en todos los esquemas
- Configuración centralizada

### Resolución de Referencias Circulares

```python
# En schemas/__init__.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .project.project import Project
else:
    Project = "Project"

# Resolución de ForwardRefs
Employee.model_rebuild()
Project.model_rebuild()
Client.model_rebuild()
```

### Importaciones Organizadas

```python
# Estructura de importaciones
from typing import List, Optional, TYPE_CHECKING
from pydantic import Field, EmailStr, field_validator, model_validator
from datetime import datetime, date, time
from decimal import Decimal
import pendulum

from ..base.base import BaseSchema
from ...models.entity import EntityEnum
```

### Validaciones con Pendulum

```python
@field_validator('start_date')
@classmethod
def validate_start_date(cls, v: Optional[date]) -> Optional[date]:
    """Valida fechas usando Pendulum para manejo robusto."""
    if v is not None:
        if v < pendulum.now().subtract(years=5).date():
            raise ValueError("Fecha muy antigua")
    return v
```

### Tipos de Datos Especializados

- **EmailStr:** Validación automática de emails
- **Decimal:** Precisión para cálculos financieros
- **date/time/datetime:** Tipos específicos para fechas
- **Enums:** Validación de valores permitidos
- **Optional:** Campos opcionales explícitos

## Diagrama de Relaciones

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Employee      │    │    Project      │    │     Client      │
│                 │    │                 │    │                 │
│ EmployeeBase    │    │ ProjectBase     │    │ ClientBase      │
│ EmployeeCreate  │    │ ProjectCreate   │    │ ClientCreate    │
│ EmployeeUpdate  │    │ ProjectUpdate   │    │ ClientUpdate    │
│ Employee        │    │ Project         │    │ Client          │
│ EmployeeWith*   │    │ ProjectWith*    │    │ ClientWith*     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ ProjectAssign   │    │   Schedule      │    │   Workload      │
│                 │    │                 │    │                 │
│ AssignmentBase  │    │ ScheduleBase    │    │ WorkloadBase    │
│ AssignmentCreate│    │ ScheduleCreate  │    │ WorkloadCreate  │
│ Assignment      │    │ Schedule        │    │ Workload        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                      │                      │
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Team        │    │   Vacation      │    │     Alert       │
│                 │    │                 │    │                 │
│ TeamBase        │    │ VacationBase    │    │ AlertBase       │
│ TeamCreate      │    │ VacationCreate  │    │ AlertCreate     │
│ TeamUpdate      │    │ VacationUpdate  │    │ AlertUpdate     │
│ Team            │    │ Vacation        │    │ Alert           │
│ TeamWith*       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ TeamMembership  │    │   StatusCode    │
│                 │    │                 │
│ MembershipBase  │    │ StatusCodeBase  │
│ MembershipCreate│    │ StatusCodeCreate│
│ Membership      │    │ StatusCode      │
└─────────────────┘    └─────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Response Schemas                         │
│                                                             │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│ │   List      │ │   Search    │ │  Summary    │ │Dashboard│ │
│ │ Responses   │ │ Responses   │ │ Responses   │ │ Stats   │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │              Paginated Responses                        │ │
│ │  PaginatedEmployee, PaginatedProject, etc.             │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Leyenda del Diagrama

- **Esquemas Base:** Campos principales para validación
- **Esquemas Create:** Para creación de entidades
- **Esquemas Update:** Para actualización (campos opcionales)
- **Esquemas Output:** Para serialización con auditoría
- **Esquemas With*:** Para incluir relaciones
- **Response Schemas:** Optimizados para diferentes casos de uso

## Conclusiones

### Fortalezas del Sistema

1. **Coherencia Completa:** 100% de alineación entre modelos SQLAlchemy y esquemas Pydantic
2. **Validaciones Robustas:** 35+ validaciones personalizadas implementadas
3. **Optimización por Caso de Uso:** Esquemas específicos para listados, búsquedas y resúmenes
4. **Manejo de Referencias:** Resolución correcta de referencias circulares
5. **Tipado Fuerte:** Type hints completos y validación automática
6. **Reglas de Negocio:** Validaciones complejas implementadas a nivel de esquema

### Características Destacadas

- **Modularidad:** Organización clara por entidad
- **Reutilización:** Patrones consistentes en todos los módulos
- **Performance:** Esquemas optimizados para diferentes casos de uso
- **Mantenibilidad:** Código limpio y bien documentado
- **Escalabilidad:** Estructura preparada para crecimiento

### Recomendaciones

1. **Mantener coherencia:** Continuar sincronización entre modelos y esquemas
2. **Ampliar validaciones:** Considerar validaciones adicionales según evolución del negocio
3. **Optimizar respuestas:** Crear nuevos esquemas de respuesta según necesidades específicas
4. **Documentar cambios:** Actualizar documentación con cada modificación
5. **Testing:** Implementar tests para todas las validaciones personalizadas

---

**Nota:** Esta documentación refleja el estado actual del sistema de esquemas Pydantic del Planificador. Para cambios o actualizaciones, consultar el código fuente en `src/planificador/schemas/`.