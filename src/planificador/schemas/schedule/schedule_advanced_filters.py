# -*- coding: utf-8 -*-
"""
Esquemas de filtros avanzados para Schedule.

Define los filtros complejos para búsquedas avanzadas de horarios
con múltiples criterios y validaciones.
"""

from typing import List, Optional, Dict, Any
from datetime import date, time
from decimal import Decimal
from pydantic import Field

from planificador.schemas.base.base import BaseSchema


class ScheduleAdvancedFilters(BaseSchema):
    """Esquema para filtros avanzados de búsqueda de horarios."""
    
    # Filtros básicos de entidades relacionadas
    employee_ids: Optional[List[int]] = None
    project_ids: Optional[List[int]] = None
    team_ids: Optional[List[int]] = None
    status_code_ids: Optional[List[int]] = None
    
    # Filtros de fechas
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    created_date_from: Optional[date] = None
    created_date_to: Optional[date] = None
    updated_date_from: Optional[date] = None
    updated_date_to: Optional[date] = None
    
    # Filtros de tiempo
    start_time_from: Optional[time] = None
    start_time_to: Optional[time] = None
    end_time_from: Optional[time] = None
    end_time_to: Optional[time] = None
    
    # Filtros de horas trabajadas
    min_hours_worked: Optional[Decimal] = Field(None, ge=0, le=24)
    max_hours_worked: Optional[Decimal] = Field(None, ge=0, le=24)
    
    # Filtros de estado
    is_confirmed: Optional[bool] = None
    is_active: Optional[bool] = None
    
    # Filtros de búsqueda de texto
    notes_search: Optional[str] = None
    description_search: Optional[str] = None
    
    # Filtros de exclusión
    exclude_schedule_ids: Optional[List[int]] = None
    exclude_employee_ids: Optional[List[int]] = None
    exclude_project_ids: Optional[List[int]] = None
    
    # Filtros de rango de fechas superpuestas
    overlapping_with_date_range: Optional[Dict[str, date]] = None
    
    # Filtros de productividad
    min_productivity_score: Optional[Decimal] = Field(None, ge=0, le=100)
    max_productivity_score: Optional[Decimal] = Field(None, ge=0, le=100)
    
    # Filtros de días de la semana
    weekdays: Optional[List[int]] = Field(None, description="Lista de días de la semana (0=Lunes, 6=Domingo)")
    
    # Filtros de horarios especiales
    is_overtime: Optional[bool] = None
    is_weekend: Optional[bool] = None
    is_holiday: Optional[bool] = None
    
    # Filtros de asignación
    has_multiple_projects: Optional[bool] = None
    has_team_assignment: Optional[bool] = None
    
    class Config:
        """Configuración del esquema."""
        json_encoders = {
            date: lambda v: v.isoformat() if v else None,
            time: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v else None
        }