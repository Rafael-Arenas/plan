# src/planificador/schemas/schedule/schedule.py

from typing import Optional
from pydantic import Field, model_validator
from datetime import datetime, date, time

from ..base.base import BaseSchema


class ScheduleBase(BaseSchema):
    """Schema base para Schedule."""

    employee_id: int
    project_id: Optional[int] = None
    team_id: Optional[int] = None
    status_code_id: Optional[int] = None
    date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    is_confirmed: bool = False
    notes: Optional[str] = None

    @model_validator(mode='after')
    def validate_time_range(self):
        """Validar que end_time sea posterior a start_time."""
        if (self.start_time is not None and 
            self.end_time is not None and 
            self.end_time <= self.start_time):
            raise ValueError('La hora de fin debe ser posterior a la hora de inicio')
        return self

    @model_validator(mode='after')
    def validate_project_or_team(self):
        """Validar que se especifique al menos un proyecto o equipo."""
        if not self.project_id and not self.team_id:
            raise ValueError('Debe especificarse al menos un proyecto o equipo para el horario')
        return self

    @model_validator(mode='after')
    def validate_time_consistency(self):
        """Validar que si se especifica una hora, se especifiquen ambas."""
        if (self.start_time is None) != (self.end_time is None):
            raise ValueError('Debe especificarse tanto la hora de inicio como la de fin, o ninguna')
        return self


class ScheduleCreate(ScheduleBase):
    """Schema para crear un Schedule."""

    pass


class ScheduleUpdate(BaseSchema):
    """Schema para actualizar un Schedule."""

    employee_id: Optional[int] = None
    project_id: Optional[int] = None
    team_id: Optional[int] = None
    status_code_id: Optional[int] = None
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    is_confirmed: Optional[bool] = None
    notes: Optional[str] = None


class Schedule(ScheduleBase):
    """Schema de salida para Schedule."""

    id: int
    created_at: datetime
    updated_at: datetime


class ScheduleSearchFilter(BaseSchema):
    """Filtros para búsqueda de horarios."""

    employee_id: Optional[int] = None
    project_id: Optional[int] = None
    team_id: Optional[int] = None
    status_code_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_confirmed: Optional[bool] = None