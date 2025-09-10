# src/planificador/models/base.py

from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession
import pendulum

from ..database.database import Base

class BaseModel(Base):
    """Modelo base con campos de auditoría y métodos comunes."""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    async def update_from_dict(self, data: Dict[str, Any], session: AsyncSession) -> None:
        """Actualiza el modelo desde un diccionario de forma asíncrona."""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        await session.flush()
    
    # Métodos de utilidad adicionales
    @property
    def age_in_days(self) -> int:
        """Días transcurridos desde la creación del registro."""
        if not self.created_at:
            return 0
        now = pendulum.now()
        created = pendulum.instance(self.created_at)
        return (now - created).days
    
    @property
    def last_modified_days(self) -> int:
        """Días transcurridos desde la última modificación."""
        if not self.updated_at:
            return 0
        now = pendulum.now()
        updated = pendulum.instance(self.updated_at)
        return (now - updated).days
    
    @property
    def is_recently_created(self) -> bool:
        """Verifica si el registro fue creado en los últimos 7 días."""
        return self.age_in_days <= 7
    
    @property
    def is_recently_modified(self) -> bool:
        """Verifica si el registro fue modificado en los últimos 7 días."""
        return self.last_modified_days <= 7
    
    @property
    def was_modified(self) -> bool:
        """Verifica si el registro ha sido modificado después de su creación."""
        if not self.created_at or not self.updated_at:
            return False
        # Tolerancia de 1 segundo para diferencias mínimas
        created = pendulum.instance(self.created_at)
        updated = pendulum.instance(self.updated_at)
        return (updated - created).total_seconds() > 1
    
    @property
    def created_at_formatted(self) -> str:
        """Fecha de creación formateada para mostrar."""
        if not self.created_at:
            return "No disponible"
        created = pendulum.instance(self.created_at)
        return created.format('DD/MM/YYYY HH:mm')
    
    @property
    def updated_at_formatted(self) -> str:
        """Fecha de actualización formateada para mostrar."""
        if not self.updated_at:
            return "No disponible"
        updated = pendulum.instance(self.updated_at)
        return updated.format('DD/MM/YYYY HH:mm')
    
    @property
    def audit_summary(self) -> str:
        """Resumen de auditoría del registro."""
        status = "Modificado" if self.was_modified else "Sin modificar"
        return f"Creado: {self.created_at_formatted} | Actualizado: {self.updated_at_formatted} | Estado: {status}"
    
    def get_field_value(self, field_name: str, default: Any = None) -> Any:
        """Obtiene el valor de un campo de forma segura."""
        return getattr(self, field_name, default)
    
    def has_field(self, field_name: str) -> bool:
        """Verifica si el modelo tiene un campo específico."""
        return hasattr(self, field_name)
    
    def get_primary_key(self) -> Optional[Any]:
        """Obtiene el valor de la clave primaria."""
        return getattr(self, 'id', None)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"