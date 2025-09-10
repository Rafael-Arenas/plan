# src/planificador/models/workload.py

from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import BaseModel, Base

class Workload(BaseModel):
    """Modelo para seguimiento de carga de trabajo."""
    __tablename__ = 'workloads'

    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    date = Column(Date, nullable=False)
    week_number = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    planned_hours = Column(Numeric(10, 9), nullable=True)
    actual_hours = Column(Numeric(10, 9), nullable=True)
    utilization_percentage = Column(Numeric(5, 2), nullable=True)
    efficiency_score = Column(Numeric(5, 2), nullable=True)
    productivity_index = Column(Numeric(5, 2), nullable=True)
    is_billable = Column(Boolean, nullable=True, default=False)
    notes = Column(Text, nullable=True)

    # Relaciones
    employee = relationship("Employee", back_populates="workloads")
    project = relationship("Project", back_populates="workloads")
    
    # Restricciones
    __table_args__ = (
        UniqueConstraint('employee_id', 'date', name='uq_workload_employee_date'),
    )

    def __repr__(self) -> str:
        return f"<Workload(employee_id={self.employee_id}, date={self.date}, planned_hours={self.planned_hours})>"
    
    # Métodos de utilidad
    @property
    def hours_variance(self) -> float | None:
        """Calcula la diferencia entre horas planificadas y reales."""
        if self.planned_hours is not None and self.actual_hours is not None:
            return float(self.actual_hours - self.planned_hours)
        return None
    
    @property
    def hours_variance_percentage(self) -> float | None:
        """Calcula el porcentaje de variación entre horas planificadas y reales."""
        if self.planned_hours is not None and self.actual_hours is not None and self.planned_hours > 0:
            variance = float(self.actual_hours - self.planned_hours)
            return (variance / float(self.planned_hours)) * 100.0
        return None
    
    @property
    def is_over_planned(self) -> bool:
        """Verifica si las horas reales exceden las planificadas."""
        if self.planned_hours is not None and self.actual_hours is not None:
            return self.actual_hours > self.planned_hours
        return False
    
    @property
    def is_under_planned(self) -> bool:
        """Verifica si las horas reales son menores a las planificadas."""
        if self.planned_hours is not None and self.actual_hours is not None:
            return self.actual_hours < self.planned_hours
        return False
    
    @property
    def efficiency_category(self) -> str:
        """Categoriza la eficiencia del trabajo."""
        if self.efficiency_score is None:
            return "Sin datos"
        
        score = float(self.efficiency_score)
        if score >= 95:
            return "Alta"
        elif score >= 90:
            return "Buena"
        elif score >= 70:
            return "Media"
        elif score >= 50:
            return "Baja"
        else:
            return "Muy Baja"
    
    @property
    def productivity_category(self) -> str:
        """Categoriza la productividad del trabajo."""
        if self.productivity_index is None:
            return "Sin Datos"
        
        index = float(self.productivity_index)
        if index >= 95:
            return "Muy Alta"
        elif index >= 90:
            return "Alta"
        elif index >= 70:
            return "Media"
        elif index >= 50:
            return "Baja"
        else:
            return "Muy Baja"
    
    @property
    def utilization_category(self) -> str:
        """Categoriza la utilización del empleado."""
        if self.utilization_percentage is None:
            return "Sin Datos"
        
        utilization = float(self.utilization_percentage)
        if utilization >= 95:
            return "Sobrecarga"
        elif utilization >= 85:
            return "Óptima"
        elif utilization >= 70:
            return "Buena"
        elif utilization >= 50:
            return "Baja"
        else:
            return "Muy Baja"
    
    @property
    def billable_status(self) -> str:
        """Retorna el estado de facturación en español."""
        if self.is_billable is None:
            return "No Definido"
        return "Facturable" if self.is_billable else "No facturable"
    
    def calculate_efficiency_score(self) -> float | None:
        """Calcula el score de eficiencia basado en horas planificadas vs reales."""
        if self.planned_hours is not None and self.actual_hours is not None:
            planned = float(self.planned_hours)
            actual = float(self.actual_hours)
            
            # Si planned_hours es 0, no se puede calcular eficiencia
            if planned == 0:
                return None
                
            # Si actual_hours es 0, no se puede calcular eficiencia
            if actual == 0:
                return None
            
            # Calcular eficiencia: mientras más cerca esté actual de planned, mejor
            if actual <= planned:
                # Si se trabajó menos o igual a lo planificado, la eficiencia es proporcional
                return (actual / planned) * 100.0
            else:
                # Si se trabajó más de lo planificado, penalizar
                return max(0.0, (planned / actual) * 100.0)
        return None
    
    @property
    def is_weekend(self) -> bool:
        """Verifica si la fecha corresponde a un fin de semana."""
        if self.date:
            return self.date.weekday() >= 5  # 5=Saturday, 6=Sunday
        return False
    
    def get_quarter(self) -> int:
        """Retorna el trimestre del año para esta carga de trabajo."""
        return ((self.month - 1) // 3) + 1
    
    @property
    def performance_summary(self) -> str:
        """Retorna un resumen del rendimiento."""
        summary_parts = []
        
        if self.efficiency_score is not None:
            summary_parts.append(f"Eficiencia: {self.efficiency_category}")
        
        if self.productivity_index is not None:
            summary_parts.append(f"Productividad: {self.productivity_category}")
        
        if self.utilization_percentage is not None:
            summary_parts.append(f"Utilización: {self.utilization_category}")
        
        return " | ".join(summary_parts) if summary_parts else "Sin métricas disponibles"