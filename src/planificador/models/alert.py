# src/planificador/models/alert.py

import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel, Base

class AlertType(enum.Enum):
    """Tipos de alertas del sistema."""
    CONFLICT = "conflict"
    INSUFFICIENT_PERSONNEL = "insufficient_personnel"
    OVERALLOCATION = "overallocation"
    DEADLINE_WARNING = "deadline_warning"
    VALIDATION_ERROR = "validation_error"
    SYSTEM_ERROR = "system_error"
    APPROVAL_PENDING = "approval_pending"
    SCHEDULE_CHANGE = "schedule_change"
    VACATION_CONFLICT = "vacation_conflict"
    OTHER = "other"

class AlertStatus(enum.Enum):
    """Estados de una alerta."""
    NEW = "new"
    READ = "read"
    RESOLVED = "resolved"
    IGNORED = "ignored"

class Alert(BaseModel):
    """Modelo para alertas y notificaciones del sistema."""
    __tablename__ = 'alerts'

    user_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.NEW, nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)

    # Relaciones
    user = relationship("Employee")

    # Métodos de utilidad
    @property
    def type_display(self) -> str:
        """Tipo de alerta para mostrar en español."""
        type_translations = {
            AlertType.CONFLICT: "Conflicto",
            AlertType.INSUFFICIENT_PERSONNEL: "Personal Insuficiente",
            AlertType.OVERALLOCATION: "Sobreasignación",
            AlertType.DEADLINE_WARNING: "Advertencia de Fecha Límite",
            AlertType.VALIDATION_ERROR: "Error de Validación",
            AlertType.SYSTEM_ERROR: "Error del Sistema",
            AlertType.APPROVAL_PENDING: "Aprobación Pendiente",
            AlertType.SCHEDULE_CHANGE: "Cambio de Horario",
            AlertType.VACATION_CONFLICT: "Conflicto de Vacaciones",
            AlertType.OTHER: "Otro"
        }
        return type_translations.get(self.alert_type, self.alert_type.value)
    
    @property
    def status_display(self) -> str:
        """Estado de la alerta para mostrar en español."""
        status_translations = {
            AlertStatus.NEW: "Nueva",
            AlertStatus.READ: "Leída",
            AlertStatus.RESOLVED: "Resuelta",
            AlertStatus.IGNORED: "Ignorada"
        }
        return status_translations.get(self.status, self.status.value)
    
    @property
    def is_unread(self) -> bool:
        """Verifica si la alerta no ha sido leída."""
        return not self.is_read
    
    @property
    def is_active(self) -> bool:
        """Verifica si la alerta está activa (nueva o leída, no resuelta ni ignorada)."""
        return self.status in [AlertStatus.NEW, AlertStatus.READ]
    
    @property
    def requires_attention(self) -> bool:
        """Verifica si la alerta requiere atención inmediata."""
        critical_types = [
            AlertType.CONFLICT,
            AlertType.SYSTEM_ERROR,
            AlertType.VALIDATION_ERROR,
            AlertType.DEADLINE_WARNING
        ]
        return self.alert_type in critical_types and self.is_active
    
    @property
    def priority_level(self) -> str:
        """Nivel de prioridad basado en el tipo de alerta."""
        high_priority = [
            AlertType.CONFLICT,
            AlertType.SYSTEM_ERROR,
            AlertType.DEADLINE_WARNING
        ]
        medium_priority = [
            AlertType.INSUFFICIENT_PERSONNEL,
            AlertType.OVERALLOCATION,
            AlertType.VALIDATION_ERROR,
            AlertType.VACATION_CONFLICT
        ]
        
        if self.alert_type in high_priority:
            return "Alta"
        elif self.alert_type in medium_priority:
            return "Media"
        else:
            return "Baja"
    
    @property
    def alert_summary(self) -> str:
        """Resumen completo de la alerta."""
        return f"{self.type_display} - {self.status_display} ({self.priority_level})"
    
    def mark_as_read(self) -> None:
        """Marca la alerta como leída."""
        self.is_read = True
        self.read_at = datetime.now()
        if self.status == AlertStatus.NEW:
            self.status = AlertStatus.READ
    
    def mark_as_resolved(self) -> None:
        """Marca la alerta como resuelta."""
        self.status = AlertStatus.RESOLVED
        if not self.is_read:
            self.mark_as_read()
    
    def mark_as_ignored(self) -> None:
        """Marca la alerta como ignorada."""
        self.status = AlertStatus.IGNORED
        if not self.is_read:
            self.mark_as_read()
    
    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, user_id={self.user_id}, type='{self.alert_type.value}', status='{self.status.value}')>"