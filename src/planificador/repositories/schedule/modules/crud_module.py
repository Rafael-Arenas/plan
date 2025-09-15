# src/planificador/repositories/schedule/modules/crud_module.py

from typing import Dict, Any, Optional
from datetime import date
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from planificador.models.schedule import Schedule
from planificador.repositories.schedule.interfaces.crud_interface import IScheduleCrudOperations
from planificador.exceptions.repository_exceptions import ScheduleRepositoryError
from planificador.exceptions.database_exceptions import convert_sqlalchemy_error


class ScheduleCrudModule(IScheduleCrudOperations):
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
        self.session = session
        self._logger = logger.bind(module="schedule_crud")

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
        try:
            self._logger.info(
                f"Creando horario para empleado {employee_id} en fecha {schedule_date}"
            )
            
            # Preparar datos del horario
            schedule_data_copy = schedule_data.copy()
            schedule_data_copy.update({
                'employee_id': employee_id,
                'date': schedule_date
            })
            
            # Crear nueva instancia
            new_schedule = Schedule(**schedule_data_copy)
            
            # Agregar a la sesión
            self.session.add(new_schedule)
            await self.session.commit()
            await self.session.refresh(new_schedule)
            
            self._logger.info(
                f"Horario creado exitosamente con ID {new_schedule.id}"
            )
            
            return new_schedule
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al crear horario: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_schedule",
                entity_type="Schedule",
                entity_id=None
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al crear horario: {e}")
            await self.session.rollback()
            raise ScheduleRepositoryError(
                message=f"Error inesperado al crear horario: {e}",
                operation="create_schedule",
                entity_type="Schedule",
                entity_id=None,
                original_error=e
            )

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
        try:
            self._logger.info(f"Actualizando horario con ID {schedule_id}")
            
            # Buscar el horario existente
            schedule = await self.session.get(Schedule, schedule_id)
            if not schedule:
                raise ScheduleRepositoryError(
                    message=f"Horario con ID {schedule_id} no encontrado",
                    operation="update_schedule",
                    entity_type="Schedule",
                    entity_id=schedule_id
                )
            
            # Actualizar campos
            for field, value in update_data.items():
                if hasattr(schedule, field):
                    setattr(schedule, field, value)
            
            await self.session.commit()
            await self.session.refresh(schedule)
            
            self._logger.info(f"Horario {schedule_id} actualizado exitosamente")
            
            return schedule
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al actualizar horario: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="update_schedule",
                entity_type="Schedule",
                entity_id=schedule_id
            )
        except ScheduleRepositoryError:
            # Re-lanzar errores específicos del repositorio
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al actualizar horario: {e}")
            await self.session.rollback()
            raise ScheduleRepositoryError(
                message=f"Error inesperado al actualizar horario: {e}",
                operation="update_schedule",
                entity_type="Schedule",
                entity_id=schedule_id,
                original_error=e
            )

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
        try:
            self._logger.info(f"Eliminando horario con ID {schedule_id}")
            
            # Buscar el horario existente
            schedule = await self.session.get(Schedule, schedule_id)
            if not schedule:
                raise ScheduleRepositoryError(
                    message=f"Horario con ID {schedule_id} no encontrado",
                    operation="delete_schedule",
                    entity_type="Schedule",
                    entity_id=schedule_id
                )
            
            # Eliminar el horario
            await self.session.delete(schedule)
            await self.session.commit()
            
            self._logger.info(f"Horario {schedule_id} eliminado exitosamente")
            
            return True
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al eliminar horario: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="delete_schedule",
                entity_type="Schedule",
                entity_id=schedule_id
            )
        except ScheduleRepositoryError:
            # Re-lanzar errores específicos del repositorio
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al eliminar horario: {e}")
            await self.session.rollback()
            raise ScheduleRepositoryError(
                message=f"Error inesperado al eliminar horario: {e}",
                operation="delete_schedule",
                entity_type="Schedule",
                entity_id=schedule_id,
                original_error=e
            )