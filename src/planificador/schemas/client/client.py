# src/planificador/schemas/client/client.py

from typing import List, Optional, TYPE_CHECKING
from pydantic import Field, EmailStr
from datetime import datetime

from ..base.base import BaseSchema
if TYPE_CHECKING:
    from ..project.project import Project


class ClientBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    is_active: bool = True
    notes: Optional[str] = Field(None, max_length=500)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseSchema):
    """Schema para actualizar un Cliente."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)


class Client(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ClientWithProjects(Client):
    projects: List["Project"] = []