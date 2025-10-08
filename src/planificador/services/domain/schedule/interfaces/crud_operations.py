"""
Interfaz para Operaciones CRUD del Servicio de Dominio Schedule.

Define los contratos para las operaciones básicas de creación, actualización
y eliminación de horarios con validaciones de negocio.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from planificador.schemas.schedule.schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    Schedule
)


class IScheduleDomainCrudOperations(ABC):
    """
    Interfaz para operaciones CRUD del servicio de dominio Schedule.
    
    Define los métodos para crear, actualizar y eliminar horarios
    con validaciones completas de reglas de negocio.
    """

    @abstractmethod
    async def create_schedule(
        self,
        schedule_data: ScheduleCreate
    ) -> Schedule:
        """
        Crea un nuevo horario con validaciones completas de negocio y detección de conflictos.
        
        Args:
            schedule_data: Datos del horario a crear
            
        Returns:
            Schedule: Horario creado con información completa
            
        Raises:
            ValidationError: Si los datos no cumplen las reglas de negocio
            ConflictError: Si existe conflicto con horarios existentes
            RepositoryError: Si hay error en la persistencia
        """
        pass

    @abstractmethod
    async def update_schedule(
        self,
        schedule_id: int,
        schedule_data: ScheduleUpdate
    ) -> Schedule:
        """
        Actualiza un horario existente con validaciones de solapamiento temporal.
        
        Args:
            schedule_id: ID del horario a actualizar
            schedule_data: Datos de actualización del horario
            
        Returns:
            Schedule: Horario actualizado o None si no existe
            
        Raises:
            ValidationError: Si los datos no cumplen las reglas de negocio
            ConflictError: Si la actualización genera conflictos
            RepositoryError: Si hay error en la persistencia
        """
        pass

    @abstractmethod
    async def get_schedule_by_id(
        self,
        schedule_id: int
    ) -> Optional[Schedule]:
        """
        Obtiene un horario por su ID.
        
        Args:
            schedule_id: ID del horario a obtener
            
        Returns:
            Optional[Schedule]: Horario encontrado o None si no existe
            
        Raises:
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def delete_schedule(
        self,
        schedule_id: int
    ) -> bool:
        """
        Elimina un horario después de validar dependencias y impacto en la planificación.
        
        Args:
            schedule_id: ID del horario a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False si no existe
            
        Raises:
            BusinessRuleError: Si el horario no puede eliminarse por reglas de negocio
            RepositoryError: Si hay error en la persistencia
        """
        pass