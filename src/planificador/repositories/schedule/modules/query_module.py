# src/planificador/repositories/schedule/modules/query_module.py

from typing import List, Optional, Dict, Any
from datetime import date

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.schedule import Schedule
from planificador.repositories.schedule.interfaces.query_interface import IScheduleQueryOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository_exceptions import ScheduleRepositoryError
from planificador.exceptions.database_exceptions import convert_sqlalchemy_error


class ScheduleQueryModule(BaseRepository[Schedule], IScheduleQueryOperations):
    """
    Módulo para operaciones de consulta del repositorio Schedule.
    
    Implementa las operaciones de consulta y recuperación
    de registros de horarios desde la base de datos.
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de consultas.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Schedule)
        self._logger = self._logger.bind(module="schedule_query")

    async def get_schedule_by_id(self, schedule_id: int) -> Optional[Schedule]:
        """
        Obtiene un horario por su ID usando BaseRepository.
        
        Args:
            schedule_id: ID del horario a buscar
            
        Returns:
            Optional[Schedule]: El horario encontrado o None
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo horario con ID: {schedule_id}")
        return await self.get_by_id(schedule_id)

    async def get_schedules_by_employee(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """
        Obtiene horarios de un empleado en un rango de fechas.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del rango (opcional)
            end_date: Fecha de fin del rango (opcional)
            
        Returns:
            List[Schedule]: Lista de horarios encontrados
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(
                f"Buscando horarios del empleado {employee_id} "
                f"desde {start_date} hasta {end_date}"
            )
            
            stmt = (
                select(Schedule)
                .options(
                    selectinload(Schedule.project),
                    selectinload(Schedule.team),
                    selectinload(Schedule.status_code)
                )
                .where(Schedule.employee_id == employee_id)
                .order_by(Schedule.date.desc(), Schedule.start_time.asc())
            )
            
            # Aplicar filtros de fecha si se proporcionan
            if start_date:
                stmt = stmt.where(Schedule.date >= start_date)
            if end_date:
                stmt = stmt.where(Schedule.date <= end_date)
            
            result = await self.session.execute(stmt)
            schedules = result.scalars().all()
            
            self._logger.debug(
                f"Encontrados {len(schedules)} horarios para empleado {employee_id}"
            )
            
            return list(schedules)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al buscar horarios: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_schedules_by_employee",
                entity_type="Schedule",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar horarios: {e}")
            raise ScheduleRepositoryError(
                message=f"Error inesperado al buscar horarios: {e}",
                operation="get_schedules_by_employee",
                entity_type="Schedule",
                entity_id=employee_id,
                original_error=e
            )

    async def get_schedules_by_date(
        self,
        target_date: date,
        employee_id: Optional[int] = None
    ) -> List[Schedule]:
        """
        Obtiene horarios para una fecha específica.
        
        Args:
            target_date: Fecha objetivo
            employee_id: ID del empleado (opcional, para filtrar)
            
        Returns:
            List[Schedule]: Lista de horarios encontrados
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(
                f"Buscando horarios para fecha {target_date} "
                f"{'del empleado ' + str(employee_id) if employee_id else ''}"
            )
            
            stmt = (
                select(Schedule)
                .options(
                    selectinload(Schedule.employee),
                    selectinload(Schedule.project),
                    selectinload(Schedule.team),
                    selectinload(Schedule.status_code)
                )
                .where(Schedule.date == target_date)
                .order_by(Schedule.start_time.asc())
            )
            
            # Filtrar por empleado si se especifica
            if employee_id:
                stmt = stmt.where(Schedule.employee_id == employee_id)
            
            result = await self.session.execute(stmt)
            schedules = result.scalars().all()
            
            self._logger.debug(
                f"Encontrados {len(schedules)} horarios para fecha {target_date}"
            )
            
            return list(schedules)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al buscar horarios: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_schedules_by_date",
                entity_type="Schedule",
                entity_id=None
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar horarios: {e}")
            raise ScheduleRepositoryError(
                message=f"Error inesperado al buscar horarios: {e}",
                operation="get_schedules_by_date",
                entity_type="Schedule",
                entity_id=None,
                original_error=e
            )

    async def get_schedules_by_project(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """
        Obtiene horarios asociados a un proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del rango (opcional)
            end_date: Fecha de fin del rango (opcional)
            
        Returns:
            List[Schedule]: Lista de horarios encontrados
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(
                f"Buscando horarios del proyecto {project_id} "
                f"desde {start_date} hasta {end_date}"
            )
            
            stmt = (
                select(Schedule)
                .options(
                    selectinload(Schedule.employee),
                    selectinload(Schedule.team),
                    selectinload(Schedule.status_code)
                )
                .where(Schedule.project_id == project_id)
                .order_by(Schedule.date.desc(), Schedule.start_time.asc())
            )
            
            # Aplicar filtros de fecha si se proporcionan
            if start_date:
                stmt = stmt.where(Schedule.date >= start_date)
            if end_date:
                stmt = stmt.where(Schedule.date <= end_date)
            
            result = await self.session.execute(stmt)
            schedules = result.scalars().all()
            
            self._logger.debug(
                f"Encontrados {len(schedules)} horarios para proyecto {project_id}"
            )
            
            return list(schedules)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al buscar horarios: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_schedules_by_project",
                entity_type="Schedule",
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar horarios: {e}")
            raise ScheduleRepositoryError(
                message=f"Error inesperado al buscar horarios: {e}",
                operation="get_schedules_by_project",
                entity_type="Schedule",
                entity_id=project_id,
                original_error=e
            )

    async def get_schedules_by_team(
        self,
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """
        Obtiene horarios asociados a un equipo.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del rango (opcional)
            end_date: Fecha de fin del rango (opcional)
            
        Returns:
            List[Schedule]: Lista de horarios encontrados
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(
                f"Buscando horarios del equipo {team_id} "
                f"desde {start_date} hasta {end_date}"
            )
            
            stmt = (
                select(Schedule)
                .options(
                    selectinload(Schedule.employee),
                    selectinload(Schedule.project),
                    selectinload(Schedule.status_code)
                )
                .where(Schedule.team_id == team_id)
                .order_by(Schedule.date.desc(), Schedule.start_time.asc())
            )
            
            # Aplicar filtros de fecha si se proporcionan
            if start_date:
                stmt = stmt.where(Schedule.date >= start_date)
            if end_date:
                stmt = stmt.where(Schedule.date <= end_date)
            
            result = await self.session.execute(stmt)
            schedules = result.scalars().all()
            
            self._logger.debug(
                f"Encontrados {len(schedules)} horarios para equipo {team_id}"
            )
            
            return list(schedules)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al buscar horarios: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_schedules_by_team",
                entity_type="Schedule",
                entity_id=team_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar horarios: {e}")
            raise ScheduleRepositoryError(
                message=f"Error inesperado al buscar horarios: {e}",
                operation="get_schedules_by_team",
                entity_type="Schedule",
                entity_id=team_id,
                original_error=e
            )

    async def get_confirmed_schedules(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> List[Schedule]:
        """
        Obtiene horarios confirmados en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            employee_id: ID del empleado (opcional, para filtrar)
            
        Returns:
            List[Schedule]: Lista de horarios confirmados
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(
                f"Buscando horarios confirmados desde {start_date} hasta {end_date} "
                f"{'del empleado ' + str(employee_id) if employee_id else ''}"
            )
            
            stmt = (
                select(Schedule)
                .options(
                    selectinload(Schedule.employee),
                    selectinload(Schedule.project),
                    selectinload(Schedule.team),
                    selectinload(Schedule.status_code)
                )
                .where(
                    and_(
                        Schedule.date >= start_date,
                        Schedule.date <= end_date,
                        Schedule.is_confirmed == True
                    )
                )
                .order_by(Schedule.date.asc(), Schedule.start_time.asc())
            )
            
            # Filtrar por empleado si se especifica
            if employee_id:
                stmt = stmt.where(Schedule.employee_id == employee_id)
            
            result = await self.session.execute(stmt)
            schedules = result.scalars().all()
            
            self._logger.debug(
                f"Encontrados {len(schedules)} horarios confirmados"
            )
            
            return list(schedules)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al buscar horarios: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_confirmed_schedules",
                entity_type="Schedule",
                entity_id=None
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar horarios: {e}")
            raise ScheduleRepositoryError(
                message=f"Error inesperado al buscar horarios: {e}",
                operation="get_confirmed_schedules",
                entity_type="Schedule",
                entity_id=None,
                original_error=e
            )

    async def search_schedules(
        self,
        filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Schedule]:
        """
        Busca horarios con filtros personalizados usando BaseRepository.
        
        Args:
            filters: Diccionario de filtros a aplicar
            limit: Límite de resultados (opcional)
            offset: Desplazamiento para paginación (opcional)
            
        Returns:
            List[Schedule]: Lista de horarios encontrados
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la búsqueda
        """
        self._logger.debug(f"Buscando horarios con filtros: {filters}")
        return await self.find_by_criteria(filters, limit=limit, offset=offset)

    async def count_schedules(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta el número de horarios que coinciden con los filtros usando BaseRepository.
        
        Args:
            filters: Diccionario de filtros a aplicar (opcional)
            
        Returns:
            int: Número de horarios encontrados
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante el conteo
        """
        self._logger.debug(f"Contando horarios con filtros: {filters}")
        return await self.count(filters or {})