# src/planificador/schemas/schedule/confirmation_schemas.py

from typing import List, Optional, Dict, Any
from pydantic import Field
from datetime import datetime, date

from ..base.base import BaseSchema


class ScheduleConfirmationSchema(BaseSchema):
    """Esquema para confirmación individual de horario."""
    
    schedule_id: int
    is_confirmed: bool = True
    confirmation_notes: Optional[str] = Field(None, max_length=500)
    confirmed_by: Optional[int] = None  # ID del usuario que confirma
    confirmation_timestamp: Optional[datetime] = None


class BulkConfirmationSchema(BaseSchema):
    """Esquema para confirmación masiva de horarios."""
    
    schedule_ids: List[int] = Field(..., min_items=1, max_items=100)
    is_confirmed: bool = True
    confirmation_notes: Optional[str] = Field(None, max_length=500)
    confirmed_by: Optional[int] = None  # ID del usuario que confirma


class ConfirmationResponseSchema(BaseSchema):
    """Esquema de respuesta para operaciones de confirmación."""
    
    success: bool
    confirmed_count: int
    failed_count: int = 0
    confirmed_schedules: List[int] = []
    failed_schedules: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []


class PendingConfirmationSchema(BaseSchema):
    """Esquema para horarios pendientes de confirmación."""
    
    schedule_id: int
    employee_id: int
    employee_name: str
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    team_id: Optional[int] = None
    team_name: Optional[str] = None
    date: date
    start_time: Optional[str] = None  # Formato HH:MM
    end_time: Optional[str] = None    # Formato HH:MM
    description: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    days_pending: int = 0
    priority_level: str = "normal"  # "low", "normal", "high", "urgent"


class ConfirmationFilterSchema(BaseSchema):
    """Filtros para búsqueda de confirmaciones pendientes."""
    
    employee_id: Optional[int] = None
    project_id: Optional[int] = None
    team_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    priority_level: Optional[str] = None
    days_pending_min: Optional[int] = None
    days_pending_max: Optional[int] = None