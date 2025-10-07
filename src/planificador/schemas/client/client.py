# src/planificador/schemas/client/client.py

from typing import List, Optional, TYPE_CHECKING, Literal
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


class ClientStatsResponse(BaseSchema):
    """Schema para respuesta de estadísticas de cliente."""
    
    total_clients: int = Field(..., ge=0)
    active_clients: int = Field(..., ge=0)
    inactive_clients: int = Field(..., ge=0)


class ClientFilter(BaseSchema):
    """Schema para filtros de búsqueda de clientes."""
    
    name: Optional[str] = Field(None, description="Filtrar por nombre")
    code: Optional[str] = Field(None, description="Filtrar por código")
    email: Optional[str] = Field(None, description="Filtrar por email")
    is_active: Optional[bool] = Field(None, description="Filtrar por estado activo")
    contact_person: Optional[str] = Field(None, description="Filtrar por persona de contacto")


class ClientSort(BaseSchema):
    """Schema para ordenamiento de clientes."""
    
    field: Literal["name", "code", "email", "created_at", "updated_at"] = Field(
        default="name", 
        description="Campo por el cual ordenar"
    )
    direction: Literal["asc", "desc"] = Field(
        default="asc", 
        description="Dirección del ordenamiento"
    )