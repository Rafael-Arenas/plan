# src/planificador/models/vacation.py

import enum
from datetime import date, timedelta
from sqlalchemy import Column, Integer, ForeignKey, Date, Text, Enum, Boolean, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .base import BaseModel, Base

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

    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    vacation_type = Column(Enum(VacationType), nullable=False)
    status = Column(Enum(VacationStatus), default=VacationStatus.PENDING, nullable=False)
    requested_date = Column(Date, nullable=False)
    approved_date = Column(Date, nullable=True)
    approved_by = Column(String(100), nullable=True)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    total_days = Column(Integer, nullable=False)
    business_days = Column(Integer, nullable=False)

    # Relaciones
    employee = relationship("Employee", back_populates="vacations")

    @hybrid_property
    def duration_days(self) -> int:
        """Calcula la duración total en días (incluyendo fines de semana)."""
        return (self.end_date - self.start_date).days + 1

    @property
    def duration_formatted(self) -> str:
        """Duración formateada como string."""
        days = self.duration_days
        if days == 1:
            return "1 día"
        return f"{days} días"

    @property
    def is_approved(self) -> bool:
        """Verifica si las vacaciones están aprobadas."""
        return self.status == VacationStatus.APPROVED

    @property
    def is_pending(self) -> bool:
        """Verifica si las vacaciones están pendientes de aprobación."""
        return self.status == VacationStatus.PENDING

    @property
    def is_active(self) -> bool:
        """Verifica si las vacaciones están actualmente en curso."""
        today = date.today()
        return (self.status == VacationStatus.APPROVED and 
                self.start_date <= today <= self.end_date)

    @property
    def is_upcoming(self) -> bool:
        """Verifica si las vacaciones son futuras."""
        today = date.today()
        return (self.status == VacationStatus.APPROVED and 
                self.start_date > today)

    @property
    def days_until_start(self) -> int:
        """Días hasta el inicio de las vacaciones."""
        today = date.today()
        if self.start_date <= today:
            return 0
        return (self.start_date - today).days

    @property
    def vacation_type_display(self) -> str:
        """Nombre del tipo de vacación en español."""
        type_names = {
            VacationType.ANNUAL: "Vacaciones Anuales",
            VacationType.SICK: "Licencia Médica",
            VacationType.PERSONAL: "Asuntos Personales",
            VacationType.MATERNITY: "Licencia Maternal",
            VacationType.PATERNITY: "Licencia Paternal",
            VacationType.TRAINING: "Capacitación",
            VacationType.OTHER: "Otros"
        }
        return type_names.get(self.vacation_type, "Desconocido")

    @property
    def status_display(self) -> str:
        """Estado de la solicitud en español."""
        status_names = {
            VacationStatus.PENDING: "Pendiente",
            VacationStatus.APPROVED: "Aprobado",
            VacationStatus.REJECTED: "Rechazado",
            VacationStatus.CANCELLED: "Cancelado"
        }
        return status_names.get(self.status, "Desconocido")

    def overlaps_with(self, other_vacation) -> bool:
        """Verifica si estas vacaciones se superponen con otras."""
        return (self.start_date <= other_vacation.end_date and 
                self.end_date >= other_vacation.start_date)

    def __repr__(self) -> str:
        return f"<Vacation(employee_id={self.employee_id}, start_date={self.start_date}, end_date={self.end_date}, status='{self.status.value}')>"