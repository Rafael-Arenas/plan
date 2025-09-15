# src/planificador/database/repositories/schedule/schedule_validator.py

from typing import Optional, Dict, Any, List
from datetime import date, time, datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import pendulum
from pendulum import DateTime, Date
from sqlalchemy.exc import SQLAlchemyError

from ....models.schedule import Schedule
from ....models.employee import Employee
from ....models.project import Project
from ....models.team import Team
from ....exceptions import (
    ValidationError,
    ScheduleValidationError,
    ScheduleTimeConflictError
)
from ....exceptions.repository import (
    convert_sqlalchemy_error,
    create_schedule_validation_repository_error,
)
from ....utils.date_utils import (
    get_current_time,
    is_business_day,
    format_datetime
)


class ScheduleValidator:
    """
    Validador especializado para Schedule.
    
    Maneja todas las validaciones de datos y reglas de negocio
    relacionadas con horarios, incluyendo conflictos de tiempo,
    validaciones de fechas y coherencia de datos.
    """
    
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self._logger = logger.bind(component="ScheduleValidator")
    
    # ==========================================
    # VALIDACIONES BÁSICAS
    # ==========================================
    
    def validate_schedule_data(self, schedule_data: Dict[str, Any]) -> None:
        """
        Valida los datos básicos de un horario.
        
        Args:
            schedule_data: Diccionario con los datos del horario
            
        Raises:
            ScheduleValidationError: Si los datos no son válidos
        """
        errors = []
        
        # Validar employee_id
        if not schedule_data.get('employee_id'):
            errors.append("employee_id es requerido")
        elif not isinstance(schedule_data['employee_id'], int) or schedule_data['employee_id'] <= 0:
            errors.append("employee_id debe ser un entero positivo")
        
        # Validar fecha
        if not schedule_data.get('date'):
            errors.append("date es requerido")
        elif not isinstance(schedule_data['date'], date):
            errors.append("date debe ser un objeto date válido")
        
        # Validar horarios si están presentes
        start_time = schedule_data.get('start_time')
        end_time = schedule_data.get('end_time')
        
        if start_time is not None and not isinstance(start_time, time):
            errors.append("start_time debe ser un objeto time válido")
        
        if end_time is not None and not isinstance(end_time, time):
            errors.append("end_time debe ser un objeto time válido")
        
        # Validar coherencia de horarios
        if start_time and end_time:
            self._validate_time_consistency(start_time, end_time, errors)
        
        # Validar project_id si está presente
        project_id = schedule_data.get('project_id')
        if project_id is not None:
            if not isinstance(project_id, int) or project_id <= 0:
                errors.append("project_id debe ser un entero positivo")
        
        # Validar team_id si está presente
        team_id = schedule_data.get('team_id')
        if team_id is not None:
            if not isinstance(team_id, int) or team_id <= 0:
                errors.append("team_id debe ser un entero positivo")
        
        # Validar location si está presente
        location = schedule_data.get('location')
        if location is not None:
            if not isinstance(location, str):
                errors.append("location debe ser una cadena de texto")
            elif len(location) > 200:
                errors.append("location no puede exceder 200 caracteres")
        
        if errors:
            raise ScheduleValidationError(
                f"Errores de validación en horario: {'; '.join(errors)}"
            )
    
    def _validate_time_consistency(
        self,
        start_time: time,
        end_time: time,
        errors: List[str]
    ) -> None:
        """
        Valida la coherencia entre horarios de inicio y fin.
        
        Args:
            start_time: Hora de inicio
            end_time: Hora de fin
            errors: Lista para agregar errores encontrados
        """
        # Convertir a datetime para comparar
        today = datetime.today().date()
        start_datetime = datetime.combine(today, start_time)
        end_datetime = datetime.combine(today, end_time)
        
        # Si end_time es menor, asumimos que es al día siguiente
        if end_datetime <= start_datetime:
            end_datetime += timedelta(days=1)
        
        # Validar duración máxima (24 horas)
        duration = end_datetime - start_datetime
        if duration > timedelta(hours=24):
            errors.append("La duración del horario no puede exceder 24 horas")
        
        # Validar duración mínima (15 minutos)
        if duration < timedelta(minutes=15):
            errors.append("La duración del horario debe ser al menos 15 minutos")
    
    # ==========================================
    # VALIDACIONES DE FECHAS
    # ==========================================
    
    def validate_schedule_date(self, schedule_date: date) -> None:
        """
        Valida que la fecha del horario sea válida.
        
        Args:
            schedule_date: Fecha a validar
            
        Raises:
            ScheduleValidationError: Si la fecha no es válida
        """
        current_date = get_current_time().date()
        
        # No permitir fechas muy antiguas (más de 1 año atrás)
        min_date = current_date - timedelta(days=365)
        if schedule_date < min_date:
            raise ScheduleValidationError(
                f"No se pueden crear horarios con más de 1 año de antigüedad. "
                f"Fecha mínima: {min_date}"
            )
        
        # No permitir fechas muy futuras (más de 2 años adelante)
        max_date = current_date + timedelta(days=730)
        if schedule_date > max_date:
            raise ScheduleValidationError(
                f"No se pueden crear horarios con más de 2 años de anticipación. "
                f"Fecha máxima: {max_date}"
            )
    
    def validate_business_day_requirement(
        self,
        schedule_date: date,
        require_business_day: bool = False
    ) -> None:
        """
        Valida si se requiere que la fecha sea un día laboral.
        
        Args:
            schedule_date: Fecha a validar
            require_business_day: Si se requiere que sea día laboral
            
        Raises:
            ScheduleValidationError: Si no cumple el requisito
        """
        if require_business_day and not is_business_day(schedule_date):
            raise ScheduleValidationError(
                f"La fecha {schedule_date} no es un día laboral"
            )
    
    # ==========================================
    # VALIDACIONES DE CONFLICTOS
    # ==========================================
    
    async def validate_no_time_conflicts(
        self,
        employee_id: int,
        schedule_date: date,
        start_time: Optional[time],
        end_time: Optional[time],
        exclude_schedule_id: Optional[int] = None
    ) -> None:
        """
        Valida que no existan conflictos de horario para un empleado.
        
        Args:
            employee_id: ID del empleado
            schedule_date: Fecha del horario
            start_time: Hora de inicio
            end_time: Hora de fin
            exclude_schedule_id: ID de horario a excluir (para actualizaciones)
            
        Raises:
            ScheduleTimeConflictError: Si existe un conflicto
        """
        if not self.session:
            self._logger.warning("No se puede validar conflictos sin sesión de base de datos")
            return
        
        if not start_time or not end_time:
            return  # No se puede validar sin horarios específicos
        
        # Buscar horarios existentes del empleado en la misma fecha
        stmt = (
            select(Schedule)
            .where(
                Schedule.employee_id == employee_id,
                Schedule.date == schedule_date,
                Schedule.start_time.isnot(None),
                Schedule.end_time.isnot(None)
            )
        )
        
        if exclude_schedule_id:
            stmt = stmt.where(Schedule.id != exclude_schedule_id)
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="validate_no_time_conflicts"
            )
            self._logger.error(
                "Error de base de datos al validar conflictos de horario",
                employee_id=employee_id,
                schedule_date=str(schedule_date),
                start_time=str(start_time),
                end_time=str(end_time),
                exclude_schedule_id=exclude_schedule_id,
                error=str(db_error),
            )
            raise create_schedule_validation_repository_error(
                "Error al validar conflictos de tiempo",
                details={
                    "employee_id": employee_id,
                    "schedule_date": str(schedule_date),
                    "start_time": str(start_time),
                    "end_time": str(end_time),
                    "exclude_schedule_id": exclude_schedule_id,
                    "db_error": str(db_error),
                },
            ) from db_error
        existing_schedules = result.scalars().all()
        
        for existing in existing_schedules:
            if self._times_overlap(start_time, end_time, existing.start_time, existing.end_time):
                raise ScheduleTimeConflictError(
                    f"Conflicto de horario detectado. El empleado {employee_id} ya tiene "
                    f"un horario programado de {existing.start_time} a {existing.end_time} "
                    f"el {schedule_date}"
                )
    
    def _times_overlap(
        self,
        start1: time,
        end1: time,
        start2: time,
        end2: time
    ) -> bool:
        """
        Verifica si dos rangos de tiempo se superponen.
        
        Args:
            start1, end1: Primer rango de tiempo
            start2, end2: Segundo rango de tiempo
            
        Returns:
            True si se superponen, False en caso contrario
        """
        # Convertir a datetime para comparar
        today = datetime.today().date()
        
        start1_dt = datetime.combine(today, start1)
        end1_dt = datetime.combine(today, end1)
        start2_dt = datetime.combine(today, start2)
        end2_dt = datetime.combine(today, end2)
        
        # Manejar horarios que cruzan medianoche
        if end1_dt <= start1_dt:
            end1_dt += timedelta(days=1)
        if end2_dt <= start2_dt:
            end2_dt += timedelta(days=1)
        
        # Verificar superposición
        return not (end1_dt <= start2_dt or end2_dt <= start1_dt)
    
    # ==========================================
    # VALIDACIONES DE RELACIONES
    # ==========================================
    
    async def validate_employee_exists(self, employee_id: int) -> None:
        """
        Valida que el empleado exista.
        
        Args:
            employee_id: ID del empleado
            
        Raises:
            ValidationError: Si el empleado no existe
        """
        if not self.session:
            return
        
        stmt = select(Employee).where(Employee.id == employee_id)
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="validate_employee_exists"
            )
            self._logger.error(
                "Error de base de datos al validar existencia de empleado",
                employee_id=employee_id,
                error=str(db_error),
            )
            raise create_schedule_validation_repository_error(
                "Error al validar existencia de empleado",
                details={
                    "employee_id": employee_id,
                    "db_error": str(db_error),
                },
            ) from db_error
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise ValidationError(f"El empleado con ID {employee_id} no existe")
        
        if not employee.is_active:
            raise ValidationError(f"El empleado con ID {employee_id} no está activo")
    
    async def validate_project_exists(self, project_id: int) -> None:
        """
        Valida que el proyecto exista.
        
        Args:
            project_id: ID del proyecto
            
        Raises:
            ValidationError: Si el proyecto no existe
        """
        if not self.session:
            return
        
        stmt = select(Project).where(Project.id == project_id)
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="validate_project_exists"
            )
            self._logger.error(
                "Error de base de datos al validar existencia de proyecto",
                project_id=project_id,
                error=str(db_error),
            )
            raise create_schedule_validation_repository_error(
                "Error al validar existencia de proyecto",
                details={
                    "project_id": project_id,
                    "db_error": str(db_error),
                },
            ) from db_error
        project = result.scalar_one_or_none()
        
        if not project:
            raise ValidationError(f"El proyecto con ID {project_id} no existe")
        
        if not project.is_active:
            raise ValidationError(f"El proyecto con ID {project_id} no está activo")
    
    async def validate_team_exists(self, team_id: int) -> None:
        """
        Valida que el equipo exista.
        
        Args:
            team_id: ID del equipo
            
        Raises:
            ValidationError: Si el equipo no existe
        """
        if not self.session:
            return
        
        stmt = select(Team).where(Team.id == team_id)
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="validate_team_exists"
            )
            self._logger.error(
                "Error de base de datos al validar existencia de equipo",
                team_id=team_id,
                error=str(db_error),
            )
            raise create_schedule_validation_repository_error(
                "Error al validar existencia de equipo",
                details={
                    "team_id": team_id,
                    "db_error": str(db_error),
                },
            ) from db_error
        team = result.scalar_one_or_none()
        
        if not team:
            raise ValidationError(f"El equipo con ID {team_id} no existe")
        
        if not team.is_active:
            raise ValidationError(f"El equipo con ID {team_id} no está activo")
    
    # ==========================================
    # VALIDACIONES COMPLEJAS
    # ==========================================
    
    async def validate_schedule_for_creation(self, schedule_data: Dict[str, Any]) -> None:
        """
        Ejecuta todas las validaciones necesarias para crear un horario.
        
        Args:
            schedule_data: Datos del horario a crear
            
        Raises:
            ValidationError: Si alguna validación falla
        """
        # Validaciones básicas
        self.validate_schedule_data(schedule_data)
        
        # Validaciones de fecha
        schedule_date = schedule_data['date']
        self.validate_schedule_date(schedule_date)
        
        # Validaciones de relaciones
        await self.validate_employee_exists(schedule_data['employee_id'])
        
        if schedule_data.get('project_id'):
            await self.validate_project_exists(schedule_data['project_id'])
        
        if schedule_data.get('team_id'):
            await self.validate_team_exists(schedule_data['team_id'])
        
        # Validaciones de conflictos
        await self.validate_no_time_conflicts(
            employee_id=schedule_data['employee_id'],
            schedule_date=schedule_date,
            start_time=schedule_data.get('start_time'),
            end_time=schedule_data.get('end_time')
        )
    
    async def validate_schedule_for_update(
        self,
        schedule_id: int,
        schedule_data: Dict[str, Any]
    ) -> None:
        """
        Ejecuta todas las validaciones necesarias para actualizar un horario.
        
        Args:
            schedule_id: ID del horario a actualizar
            schedule_data: Datos actualizados del horario
            
        Raises:
            ValidationError: Si alguna validación falla
        """
        # Validaciones básicas
        self.validate_schedule_data(schedule_data)
        
        # Validaciones de fecha si está presente
        if 'date' in schedule_data and schedule_data['date']:
            self.validate_schedule_date(schedule_data['date'])
        
        # Validaciones de relaciones si están presentes
        if 'employee_id' in schedule_data and schedule_data['employee_id']:
            await self.validate_employee_exists(schedule_data['employee_id'])
        
        if 'project_id' in schedule_data and schedule_data['project_id']:
            await self.validate_project_exists(schedule_data['project_id'])
        
        if 'team_id' in schedule_data and schedule_data['team_id']:
            await self.validate_team_exists(schedule_data['team_id'])
        
        # Validaciones de conflictos si hay horarios
        if schedule_data.get('start_time') and schedule_data.get('end_time'):
            await self.validate_no_time_conflicts(
                employee_id=schedule_data.get('employee_id'),
                schedule_date=schedule_data.get('date'),
                start_time=schedule_data.get('start_time'),
                end_time=schedule_data.get('end_time'),
                exclude_schedule_id=schedule_id,
            )