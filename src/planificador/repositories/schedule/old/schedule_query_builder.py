# src/planificador/database/repositories/schedule/schedule_query_builder.py

from typing import List, Optional, Dict, Any, Tuple
from datetime import date, time
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import pendulum
from pendulum import DateTime, Date
from sqlalchemy.exc import SQLAlchemyError

from ....models.schedule import Schedule
from ....models.employee import Employee
from ....models.project import Project
from ....models.team import Team
from ....models.status_code import StatusCode
from ....exceptions import ValidationError
from ....exceptions.repository import (
    convert_sqlalchemy_error,
    create_schedule_query_error,
)
from ....utils.date_utils import (
    get_current_time,
    format_datetime,
    is_business_day,
    get_week_range,
    get_month_range
)


class ScheduleQueryBuilder:
    """
    Constructor de consultas especializadas para Schedule.
    
    Maneja la construcción de consultas complejas para horarios,
    incluyendo filtros por fechas, empleados, proyectos y equipos.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._logger = logger.bind(component="ScheduleQueryBuilder")
    
    # ==========================================
    # CONSULTAS POR EMPLEADO
    # ==========================================
    
    async def find_by_employee(self, employee_id: int) -> List[Schedule]:
        """
        Busca todos los horarios de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de horarios del empleado
        """
        stmt = (
            select(Schedule)
            .options(
                selectinload(Schedule.employee),
                selectinload(Schedule.project),
                selectinload(Schedule.team),
                selectinload(Schedule.status_code)
            )
            .where(Schedule.employee_id == employee_id)
            .order_by(desc(Schedule.date), asc(Schedule.start_time))
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(exc, context="find_by_employee")
            logger.error(
                "Error de base de datos al buscar horarios por empleado",
                employee_id=employee_id,
                error=str(db_error),
            )
            raise create_schedule_query_error(
                "Error al buscar horarios por empleado",
                details={"employee_id": employee_id, "db_error": str(db_error)},
            ) from db_error
        return list(result.scalars().all())
    
    async def find_by_employee_and_date_range(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> List[Schedule]:
        """
        Busca horarios de un empleado en un rango de fechas.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Lista de horarios del empleado en el rango
        """
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
                    Schedule.employee_id == employee_id,
                    Schedule.date >= start_date,
                    Schedule.date <= end_date
                )
            )
            .order_by(asc(Schedule.date), asc(Schedule.start_time))
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="find_by_employee_and_date_range"
            )
            logger.error(
                "Error de base de datos al buscar horarios por empleado y rango de fechas",
                employee_id=employee_id,
                start_date=str(start_date),
                end_date=str(end_date),
                error=str(db_error),
            )
            raise create_schedule_query_error(
                "Error al buscar horarios por empleado y rango de fechas",
                details={
                    "employee_id": employee_id,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "db_error": str(db_error),
                },
            ) from db_error
        return list(result.scalars().all())
    
    async def get_by_employee_and_date(
        self,
        employee_id: int,
        schedule_date: date
    ) -> Optional[Schedule]:
        """
        Busca un horario específico por empleado y fecha.
        
        Args:
            employee_id: ID del empleado
            schedule_date: Fecha del horario
            
        Returns:
            Horario encontrado o None
        """
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
                    Schedule.employee_id == employee_id,
                    Schedule.date == schedule_date
                )
            )
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="get_by_employee_and_date"
            )
            logger.error(
                "Error de base de datos al buscar horario por empleado y fecha",
                employee_id=employee_id,
                schedule_date=str(schedule_date),
                error=str(db_error),
            )
            raise create_schedule_query_error(
                "Error al buscar horario por empleado y fecha",
                details={
                    "employee_id": employee_id,
                    "schedule_date": str(schedule_date),
                    "db_error": str(db_error),
                },
            ) from db_error
        return result.scalar_one_or_none()
    
    def build_overlapping_schedules_query(
        self,
        employee_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time
    ) -> select:
        """
        Construye consulta para horarios superpuestos.
        
        Args:
            employee_id: ID del empleado
            schedule_date: Fecha del horario
            start_time: Hora de inicio
            end_time: Hora de fin
            
        Returns:
            Consulta SQLAlchemy para horarios superpuestos
        """
        return (
            select(Schedule)
            .options(
                selectinload(Schedule.employee),
                selectinload(Schedule.project),
                selectinload(Schedule.team),
                selectinload(Schedule.status_code)
            )
            .where(
                and_(
                    Schedule.employee_id == employee_id,
                    Schedule.date == schedule_date,
                    or_(
                        and_(
                            Schedule.start_time <= start_time,
                            Schedule.end_time > start_time
                        ),
                        and_(
                            Schedule.start_time < end_time,
                            Schedule.end_time >= end_time
                        ),
                        and_(
                            Schedule.start_time >= start_time,
                            Schedule.end_time <= end_time
                        )
                    )
                )
            )
        )
    
    # ==========================================
    # CONSULTAS POR PROYECTO
    # ==========================================
    
    async def find_by_project(self, project_id: int) -> List[Schedule]:
        """
        Busca todos los horarios de un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Lista de horarios del proyecto
        """
        stmt = (
            select(Schedule)
            .options(
                selectinload(Schedule.employee),
                selectinload(Schedule.project),
                selectinload(Schedule.team),
                selectinload(Schedule.status_code)
            )
            .where(Schedule.project_id == project_id)
            .order_by(desc(Schedule.date), asc(Schedule.start_time))
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(exc, context="find_by_project")
            logger.error(
                "Error de base de datos al buscar horarios por proyecto",
                project_id=project_id,
                error=str(db_error),
            )
            raise create_schedule_query_error(
                "Error al buscar horarios por proyecto",
                details={"project_id": project_id, "db_error": str(db_error)},
            ) from db_error
        return list(result.scalars().all())
    
    async def find_by_project_and_date_range(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> List[Schedule]:
        """
        Busca horarios de un proyecto en un rango de fechas.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Lista de horarios del proyecto en el rango
        """
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
                    Schedule.project_id == project_id,
                    Schedule.date >= start_date,
                    Schedule.date <= end_date
                )
            )
            .order_by(asc(Schedule.date), asc(Schedule.start_time))
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="find_by_project_and_date_range"
            )
            logger.error(
                "Error de base de datos al buscar horarios por proyecto y rango de fechas",
                project_id=project_id,
                start_date=str(start_date),
                end_date=str(end_date),
                error=str(db_error),
            )
            raise create_schedule_query_error(
                "Error al buscar horarios por proyecto y rango de fechas",
                details={
                    "project_id": project_id,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "db_error": str(db_error),
                },
            ) from db_error
        return list(result.scalars().all())
    
    async def find_overlapping_schedules(
        self,
        employee_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
        exclude_schedule_id: Optional[int] = None
    ) -> List[Schedule]:
        """
        Ejecuta consulta de horarios superpuestos con exclusión opcional.
        
        Args:
            employee_id: ID del empleado
            schedule_date: Fecha del horario
            start_time: Hora de inicio
            end_time: Hora de fin
            exclude_schedule_id: ID del horario a excluir (opcional)
            
        Returns:
            Lista de horarios superpuestos
        """
        stmt = self.build_overlapping_schedules_query(
            employee_id, schedule_date, start_time, end_time
        )
        
        if exclude_schedule_id is not None:
            stmt = stmt.where(Schedule.id != exclude_schedule_id)
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="find_overlapping_schedules"
            )
            logger.error(
                "Error de base de datos al buscar horarios superpuestos",
                employee_id=employee_id,
                schedule_date=str(schedule_date),
                start_time=str(start_time),
                end_time=str(end_time),
                exclude_schedule_id=exclude_schedule_id,
                error=str(db_error),
            )
            raise create_schedule_query_error(
                "Error al buscar horarios superpuestos",
                details={
                    "employee_id": employee_id,
                    "schedule_date": str(schedule_date),
                    "start_time": str(start_time),
                    "end_time": str(end_time),
                    "exclude_schedule_id": exclude_schedule_id,
                    "db_error": str(db_error),
                },
            ) from db_error
        return list(result.scalars().all())
    
    # ==========================================
    # CONSULTAS POR FECHA Y EQUIPO
    # ==========================================
    
    async def find_by_date(self, schedule_date: date) -> List[Schedule]:
        """
        Encuentra horarios de una fecha específica.
        
        Args:
            schedule_date: Fecha específica
            
        Returns:
            Lista de horarios de la fecha
        """
        stmt = (
            select(Schedule)
            .options(
                selectinload(Schedule.employee),
                selectinload(Schedule.project),
                selectinload(Schedule.team),
                selectinload(Schedule.status_code)
            )
            .where(Schedule.date == schedule_date)
            .order_by(asc(Schedule.start_time))
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(exc, context="find_by_date")
            logger.error(
                "Error de base de datos al buscar horarios por fecha",
                schedule_date=str(schedule_date),
                error=str(db_error),
            )
            raise create_schedule_query_error(
                "Error al buscar horarios por fecha",
                details={
                    "schedule_date": str(schedule_date),
                    "db_error": str(db_error),
                },
            ) from db_error
        return list(result.scalars().all())
    
    async def find_by_date_range(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None,
        team_id: Optional[int] = None,
        status_code_id: Optional[int] = None,
        is_confirmed: Optional[bool] = None
    ) -> List[Schedule]:
        """
        Encuentra horarios en rango de fechas con filtros opcionales.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            employee_id: ID del empleado (opcional)
            project_id: ID del proyecto (opcional)
            team_id: ID del equipo (opcional)
            status_code_id: ID del código de estado (opcional)
            is_confirmed: Filtro por confirmación (opcional)
            
        Returns:
            Lista de horarios en el rango con filtros aplicados
        """
        conditions = [
            Schedule.date >= start_date,
            Schedule.date <= end_date
        ]
        
        if employee_id is not None:
            conditions.append(Schedule.employee_id == employee_id)
        if project_id is not None:
            conditions.append(Schedule.project_id == project_id)
        if team_id is not None:
            conditions.append(Schedule.team_id == team_id)
        if status_code_id is not None:
            conditions.append(Schedule.status_code_id == status_code_id)
        
        stmt = (
            select(Schedule)
            .options(
                selectinload(Schedule.employee),
                selectinload(Schedule.project),
                selectinload(Schedule.team),
                selectinload(Schedule.status_code)
            )
            .where(and_(*conditions))
            .order_by(asc(Schedule.date), asc(Schedule.start_time))
        )
        
        if is_confirmed is not None:
            if is_confirmed:
                stmt = stmt.join(StatusCode).where(StatusCode.code == "CONFIRMED")
            else:
                stmt = stmt.join(StatusCode).where(StatusCode.code != "CONFIRMED")
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="find_by_date_range"
            )
            logger.error(
                "Error de base de datos al buscar horarios por rango de fechas",
                start_date=str(start_date),
                end_date=str(end_date),
                employee_id=employee_id,
                project_id=project_id,
                team_id=team_id,
                status_code_id=status_code_id,
                is_confirmed=is_confirmed,
                error=str(db_error),
            )
            raise create_schedule_query_error(
                "Error al buscar horarios por rango de fechas",
                details={
                    "start_date": str(start_date),
                "end_date": str(end_date),
                "employee_id": employee_id,
                "project_id": project_id,
                "team_id": team_id,
                "status_code_id": status_code_id,
                "is_confirmed": is_confirmed,
                "db_error": str(db_error),
                },
            ) from db_error
        return list(result.scalars().all())
    
    async def find_by_team(self, team_id: int) -> List[Schedule]:
        """
        Encuentra horarios de un equipo específico.
        
        Args:
            team_id: ID del equipo
            
        Returns:
            Lista de horarios del equipo
        """
        stmt = (
            select(Schedule)
            .options(
                selectinload(Schedule.employee),
                selectinload(Schedule.project),
                selectinload(Schedule.team),
                selectinload(Schedule.status_code)
            )
            .where(Schedule.team_id == team_id)
            .order_by(asc(Schedule.date), asc(Schedule.start_time))
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(exc, context="find_by_team")
            logger.error(
                "Error de base de datos al buscar horarios por equipo",
                team_id=team_id,
                error=str(db_error),
            )
            raise create_schedule_query_error(
                "Error al buscar horarios por equipo",
                details={
                    "team_id": team_id,
                    "db_error": str(db_error),
                },
            ) from db_error
        return list(result.scalars().all())
    
    # ==========================================
    # CONSULTAS POR ESTADO
    # ==========================================
    
    async def find_confirmed_schedules(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """
        Encuentra horarios confirmados con filtro de fechas opcional.
        
        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            
        Returns:
            Lista de horarios confirmados
        """
        stmt = (
            select(Schedule)
            .options(
                selectinload(Schedule.employee),
                selectinload(Schedule.project),
                selectinload(Schedule.team),
                selectinload(Schedule.status_code)
            )
            .join(ScheduleStatusCode)
            .where(ScheduleStatusCode.code == "CONFIRMED")
        )
        
        if start_date is not None:
            stmt = stmt.where(Schedule.date >= start_date)
        if end_date is not None:
            stmt = stmt.where(Schedule.date <= end_date)
        
        stmt = stmt.order_by(asc(Schedule.date), asc(Schedule.start_time))
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="find_confirmed_schedules"
            )
            logger.error(
                "Error de base de datos al buscar horarios confirmados",
                start_date=str(start_date) if start_date else None,
                end_date=str(end_date) if end_date else None,
                error=str(db_error),
            )
            raise create_schedule_query_error(
                "Error al buscar horarios confirmados",
                details={
                    "start_date": str(start_date) if start_date else None,
                    "end_date": str(end_date) if end_date else None,
                    "db_error": str(db_error),
                },
            ) from db_error
        return list(result.scalars().all())
    
    async def find_unconfirmed_schedules(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """
        Encuentra horarios no confirmados con filtro de fechas opcional.
        
        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            
        Returns:
            Lista de horarios no confirmados
        """
        stmt = (
            select(Schedule)
            .options(
                selectinload(Schedule.employee),
                selectinload(Schedule.project),
                selectinload(Schedule.team),
                selectinload(Schedule.status_code)
            )
            .join(ScheduleStatusCode)
            .where(ScheduleStatusCode.code != "CONFIRMED")
        )
        
        if start_date is not None:
            stmt = stmt.where(Schedule.date >= start_date)
        if end_date is not None:
            stmt = stmt.where(Schedule.date <= end_date)
        
        stmt = stmt.order_by(asc(Schedule.date), asc(Schedule.start_time))
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="find_unconfirmed_schedules"
            )
            logger.error(
                "Error de base de datos al buscar horarios no confirmados",
                start_date=str(start_date) if start_date else None,
                end_date=str(end_date) if end_date else None,
                error=str(db_error),
            )
            raise create_schedule_query_error(
                "Error al buscar horarios no confirmados",
                details={
                    "start_date": str(start_date) if start_date else None,
                    "end_date": str(end_date) if end_date else None,
                    "db_error": str(db_error),
                },
            ) from db_error
        return list(result.scalars().all())
    
    # ==========================================
    # BÚSQUEDA AVANZADA
    # ==========================================
    
    async def search_with_filters(
        self,
        employee_name: Optional[str] = None,
        project_name: Optional[str] = None,
        team_name: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status_code: Optional[str] = None
    ) -> List[Schedule]:
        """
        Búsqueda comprehensiva con múltiples filtros opcionales incluyendo estado por código.
        
        Args:
            employee_name: Nombre del empleado (búsqueda parcial)
            project_name: Nombre del proyecto (búsqueda parcial)
            team_name: Nombre del equipo (búsqueda parcial)
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            status_code: Código de estado (opcional)
            
        Returns:
            Lista de horarios que coinciden con los criterios
        """
        stmt = (
            select(Schedule)
            .options(
                selectinload(Schedule.employee),
                selectinload(Schedule.project),
                selectinload(Schedule.team),
                selectinload(Schedule.status_code)
            )
        )
        
        conditions = []
        
        if employee_name:
            stmt = stmt.join(Employee)
            conditions.append(
                Employee.name.ilike(f"%{employee_name}%")
            )
        
        if project_name:
            stmt = stmt.join(Project)
            conditions.append(
                Project.name.ilike(f"%{project_name}%")
            )
        
        if team_name:
            stmt = stmt.join(Team)
            conditions.append(
                Team.name.ilike(f"%{team_name}%")
            )
        
        if start_date:
            conditions.append(Schedule.date >= start_date)
        
        if end_date:
            conditions.append(Schedule.date <= end_date)
        
        if status_code:
            stmt = stmt.join(ScheduleStatusCode)
            conditions.append(ScheduleStatusCode.code == status_code)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.order_by(asc(Schedule.date), asc(Schedule.start_time))
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(exc, context="search_with_filters")
            logger.error(
                "Error de base de datos en búsqueda avanzada de horarios",
                employee_name=employee_name,
                project_name=project_name,
                team_name=team_name,
                start_date=str(start_date) if start_date else None,
                end_date=str(end_date) if end_date else None,
                status_code=status_code,
                error=str(db_error),
            )
            raise create_schedule_query_error(
                "Error en búsqueda avanzada de horarios",
                details={
                    "employee_name": employee_name,
                    "project_name": project_name,
                    "team_name": team_name,
                    "start_date": str(start_date) if start_date else None,
                    "end_date": str(end_date) if end_date else None,
                    "status_code": status_code,
                    "db_error": str(db_error),
                },
            ) from db_error
        return list(result.scalars().all())