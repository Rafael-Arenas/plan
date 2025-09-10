# src/planificador/models/team.py

from sqlalchemy import Column, String, Text, Boolean, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel, Base

class Team(BaseModel):
    """Modelo para gestión de equipos."""
    __tablename__ = 'teams'

    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), unique=True)
    description = Column(Text, nullable=True)
    color_hex = Column(String(7), default='#3498db')
    max_members = Column(Integer, default=10)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)

    # Relaciones
    memberships = relationship("TeamMembership", back_populates="team", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="team")

    # Métodos de utilidad
    @property
    def display_name(self) -> str:
        """Nombre para mostrar con código si existe."""
        if self.code:
            return f"{self.name} ({self.code})"
        return self.name
    
    @property
    def current_members_count(self) -> int:
        """Número actual de miembros activos."""
        return len([m for m in self.memberships if m.is_active])
    
    @property
    def is_at_capacity(self) -> bool:
        """Verifica si el equipo está a capacidad máxima."""
        return self.current_members_count >= self.max_members
    
    @property
    def available_spots(self) -> int:
        """Espacios disponibles en el equipo."""
        return max(0, self.max_members - self.current_members_count)
    
    @property
    def capacity_percentage(self) -> float:
        """Porcentaje de capacidad utilizada."""
        if self.max_members == 0:
            return 0.0
        return (self.current_members_count / self.max_members) * 100
    
    @property
    def status_display(self) -> str:
        """Estado para mostrar en español."""
        return "Activo" if self.is_active else "Inactivo"
    
    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.name}', code='{self.code}')>"