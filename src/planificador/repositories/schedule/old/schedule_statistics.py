# src/planificador/database/repositories/schedule/schedule_statistics.py

from typing import Dict, Any, List, Optional, Tuple
from datetime import date, datetime, timedelta
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import pendulum
from pendulum import DateTime, Date
from sqlalchemy.exc import SQLAlchemyError

from ....models.schedule import Schedule
from ....models.employee import Employee
from ....models.project import Project
from ....models.team import Team
from ....utils.date_utils import (
    get_current_time,
    get_week_range,
    get_month_range,
    get_business_days
)
from ....exceptions.repository import (
    convert_sqlalchemy_error,
    create_schedule_statistics_error,
)


class ScheduleStatistics:
    """
    Generador de estadísticas y métricas para Schedule.
    
    Proporciona métodos para calcular estadísticas relacionadas
    con horarios, incluyendo horas trabajadas, distribución por
    proyectos, empleados y equipos.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._logger = logger.bind(component="ScheduleStatistics")
    
    # ==========================================
    # ESTADÍSTICAS GENERALES
    # ==========================================
    
    async def get_total_schedules_count(self) -> int:
        """
        Obtiene el conteo total de horarios.
        
        Returns:
            Número total de horarios en el sistema
        """
        stmt = select(func.count(Schedule.id))
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="get_total_schedules_count"
            )
            logger.error(
                "Error de base de datos al obtener conteo total de horarios",
                error=str(db_error),
            )
            raise create_schedule_statistics_error(
                "Error al obtener el conteo total de horarios",
                details={"db_error": str(db_error)},
            ) from db_error
        
        return result.scalar() or 0
    
    async def get_confirmed_schedules_count(self) -> int:
        """
        Obtiene el conteo de horarios confirmados.
        
        Returns:
            Número de horarios confirmados
        """
        stmt = select(func.count(Schedule.id)).where(Schedule.is_confirmed == True)
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="get_confirmed_schedules_count"
            )
            logger.error(
                "Error de base de datos al obtener conteo de horarios confirmados",
                error=str(db_error),
            )
            raise create_schedule_statistics_error(
                "Error al obtener el conteo de horarios confirmados",
                details={"db_error": str(db_error)},
            ) from db_error
        
        return result.scalar() or 0
    
    async def get_schedules_by_date_range_count(
        self,
        start_date: date,
        end_date: date
    ) -> int:
        """
        Obtiene el conteo de horarios en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Número de horarios en el rango de fechas
        """
        stmt = (
            select(func.count(Schedule.id))
            .where(
                and_(
                    Schedule.date >= start_date,
                    Schedule.date <= end_date
                )
            )
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="get_schedules_by_date_range_count"
            )
            logger.error(
                "Error de base de datos al obtener conteo de horarios por rango de fechas",
                start_date=str(start_date),
                end_date=str(end_date),
                error=str(db_error),
            )
            raise create_schedule_statistics_error(
                "Error al obtener el conteo de horarios por rango de fechas",
                details={
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "db_error": str(db_error),
                },
            ) from db_error
        
        return result.scalar() or 0
    
    async def get_schedule_counts(self) -> Dict[str, int]:
        """
        Obtiene conteos generales de horarios.
        
        Returns:
            Diccionario con conteos de horarios
        """
        stmt = (
            select(
                func.count(Schedule.id).label('total'),
                func.count(case((Schedule.is_confirmed == True, 1))).label('confirmed'),
                func.count(case((Schedule.is_confirmed == False, 1))).label('unconfirmed')
            )
        )
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="get_schedule_counts"
            )
            logger.error(
                "Error de base de datos al obtener conteos de horarios",
                error=str(db_error),
            )
            raise create_schedule_statistics_error(
                "Error al obtener los conteos de horarios",
                details={"db_error": str(db_error)},
            ) from db_error
        row = result.first()
        
        return {
            'total': row.total or 0,
            'confirmed': row.confirmed or 0,
            'unconfirmed': row.unconfirmed or 0
        }
    
    # ==========================================
    # ESTADÍSTICAS DE EMPLEADOS
    # ==========================================
    
    async def get_employee_schedule_summary(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene un resumen de horarios para un empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            
        Returns:
            Diccionario con resumen de horarios del empleado
        """
        conditions = [Schedule.employee_id == employee_id]
        
        if start_date:
            conditions.append(Schedule.date >= start_date)
        if end_date:
            conditions.append(Schedule.date <= end_date)
        
        stmt = (
            select(
                func.count(Schedule.id).label('total_schedules'),
                func.count(case((Schedule.is_confirmed == True, 1))).label('confirmed_schedules'),
                func.sum(Schedule.hours_worked).label('total_hours'),
                func.avg(Schedule.hours_worked).label('avg_hours_per_day')
            )
            .where(and_(*conditions))
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="get_employee_schedule_summary"
            )
            logger.error(
                "Error de base de datos al obtener resumen de empleado",
                employee_id=employee_id,
                start_date=str(start_date) if start_date else None,
                end_date=str(end_date) if end_date else None,
                error=str(db_error),
            )
            raise create_schedule_statistics_error(
                "Error al obtener el resumen del empleado",
                details={
                    "employee_id": employee_id,
                    "start_date": str(start_date) if start_date else None,
                    "end_date": str(end_date) if end_date else None,
                    "db_error": str(db_error),
                },
            ) from db_error
        
        row = result.first()
        
        return {
            'employee_id': employee_id,
            'total_schedules': row.total_schedules or 0,
            'confirmed_schedules': row.confirmed_schedules or 0,
            'total_hours': float(row.total_hours or 0),
            'avg_hours_per_day': float(row.avg_hours_per_day or 0),
            'period': {
                'start_date': str(start_date) if start_date else None,
                'end_date': str(end_date) if end_date else None
            }
        }
    
    async def get_employee_hours_worked(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Calcula las horas trabajadas por un empleado en un período.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Diccionario con información de horas trabajadas
        """
        stmt = (
            select(Schedule)
            .where(
                and_(
                    Schedule.employee_id == employee_id,
                    Schedule.date >= start_date,
                    Schedule.date <= end_date,
                    Schedule.start_time.isnot(None),
                    Schedule.end_time.isnot(None)
                )
            )
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="get_employee_hours_worked"
            )
            logger.error(
                "Error de base de datos al obtener horas trabajadas del empleado",
                employee_id=employee_id,
                start_date=str(start_date),
                end_date=str(end_date),
                error=str(db_error),
            )
            raise create_schedule_statistics_error(
                "Error al obtener las horas trabajadas del empleado",
                details={
                    "employee_id": employee_id,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "db_error": str(db_error),
                },
            ) from db_error
        schedules = result.scalars().all()
        
        total_hours = sum(schedule.hours_worked for schedule in schedules)
        working_days = len(set(schedule.date for schedule in schedules))
        
        return {
            'employee_id': employee_id,
            'total_hours': round(total_hours, 2),
            'working_days': working_days,
            'average_hours_per_day': round(total_hours / working_days, 2) if working_days > 0 else 0,
            'schedules_count': len(schedules),
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
    
    # ==========================================
    # ESTADÍSTICAS DE PROYECTOS
    # ==========================================
    
    async def get_project_schedule_summary(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene un resumen de horarios para un proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            
        Returns:
            Diccionario con resumen de horarios del proyecto
        """
        conditions = [Schedule.project_id == project_id]
        
        if start_date:
            conditions.append(Schedule.date >= start_date)
        if end_date:
            conditions.append(Schedule.date <= end_date)
        
        stmt = (
            select(
                func.count(Schedule.id).label('total_schedules'),
                func.count(case((Schedule.is_confirmed == True, 1))).label('confirmed_schedules'),
                func.sum(Schedule.hours_worked).label('total_hours'),
                func.count(func.distinct(Schedule.employee_id)).label('unique_employees')
            )
            .where(and_(*conditions))
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="get_project_schedule_summary"
            )
            logger.error(
                "Error de base de datos al obtener resumen de proyecto",
                project_id=project_id,
                start_date=str(start_date) if start_date else None,
                end_date=str(end_date) if end_date else None,
                error=str(db_error),
            )
            raise create_schedule_statistics_error(
                "Error al obtener el resumen del proyecto",
                details={
                    "project_id": project_id,
                    "start_date": str(start_date) if start_date else None,
                    "end_date": str(end_date) if end_date else None,
                    "db_error": str(db_error),
                },
            ) from db_error
        
        row = result.first()
        
        return {
            'project_id': project_id,
            'total_schedules': row.total_schedules or 0,
            'confirmed_schedules': row.confirmed_schedules or 0,
            'total_hours': float(row.total_hours or 0),
            'unique_employees': row.unique_employees or 0,
            'period': {
                'start_date': str(start_date) if start_date else None,
                'end_date': str(end_date) if end_date else None
            }
        }
    
    async def get_project_hours_allocation(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Calcula la asignación de horas para un proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Diccionario con información de asignación de horas
        """
        stmt = (
            select(Schedule)
            .where(
                and_(
                    Schedule.project_id == project_id,
                    Schedule.date >= start_date,
                    Schedule.date <= end_date,
                    Schedule.start_time.isnot(None),
                    Schedule.end_time.isnot(None)
                )
            )
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="get_project_hours_allocation"
            )
            logger.error(
                "Error de base de datos al obtener asignación de horas del proyecto",
                project_id=project_id,
                start_date=str(start_date),
                end_date=str(end_date),
                error=str(db_error),
            )
            raise create_schedule_statistics_error(
                "Error al obtener la asignación de horas del proyecto",
                details={
                    "project_id": project_id,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "db_error": str(db_error),
                },
            ) from db_error
        schedules = result.scalars().all()
        
        total_hours = sum(schedule.hours_worked for schedule in schedules)
        unique_employees = len(set(schedule.employee_id for schedule in schedules))
        working_days = len(set(schedule.date for schedule in schedules))
        
        return {
            'project_id': project_id,
            'total_hours': round(total_hours, 2),
            'unique_employees': unique_employees,
            'working_days': working_days,
            'average_hours_per_day': round(total_hours / working_days, 2) if working_days > 0 else 0,
            'average_hours_per_employee': round(total_hours / unique_employees, 2) if unique_employees > 0 else 0,
            'schedules_count': len(schedules),
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
    
    # ==========================================
    # ESTADÍSTICAS DE EQUIPOS
    # ==========================================
    
    async def get_team_schedule_summary(
        self,
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene un resumen de horarios para un equipo.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            
        Returns:
            Diccionario con resumen de horarios del equipo
        """
        conditions = [Schedule.team_id == team_id]
        
        if start_date:
            conditions.append(Schedule.date >= start_date)
        if end_date:
            conditions.append(Schedule.date <= end_date)
        
        stmt = (
            select(
                func.count(Schedule.id).label('total_schedules'),
                func.count(case((Schedule.is_confirmed == True, 1))).label('confirmed_schedules'),
                func.sum(Schedule.hours_worked).label('total_hours'),
                func.count(func.distinct(Schedule.employee_id)).label('unique_employees'),
                func.count(func.distinct(Schedule.project_id)).label('unique_projects')
            )
            .where(and_(*conditions))
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="get_team_schedule_summary"
            )
            logger.error(
                "Error de base de datos al obtener resumen de equipo",
                team_id=team_id,
                start_date=str(start_date) if start_date else None,
                end_date=str(end_date) if end_date else None,
                error=str(db_error),
            )
            raise create_schedule_statistics_error(
                "Error al obtener el resumen del equipo",
                details={
                    "team_id": team_id,
                    "start_date": str(start_date) if start_date else None,
                    "end_date": str(end_date) if end_date else None,
                    "db_error": str(db_error),
                },
            ) from db_error
        
        row = result.first()
        
        return {
            'team_id': team_id,
            'total_schedules': row.total_schedules or 0,
            'confirmed_schedules': row.confirmed_schedules or 0,
            'total_hours': float(row.total_hours or 0),
            'unique_employees': row.unique_employees or 0,
            'unique_projects': row.unique_projects or 0,
            'period': {
                'start_date': str(start_date) if start_date else None,
                'end_date': str(end_date) if end_date else None
            }
        }
    
    # ==========================================
    # DISTRIBUCIÓN TEMPORAL
    # ==========================================
    
    async def get_daily_schedule_distribution(
        self,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Obtiene la distribución diaria de horarios en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Lista con distribución diaria de horarios
        """
        stmt = (
            select(
                Schedule.date,
                func.count(Schedule.id).label('total_schedules'),
                func.count(case((Schedule.is_confirmed == True, 1))).label('confirmed_schedules'),
                func.sum(Schedule.hours_worked).label('total_hours')
            )
            .where(
                and_(
                    Schedule.date >= start_date,
                    Schedule.date <= end_date
                )
            )
            .group_by(Schedule.date)
            .order_by(Schedule.date)
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="get_daily_schedule_distribution"
            )
            logger.error(
                "Error de base de datos al obtener distribución diaria",
                start_date=str(start_date),
                end_date=str(end_date),
                error=str(db_error),
            )
            raise create_schedule_statistics_error(
                "Error al obtener la distribución diaria",
                details={
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "db_error": str(db_error),
                },
            ) from db_error
        
        rows = result.fetchall()
        
        return [
            {
                'date': str(row.date),
                'total_schedules': row.total_schedules or 0,
                'confirmed_schedules': row.confirmed_schedules or 0,
                'total_hours': float(row.total_hours or 0)
            }
            for row in rows
        ]
    
    async def get_weekly_schedule_summary(
        self,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Obtiene un resumen semanal de horarios en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Lista con resumen semanal de horarios
        """
        stmt = (
            select(
                func.strftime('%Y-%W', Schedule.date).label('week'),
                func.count(Schedule.id).label('total_schedules'),
                func.count(case((Schedule.is_confirmed == True, 1))).label('confirmed_schedules'),
                func.sum(Schedule.hours_worked).label('total_hours'),
                func.count(func.distinct(Schedule.employee_id)).label('unique_employees')
            )
            .where(
                and_(
                    Schedule.date >= start_date,
                    Schedule.date <= end_date
                )
            )
            .group_by(func.strftime('%Y-%W', Schedule.date))
            .order_by(func.strftime('%Y-%W', Schedule.date))
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="get_weekly_schedule_summary"
            )
            logger.error(
                "Error de base de datos al obtener resumen semanal",
                start_date=str(start_date),
                end_date=str(end_date),
                error=str(db_error),
            )
            raise create_schedule_statistics_error(
                "Error al obtener el resumen semanal",
                details={
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "db_error": str(db_error),
                },
            ) from db_error
        
        rows = result.fetchall()
        
        return [
            {
                'week': row.week,
                'total_schedules': row.total_schedules or 0,
                'confirmed_schedules': row.confirmed_schedules or 0,
                'total_hours': float(row.total_hours or 0),
                'unique_employees': row.unique_employees or 0
            }
            for row in rows
        ]
    
    # ==========================================
    # MÉTRICAS DE EFICIENCIA
    # ==========================================
    
    async def get_schedule_efficiency_metrics(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de eficiencia de horarios.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Diccionario con métricas de eficiencia
        """
        stmt = (
            select(
                func.count(Schedule.id).label('total_schedules'),
                func.count(case((Schedule.is_confirmed == True, 1))).label('confirmed_schedules'),
                func.sum(Schedule.hours_worked).label('total_hours'),
                func.avg(Schedule.hours_worked).label('avg_hours_per_schedule'),
                func.count(func.distinct(Schedule.employee_id)).label('unique_employees'),
                func.count(func.distinct(Schedule.project_id)).label('unique_projects')
            )
            .where(
                and_(
                    Schedule.date >= start_date,
                    Schedule.date <= end_date
                )
            )
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="get_schedule_efficiency_metrics"
            )
            logger.error(
                "Error de base de datos al obtener métricas de eficiencia",
                start_date=str(start_date),
                end_date=str(end_date),
                error=str(db_error),
            )
            raise create_schedule_statistics_error(
                "Error al obtener las métricas de eficiencia",
                details={
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "db_error": str(db_error),
                },
            ) from db_error
        
        row = result.first()
        
        # Calcular métricas derivadas
        total_schedules = row.total_schedules or 0
        confirmed_schedules = row.confirmed_schedules or 0
        total_hours = float(row.total_hours or 0)
        unique_employees = row.unique_employees or 0
        unique_projects = row.unique_projects or 0
        
        confirmation_rate = (confirmed_schedules / total_schedules * 100) if total_schedules > 0 else 0
        avg_hours_per_employee = (total_hours / unique_employees) if unique_employees > 0 else 0
        avg_schedules_per_employee = (total_schedules / unique_employees) if unique_employees > 0 else 0
        
        return {
            'period': {
                'start_date': str(start_date),
                'end_date': str(end_date)
            },
            'basic_metrics': {
                'total_schedules': total_schedules,
                'confirmed_schedules': confirmed_schedules,
                'total_hours': total_hours,
                'unique_employees': unique_employees,
                'unique_projects': unique_projects
            },
            'efficiency_metrics': {
                'confirmation_rate': round(confirmation_rate, 2),
                'avg_hours_per_schedule': float(row.avg_hours_per_schedule or 0),
                'avg_hours_per_employee': round(avg_hours_per_employee, 2),
                'avg_schedules_per_employee': round(avg_schedules_per_employee, 2)
            }
        }