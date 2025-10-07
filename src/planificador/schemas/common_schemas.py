# -*- coding: utf-8 -*-
"""
Esquemas comunes reutilizables en toda la aplicación.

Este módulo contiene esquemas base que son utilizados por múltiples servicios
y módulos de la aplicación, como paginación, ordenamiento y rangos de fechas.
"""

from datetime import date
from typing import Optional
from pydantic import Field, validator

from planificador.schemas.base.base import BaseSchema


class PaginationSchema(BaseSchema):
    """Esquema para parámetros de paginación."""
    
    page: int = Field(default=1, ge=1, description="Número de página (1-based)")
    page_size: int = Field(default=50, ge=1, le=1000, description="Elementos por página")
    
    @validator('page')
    def validate_page(cls, v):
        """Valida que la página sea positiva."""
        if v < 1:
            raise ValueError("La página debe ser mayor a 0")
        return v
    
    @validator('page_size')
    def validate_page_size(cls, v):
        """Valida el tamaño de página."""
        if v < 1:
            raise ValueError("El tamaño de página debe ser mayor a 0")
        if v > 1000:
            raise ValueError("El tamaño de página no puede ser mayor a 1000")
        return v


class SortingSchema(BaseSchema):
    """Esquema para parámetros de ordenamiento."""
    
    sort_by: str = Field(default="created_at", description="Campo por el cual ordenar")
    sort_order: str = Field(default="desc", description="Orden: 'asc' o 'desc'")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        """Valida el orden de clasificación."""
        if v.lower() not in ['asc', 'desc']:
            raise ValueError("El orden debe ser 'asc' o 'desc'")
        return v.lower()


class DateRangeSchema(BaseSchema):
    """Esquema para rangos de fechas."""
    
    start_date: Optional[date] = Field(None, description="Fecha de inicio del rango")
    end_date: Optional[date] = Field(None, description="Fecha de fin del rango")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Valida que la fecha de fin sea posterior a la de inicio."""
        if v is not None and 'start_date' in values and values['start_date'] is not None:
            if v < values['start_date']:
                raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")
        return v


class PaginatedResponseMetadata(BaseSchema):
    """Metadatos para respuestas paginadas."""
    
    current_page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Elementos por página")
    total_count: int = Field(..., description="Total de elementos")
    total_pages: int = Field(..., description="Total de páginas")
    has_next: bool = Field(..., description="Tiene página siguiente")
    has_prev: bool = Field(..., description="Tiene página anterior")