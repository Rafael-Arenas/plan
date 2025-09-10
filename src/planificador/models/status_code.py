# src/planificador/models/status_code.py

from sqlalchemy import Column, String, Text, Boolean, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel, Base

class StatusCode(BaseModel):
    """Modelo para códigos de estado configurables."""
    __tablename__ = 'status_codes'

    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)
    icon = Column(String(50), nullable=True)
    is_billable = Column(Boolean, default=True, nullable=False)
    is_productive = Column(Boolean, default=True, nullable=False)
    requires_approval = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)

    # Relaciones
    schedules = relationship("Schedule", back_populates="status_code")

    # Métodos de utilidad
    @property
    def display_name(self) -> str:
        """Nombre para mostrar con código."""
        return f"{self.code} - {self.name}"
    
    @property
    def is_billable_productive(self) -> bool:
        """Verifica si es facturable y productivo."""
        return self.is_billable and self.is_productive
    
    @property
    def status_category(self) -> str:
        """Categoría del estado basada en sus propiedades."""
        if self.is_billable and self.is_productive:
            return "Productivo Facturable"
        elif self.is_productive and not self.is_billable:
            return "Productivo No Facturable"
        elif self.is_billable and not self.is_productive:
            return "Facturable No Productivo"
        else:
            return "No Productivo No Facturable"
    
    @property
    def requires_special_handling(self) -> bool:
        """Verifica si requiere manejo especial."""
        return self.requires_approval or not self.is_active
    
    @property
    def status_display(self) -> str:
        """Estado para mostrar en español."""
        return "Activo" if self.is_active else "Inactivo"
    
    def __repr__(self) -> str:
        return f"<StatusCode(id={self.id}, code='{self.code}', name='{self.name}')>"