# Modelos de Base de Datos - Sistema de Planificación AkGroup

## Modelos SQLAlchemy

### Modelo Base

```python
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()

class BaseModel(Base):
    """Modelo base con campos de auditoría y métodos comunes."""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update_from_dict(self, data: Dict[str, Any], session: Session) -> None:
        """Actualiza el modelo desde un diccionario."""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        session.commit()
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
```

### 1. Modelo Client

```python
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship

class Client(BaseModel):
    """Modelo para gestión de clientes - Versión simplificada para MVP."""
    __tablename__ = 'clients'
    
    # Campos esenciales (del Excel original)
    name = Column(String(200), nullable=False, unique=True)  # Columna E "CLIENT" del Excel
    code = Column(String(10), nullable=True, unique=True)    # Código interno opcional para referencias rápidas
    
    # Contacto básico (opcional para gestión)
    contact_person = Column(String(100), nullable=True)      # Persona de contacto
    email = Column(String(100), nullable=True)               # Email de contacto
    phone = Column(String(20), nullable=True)                # Teléfono de contacto
    
    # Estado y observaciones
    is_active = Column(Boolean, default=True, nullable=False)  # Gestión de clientes activos/inactivos
    notes = Column(Text, nullable=True)                        # Observaciones generales
    
    # Relaciones
    projects = relationship("Project", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name='{self.name}', code='{self.code}')>"
```

### 2. Modelo Project

```python
from sqlalchemy import Column, String, Text, Date, Integer, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
import enum

class ProjectStatus(enum.Enum):
    """Estados posibles de un proyecto."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProjectPriority(enum.Enum):
    """Prioridades de proyecto."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Project(BaseModel):
    """Modelo para gestión de proyectos."""
    __tablename__ = 'projects'
    
    # Información básica del proyecto
    reference = Column(String(50), nullable=False, unique=True)  # Référence projet
    trigram = Column(String(3), nullable=False, unique=True)     # TRI-GRAMME
    name = Column(String(200), nullable=False)                   # Nom du projet/Centrale
    job_code = Column(String(50), nullable=True)                 # JOB
    
    # Cliente
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    
    # Fechas y duración
    start_date = Column(Date, nullable=True)                     # Date début
    end_date = Column(Date, nullable=True)                       # Date fin
    shutdown_dates = Column(Text, nullable=True)                 # Dates d'arrêt
    duration_days = Column(Integer, nullable=True)               # Durée
    
    # Personal y formación
    required_personnel = Column(Text, nullable=True)             # Personnel
    special_training = Column(Text, nullable=True)               # Formation spéciale
    
    # Estado y prioridad
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNED, nullable=False)
    priority = Column(Enum(ProjectPriority), default=ProjectPriority.MEDIUM, nullable=False)
    
    # Información financiera eliminada para MVP
    
    # Responsabilidad y seguimiento
    responsible_person = Column(String(100), nullable=True)      # Responsable
    last_updated_by = Column(String(100), nullable=True)        # Auteur MAJ
    
    # Detalles adicionales
    details = Column(Text, nullable=True)                        # DETAILS
    comments = Column(Text, nullable=True)                       # Commentaires
    notes = Column(Text, nullable=True)
    
    # Control de calidad
    validation_status = Column(String(50), nullable=True)       # Validation
    approval_status = Column(String(50), nullable=True)         # Approbation
    revision_number = Column(Integer, default=1, nullable=False) # Révision
    is_archived = Column(Boolean, default=False, nullable=False) # Archive
    
    # Relaciones
    client = relationship("Client", back_populates="projects")
    assignments = relationship("ProjectAssignment", back_populates="project", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="project", cascade="all, delete-orphan")
    workloads = relationship("Workload", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, reference='{self.reference}', trigram='{self.trigram}', name='{self.name}')>"
```

### 3. Modelo Employee

```python
from sqlalchemy import Column, String, Date, Boolean, Text, Enum
from sqlalchemy.orm import relationship
import enum

class EmployeeStatus(enum.Enum):
    """Estados posibles de un empleado."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"

class Employee(BaseModel):
    """Modelo para gestión de empleados."""
    __tablename__ = 'employees'
    
    # Información personal
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    full_name = Column(String(255), nullable=False)  # Nombre completo como aparece en Excel
    employee_code = Column(String(20), nullable=True, unique=True)
    
    # Información de contacto
    email = Column(String(100), nullable=True, unique=True)
    phone = Column(String(20), nullable=True)
    
    # Información laboral
    hire_date = Column(Date, nullable=True)
    position = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    qualification_level = Column(String(10))  # HN1, HN2, etc.
    qualification_type = Column(String(50))  # 'montador', 'supervisor', etc.
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.ACTIVE, nullable=False)
    
    # Capacidades y certificaciones
    skills = Column(Text, nullable=True)  # JSON o texto con habilidades
    certifications = Column(Text, nullable=True)  # Certificaciones
    special_training = Column(Text, nullable=True)  # Formación especial
    
    # Configuración de trabajo
    weekly_hours = Column(Integer, default=40, nullable=False)
    hourly_rate = Column(Numeric(8, 2), nullable=True)
    
    # Estado y disponibilidad
    is_available = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relaciones
    team_memberships = relationship("TeamMembership", back_populates="employee", cascade="all, delete-orphan")
    project_assignments = relationship("ProjectAssignment", back_populates="employee", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="employee", cascade="all, delete-orphan")
    vacations = relationship("Vacation", back_populates="employee", cascade="all, delete-orphan")
    workloads = relationship("Workload", back_populates="employee", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, full_name='{self.full_name}', status='{self.status.value}')>"
```

### 4. Modelo Team

```python
from sqlalchemy import Column, String, Text, Boolean, Integer
from sqlalchemy.orm import relationship

class Team(BaseModel):
    """Modelo para gestión de equipos."""
    __tablename__ = 'teams'
    
    # Información básica
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), unique=True)  # Código corto del equipo
    description = Column(Text, nullable=True)
    color_hex = Column(String(7), default='#3498db')  # Color para visualización
    
    # Configuración del equipo
    max_members = Column(Integer, default=10)
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Metadatos
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    memberships = relationship("TeamMembership", back_populates="team", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="team")
    
    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.name}', code='{self.code}')>"
```

### 5. Modelo TeamMembership

```python
from sqlalchemy import Column, Integer, ForeignKey, Date, Enum, Boolean
from sqlalchemy.orm import relationship
import enum

class MembershipRole(enum.Enum):
    """Roles dentro de un equipo."""
    MEMBER = "member"
    LEAD = "lead"
    SUPERVISOR = "supervisor"
    COORDINATOR = "coordinator"

class TeamMembership(BaseModel):
    """Modelo para membresías de equipos (relación many-to-many con roles)."""
    __tablename__ = 'team_memberships'
    
    # Relaciones
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    
    # Información de la membresía
    role = Column(Enum(MembershipRole), default=MembershipRole.MEMBER, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    employee = relationship("Employee", back_populates="team_memberships")
    team = relationship("Team", back_populates="memberships")
    
    def __repr__(self) -> str:
        return f"<TeamMembership(employee_id={self.employee_id}, team_id={self.team_id}, role='{self.role.value}')>"
```

### 6. Modelo ProjectAssignment

```python
from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric, Text, Boolean
from sqlalchemy.orm import relationship

class ProjectAssignment(BaseModel):
    """Modelo para asignaciones de empleados a proyectos."""
    __tablename__ = 'project_assignments'
    
    # Relaciones
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    # Información de la asignación
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    
    # Carga de trabajo
    allocated_hours_per_day = Column(Numeric(4, 2), nullable=True)  # Horas asignadas por día
    percentage_allocation = Column(Numeric(5, 2), nullable=True)    # Porcentaje de dedicación
    
    # Rol en el proyecto
    role_in_project = Column(String(100), nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relaciones
    employee = relationship("Employee", back_populates="project_assignments")
    project = relationship("Project", back_populates="assignments")
    
    def __repr__(self) -> str:
        return f"<ProjectAssignment(employee_id={self.employee_id}, project_id={self.project_id})>"
```

### 7. Modelo Schedule

```python
from sqlalchemy import Column, Integer, ForeignKey, Date, Time, Text, Boolean
from sqlalchemy.orm import relationship

class Schedule(BaseModel):
    """Modelo para planificación diaria/semanal."""
    __tablename__ = 'schedules'
    
    # Relaciones
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    status_code_id = Column(Integer, ForeignKey('status_codes.id'), nullable=True)
    
    # Información temporal
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    
    # Detalles de la planificación
    description = Column(Text, nullable=True)
    location = Column(String(200), nullable=True)
    
    # Estado
    is_confirmed = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relaciones
    employee = relationship("Employee", back_populates="schedules")
    project = relationship("Project", back_populates="schedules")
    team = relationship("Team", back_populates="schedules")
    status_code = relationship("StatusCode", back_populates="schedules")
    
    def __repr__(self) -> str:
        return f"<Schedule(employee_id={self.employee_id}, date={self.date}, project_id={self.project_id})>"
```

### 8. Modelo StatusCode

```python
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship

class StatusCode(BaseModel):
    """Modelo para códigos de estado configurables."""
    __tablename__ = 'status_codes'
    
    # Información básica
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuración visual
    color = Column(String(7), nullable=True)  # Color hex
    icon = Column(String(50), nullable=True)  # Icono para UI
    
    # Configuración funcional
    is_billable = Column(Boolean, default=True, nullable=False)
    is_productive = Column(Boolean, default=True, nullable=False)
    requires_approval = Column(Boolean, default=False, nullable=False)
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Relaciones
    schedules = relationship("Schedule", back_populates="status_code")
    
    def __repr__(self) -> str:
        return f"<StatusCode(id={self.id}, code='{self.code}', name='{self.name}')>"
```

### 9. Modelo Vacation

```python
from sqlalchemy import Column, Integer, ForeignKey, Date, Text, Enum, Boolean
from sqlalchemy.orm import relationship
import enum

class VacationType(enum.Enum):
    """Tipos de vacaciones."""
    ANNUAL = "annual"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    TRAINING = "training"
    OTHER = "other"

class VacationStatus(enum.Enum):
    """Estados de solicitud de vacaciones."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class Vacation(BaseModel):
    """Modelo para gestión de vacaciones."""
    __tablename__ = 'vacations'
    
    # Relaciones
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    
    # Información de la vacación
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    vacation_type = Column(Enum(VacationType), nullable=False)
    
    # Proceso de aprobación
    status = Column(Enum(VacationStatus), default=VacationStatus.PENDING, nullable=False)
    requested_date = Column(Date, nullable=False)
    approved_date = Column(Date, nullable=True)
    approved_by = Column(String(100), nullable=True)
    
    # Detalles
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Cálculos
    total_days = Column(Integer, nullable=False)  # Días totales
    business_days = Column(Integer, nullable=False)  # Días laborables
    
    # Relaciones
    employee = relationship("Employee", back_populates="vacations")
    
    def __repr__(self) -> str:
        return f"<Vacation(employee_id={self.employee_id}, start_date={self.start_date}, end_date={self.end_date}, status='{self.status.value}')>"
```

### 10. Modelo Workload

```python
from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric, Text
from sqlalchemy.orm import relationship

class Workload(BaseModel):
    """Modelo para seguimiento de carga de trabajo."""
    __tablename__ = 'workloads'
    
    # Relaciones
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    
    # Información temporal
    date = Column(Date, nullable=False)
    week_number = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    
    # Métricas de carga
    planned_hours = Column(Numeric(5, 2), nullable=True)
    actual_hours = Column(Numeric(5, 2), nullable=True)
    utilization_percentage = Column(Numeric(5, 2), nullable=True)
    
    # Eficiencia
    efficiency_score = Column(Numeric(5, 2), nullable=True)  # 0-100
    productivity_index = Column(Numeric(5, 2), nullable=True)
    
    # Detalles
    notes = Column(Text, nullable=True)
    
    # Relaciones
    employee = relationship("Employee", back_populates="workloads")
    project = relationship("Project", back_populates="workloads")
    
    def __repr__(self) -> str:
        return f"<Workload(employee_id={self.employee_id}, date={self.date}, planned_hours={self.planned_hours})>"
```

### 11. Modelo ChangeLog

```python
from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.sql import func

class ChangeLog(BaseModel):
    """Modelo para auditoría de cambios en el sistema."""
    __tablename__ = 'change_logs'
    
    # Información de la entidad modificada
    entity_type = Column(String(50), nullable=False)  # Tipo de entidad (Employee, Project, etc.)
    entity_id = Column(Integer, nullable=False)       # ID de la entidad modificada
    
    # Información del cambio
    action = Column(String(20), nullable=False)       # CREATE, UPDATE, DELETE
    field_name = Column(String(100), nullable=True)   # Campo modificado
    old_value = Column(Text, nullable=True)           # Valor anterior
    new_value = Column(Text, nullable=True)           # Valor nuevo
    
    # Información del usuario
    change_reason = Column(Text, nullable=True)       # Razón del cambio
    changed_by = Column(String(100), nullable=False)  # Usuario que realizó el cambio
    change_date = Column(DateTime, default=func.now(), nullable=False)
    
    # Información técnica
    ip_address = Column(String(45), nullable=True)    # IPv4 o IPv6
    user_agent = Column(Text, nullable=True)          # Información del navegador
    session_id = Column(String(100), nullable=True)   # ID de sesión
    
    # Metadatos (sin updated_at ya que es inmutable)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<ChangeLog(entity_type='{self.entity_type}', entity_id={self.entity_id}, action='{self.action}')>"
```

### 12. Modelo Alert

```python
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

class AlertType(enum.Enum):
    """Tipos de alertas del sistema."""
    CONFLICT = "conflict"                    # Conflictos de planificación
    INSUFFICIENT_PERSONNEL = "insufficient_personnel"  # Personal insuficiente
    OVERALLOCATION = "overallocation"        # Sobreasignación de recursos
    DEADLINE_WARNING = "deadline_warning"    # Advertencia de fecha límite
    VALIDATION_ERROR = "validation_error"    # Error de validación
    SYSTEM_ERROR = "system_error"            # Error del sistema
    APPROVAL_PENDING = "approval_pending"    # Aprobación pendiente
    SCHEDULE_CHANGE = "schedule_change"      # Cambio de horario
    VACATION_CONFLICT = "vacation_conflict"  # Conflicto de vacaciones
    OTHER = "other"                          # Otros tipos

class AlertPriority(enum.Enum):
    """Prioridades de alertas."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Alert(BaseModel):
    """Modelo para sistema de alertas y notificaciones."""
    __tablename__ = 'alerts'
    
    # Información básica de la alerta
    alert_type = Column(Enum(AlertType), nullable=False)
    priority = Column(Enum(AlertPriority), default=AlertPriority.MEDIUM, nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    
    # Relaciones opcionales (pueden ser NULL)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    schedule_id = Column(Integer, ForeignKey('schedules.id'), nullable=True)
    
    # Estado de la alerta
    is_active = Column(Boolean, default=True, nullable=False)
    is_acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Metadatos
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    project = relationship("Project", backref="alerts")
    employee = relationship("Employee", backref="alerts")
    schedule = relationship("Schedule", backref="alerts")
    
    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, type='{self.alert_type.value}', priority='{self.priority.value}', title='{self.title}')>"
```

## Índices Recomendados

```python
# Índices para optimizar consultas frecuentes
from sqlalchemy import Index

# Índices para Employee
Index('idx_employee_status', Employee.status)
Index('idx_employee_full_name', Employee.full_name)
Index('idx_employee_active', Employee.is_available)

# Índices para Project
Index('idx_project_reference', Project.reference)
Index('idx_project_trigram', Project.trigram)
Index('idx_project_client', Project.client_id)
Index('idx_project_status', Project.status)
Index('idx_project_dates', Project.start_date, Project.end_date)

# Índices para Schedule
Index('idx_schedule_employee_date', Schedule.employee_id, Schedule.date)
Index('idx_schedule_project_date', Schedule.project_id, Schedule.date)
Index('idx_schedule_date_range', Schedule.date)

# Índices para ProjectAssignment
Index('idx_assignment_employee', ProjectAssignment.employee_id)
Index('idx_assignment_project', ProjectAssignment.project_id)
Index('idx_assignment_active', ProjectAssignment.is_active)
Index('idx_assignment_dates', ProjectAssignment.start_date, ProjectAssignment.end_date)

# Índices para Vacation
Index('idx_vacation_employee', Vacation.employee_id)
Index('idx_vacation_dates', Vacation.start_date, Vacation.end_date)
Index('idx_vacation_status', Vacation.status)

# Índices para Workload
Index('idx_workload_employee_date', Workload.employee_id, Workload.date)
Index('idx_workload_project_date', Workload.project_id, Workload.date)
Index('idx_workload_week', Workload.year, Workload.week_number)
Index('idx_workload_month', Workload.year, Workload.month)

# Índices para ChangeLog
Index('idx_changelog_entity', ChangeLog.entity_type, ChangeLog.entity_id)
Index('idx_changelog_user_date', ChangeLog.changed_by, ChangeLog.change_date)
Index('idx_changelog_date', ChangeLog.change_date)
Index('idx_changelog_action', ChangeLog.action)

# Índices para Alert
Index('idx_alert_type_priority', Alert.alert_type, Alert.priority)
Index('idx_alert_active', Alert.is_active)
Index('idx_alert_project', Alert.project_id, Alert.is_active)
Index('idx_alert_employee', Alert.employee_id, Alert.is_active)
Index('idx_alert_created', Alert.created_at)
Index('idx_alert_acknowledged', Alert.is_acknowledged, Alert.acknowledged_at)
```

## Restricciones Únicas

```python
from sqlalchemy import UniqueConstraint

# Restricciones para evitar duplicados

# Client - Códigos y nombres únicos
UniqueConstraint('code', name='uq_client_code')
UniqueConstraint('name', name='uq_client_name')

# Project - Referencias y trigramas únicos
UniqueConstraint('reference', name='uq_project_reference')
UniqueConstraint('trigram', name='uq_project_trigram')

# Employee - Códigos y emails únicos
UniqueConstraint('employee_code', name='uq_employee_code')
UniqueConstraint('email', name='uq_employee_email')

# Team - Nombres y códigos únicos
UniqueConstraint('name', name='uq_team_name')
UniqueConstraint('code', name='uq_team_code')

# StatusCode - Códigos únicos
UniqueConstraint('code', name='uq_status_code')

# TeamMembership - Evitar duplicados por empleado/equipo/fecha
UniqueConstraint('employee_id', 'team_id', 'start_date', name='uq_team_membership')

# ProjectAssignment - Evitar duplicados por empleado/proyecto/fecha
UniqueConstraint('employee_id', 'project_id', 'start_date', name='uq_project_assignment')

# Schedule - Un empleado solo puede tener un horario por fecha/proyecto
UniqueConstraint('employee_id', 'date', 'project_id', name='uq_schedule_employee_date_project')

# Workload - Un empleado solo puede tener una carga por fecha
UniqueConstraint('employee_id', 'date', name='uq_workload_employee_date')
```

## Consideraciones de Implementación

### 1. Validaciones a Nivel de Modelo
- Validar que las fechas de fin sean posteriores a las de inicio
- Verificar que los porcentajes estén entre 0 y 100
- Validar que las horas no excedan límites razonables
- Comprobar solapamientos en asignaciones y vacaciones

### 2. Triggers y Funciones Automáticas
- Cálculo automático de días laborables en vacaciones
- Actualización automática de cargas de trabajo
- Notificaciones de conflictos de planificación
- Auditoría de cambios importantes

### 3. Vistas Materializadas Recomendadas
- Vista de disponibilidad de empleados por fecha
- Vista de carga de trabajo agregada por equipo/proyecto
- Vista de métricas de proyecto (progreso, costos, recursos)
- Vista de métricas mensuales de empleados

### 4. Consideraciones de Performance
- Particionado de tablas por fecha para datos históricos
- Índices compuestos para consultas complejas
- Cache de consultas frecuentes
- Optimización de joins entre tablas relacionadas

### 5. Seguridad y Auditoría
- Logging de todos los cambios críticos
- Validación de permisos por rol de usuario
- Encriptación de datos sensibles
- Backup automático de datos críticos