# src/planificador/schemas/workload/workload.py

from typing import Optional
from pydantic import Field, model_validator
from datetime import datetime, date
from decimal import Decimal

from ..base.base import BaseSchema


class WorkloadBase(BaseSchema):
    """Schema base para Workload."""

    employee_id: int
    project_id: Optional[int] = None
    date: date
    week_number: int = Field(..., ge=1, le=53)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2050)
    planned_hours: Optional[Decimal] = Field(None, ge=0, le=24)
    actual_hours: Optional[Decimal] = Field(None, ge=0, le=24)
    utilization_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    efficiency_score: Optional[Decimal] = Field(None, ge=0, le=100)
    productivity_index: Optional[Decimal] = Field(None, ge=0, le=100)
    is_billable: Optional[bool] = Field(default=False)
    notes: Optional[str] = None

    @model_validator(mode='after')
    def validate_date_consistency(self):
        """Validar que la fecha sea consistente con semana, mes y año."""
        if self.date.year != self.year:
            raise ValueError('El año de la fecha debe coincidir con el campo year')
        if self.date.month != self.month:
            raise ValueError('El mes de la fecha debe coincidir con el campo month')
        return self

    @model_validator(mode='after')
    def validate_hours_consistency(self):
        """Validar consistencia entre horas planificadas y reales."""
        if (self.planned_hours is not None and 
            self.actual_hours is not None and 
            self.actual_hours > self.planned_hours * 2):
            raise ValueError(
                'Las horas reales no pueden ser más del doble de las horas planificadas'
            )
        return self

    @model_validator(mode='after')
    def validate_efficiency_metrics(self):
        """Validar que las métricas de eficiencia sean consistentes."""
        if (self.planned_hours is not None and 
            self.actual_hours is not None and 
            self.planned_hours > 0 and 
            self.efficiency_score is not None):
            # Eficiencia = (horas planificadas / horas reales) * 100
            calculated_efficiency = (self.planned_hours / self.actual_hours) * 100
            if abs(float(self.efficiency_score) - float(calculated_efficiency)) > 10:
                raise ValueError(
                    'El score de eficiencia no es consistente con las horas planificadas y reales'
                )
        return self


class WorkloadCreate(WorkloadBase):
    """Schema para crear un Workload."""

    pass


class Workload(WorkloadBase):
    """Schema de salida para Workload."""

    id: int
    created_at: datetime
    updated_at: datetime