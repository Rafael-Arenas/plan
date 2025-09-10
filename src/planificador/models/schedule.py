# src/planificador/models/schedule.py

from sqlalchemy import Column, Integer, ForeignKey, Date, Time, Text, Boolean, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timedelta

from .base import BaseModel, Base

class Schedule(BaseModel):
    """Modelo para planificación diaria/semanal."""
    __tablename__ = 'schedules'

    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    status_code_id = Column(Integer, ForeignKey('status_codes.id'), nullable=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String(200), nullable=True)
    is_confirmed = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)

    # Relaciones
    employee = relationship("Employee", back_populates="schedules")
    project = relationship("Project", back_populates="schedules")
    team = relationship("Team", back_populates="schedules")
    status_code = relationship("StatusCode", back_populates="schedules")

    @hybrid_property
    def hours_worked(self) -> float:
        """
        Calcula las horas trabajadas basándose en start_time y end_time.
        
        Returns:
            Número de horas trabajadas como float
        """
        if self.start_time is None or self.end_time is None:
            return 0.0
        
        # Convertir time a datetime para poder calcular la diferencia
        start_datetime = datetime.combine(datetime.today(), self.start_time)
        end_datetime = datetime.combine(datetime.today(), self.end_time)
        
        # Manejar el caso donde end_time es menor que start_time (trabajo nocturno)
        if end_datetime < start_datetime:
            end_datetime += timedelta(days=1)
        
        # Calcular la diferencia en horas
        time_diff = end_datetime - start_datetime
        return time_diff.total_seconds() / 3600.0

    @property
    def duration_formatted(self) -> str:
        """Duración formateada como string (ej: '8h 30m')."""
        hours = self.hours_worked
        if hours == 0:
            return "0h"
        
        whole_hours = int(hours)
        minutes = int((hours - whole_hours) * 60)
        
        if minutes == 0:
            return f"{whole_hours}h"
        return f"{whole_hours}h {minutes}m"

    @property
    def time_range_formatted(self) -> str:
        """Rango de tiempo formateado (ej: '09:00 - 17:30')."""
        if not self.start_time or not self.end_time:
            return "Sin horario definido"
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

    @property
    def is_full_day(self) -> bool:
        """Verifica si es un evento de día completo (sin horarios específicos)."""
        return self.start_time is None and self.end_time is None

    @property
    def assignment_type(self) -> str:
        """Tipo de asignación basado en si tiene proyecto o equipo."""
        if self.project_id:
            return "Proyecto"
        elif self.team_id:
            return "Equipo"
        return "General"

    def is_overlapping_with(self, other_schedule) -> bool:
        """Verifica si este horario se superpone con otro."""
        if self.date != other_schedule.date:
            return False
        
        if self.is_full_day or other_schedule.is_full_day:
            return True
        
        if not all([self.start_time, self.end_time, 
                   other_schedule.start_time, other_schedule.end_time]):
            return False
        
        return (self.start_time < other_schedule.end_time and 
                self.end_time > other_schedule.start_time)

    def __repr__(self) -> str:
        return f"<Schedule(employee_id={self.employee_id}, date={self.date}, project_id={self.project_id})>"