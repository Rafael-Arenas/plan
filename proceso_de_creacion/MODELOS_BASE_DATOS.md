# Diseño de Modelos de Base de Datos - Sistema de Planificación de Equipos

## 1. Análisis de Datos del Excel

### Estructura Identificada en "Planning" (52 columnas)

#### Información de Proyectos (Columnas A-K)
- **Référence projet**: Referencia única del proyecto
- **TRI-GRAMME**: Código de tres letras del proyecto
- **Nom du projet/Centrale**: Nombre completo del proyecto o central
- **JOB**: Identificador del trabajo específico
- **CLIENT**: Cliente asociado al proyecto
- **Dates d'arrêt**: Fechas de parada o mantenimiento
- **Personnel**: Personal asignado al proyecto
- **Formation spéciale**: Formación especial requerida
- **Durée**: Duración estimada del proyecto
- **Auteur MAJ**: Autor de la última actualización
- **Date MAJ**: Fecha de la última actualización

## 2. Diseño de Modelos SQLAlchemy

### 2.1 Modelo Cliente (Client)

```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from .base import BaseModel

class Client(BaseModel):
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Campos esenciales (del Excel original)
    name = Column(String(200), nullable=False, unique=True)  # Columna E "CLIENT" del Excel
    code = Column(String(10), unique=True)  # Código interno opcional para referencias rápidas
    
    # Contacto básico (opcional para gestión)
    contact_person = Column(String(100))  # Persona de contacto
    email = Column(String(100))  # Email de contacto
    phone = Column(String(20))  # Teléfono de contacto
    
    # Estado y observaciones
    is_active = Column(Boolean, default=True, nullable=False)  # Gestión de clientes activos/inactivos
    notes = Column(Text)  # Observaciones generales
    
    # Metadatos técnicos
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    projects = relationship("Project", back_populates="client")
    
    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', code='{self.code}')>"
```

### 2.2 Modelo Proyecto (Project)

```python
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from .base import BaseModel

class Project(BaseModel):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    reference = Column(String(50), unique=True, nullable=False)  # Référence projet
    trigram = Column(String(3), nullable=False, unique=True)  # TRI-GRAMME
    name = Column(String(255), nullable=False)  # Nom du projet/Centrale
    job_code = Column(String(50))  # JOB
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    
    # Fechas del proyecto
    start_date = Column(Date)
    end_date = Column(Date)
    shutdown_dates = Column(Text)  # Dates d'arrêt (formato JSON o texto)
    
    # Detalles del proyecto
    duration_days = Column(Integer)  # Durée
    special_training = Column(Text)  # Formation spéciale
    description = Column(Text)
    
    # Metadatos
    last_updated_by = Column(String(100))  # Auteur MAJ
    last_updated_date = Column(Date)  # Date MAJ
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    client = relationship("Client", back_populates="projects")
    schedules = relationship("Schedule", back_populates="project")
    project_assignments = relationship("ProjectAssignment", back_populates="project")
    
    def __repr__(self):
        return f"<Project(id={self.id}, reference='{self.reference}', name='{self.name}')>"
```

### 2.3 Modelo Empleado (Employee)

```python
from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, func, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class Employee(BaseModel):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(255), nullable=False)  # Nombre completo como aparece en Excel
    employee_code = Column(String(20), unique=True)  # Código único del empleado
    
    # Información personal
    email = Column(String(255))
    phone = Column(String(50))
    position = Column(String(100))
    department = Column(String(100))
    
    # Fechas importantes
    hire_date = Column(Date)
    birth_date = Column(Date)
    
    # Cualificaciones y habilidades
    qualification_level = Column(String(10))  # HN1, HN2, etc.
    qualification_type = Column(String(50))  # 'montador', 'supervisor', etc.
    special_training = Column(Text)  # Formación especial requerida
    certifications = Column(Text)  # Certificaciones (formato JSON)
    special_skills = Column(Text)  # Habilidades especiales
    
    # Estado y configuración
    is_active = Column(Boolean, default=True, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    availability_status = Column(String(20), default='available')  # 'available', 'uncertain', 'unavailable'
    can_work_weekends = Column(Boolean, default=False)
    
    # Metadatos
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    schedules = relationship("Schedule", back_populates="employee")
    vacations = relationship("Vacation", back_populates="employee")
    workloads = relationship("Workload", back_populates="employee")
    project_assignments = relationship("ProjectAssignment", back_populates="employee")
    team_memberships = relationship("TeamMembership", back_populates="employee")
    
    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.display_name}', code='{self.employee_code}')>"
```

### 2.4 Modelo Equipo (Team)

```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from .base import BaseModel

class Team(BaseModel):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), unique=True)  # Código corto del equipo
    description = Column(Text)
    color_hex = Column(String(7), default='#3498db')  # Color para visualización
    
    # Configuración del equipo
    max_members = Column(Integer, default=10)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Metadatos
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    schedules = relationship("Schedule", back_populates="team")
    team_memberships = relationship("TeamMembership", back_populates="team")
    
    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', code='{self.code}')>"
```

### 2.5 Modelo Membresía de Equipo (TeamMembership)

```python
from sqlalchemy import Column, Integer, ForeignKey, Date, Boolean, DateTime, func, String
from sqlalchemy.orm import relationship
from .base import BaseModel

class TeamMembership(BaseModel):
    __tablename__ = 'team_memberships'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    
    # Fechas de membresía
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)  # NULL significa membresía activa
    
    # Rol en el equipo
    role = Column(String(50), default='member')  # 'leader', 'member', 'specialist'
    is_primary_team = Column(Boolean, default=False)  # Equipo principal del empleado
    
    # Metadatos
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    employee = relationship("Employee", back_populates="team_memberships")
    team = relationship("Team", back_populates="team_memberships")
    
    def __repr__(self):
        return f"<TeamMembership(employee_id={self.employee_id}, team_id={self.team_id}, role='{self.role}')>"
```

### 2.6 Modelo Asignación de Proyecto (ProjectAssignment)

```python
from sqlalchemy import Column, Integer, ForeignKey, Date, Boolean, DateTime, func, String, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class ProjectAssignment(BaseModel):
    __tablename__ = 'project_assignments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    
    # Fechas de asignación
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    
    # Detalles de la asignación
    role_in_project = Column(String(100))  # Rol específico en el proyecto
    allocation_percentage = Column(Integer, default=100)  # % de dedicación
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Metadatos
    assigned_by = Column(String(100))  # Quien asignó
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    project = relationship("Project", back_populates="project_assignments")
    employee = relationship("Employee", back_populates="project_assignments")
    
    def __repr__(self):
        return f"<ProjectAssignment(project_id={self.project_id}, employee_id={self.employee_id}, role='{self.role_in_project}')>"
```

### 2.7 Modelo Planificación (Schedule)

```python
from sqlalchemy import Column, Integer, ForeignKey, Date, String, Text, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from .base import BaseModel

class Schedule(BaseModel):
    __tablename__ = 'schedules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    schedule_date = Column(Date, nullable=False)
    
    # Asignaciones opcionales
    team_id = Column(Integer, ForeignKey('teams.id'))
    project_id = Column(Integer, ForeignKey('projects.id'))
    
    # Estado y detalles
    status_code = Column(String(10), nullable=False)  # Código de estado del día
    work_hours = Column(Integer, default=8)  # Horas de trabajo planificadas
    notes = Column(Text)  # Notas adicionales
    
    # Información adicional
    is_overtime = Column(Boolean, default=False)
    is_weekend_work = Column(Boolean, default=False)
    location = Column(String(100))  # Ubicación de trabajo
    
    # Metadatos
    created_by = Column(String(100))
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    employee = relationship("Employee", back_populates="schedules")
    team = relationship("Team", back_populates="schedules")
    project = relationship("Project", back_populates="schedules")
    status = relationship("StatusCode", foreign_keys=[status_code], primaryjoin="Schedule.status_code == StatusCode.code")
    
    # Constraint único para evitar duplicados
    __table_args__ = (
        {'extend_existing': True}
    )
    
    def __repr__(self):
        return f"<Schedule(employee_id={self.employee_id}, date={self.schedule_date}, status='{self.status_code}')>"
```

### 2.8 Modelo Códigos de Estado (StatusCode)

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text
from .base import BaseModel

class StatusCode(BaseModel):
    __tablename__ = 'status_codes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)  # Código corto (ej: 'T', 'V', 'M')
    name = Column(String(100), nullable=False)  # Nombre descriptivo
    description = Column(String(255), nullable=False)  # Descripción completa
    color_hex = Column(String(7), nullable=False)  # Color para visualización
    
    # Tipos específicos de estado según requerimientos
    status_category = Column(String(50))  # 'presence', 'travel', 'vacation', 'uncertain'
    # Ejemplos: verde para presencia en sitio, azul para viajando
    
    # Categorización
    category = Column(String(50), nullable=False)  # 'work', 'vacation', 'absence', 'training'
    is_productive = Column(Boolean, default=True)  # Si cuenta como tiempo productivo
    is_billable = Column(Boolean, default=False)  # Si es facturable al cliente
    
    # Configuración adicional
    indicates_uncertainty = Column(Boolean, default=False)  # Para disponibilidad incierta
    triggers_alert = Column(Boolean, default=False)  # Si debe generar alertas
    requires_approval = Column(Boolean, default=False)  # Si requiere aprobación
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0)  # Para ordenamiento en UI
    
    # Metadatos
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<StatusCode(code='{self.code}', description='{self.description}', category='{self.category}')>"
```

### 2.9 Modelo Vacaciones (Vacation)

```python
from sqlalchemy import Column, Integer, ForeignKey, Date, String, Text, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from .base import BaseModel

class Vacation(BaseModel):
    __tablename__ = 'vacations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    
    # Fechas de vacaciones
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Tipo y detalles
    vacation_type = Column(String(50), nullable=False)  # 'annual', 'sick', 'personal', 'maternity'
    description = Column(Text)
    reason = Column(Text)  # Motivo específico
    
    # Estado de aprobación
    status = Column(String(20), default='pending')  # 'pending', 'approved', 'rejected', 'cancelled'
    approved_by = Column(String(100))  # Quien aprobó
    approved_date = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Cálculos
    total_days = Column(Integer, nullable=False)  # Días totales de vacaciones
    business_days = Column(Integer, nullable=False)  # Días laborables
    
    # Metadatos
    requested_by = Column(String(100))  # Quien solicitó (puede ser diferente del empleado)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    employee = relationship("Employee", back_populates="vacations")
    
    def __repr__(self):
        return f"<Vacation(employee_id={self.employee_id}, start={self.start_date}, end={self.end_date}, type='{self.vacation_type}')>"
```

### 2.10 Modelo Carga de Trabajo (Workload)

```python
from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from .base import BaseModel

class Workload(BaseModel):
    __tablename__ = 'workloads'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    
    # Período
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    
    # Horas planificadas vs reales
    planned_hours = Column(Numeric(7, 2), default=0.0)  # Horas planificadas
    actual_hours = Column(Numeric(7, 2), default=0.0)   # Horas reales trabajadas
    overtime_hours = Column(Numeric(7, 2), default=0.0) # Horas extra
    
    # Métricas calculadas
    efficiency_percentage = Column(Numeric(5, 2))  # % de eficiencia
    utilization_percentage = Column(Numeric(5, 2)) # % de utilización
    
    # Detalles adicionales
    billable_hours = Column(Numeric(7, 2), default=0.0)  # Horas facturables
    training_hours = Column(Numeric(7, 2), default=0.0)  # Horas de formación
    vacation_hours = Column(Numeric(7, 2), default=0.0)  # Horas de vacaciones
    
    # Estado
    is_finalized = Column(Boolean, default=False)  # Si el mes está cerrado
    notes = Column(String(500))  # Notas del período
    
    # Metadatos
    calculated_at = Column(DateTime)  # Cuándo se calculó
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    employee = relationship("Employee", back_populates="workloads")
    
    # Constraint único para evitar duplicados
    __table_args__ = (
        {'extend_existing': True}
    )
    
    def __repr__(self):
        return f"<Workload(employee_id={self.employee_id}, year={self.year}, month={self.month}, planned={self.planned_hours}h)>"
```

### 2.11 Modelo Seguimiento de Cambios (ChangeLog)

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class ChangeLog(BaseModel):
    __tablename__ = 'change_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Información del cambio
    entity_type = Column(String(50), nullable=False)  # 'project', 'schedule', 'employee'
    entity_id = Column(Integer, nullable=False)  # ID de la entidad modificada
    action = Column(String(20), nullable=False)  # 'create', 'update', 'delete'
    
    # Detalles del cambio
    field_name = Column(String(100))  # Campo modificado
    old_value = Column(Text)  # Valor anterior
    new_value = Column(Text)  # Nuevo valor
    change_reason = Column(Text)  # Razón del cambio
    
    # Usuario responsable
    changed_by = Column(String(100), nullable=False)  # Usuario que realizó el cambio
    change_date = Column(DateTime, default=func.now(), nullable=False)
    
    # Información adicional
    ip_address = Column(String(45))  # Dirección IP del usuario
    user_agent = Column(Text)  # Información del navegador
    session_id = Column(String(100))  # ID de sesión
    
    # Metadatos
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ChangeLog(id={self.id}, entity='{self.entity_type}', action='{self.action}')>"
```

### 2.12 Modelo Alertas y Notificaciones (Alert)

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, func, Boolean, Enum
from .base import BaseModel
import enum

class AlertType(enum.Enum):
    INSUFFICIENT_PERSONNEL = "insufficient_personnel"
    SCHEDULE_CONFLICT = "schedule_conflict"
    PROJECT_DELAY = "project_delay"
    VACATION_CONFLICT = "vacation_conflict"
    QUALIFICATION_MISSING = "qualification_missing"
    UNCERTAIN_AVAILABILITY = "uncertain_availability"

class AlertPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Alert(BaseModel):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Tipo y prioridad
    alert_type = Column(Enum(AlertType), nullable=False)
    priority = Column(Enum(AlertPriority), default=AlertPriority.MEDIUM)
    
    # Contenido de la alerta
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(Text)  # Información adicional en formato JSON
    
    # Entidades relacionadas
    project_id = Column(Integer, ForeignKey('projects.id'))
    employee_id = Column(Integer, ForeignKey('employees.id'))
    schedule_id = Column(Integer, ForeignKey('schedules.id'))
    
    # Estado de la alerta
    is_active = Column(Boolean, default=True, nullable=False)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # Metadatos
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    project = relationship("Project")
    employee = relationship("Employee")
    schedule = relationship("Schedule")
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type='{self.alert_type.value}', priority='{self.priority.value}')>"
```

## 3. Modelo Base (BaseModel)

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    # Campos comunes para auditoría
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """Convierte el modelo a diccionario para serialización"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def update_from_dict(self, data: dict):
        """Actualiza el modelo desde un diccionario"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
```

## 4. Índices y Constraints Recomendados

```sql
-- Índices para optimizar consultas frecuentes
CREATE INDEX idx_schedules_employee_date ON schedules(employee_id, schedule_date);
CREATE INDEX idx_schedules_date_status ON schedules(schedule_date, status_code);
CREATE INDEX idx_schedules_team_date ON schedules(team_id, schedule_date);
CREATE INDEX idx_schedules_project_date ON schedules(project_id, schedule_date);

CREATE INDEX idx_vacations_employee_dates ON vacations(employee_id, start_date, end_date);
CREATE INDEX idx_vacations_dates ON vacations(start_date, end_date);

CREATE INDEX idx_workloads_employee_period ON workloads(employee_id, year, month);
CREATE INDEX idx_workloads_period ON workloads(year, month);

CREATE INDEX idx_project_assignments_employee ON project_assignments(employee_id, is_active);
CREATE INDEX idx_project_assignments_project ON project_assignments(project_id, is_active);

CREATE INDEX idx_team_memberships_employee ON team_memberships(employee_id, end_date);
CREATE INDEX idx_team_memberships_team ON team_memberships(team_id, end_date);

CREATE INDEX idx_changelog_entity ON change_logs(entity_type, entity_id);
CREATE INDEX idx_changelog_user_date ON change_logs(changed_by, change_date);
CREATE INDEX idx_changelog_date ON change_logs(change_date);

CREATE INDEX idx_alert_type_priority ON alerts(alert_type, priority);
CREATE INDEX idx_alert_active ON alerts(is_active, created_at);
CREATE INDEX idx_alert_project ON alerts(project_id, is_active);
CREATE INDEX idx_alert_employee ON alerts(employee_id, is_active);
CREATE INDEX idx_alert_schedule ON alerts(schedule_id, is_active);

-- Constraints únicos para integridad de datos
ALTER TABLE clients ADD CONSTRAINT uq_client_code UNIQUE(code);
ALTER TABLE clients ADD CONSTRAINT uq_client_name UNIQUE(name);
ALTER TABLE projects ADD CONSTRAINT uq_project_reference UNIQUE(reference);
ALTER TABLE projects ADD CONSTRAINT uq_project_trigram UNIQUE(trigram);
ALTER TABLE employees ADD CONSTRAINT uq_employee_code UNIQUE(employee_code);
ALTER TABLE employees ADD CONSTRAINT uq_employee_email UNIQUE(email);
ALTER TABLE teams ADD CONSTRAINT uq_team_name UNIQUE(name);
ALTER TABLE teams ADD CONSTRAINT uq_team_code UNIQUE(code);
ALTER TABLE status_codes ADD CONSTRAINT uq_status_code UNIQUE(code);
ALTER TABLE team_memberships ADD CONSTRAINT uq_team_membership UNIQUE(team_id, employee_id);
ALTER TABLE project_assignments ADD CONSTRAINT uq_project_assignment UNIQUE(project_id, employee_id);
ALTER TABLE schedules ADD CONSTRAINT uq_schedule_employee_date_project UNIQUE(employee_id, schedule_date, project_id);
ALTER TABLE workloads ADD CONSTRAINT uq_workload_employee_date UNIQUE(employee_id, year, month);
```

## 5. Consideraciones de Implementación

### 5.1 Entrada Manual de Datos
- Los modelos están diseñados para facilitar la entrada manual de datos desde cero
- Se incluyen validaciones robustas para garantizar la integridad de los datos
- Los campos opcionales permiten configuración gradual del sistema

### 5.2 Validaciones a Nivel de Modelo
- **Fechas**: Validar que end_date >= start_date
- **Porcentajes**: Validar rangos 0-100 para efficiency_percentage, utilization_percentage
- **Códigos únicos**: Validar unicidad de códigos de empleados, proyectos, equipos
- **Horas**: Validar que las horas sean valores positivos

### 5.3 Triggers y Funciones Automáticas
- **Cálculo automático de días laborables** en vacaciones
- **Actualización automática de workloads** cuando se modifican schedules
- **Validación de conflictos** de asignaciones de empleados
- **Auditoría automática** de cambios críticos

### 5.4 Vistas Materializadas Recomendadas
- **Vista de disponibilidad de empleados** por fecha
- **Vista de carga de trabajo actual** por equipo
- **Vista de proyectos activos** con asignaciones
- **Vista de métricas mensuales** por empleado

---

*Este diseño de modelos proporciona una base sólida y escalable para manejar todos los aspectos identificados en el Excel de planificación de equipos, con relaciones bien definidas y optimizaciones para consultas frecuentes.*