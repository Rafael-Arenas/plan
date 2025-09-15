# src/planificador/database/repositories/schedule_repository.py

from typing import List, Optional, Dict, Any
from datetime import date, time, datetime
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import pendulum
from pendulum import DateTime, Date

from ..base_repository import BaseRepository
from ....models.schedule import Schedule
from ....exceptions.repository import (
    convert_sqlalchemy_error,
    ScheduleRepositoryError,
    ScheduleQueryError,
    ScheduleStatisticsError,
    ScheduleValidationRepositoryError,
    ScheduleRelationshipError,
    ScheduleBulkOperationError,
    ScheduleDateRangeError,
    ScheduleOverlapError,
    create_schedule_query_error,
    create_schedule_statistics_error,
    create_schedule_validation_repository_error,
    create_schedule_relationship_error,
    create_schedule_bulk_operation_error,
    create_schedule_date_range_error,
    create_schedule_overlap_error,
)
from ....utils.date_utils import get_current_time, format_datetime
from .schedule_query_builder import ScheduleQueryBuilder
from .schedule_validator import ScheduleValidator
from .schedule_statistics import ScheduleStatistics
from .schedule_relationship_manager import ScheduleRelationshipManager


class ScheduleRepository(BaseRepository[Schedule]):
    """
    Repositorio para gestión de horarios (Schedule).
    
    Proporciona operaciones CRUD y consultas especializadas
    para la entidad Schedule, incluyendo validaciones de negocio
    y manejo de relaciones con empleados, proyectos y equipos.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(Schedule, session)
        self._logger = logger.bind(component="ScheduleRepository")
        
        # Inicializar componentes especializados
        self.query_builder = ScheduleQueryBuilder(session)
        self.validator = ScheduleValidator(session)
        self.statistics = ScheduleStatistics(session)
        self.relationship_manager = ScheduleRelationshipManager(session)
    
    # ==========================================
    # OPERACIONES CRUD EXTENDIDAS
    # ==========================================
    
    # ===== OPERACIONES CRUD BÁSICAS =====
    
    async def create_schedule(
        self,
        schedule_data: Optional[Dict[str, Any]] = None,
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None,
        date: Optional[date] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        team_id: Optional[int] = None,
        status_code_id: Optional[int] = None,
        is_confirmed: bool = False,
        notes: Optional[str] = None
    ) -> Schedule:
        """Crea un nuevo horario."""
        try:
            # Validar datos antes de crear
            await self.validator.validate_schedule_data(
                employee_id=employee_id,
                project_id=project_id,
                date=date,
                start_time=start_time,
                end_time=end_time,
                team_id=team_id,
                status_code_id=status_code_id
            )
            
            # Si se proporciona schedule_data, usarlo; si no, construir desde parámetros
            if schedule_data:
                data = schedule_data.copy()
            else:
                data = {
                    'employee_id': employee_id,
                    'project_id': project_id,
                    'date': date,
                    'start_time': start_time,
                    'end_time': end_time,
                    'team_id': team_id,
                    'status_code_id': status_code_id,
                    'is_confirmed': is_confirmed,
                    'notes': notes
                }
            
            # Crear el horario usando el método base
            schedule = await self.create(data)
            
            self._logger.info(f"Horario creado exitosamente: ID {schedule.id}")
            return schedule
            
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
                original_error=e,
                context={
                    "employee_id": employee_id,
                    "project_id": project_id,
                    "date": str(date) if date else None,
                    "start_time": str(start_time) if start_time else None,
                    "end_time": str(end_time) if end_time else None
                }
            )
    
    async def update_schedule(
        self,
        schedule_id: int,
        **update_data
    ) -> Schedule:
        """Actualiza un horario existente."""
        try:
            # Obtener el horario actual para validación
            current_schedule = await self.get_by_id(schedule_id)
            if not current_schedule:
                raise ScheduleRepositoryError(
                    message=f"Horario con ID {schedule_id} no encontrado",
                    operation="update_schedule",
                    entity_type="Schedule",
                    entity_id=schedule_id
                )
            
            # Validar los nuevos datos si incluyen campos críticos
            if any(key in update_data for key in ['employee_id', 'project_id', 'date', 'start_time', 'end_time']):
                # Combinar datos actuales con actualizaciones para validación completa
                validation_data = {
                    'employee_id': update_data.get('employee_id', current_schedule.employee_id),
                    'project_id': update_data.get('project_id', current_schedule.project_id),
                    'date': update_data.get('date', current_schedule.date),
                    'start_time': update_data.get('start_time', current_schedule.start_time),
                    'end_time': update_data.get('end_time', current_schedule.end_time),
                    'team_id': update_data.get('team_id', current_schedule.team_id),
                    'status_code_id': update_data.get('status_code_id', current_schedule.status_code_id)
                }
                
                await self.validator.validate_schedule_data(**validation_data)
            
            # Actualizar usando el método base
            updated_schedule = await self.update(schedule_id, update_data)
            
            self._logger.info(f"Horario actualizado exitosamente: ID {schedule_id}")
            return updated_schedule
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al actualizar horario {schedule_id}: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="update_schedule",
                entity_type="Schedule",
                entity_id=schedule_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al actualizar horario {schedule_id}: {e}")
            await self.session.rollback()
            raise ScheduleRepositoryError(
                message=f"Error inesperado al actualizar horario: {e}",
                operation="update_schedule",
                entity_type="Schedule",
                entity_id=schedule_id,
                original_error=e,
                context={
                    "update_data": update_data
                }
            )
    
    async def get_by_employee_and_date(
        self,
        employee_id: int,
        target_date: date
    ) -> List[Schedule]:
        """
        Obtiene horarios de un empleado para una fecha específica.
        
        Args:
            employee_id: ID del empleado
            target_date: Fecha objetivo
            
        Returns:
            Lista de horarios del empleado en la fecha especificada
        """
        try:
            return await self.query_builder.get_by_employee_and_date(
                employee_id, target_date
            )
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy a excepciones de repositorio
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_employee_and_date",
                entity_type="Schedule",
                entity_id=str(employee_id)  # Usar employee_id como contexto
            )
        except Exception as e:
            # Manejar errores inesperados como errores de consulta
            self._logger.error(
                f"Error inesperado en get_by_employee_and_date(emp_id={employee_id}, "
                f"date={target_date}): {e}"
            )
            raise create_schedule_query_error(
                query_type="get_by_employee_and_date",
                parameters={
                    "employee_id": employee_id,
                    "target_date": target_date,
                },
                reason=f"Error inesperado: {str(e)}",
            )

    async def find_by_employee(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """
        Busca horarios por empleado con rango de fechas opcional.
        """
        return await self.query_builder.find_by_employee(
            employee_id, start_date, end_date
        )

    async def find_by_project(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """
        Busca horarios por proyecto con rango de fechas opcional.
        """
        return await self.query_builder.find_by_project(
            project_id, start_date, end_date
        )

    async def find_by_team(
        self,
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """
        Busca horarios por equipo con rango de fechas opcional.
        """
        return await self.query_builder.find_by_team(
            team_id, start_date, end_date
        )

    async def find_by_date_range(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None,
        team_id: Optional[int] = None
    ) -> List[Schedule]:
        """
        Busca horarios en un rango de fechas con filtros opcionales.
        """
        return await self.query_builder.find_by_date_range(
            start_date, end_date, employee_id, project_id, team_id
        )

    async def find_confirmed_schedules(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """
        Busca horarios confirmados en un rango de fechas opcional.
        """
        return await self.query_builder.find_by_confirmation_status(
            is_confirmed=True, start_date=start_date, end_date=end_date
        )

    async def find_unconfirmed_schedules(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """
        Busca horarios no confirmados en un rango de fechas opcional.
        """
        return await self.query_builder.find_by_confirmation_status(
            is_confirmed=False, start_date=start_date, end_date=end_date
        )

    async def search_schedules(
        self,
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None,
        team_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        is_confirmed: Optional[bool] = None,
        status_code_id: Optional[int] = None
    ) -> List[Schedule]:
        """
        Búsqueda general de horarios con múltiples filtros opcionales.
        """
        return await self.query_builder.search(
            employee_id=employee_id,
            project_id=project_id,
            team_id=team_id,
            start_date=start_date,
            end_date=end_date,
            is_confirmed=is_confirmed,
            status_code_id=status_code_id
        )
    
    # ===== CONSULTAS DE DELEGACIÓN - ESTADÍSTICAS =====
    
    async def get_schedule_counts(self) -> Dict[str, int]:
        """
        Obtiene conteos generales de horarios.
        """
        return await self.statistics.get_general_counts()
    
    async def get_employee_schedule_summary(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene resumen de horarios de un empleado.
        """
        return await self.statistics.get_employee_summary(
            employee_id, start_date, end_date
        )
    
    async def get_project_schedule_summary(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene resumen de horarios de un proyecto.
        """
        return await self.statistics.get_project_summary(
            project_id, start_date, end_date
        )
    
    # ===== CONSULTAS DE DELEGACIÓN - RELACIONES =====
    
    async def get_employee_schedules_with_details(
        self,
        employee_id: int,
        include_projects: bool = True,
        include_teams: bool = True,
        include_status_codes: bool = True
    ) -> List[Schedule]:
        """
        Obtiene horarios de un empleado con detalles de relaciones.
        """
        return await self.relationship_manager.get_employee_schedules_with_details(
            employee_id, include_projects, include_teams, include_status_codes
        )
    
    async def assign_schedule_to_project(
        self,
        schedule_id: int,
        project_id: int
    ) -> Schedule:
        """
        Asigna un horario a un proyecto.
        """
        return await self.relationship_manager.assign_schedule_to_project(
            schedule_id, project_id
        )
    
    async def assign_schedule_to_team(
        self,
        schedule_id: int,
        team_id: int
    ) -> Schedule:
        """
        Asigna un horario a un equipo.
        """
        return await self.relationship_manager.assign_schedule_to_team(
            schedule_id, team_id
        )
    
    # ===== CONSULTAS DE DELEGACIÓN - VALIDACIONES =====
    
    async def validate_schedule_data(
        self,
        employee_id: int,
        project_id: Optional[int],
        date: date,
        start_time: time,
        end_time: time,
        team_id: Optional[int] = None,
        status_code_id: Optional[int] = None
    ) -> bool:
        """
        Valida datos de horario.
        """
        await self.validator.validate_schedule_data(
            employee_id=employee_id,
            project_id=project_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            team_id=team_id,
            status_code_id=status_code_id
        )
        return True

    async def check_time_conflicts(
        self,
        employee_id: int,
        date: date,
        start_time: time,
        end_time: time,
        exclude_schedule_id: Optional[int] = None
    ) -> bool:
        """
        Verifica conflictos de tiempo para un empleado.
        """
        await self.validator.validate_time_conflicts(
            employee_id=employee_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            exclude_schedule_id=exclude_schedule_id
        )
        return True
        
    # ===== MÉTODOS DE COMPATIBILIDAD =====
    
    async def get_by_employee(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """Obtiene horarios por empleado (método de compatibilidad)."""
        return await self.find_by_employee(employee_id, start_date, end_date)

    async def find_by_employee_and_date_range(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> List[Schedule]:
        """Busca horarios por empleado en rango de fechas (método de compatibilidad)."""
        return await self.find_by_employee(employee_id, start_date, end_date)

    async def get_by_project(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """Obtiene horarios por proyecto (método de compatibilidad)."""
        return await self.find_by_project(project_id, start_date, end_date)

    async def get_overlapping_schedules(
        self,
        employee_id: int,
        date: date,
        start_time: time,
        end_time: time
    ) -> List[Schedule]:
        """Obtiene horarios que se solapan (método de compatibilidad)."""
        return await self.validator.get_overlapping_schedules(
            employee_id, date, start_time, end_time
        )

    async def get_daily_total_hours(self, employee_id: int, target_date: date) -> float:
        """Obtiene el total de horas trabajadas por un empleado en un día."""
        schedules = await self.get_by_employee(
            employee_id, target_date, target_date
        )
        
        if not schedules:
            return 0.0
        
        total_hours = 0.0
        for schedule in schedules:
            # Usar el método hours_worked del modelo Schedule
            total_hours += schedule.hours_worked
        
        return total_hours
    
    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[Schedule]:
        """Obtiene horarios en un rango de fechas."""
        try:
            return await self.query_builder.find_by_date_range(start_date, end_date)
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy a excepciones de repositorio
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_by_date_range",
                entity_type="Schedule",
                entity_id=f"{start_date}_{end_date}"  # Usar rango como contexto
            )
        except Exception as e:
            # Manejar errores inesperados como errores de consulta
            self._logger.error(
                f"Error inesperado en find_by_date_range({start_date}, {end_date}): {e}"
            )
            raise create_schedule_query_error(
                query_type="find_by_date_range",
                parameters={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                reason=f"Error inesperado: {str(e)}",
            )
    
    async def get_weekly_total_hours(self, employee_id: int, week_start: date) -> float:
        """Obtiene el total de horas trabajadas por un empleado en una semana."""
        from datetime import timedelta
        week_end = week_start + timedelta(days=6)
        summary = await self.statistics.get_employee_hours_worked(
            employee_id, week_start, week_end
        )
        return summary.get('total_hours', 0.0)
    
    async def get_project_allocation(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> List[Schedule]:
        """Obtiene los horarios asignados a un proyecto en un rango de fechas."""
        return await self.get_by_project(
            project_id, start_date, end_date
        )
    
    async def get_employee_workload(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> List[Schedule]:
        """Obtiene la carga de trabajo de un empleado en un rango de fechas."""
        return await self.get_by_employee(
            employee_id, start_date, end_date
        )
    
