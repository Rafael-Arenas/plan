# src/planificador/models/client.py

from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel, Base

class Client(BaseModel):
    """Modelo para gestión de clientes."""
    __tablename__ = 'clients'

    name = Column(String(200), nullable=False, unique=True)
    code = Column(String(10), nullable=True, unique=True)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)

    # Relaciones
    projects = relationship(
        "Project", 
        back_populates="client", 
        cascade="all, delete-orphan",
        lazy="selectin"  # Carga ansiosa para contextos asíncronos
    )

    # Métodos de utilidad
    @property
    def display_name(self) -> str:
        """Nombre para mostrar con código si existe."""
        if self.code:
            return f"{self.name} ({self.code})"
        return self.name
    
    @property
    def has_contact_info(self) -> bool:
        """Verifica si tiene información de contacto."""
        return bool(self.contact_person or self.email or self.phone)
    
    @property
    def contact_summary(self) -> str:
        """Resumen de información de contacto."""
        parts = []
        if self.contact_person:
            parts.append(f"Contacto: {self.contact_person}")
        if self.email:
            parts.append(f"Email: {self.email}")
        if self.phone:
            parts.append(f"Teléfono: {self.phone}")
        return " | ".join(parts) if parts else "Sin información de contacto"
    
    @property
    def status_display(self) -> str:
        """Estado para mostrar en español."""
        return "Activo" if self.is_active else "Inactivo"
    
    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name='{self.name}')>"