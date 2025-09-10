# src/planificador/schemas/base/base.py

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Esquema base con configuración para ORM."""

    model_config = ConfigDict(from_attributes=True)