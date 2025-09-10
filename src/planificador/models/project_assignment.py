# src/planificador/models/project_assignment.py

from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric, Text, Boolean, String
from sqlalchemy.orm import relationship

from .base import BaseModel, Base

class ProjectAssignment(BaseModel):
    """Modelo para asignaciones de empleados a proyectos."""
    __tablename__ = 'project_assignments'

    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    allocated_hours_per_day = Column(Numeric(4, 2), nullable=True)
    percentage_allocation = Column(Numeric(5, 2), nullable=True)
    role_in_project = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)

    # Relaciones
    employee = relationship("Employee", back_populates="project_assignments")
    project = relationship("Project", back_populates="assignments")

    def __repr__(self) -> str:
        return f"<ProjectAssignment(employee_id={self.employee_id}, project_id={self.project_id})>"
    
    # Métodos de utilidad
    @property
    def duration_days(self) -> int | None:
        """Calcula la duración en días de la asignación."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return None
    
    @property
    def is_current(self) -> bool:
        """Verifica si la asignación está activa en la fecha actual."""
        if not self.is_active:
            return False
        
        from datetime import date
        today = date.today()
        
        if self.start_date > today:
            return False
        
        if self.end_date and self.end_date < today:
            return False
        
        return True
    
    @property
    def is_future(self) -> bool:
        """Verifica si la asignación es futura."""
        from datetime import date
        today = date.today()
        return self.start_date > today
    
    @property
    def is_past(self) -> bool:
        """Verifica si la asignación ya terminó."""
        if not self.end_date:
            return False
        
        from datetime import date
        today = date.today()
        return self.end_date < today
    
    @property
    def is_indefinite(self) -> bool:
        """Verifica si la asignación no tiene fecha de fin."""
        return self.end_date is None
    
    @property
    def allocation_category(self) -> str:
        """Categoriza el porcentaje de asignación."""
        if self.percentage_allocation is None:
            return "Sin Definir"
        
        allocation = float(self.percentage_allocation)
        if allocation >= 90:
            return "Tiempo Completo"
        elif allocation >= 70:
            return "Alta Dedicación"
        elif allocation >= 50:
            return "Media Dedicación"
        elif allocation >= 25:
            return "Baja Dedicación"
        else:
            return "Mínima Dedicación"
    
    @property
    def workload_category(self) -> str:
        """Categoriza las horas asignadas por día."""
        if self.allocated_hours_per_day is None:
            return "Sin Definir"
        
        hours = float(self.allocated_hours_per_day)
        if hours >= 8:
            return "Jornada Completa"
        elif hours >= 6:
            return "Jornada Alta"
        elif hours >= 4:
            return "Media Jornada"
        elif hours >= 2:
            return "Jornada Baja"
        else:
            return "Jornada Mínima"
    
    def days_until_start(self) -> int | None:
        """Calcula los días hasta el inicio de la asignación."""
        from datetime import date
        today = date.today()
        
        if self.start_date > today:
            return (self.start_date - today).days
        return 0
    
    def days_until_end(self) -> int | None:
        """Calcula los días hasta el fin de la asignación."""
        if not self.end_date:
            return None
        
        from datetime import date
        today = date.today()
        
        if self.end_date > today:
            return (self.end_date - today).days
        return 0
    
    def progress_percentage(self) -> float | None:
        """Calcula el porcentaje de progreso de la asignación basado en fechas."""
        if not self.end_date:
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
    
    @property
    def status_display(self) -> str:
        """Retorna el estado de la asignación en español."""
        if not self.is_active:
            return "Inactiva"
        
        if self.is_future:
            return "Futura"
        elif self.is_current:
            return "Activa"
        elif self.is_past:
            return "Finalizada"
        else:
            return "Desconocida"
    
    @property
    def assignment_summary(self) -> str:
        """Retorna un resumen de la asignación."""
        summary_parts = []
        
        if self.role_in_project:
            summary_parts.append(f"Rol: {self.role_in_project}")
        
        if self.percentage_allocation is not None:
            summary_parts.append(f"Dedicación: {self.allocation_category}")
        
        if self.allocated_hours_per_day is not None:
            summary_parts.append(f"Carga: {self.workload_category}")
        
        summary_parts.append(f"Estado: {self.status_display}")
        
        return " | ".join(summary_parts)
    
    def overlaps_with(self, other_assignment: 'ProjectAssignment') -> bool:
        """Verifica si esta asignación se superpone con otra."""
        if not self.is_active or not other_assignment.is_active:
            return False
        
        # Si alguna no tiene fecha de fin, usar una fecha muy lejana para comparación
        from datetime import date
        far_future = date(2099, 12, 31)
        
        self_end = self.end_date or far_future
        other_end = other_assignment.end_date or far_future
        
        # Verificar superposición de fechas
        # No hay superposición si una termina antes de que la otra empiece
        return not (self_end < other_assignment.start_date or other_end < self.start_date)