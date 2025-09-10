# src/planificador/models/project.py

import enum
from sqlalchemy import Column, String, Text, Date, Integer, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel, Base

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

    reference = Column(String(50), nullable=False, unique=True)
    trigram = Column(String(3), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    job_code = Column(String(50), nullable=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    shutdown_dates = Column(Text, nullable=True)
    duration_days = Column(Integer, nullable=True)
    required_personnel = Column(Text, nullable=True)
    special_training = Column(Text, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNED, nullable=False)
    priority = Column(Enum(ProjectPriority), default=ProjectPriority.MEDIUM, nullable=False)
    responsible_person = Column(String(100), nullable=True)
    last_updated_by = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    comments = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    validation_status = Column(String(50), nullable=True)
    approval_status = Column(String(50), nullable=True)
    revision_number = Column(Integer, default=1, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    # Relaciones
    client = relationship("Client", back_populates="projects", lazy="selectin")
    assignments = relationship("ProjectAssignment", back_populates="project", cascade="all, delete-orphan", lazy="noload")
    schedules = relationship("Schedule", back_populates="project", cascade="all, delete-orphan", lazy="noload")
    workloads = relationship("Workload", back_populates="project", cascade="all, delete-orphan", lazy="select")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, reference='{self.reference}', name='{self.name}')>"
    
    # Métodos de utilidad
    @property
    def duration_days_calculated(self) -> int | None:
        """Calcula la duración en días entre start_date y end_date."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return None
    
    @property
    def is_active(self) -> bool:
        """Verifica si el proyecto está activo (no archivado y en progreso)."""
        return not self.is_archived and self.status == ProjectStatus.IN_PROGRESS
    
    @property
    def is_completed(self) -> bool:
        """Verifica si el proyecto está completado."""
        return self.status == ProjectStatus.COMPLETED
    
    @property
    def is_planned(self) -> bool:
        """Verifica si el proyecto está en estado planificado."""
        return self.status == ProjectStatus.PLANNED
    
    @property
    def is_on_hold(self) -> bool:
        """Verifica si el proyecto está en pausa."""
        return self.status == ProjectStatus.ON_HOLD
    
    @property
    def is_cancelled(self) -> bool:
        """Verifica si el proyecto está cancelado."""
        return self.status == ProjectStatus.CANCELLED
    
    @property
    def status_display(self) -> str:
        """Retorna el estado del proyecto en español."""
        status_map = {
            ProjectStatus.PLANNED: "Planificado",
            ProjectStatus.IN_PROGRESS: "En Progreso",
            ProjectStatus.ON_HOLD: "En Pausa",
            ProjectStatus.COMPLETED: "Completado",
            ProjectStatus.CANCELLED: "Cancelado"
        }
        return status_map.get(self.status, "Desconocido")
    
    @property
    def priority_display(self) -> str:
        """Retorna la prioridad del proyecto en español."""
        priority_map = {
            ProjectPriority.LOW: "Baja",
            ProjectPriority.MEDIUM: "Media",
            ProjectPriority.HIGH: "Alta",
            ProjectPriority.CRITICAL: "Crítica"
        }
        return priority_map.get(self.priority, "Desconocida")
    
    @property
    def display_name(self) -> str:
        """Retorna el nombre completo del proyecto con referencia."""
        return f"[{self.reference}] {self.name}"
    
    def days_until_start(self) -> int | None:
        """Calcula los días hasta el inicio del proyecto."""
        if not self.start_date:
            return None
        from datetime import date
        today = date.today()
        if self.start_date > today:
            return (self.start_date - today).days
        return 0
    
    def days_since_start(self) -> int | None:
        """Calcula los días transcurridos desde el inicio del proyecto."""
        if not self.start_date:
            return None
        from datetime import date
        today = date.today()
        if self.start_date <= today:
            return (today - self.start_date).days
        return 0
    
    def is_overdue(self) -> bool:
        """Verifica si el proyecto está atrasado (pasó la fecha de fin y no está completado)."""
        if not self.end_date:
            return False
        from datetime import date
        today = date.today()
        return self.end_date < today and not self.is_completed
    
    def progress_percentage(self) -> float | None:
        """Calcula el porcentaje de progreso basado en fechas."""
        if not self.start_date or not self.end_date:
            return None
        
        from datetime import date
        today = date.today()
        
        if today < self.start_date:
            return 0.0
        elif today > self.end_date:
            return 100.0
        else:
            total_days = (self.end_date - self.start_date).days
            elapsed_days = (today - self.start_date).days
            return (elapsed_days / total_days) * 100.0 if total_days > 0 else 0.0