# src/planificador/schemas/alert/alert.py

from typing import Optional
from pydantic import Field, field_validator, model_validator
from datetime import datetime
import pendulum

from ..base.base import BaseSchema
from ...models.alert import AlertType, AlertStatus


class AlertBase(BaseSchema):
    """Schema base para Alert."""

    user_id: int
    alert_type: AlertType
    status: AlertStatus = AlertStatus.NEW
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    related_entity_type: Optional[str] = Field(None, max_length=50)
    related_entity_id: Optional[int] = None
    is_read: bool = False
    read_at: Optional[datetime] = None

    @field_validator('read_at')
    @classmethod
    def validate_read_at(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Valida que read_at no sea futuro."""
        if v is not None:
            if v > pendulum.now():
                raise ValueError("La fecha de lectura no puede ser futura")
        return v

    @model_validator(mode='after')
    def validate_read_consistency(self) -> 'AlertBase':
        """Valida la coherencia entre is_read y read_at."""
        if self.is_read and self.read_at is None:
            raise ValueError("Si la alerta está marcada como leída, debe tener fecha de lectura")
        if not self.is_read and self.read_at is not None:
            raise ValueError("Si la alerta no está leída, no debe tener fecha de lectura")
        return self


class AlertCreate(AlertBase):
    """Schema para crear una Alert."""

    pass


class AlertUpdate(AlertBase):
    """Schema para actualizar una Alert."""

    user_id: Optional[int] = None
    alert_type: Optional[AlertType] = None
    status: Optional[AlertStatus] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    message: Optional[str] = Field(None, min_length=1)
    related_entity_type: Optional[str] = Field(None, max_length=50)
    related_entity_id: Optional[int] = None
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None


class Alert(AlertBase):
    """Schema de salida para Alert."""

    id: int
    created_at: datetime
    updated_at: datetime


class AlertSearchFilter(BaseSchema):
    """Filtros para búsqueda de alertas."""

    user_id: Optional[int] = None
    alert_type: Optional[AlertType] = None
    status: Optional[AlertStatus] = None
    is_read: Optional[bool] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None