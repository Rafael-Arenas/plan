# src/planificador/repositories/schedule/modules/crud_module.py

from typing import Dict, Any, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.schedule import Schedule
from planificador.repositories.base_repository import BaseRepository
from planificador.repositories.schedule.interfaces.crud_interface import IScheduleCrudOperations
from planificador.exceptions.repository import ScheduleRepositoryError


class ScheduleCrudModule(BaseRepository[Schedule], IScheduleCrudOperations):
    """
    Módulo para operaciones CRUD del repositorio Schedule.
    
    Implementa las operaciones de creación, actualización y eliminación
    de registros de horarios en la base de datos.
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo CRUD.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Schedule)
        self._logger = self._logger.bind(component="ScheduleCrudModule")
        self._logger.debug("ScheduleCrudModule inicializado")

    async def create_schedule(
        self,
        employee_id: int,
        schedule_date: date,
        schedule_data: Dict[str, Any]
    ) -> Schedule:
        """
        Crea un nuevo registro de horario delegando en el repositorio base.
        
        Args:
            employee_id: ID del empleado
            schedule_date: Fecha del horario
            schedule_data: Datos del horario a crear
            
        Returns:
            Schedule: El horario creado
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la creación
        """
        self._logger.debug(
            f"Creando horario para empleado {employee_id} en fecha {schedule_date}"
        )
        
        # Preparar datos del horario
        schedule_data_copy = schedule_data.copy()
        schedule_data_copy.update({
            'employee_id': employee_id,
            'date': schedule_date
        })
        
        return await self.create(schedule_data_copy)

    async def update_schedule(
        self,
        schedule_id: int,
        update_data: Dict[str, Any]
    ) -> Schedule:
        """
        Actualiza un registro de horario existente delegando en el repositorio base.
        
        Args:
            schedule_id: ID del horario a actualizar
            update_data: Datos a actualizar
            
        Returns:
            Schedule: El horario actualizado
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la actualización
        """
        self._logger.debug(f"Actualizando horario con ID {schedule_id}")
        
        updated_schedule = await self.update(schedule_id, update_data)
        if not updated_schedule:
            raise ScheduleRepositoryError(
                message=f"Horario con ID {schedule_id} no encontrado",
                operation="update_schedule",
                entity_type="Schedule",
                entity_id=schedule_id
            )
        
        return updated_schedule

    async def delete_schedule(self, schedule_id: int) -> bool:
        """
        Elimina un registro de horario delegando en el repositorio base.
        
        Args:
            schedule_id: ID del horario a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la eliminación
        """
        self._logger.debug(f"Eliminando horario con ID {schedule_id}")
        
        return await self.delete(schedule_id)

    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[Schedule]:
        """
        Obtiene un horario por un campo único específico.
        
        Args:
            field_name: Nombre del campo único
            value: Valor a buscar
            
        Returns:
            Schedule encontrado o None si no existe
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo horario por campo {field_name}={value}")
        
        return await self.get_by_field(field_name, value)