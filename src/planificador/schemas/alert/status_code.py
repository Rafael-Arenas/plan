# src/planificador/schemas/common/status_code.py

from typing import Optional
from pydantic import Field
from datetime import datetime

from ..base.base import BaseSchema


class StatusCodeBase(BaseSchema):
    """Schema base para StatusCode."""

    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    is_billable: bool = True
    is_productive: bool = True
    requires_approval: bool = False
    is_active: bool = True
    sort_order: int = Field(default=0, ge=0)


class StatusCodeCreate(StatusCodeBase):
    """Schema para crear un StatusCode."""

    pass


class StatusCodeUpdate(BaseSchema):
    """Schema para actualizar un StatusCode."""

    code: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    is_billable: Optional[bool] = None
    is_productive: Optional[bool] = None
    requires_approval: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)


class StatusCode(StatusCodeBase):
    """Schema de salida para StatusCode."""

    id: int
    created_at: datetime
    updated_at: datetime