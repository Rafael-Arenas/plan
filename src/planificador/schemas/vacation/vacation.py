# src/planificador/schemas/vacation/vacation.py

from typing import Optional
from pydantic import Field, model_validator
from datetime import datetime, date

from ..base.base import BaseSchema
from ...models.vacation import VacationType, VacationStatus


class VacationBase(BaseSchema):
    """Schema base para Vacation."""

    employee_id: int = Field(..., gt=0)
    start_date: date
    end_date: date
    vacation_type: VacationType
    status: VacationStatus = VacationStatus.PENDING
    requested_date: date
    approved_date: Optional[date] = None
    approved_by: Optional[str] = Field(None, max_length=100)
    reason: Optional[str] = None
    notes: Optional[str] = None
    total_days: int = Field(..., ge=1)
    business_days: int = Field(..., ge=1)

    @model_validator(mode='after')
    def validate_date_range(self):
        """Validar que end_date sea posterior a start_date."""
        if self.start_date is not None and self.end_date is not None:
            if self.end_date <= self.start_date:
                raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return self

    @model_validator(mode='after')
    def validate_approval_consistency(self):
        """Validar consistencia entre estado de aprobación y campos relacionados."""
        if self.status is not None:
            if self.status == VacationStatus.APPROVED:
                if not self.approved_date:
                    raise ValueError('Las vacaciones aprobadas deben tener fecha de aprobación')
                if not self.approved_by:
                    raise ValueError('Las vacaciones aprobadas deben indicar quién las aprobó')
            elif self.status == VacationStatus.PENDING:
                if self.approved_date or self.approved_by:
                    raise ValueError('Las vacaciones pendientes no pueden tener datos de aprobación')
        return self

    @model_validator(mode='after')
    def validate_requested_date(self):
        """Validar que requested_date no sea posterior a start_date."""
        if self.requested_date is not None and self.start_date is not None:
            if self.requested_date > self.start_date:
                raise ValueError('La fecha de solicitud no puede ser posterior al inicio de vacaciones')
        return self


class VacationCreate(VacationBase):
    """Schema para crear una Vacation."""

    pass


class VacationUpdate(VacationBase):
    """Schema para actualizar una Vacation."""

    employee_id: Optional[int] = Field(None, gt=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    vacation_type: Optional[VacationType] = None
    status: Optional[VacationStatus] = None
    requested_date: Optional[date] = None
    approved_date: Optional[date] = None
    approved_by: Optional[str] = Field(None, max_length=100)
    reason: Optional[str] = None
    notes: Optional[str] = None
    total_days: Optional[int] = Field(None, ge=1)
    business_days: Optional[int] = Field(None, ge=1)


class Vacation(VacationBase):
    """Schema de salida para Vacation."""

    id: int = Field(..., gt=0)
    created_at: datetime
    updated_at: datetime


class VacationSearchFilter(BaseSchema):
    """Filtros para búsqueda de vacaciones."""

    employee_id: Optional[int] = Field(None, gt=0)
    vacation_type: Optional[VacationType] = None
    status: Optional[VacationStatus] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    end_date_from: Optional[date] = None
    end_date_to: Optional[date] = None