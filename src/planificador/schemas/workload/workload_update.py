# src/planificador/schemas/workload/workload_update.py

from typing import Optional
from pydantic import Field
from datetime import date
from decimal import Decimal

from ..base.base import BaseSchema


class WorkloadUpdate(BaseSchema):
    """Schema para actualizar un Workload."""

    employee_id: Optional[int] = None
    project_id: Optional[int] = None
    date: Optional[date] = None
    week_number: Optional[int] = Field(None, ge=1, le=53)
    month: Optional[int] = Field(None, ge=1, le=12)
    year: Optional[int] = Field(None, ge=2020, le=2050)
    planned_hours: Optional[Decimal] = Field(None, ge=0, le=24)
    actual_hours: Optional[Decimal] = Field(None, ge=0, le=24)
    utilization_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    efficiency_score: Optional[Decimal] = Field(None, ge=0, le=100)
    productivity_index: Optional[Decimal] = Field(None, ge=0, le=100)
    is_billable: Optional[bool] = None
    notes: Optional[str] = None