# src/planificador/repositories/schedule/interfaces/crud_interface.py

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import date

from planificador.models.schedule import Schedule
from planificador.exceptions.repository import ScheduleRepositoryError


class IScheduleCrudOperations(ABC):
    """
    Interfaz para operaciones CRUD del repositorio Schedule.
    
    Define los métodos abstractos para crear, actualizar y eliminar
    registros de horarios en la base de datos.
    
    Raises:
        ScheduleRepositoryError: Para errores específicos del repositorio de horarios
    """

    @abstractmethod
    async def create_schedule(
        self,
        employee_id: int,
        schedule_date: date,
        schedule_data: Dict[str, Any]
    ) -> Schedule:
        """
        Crea un nuevo registro de horario.
        
        Args:
            employee_id: ID del empleado
            schedule_date: Fecha del horario
            schedule_data: Datos del horario a crear
            
        Returns:
            Schedule: El horario creado
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la creación
        """
        pass

    @abstractmethod
    async def update_schedule(
        self,
        schedule_id: int,
        update_data: Dict[str, Any]
    ) -> Schedule:
        """
        Actualiza un registro de horario existente.
        
        Args:
            schedule_id: ID del horario a actualizar
            update_data: Datos a actualizar
            
        Returns:
            Schedule: El horario actualizado
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la actualización
        """
        pass

    @abstractmethod
    async def delete_schedule(self, schedule_id: int) -> bool:
        """
        Elimina un registro de horario.
        
        Args:
            schedule_id: ID del horario a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la eliminación
        """
        pass