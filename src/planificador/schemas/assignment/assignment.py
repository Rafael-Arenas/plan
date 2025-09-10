# src/planificador/schemas/assignment/assignment.py

from typing import Optional
from pydantic import Field, model_validator
from datetime import datetime, date
from decimal import Decimal

from ..base.base import BaseSchema


class ProjectAssignmentBase(BaseSchema):
    """Schema base para ProjectAssignment."""

    employee_id: int
    project_id: int
    start_date: date
    end_date: Optional[date] = None
    allocated_hours_per_day: Optional[Decimal] = Field(None, ge=0, le=24)
    percentage_allocation: Optional[Decimal] = Field(None, ge=0, le=100)
    role_in_project: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    notes: Optional[str] = None

    @model_validator(mode='after')
    def validate_date_range(self):
        """Validar que end_date sea posterior a start_date."""
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return self

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


class ProjectAssignmentCreate(ProjectAssignmentBase):
    """Schema para crear una ProjectAssignment."""

    pass


class ProjectAssignmentUpdate(BaseSchema):
    """Schema para actualizar una ProjectAssignment."""

    employee_id: Optional[int] = None
    project_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    allocated_hours_per_day: Optional[Decimal] = Field(None, ge=0, le=24)
    percentage_allocation: Optional[Decimal] = Field(None, ge=0, le=100)
    role_in_project: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class ProjectAssignment(ProjectAssignmentBase):
    """Schema de salida para ProjectAssignment."""

    id: int
    created_at: datetime
    updated_at: datetime