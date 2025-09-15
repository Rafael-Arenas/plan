# src/planificador/repositories/schedule/modules/validation_module.py

from typing import Dict, Any, Optional
from datetime import date, time
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from planificador.models.schedule import Schedule
from planificador.models.employee import Employee
from planificador.models.project import Project
from planificador.models.team import Team
from planificador.repositories.base_repository import BaseRepository
from planificador.repositories.schedule.interfaces.validation_interface import IScheduleValidationOperations
from planificador.exceptions.repository_exceptions import ScheduleRepositoryError
from planificador.exceptions.database_exceptions import convert_sqlalchemy_error
from planificador.exceptions.validation_exceptions import ValidationError


class ScheduleValidationModule(BaseRepository[Schedule], IScheduleValidationOperations):
    """
    Módulo para operaciones de validación del repositorio Schedule.
    
    Implementa las validaciones de datos y reglas de negocio
    para los registros de horarios.
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de validación.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Schedule)
        self._logger = logger.bind(module="schedule_validation")
        
        # Repositorios auxiliares para validaciones
        self._employee_repo = BaseRepository(session, Employee)
        self._project_repo = BaseRepository(session, Project)
        self._team_repo = BaseRepository(session, Team)

    async def validate_schedule_data(self, schedule_data: Dict[str, Any]) -> bool:
        """
        Valida los datos de un horario.
        
        Args:
            schedule_data: Diccionario con los datos del horario
            
        Returns:
            bool: True si los datos son válidos
            
        Raises:
            ValidationError: Si los datos no son válidos
            ScheduleRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug("Validando datos de horario")
            
            # Validar campos requeridos
            required_fields = [
                'employee_id', 'project_id', 'date', 
                'start_time', 'end_time'
            ]
            
            for field in required_fields:
                if field not in schedule_data or schedule_data[field] is None:
                    raise ValidationError(
                        message=f"Campo requerido faltante: {field}",
                        field=field,
                        value=schedule_data.get(field)
                    )
            
            # Validar tipos de datos
            if not isinstance(schedule_data['employee_id'], int):
                raise ValidationError(
                    message="employee_id debe ser un entero",
                    field="employee_id",
                    value=schedule_data['employee_id']
                )
            
            if not isinstance(schedule_data['project_id'], int):
                raise ValidationError(
                    message="project_id debe ser un entero",
                    field="project_id",
                    value=schedule_data['project_id']
                )
            
            if not isinstance(schedule_data['date'], date):
                raise ValidationError(
                    message="date debe ser un objeto date",
                    field="date",
                    value=schedule_data['date']
                )
            
            if not isinstance(schedule_data['start_time'], time):
                raise ValidationError(
                    message="start_time debe ser un objeto time",
                    field="start_time",
                    value=schedule_data['start_time']
                )
            
            if not isinstance(schedule_data['end_time'], time):
                raise ValidationError(
                    message="end_time debe ser un objeto time",
                    field="end_time",
                    value=schedule_data['end_time']
                )
            
            # Validar que la hora de fin sea posterior a la de inicio
            if schedule_data['start_time'] >= schedule_data['end_time']:
                raise ValidationError(
                    message="La hora de fin debe ser posterior a la hora de inicio",
                    field="end_time",
                    value=schedule_data['end_time']
                )
            
            # Validar campos opcionales si están presentes
            if 'team_id' in schedule_data and schedule_data['team_id'] is not None:
                if not isinstance(schedule_data['team_id'], int):
                    raise ValidationError(
                        message="team_id debe ser un entero",
                        field="team_id",
                        value=schedule_data['team_id']
                    )
            
            if 'status_code_id' in schedule_data and schedule_data['status_code_id'] is not None:
                if not isinstance(schedule_data['status_code_id'], int):
                    raise ValidationError(
                        message="status_code_id debe ser un entero",
                        field="status_code_id",
                        value=schedule_data['status_code_id']
                    )
            
            if 'is_confirmed' in schedule_data and schedule_data['is_confirmed'] is not None:
                if not isinstance(schedule_data['is_confirmed'], bool):
                    raise ValidationError(
                        message="is_confirmed debe ser un booleano",
                        field="is_confirmed",
                        value=schedule_data['is_confirmed']
                    )
            
            if 'location' in schedule_data and schedule_data['location'] is not None:
                if not isinstance(schedule_data['location'], str):
                    raise ValidationError(
                        message="location debe ser una cadena",
                        field="location",
                        value=schedule_data['location']
                    )
                
                if len(schedule_data['location'].strip()) == 0:
                    raise ValidationError(
                        message="location no puede estar vacía",
                        field="location",
                        value=schedule_data['location']
                    )
            
            if 'notes' in schedule_data and schedule_data['notes'] is not None:
                if not isinstance(schedule_data['notes'], str):
                    raise ValidationError(
                        message="notes debe ser una cadena",
                        field="notes",
                        value=schedule_data['notes']
                    )
            
            self._logger.debug("Datos de horario válidos")
            return True
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos en validación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_schedule_data",
                entity_type="Schedule",
                entity_id=None
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en validación: {e}")
            raise ScheduleRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_schedule_data",
                entity_type="Schedule",
                entity_id=None,
                original_error=e
            )

    async def validate_schedule_id(self, schedule_id: int) -> bool:
        """
        Valida que un ID de horario sea válido y exista.
        
        Args:
            schedule_id: ID del horario a validar
            
        Returns:
            bool: True si el ID es válido y existe
            
        Raises:
            ValidationError: Si el ID no es válido o no existe
            ScheduleRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(f"Validando ID de horario: {schedule_id}")
            
            # Validar tipo de dato
            if not isinstance(schedule_id, int):
                raise ValidationError(
                    message="schedule_id debe ser un entero",
                    field="schedule_id",
                    value=schedule_id
                )
            
            # Validar que sea positivo
            if schedule_id <= 0:
                raise ValidationError(
                    message="schedule_id debe ser un entero positivo",
                    field="schedule_id",
                    value=schedule_id
                )
            
            # Verificar que existe en la base de datos usando BaseRepository
            exists = await self.exists(schedule_id)
            
            if not exists:
                raise ValidationError(
                    message=f"No existe un horario con ID {schedule_id}",
                    field="schedule_id",
                    value=schedule_id
                )
            
            self._logger.debug(f"ID de horario {schedule_id} válido")
            return True
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos en validación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_schedule_id",
                entity_type="Schedule",
                entity_id=schedule_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en validación: {e}")
            raise ScheduleRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_schedule_id",
                entity_type="Schedule",
                entity_id=schedule_id,
                original_error=e
            )

    async def validate_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> bool:
        """
        Valida un rango de fechas.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            bool: True si el rango es válido
            
        Raises:
            ValidationError: Si el rango no es válido
            ScheduleRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(f"Validando rango de fechas: {start_date} - {end_date}")
            
            # Validar tipos de datos
            if not isinstance(start_date, date):
                raise ValidationError(
                    message="start_date debe ser un objeto date",
                    field="start_date",
                    value=start_date
                )
            
            if not isinstance(end_date, date):
                raise ValidationError(
                    message="end_date debe ser un objeto date",
                    field="end_date",
                    value=end_date
                )
            
            # Validar que la fecha de fin sea posterior o igual a la de inicio
            if start_date > end_date:
                raise ValidationError(
                    message="La fecha de fin debe ser posterior o igual a la fecha de inicio",
                    field="end_date",
                    value=end_date
                )
            
            self._logger.debug("Rango de fechas válido")
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en validación: {e}")
            raise ScheduleRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_date_range",
                entity_type="Schedule",
                entity_id=None,
                original_error=e
            )

    async def validate_time_range(
        self,
        start_time: time,
        end_time: time
    ) -> bool:
        """
        Valida un rango de horas.
        
        Args:
            start_time: Hora de inicio
            end_time: Hora de fin
            
        Returns:
            bool: True si el rango es válido
            
        Raises:
            ValidationError: Si el rango no es válido
            ScheduleRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(f"Validando rango de horas: {start_time} - {end_time}")
            
            # Validar tipos de datos
            if not isinstance(start_time, time):
                raise ValidationError(
                    message="start_time debe ser un objeto time",
                    field="start_time",
                    value=start_time
                )
            
            if not isinstance(end_time, time):
                raise ValidationError(
                    message="end_time debe ser un objeto time",
                    field="end_time",
                    value=end_time
                )
            
            # Validar que la hora de fin sea posterior a la de inicio
            if start_time >= end_time:
                raise ValidationError(
                    message="La hora de fin debe ser posterior a la hora de inicio",
                    field="end_time",
                    value=end_time
                )
            
            self._logger.debug("Rango de horas válido")
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en validación: {e}")
            raise ScheduleRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_time_range",
                entity_type="Schedule",
                entity_id=None,
                original_error=e
            )

    async def validate_schedule_conflicts(
        self,
        employee_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
        exclude_schedule_id: Optional[int] = None
    ) -> bool:
        """
        Valida que no existan conflictos de horarios para un empleado.
        
        Args:
            employee_id: ID del empleado
            schedule_date: Fecha del horario
            start_time: Hora de inicio
            end_time: Hora de fin
            exclude_schedule_id: ID de horario a excluir de la validación (opcional)
            
        Returns:
            bool: True si no hay conflictos
            
        Raises:
            ValidationError: Si existen conflictos
            ScheduleRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(
                f"Validando conflictos para empleado {employee_id} "
                f"el {schedule_date} de {start_time} a {end_time}"
            )
            
            # Construir filtros para buscar conflictos usando BaseRepository
            filters = {
                "employee_id": employee_id,
                "date": schedule_date,
                "_time_overlap": {
                    "start_time": start_time,
                    "end_time": end_time
                }
            }
            
            # Excluir el horario actual si se está actualizando
            if exclude_schedule_id:
                filters["id__ne"] = exclude_schedule_id
            
            # Usar consulta manual para solapamiento de horarios (lógica compleja)
            stmt = (
                select(Schedule)
                .where(
                    and_(
                        Schedule.employee_id == employee_id,
                        Schedule.date == schedule_date,
                        # Verificar solapamiento de horarios
                        or_(
                            # El nuevo horario empieza durante un horario existente
                            and_(
                                Schedule.start_time <= start_time,
                                Schedule.end_time > start_time
                            ),
                            # El nuevo horario termina durante un horario existente
                            and_(
                                Schedule.start_time < end_time,
                                Schedule.end_time >= end_time
                            ),
                            # El nuevo horario contiene completamente un horario existente
                            and_(
                                Schedule.start_time >= start_time,
                                Schedule.end_time <= end_time
                            )
                        )
                    )
                )
            )
            
            # Excluir el horario actual si se está actualizando
            if exclude_schedule_id:
                stmt = stmt.where(Schedule.id != exclude_schedule_id)
            
            result = await self.get_session().execute(stmt)
            conflicting_schedules = result.scalars().all()
            
            if conflicting_schedules:
                conflict_details = [
                    f"ID {s.id}: {s.start_time}-{s.end_time}"
                    for s in conflicting_schedules
                ]
                
                raise ValidationError(
                    message=(
                        f"Conflicto de horarios para empleado {employee_id} "
                        f"el {schedule_date}. Horarios en conflicto: {', '.join(conflict_details)}"
                    ),
                    field="schedule_time",
                    value=f"{start_time}-{end_time}"
                )
            
            self._logger.debug("No se encontraron conflictos de horarios")
            return True
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos en validación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_schedule_conflicts",
                entity_type="Schedule",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en validación: {e}")
            raise ScheduleRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_schedule_conflicts",
                entity_type="Schedule",
                entity_id=employee_id,
                original_error=e
            )

    async def validate_project_assignment(
        self,
        employee_id: int,
        project_id: int
    ) -> bool:
        """
        Valida que un empleado esté asignado a un proyecto.
        
        Args:
            employee_id: ID del empleado
            project_id: ID del proyecto
            
        Returns:
            bool: True si la asignación es válida
            
        Raises:
            ValidationError: Si la asignación no es válida
            ScheduleRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(
                f"Validando asignación de empleado {employee_id} a proyecto {project_id}"
            )
            
            # Verificar que el empleado existe usando BaseRepository
            employee_exists = await self._employee_repo.exists(employee_id)
            
            if not employee_exists:
                raise ValidationError(
                    message=f"No existe un empleado con ID {employee_id}",
                    field="employee_id",
                    value=employee_id
                )
            
            # Verificar que el proyecto existe usando BaseRepository
            project_exists = await self._project_repo.exists(project_id)
            
            if not project_exists:
                raise ValidationError(
                    message=f"No existe un proyecto con ID {project_id}",
                    field="project_id",
                    value=project_id
                )
            
            # TODO: Aquí se podría agregar validación adicional para verificar
            # que el empleado esté realmente asignado al proyecto a través
            # de una tabla de asignaciones si existe en el modelo
            
            self._logger.debug("Asignación de proyecto válida")
            return True
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos en validación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_project_assignment",
                entity_type="Schedule",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en validación: {e}")
            raise ScheduleRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_project_assignment",
                entity_type="Schedule",
                entity_id=employee_id,
                original_error=e
            )

    async def validate_team_membership(
        self,
        employee_id: int,
        team_id: int
    ) -> bool:
        """
        Valida que un empleado pertenezca a un equipo.
        
        Args:
            employee_id: ID del empleado
            team_id: ID del equipo
            
        Returns:
            bool: True si la membresía es válida
            
        Raises:
            ValidationError: Si la membresía no es válida
            ScheduleRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(
                f"Validando membresía de empleado {employee_id} en equipo {team_id}"
            )
            
            # Verificar que el empleado existe usando BaseRepository
            employee_exists = await self._employee_repo.exists(employee_id)
            
            if not employee_exists:
                raise ValidationError(
                    message=f"No existe un empleado con ID {employee_id}",
                    field="employee_id",
                    value=employee_id
                )
            
            # Verificar que el equipo existe usando BaseRepository
            team_exists = await self._team_repo.exists(team_id)
            
            if not team_exists:
                raise ValidationError(
                    message=f"No existe un equipo con ID {team_id}",
                    field="team_id",
                    value=team_id
                )
            
            # TODO: Aquí se podría agregar validación adicional para verificar
            # que el empleado pertenezca realmente al equipo a través
            # de una relación en el modelo si existe
            
            self._logger.debug("Membresía de equipo válida")
            return True
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos en validación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_team_membership",
                entity_type="Schedule",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en validación: {e}")
            raise ScheduleRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_team_membership",
                entity_type="Schedule",
                entity_id=employee_id,
                original_error=e
            )

    async def validate_search_filters(
        self,
        filters: Dict[str, Any]
    ) -> bool:
        """
        Valida los filtros de búsqueda.
        
        Args:
            filters: Diccionario de filtros a validar
            
        Returns:
            bool: True si los filtros son válidos
            
        Raises:
            ValidationError: Si los filtros no son válidos
            ScheduleRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(f"Validando filtros de búsqueda: {filters}")
            
            if not isinstance(filters, dict):
                raise ValidationError(
                    message="Los filtros deben ser un diccionario",
                    field="filters",
                    value=filters
                )
            
            # Validar filtros específicos
            valid_filters = {
                'employee_id': int,
                'project_id': int,
                'team_id': int,
                'status_code_id': int,
                'date_from': date,
                'date_to': date,
                'is_confirmed': bool,
                'location': str
            }
            
            for filter_name, filter_value in filters.items():
                if filter_name not in valid_filters:
                    raise ValidationError(
                        message=f"Filtro no válido: {filter_name}",
                        field="filters",
                        value=filter_name
                    )
                
                expected_type = valid_filters[filter_name]
                if not isinstance(filter_value, expected_type):
                    raise ValidationError(
                        message=f"Tipo incorrecto para filtro {filter_name}. Esperado: {expected_type.__name__}",
                        field=filter_name,
                        value=filter_value
                    )
                
                # Validaciones específicas por tipo de filtro
                if filter_name in ['employee_id', 'project_id', 'team_id', 'status_code_id']:
                    if filter_value <= 0:
                        raise ValidationError(
                            message=f"{filter_name} debe ser un entero positivo",
                            field=filter_name,
                            value=filter_value
                        )
                
                if filter_name == 'location' and len(filter_value.strip()) == 0:
                    raise ValidationError(
                        message="location no puede estar vacía",
                        field="location",
                        value=filter_value
                    )
            
            # Validar rango de fechas si ambas están presentes
            if 'date_from' in filters and 'date_to' in filters:
                await self.validate_date_range(filters['date_from'], filters['date_to'])
            
            self._logger.debug("Filtros de búsqueda válidos")
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en validación: {e}")
            raise ScheduleRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_search_filters",
                entity_type="Schedule",
                entity_id=None,
                original_error=e
            )