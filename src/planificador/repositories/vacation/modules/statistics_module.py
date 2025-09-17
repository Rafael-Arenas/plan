# src/planificador/repositories/vacation/modules/statistics_module.py

"""
Módulo de estadísticas para operaciones analíticas del repositorio Vacation.

Este módulo implementa las operaciones de análisis estadístico, métricas
y reportes de vacaciones con cálculos avanzados y agregaciones.

Principios de Diseño:
    - Single Responsibility: Solo operaciones estadísticas y analíticas
    - Performance: Consultas optimizadas con agregaciones en BD
    - Business Intelligence: Métricas relevantes para gestión de vacaciones

Uso:
    ```python
    stats_module = VacationStatisticsModule(session)
    employee_stats = await stats_module.get_employee_vacation_statistics(employee_id)
    team_balance = await stats_module.get_team_vacation_balance(team_id)
    trends = await stats_module.get_vacation_trends()
    ```
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime
from sqlalchemy import select, func, and_, or_, case, distinct, extract
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.vacation import Vacation
from planificador.models.employee import Employee
from planificador.repositories.vacation.interfaces.statistics_interface import IVacationStatisticsOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    VacationRepositoryError,
    convert_sqlalchemy_error
)
import pendulum


class VacationStatisticsModule(BaseRepository[Vacation], IVacationStatisticsOperations):
    """
    Módulo para operaciones estadísticas del repositorio Vacation.
    
    Implementa las operaciones de análisis estadístico, métricas
    y reportes de vacaciones con cálculos avanzados usando Pendulum
    para manejo de fechas y agregaciones optimizadas.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Vacation
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de estadísticas para vacaciones.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Vacation)
        self._logger = self._logger.bind(component="VacationStatisticsModule")
        self._logger.debug("VacationStatisticsModule inicializado")

    async def get_employee_vacation_statistics(
        self, 
        employee_id: int,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de vacaciones para un empleado específico.
        
        Args:
            employee_id: ID del empleado
            year: Año específico (opcional, por defecto año actual)
        
        Returns:
            Dict[str, Any]: Estadísticas del empleado
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            if year is None:
                year = pendulum.now().year
            
            self._logger.debug(f"Obteniendo estadísticas de empleado {employee_id} para año {year}")
            
            # Consulta base para vacaciones del empleado en el año
            base_conditions = [
                self.model_class.employee_id == employee_id,
                extract('year', self.model_class.start_date) == year
            ]
            
            # Total de días de vacaciones
            total_days_stmt = select(
                func.coalesce(func.sum(self.model_class.days_requested), 0)
            ).where(and_(*base_conditions))
            
            # Días por estado
            approved_days_stmt = select(
                func.coalesce(func.sum(self.model_class.days_requested), 0)
            ).where(and_(
                *base_conditions,
                self.model_class.status == 'APPROVED'
            ))
            
            pending_days_stmt = select(
                func.coalesce(func.sum(self.model_class.days_requested), 0)
            ).where(and_(
                *base_conditions,
                self.model_class.status == 'PENDING'
            ))
            
            # Días por tipo de vacación
            annual_days_stmt = select(
                func.coalesce(func.sum(self.model_class.days_requested), 0)
            ).where(and_(
                *base_conditions,
                self.model_class.vacation_type == 'ANNUAL',
                self.model_class.status == 'APPROVED'
            ))
            
            sick_days_stmt = select(
                func.coalesce(func.sum(self.model_class.days_requested), 0)
            ).where(and_(
                *base_conditions,
                self.model_class.vacation_type == 'SICK',
                self.model_class.status == 'APPROVED'
            ))
            
            # Ejecutar consultas
            total_days_result = await self.session.execute(total_days_stmt)
            approved_days_result = await self.session.execute(approved_days_stmt)
            pending_days_result = await self.session.execute(pending_days_stmt)
            annual_days_result = await self.session.execute(annual_days_stmt)
            sick_days_result = await self.session.execute(sick_days_stmt)
            
            total_days = total_days_result.scalar() or 0
            approved_days = approved_days_result.scalar() or 0
            pending_days = pending_days_result.scalar() or 0
            annual_days = annual_days_result.scalar() or 0
            sick_days = sick_days_result.scalar() or 0
            
            # Contar vacaciones por estado
            count_stmt = select(
                func.count(case((self.model_class.status == 'APPROVED', 1))).label('approved_count'),
                func.count(case((self.model_class.status == 'PENDING', 1))).label('pending_count'),
                func.count(case((self.model_class.status == 'REJECTED', 1))).label('rejected_count'),
                func.count(self.model_class.id).label('total_count')
            ).where(and_(*base_conditions))
            
            count_result = await self.session.execute(count_stmt)
            counts = count_result.first()
            
            # Calcular balance (asumiendo 25 días anuales estándar)
            annual_allowance = 25
            remaining_days = annual_allowance - annual_days
            
            statistics = {
                'employee_id': employee_id,
                'year': year,
                'total_days_requested': total_days,
                'approved_days': approved_days,
                'pending_days': pending_days,
                'annual_days_used': annual_days,
                'sick_days_used': sick_days,
                'annual_allowance': annual_allowance,
                'remaining_annual_days': max(0, remaining_days),
                'vacation_counts': {
                    'total': counts.total_count if counts else 0,
                    'approved': counts.approved_count if counts else 0,
                    'pending': counts.pending_count if counts else 0,
                    'rejected': counts.rejected_count if counts else 0
                },
                'utilization_rate': round((annual_days / annual_allowance) * 100, 2) if annual_allowance > 0 else 0
            }
            
            self._logger.debug(f"Estadísticas calculadas para empleado {employee_id}")
            
            return statistics
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo estadísticas de empleado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_vacation_statistics",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo estadísticas: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado obteniendo estadísticas: {e}",
                operation="get_employee_vacation_statistics",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )

    async def get_team_vacation_balance(
        self, 
        team_id: int,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene el balance de vacaciones para un equipo específico.
        
        Args:
            team_id: ID del equipo
            year: Año específico (opcional, por defecto año actual)
        
        Returns:
            Dict[str, Any]: Balance de vacaciones del equipo
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            if year is None:
                year = pendulum.now().year
            
            self._logger.debug(f"Obteniendo balance de equipo {team_id} para año {year}")
            
            # Consulta para obtener empleados del equipo y sus vacaciones
            # Nota: Asumiendo que existe una relación entre Employee y Team
            stmt = select(
                Employee.id.label('employee_id'),
                Employee.name.label('employee_name'),
                func.coalesce(func.sum(
                    case((
                        and_(
                            self.model_class.vacation_type == 'ANNUAL',
                            self.model_class.status == 'APPROVED',
                            extract('year', self.model_class.start_date) == year
                        ), 
                        self.model_class.days_requested
                    ), else_=0)
                ), 0).label('annual_days_used'),
                func.coalesce(func.sum(
                    case((
                        and_(
                            self.model_class.status == 'PENDING',
                            extract('year', self.model_class.start_date) == year
                        ), 
                        self.model_class.days_requested
                    ), else_=0)
                ), 0).label('pending_days')
            ).select_from(
                Employee
            ).outerjoin(
                self.model_class, Employee.id == self.model_class.employee_id
            ).where(
                Employee.team_id == team_id  # Asumiendo que Employee tiene team_id
            ).group_by(Employee.id, Employee.name)
            
            result = await self.session.execute(stmt)
            employee_balances = result.all()
            
            # Calcular estadísticas del equipo
            team_stats = {
                'team_id': team_id,
                'year': year,
                'employee_count': len(employee_balances),
                'total_annual_allowance': len(employee_balances) * 25,  # 25 días por empleado
                'total_annual_used': sum(emp.annual_days_used for emp in employee_balances),
                'total_pending_days': sum(emp.pending_days for emp in employee_balances),
                'employees': []
            }
            
            # Detalles por empleado
            for emp in employee_balances:
                annual_allowance = 25
                remaining = annual_allowance - emp.annual_days_used
                
                team_stats['employees'].append({
                    'employee_id': emp.employee_id,
                    'employee_name': emp.employee_name,
                    'annual_allowance': annual_allowance,
                    'annual_days_used': emp.annual_days_used,
                    'pending_days': emp.pending_days,
                    'remaining_days': max(0, remaining),
                    'utilization_rate': round((emp.annual_days_used / annual_allowance) * 100, 2)
                })
            
            # Calcular métricas del equipo
            if team_stats['total_annual_allowance'] > 0:
                team_stats['team_utilization_rate'] = round(
                    (team_stats['total_annual_used'] / team_stats['total_annual_allowance']) * 100, 2
                )
            else:
                team_stats['team_utilization_rate'] = 0
            
            team_stats['remaining_allowance'] = team_stats['total_annual_allowance'] - team_stats['total_annual_used']
            
            self._logger.debug(f"Balance calculado para equipo {team_id}")
            
            return team_stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo balance de equipo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_vacation_balance",
                entity_type=self.model_class.__name__,
                entity_id=team_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo balance: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado obteniendo balance: {e}",
                operation="get_team_vacation_balance",
                entity_type=self.model_class.__name__,
                entity_id=team_id,
                original_error=e
            )

    async def get_vacation_trends(
        self, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene tendencias de vacaciones en un período específico.
        
        Args:
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
        
        Returns:
            Dict[str, Any]: Tendencias de vacaciones
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante el análisis
        """
        try:
            # Usar último año si no se especifican fechas
            if not start_date:
                start_date = pendulum.now().subtract(years=1).date()
            if not end_date:
                end_date = pendulum.now().date()
            
            self._logger.debug(f"Analizando tendencias del {start_date} al {end_date}")
            
            # Tendencias por mes
            monthly_stmt = select(
                extract('year', self.model_class.start_date).label('year'),
                extract('month', self.model_class.start_date).label('month'),
                func.count(self.model_class.id).label('vacation_count'),
                func.sum(self.model_class.days_requested).label('total_days'),
                func.count(case((self.model_class.status == 'APPROVED', 1))).label('approved_count'),
                func.count(case((self.model_class.status == 'PENDING', 1))).label('pending_count')
            ).where(
                and_(
                    self.model_class.start_date >= start_date,
                    self.model_class.start_date <= end_date
                )
            ).group_by(
                extract('year', self.model_class.start_date),
                extract('month', self.model_class.start_date)
            ).order_by(
                extract('year', self.model_class.start_date),
                extract('month', self.model_class.start_date)
            )
            
            monthly_result = await self.session.execute(monthly_stmt)
            monthly_trends = monthly_result.all()
            
            # Tendencias por tipo de vacación
            type_stmt = select(
                self.model_class.vacation_type,
                func.count(self.model_class.id).label('count'),
                func.sum(self.model_class.days_requested).label('total_days'),
                func.avg(self.model_class.days_requested).label('avg_days')
            ).where(
                and_(
                    self.model_class.start_date >= start_date,
                    self.model_class.start_date <= end_date
                )
            ).group_by(self.model_class.vacation_type)
            
            type_result = await self.session.execute(type_stmt)
            type_trends = type_result.all()
            
            # Patrones estacionales (por trimestre)
            seasonal_stmt = select(
                case(
                    (extract('month', self.model_class.start_date).in_([1, 2, 3]), 'Q1'),
                    (extract('month', self.model_class.start_date).in_([4, 5, 6]), 'Q2'),
                    (extract('month', self.model_class.start_date).in_([7, 8, 9]), 'Q3'),
                    else_='Q4'
                ).label('quarter'),
                func.count(self.model_class.id).label('vacation_count'),
                func.sum(self.model_class.days_requested).label('total_days')
            ).where(
                and_(
                    self.model_class.start_date >= start_date,
                    self.model_class.start_date <= end_date
                )
            ).group_by('quarter')
            
            seasonal_result = await self.session.execute(seasonal_stmt)
            seasonal_trends = seasonal_result.all()
            
            # Compilar resultados
            trends = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'monthly_trends': [
                    {
                        'year': int(row.year),
                        'month': int(row.month),
                        'vacation_count': row.vacation_count,
                        'total_days': row.total_days or 0,
                        'approved_count': row.approved_count,
                        'pending_count': row.pending_count
                    }
                    for row in monthly_trends
                ],
                'vacation_type_trends': [
                    {
                        'vacation_type': row.vacation_type,
                        'count': row.count,
                        'total_days': row.total_days or 0,
                        'average_days': round(float(row.avg_days or 0), 2)
                    }
                    for row in type_trends
                ],
                'seasonal_patterns': [
                    {
                        'quarter': row.quarter,
                        'vacation_count': row.vacation_count,
                        'total_days': row.total_days or 0
                    }
                    for row in seasonal_trends
                ]
            }
            
            self._logger.debug("Análisis de tendencias completado")
            
            return trends
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error analizando tendencias: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_vacation_trends",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado analizando tendencias: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado analizando tendencias: {e}",
                operation="get_vacation_trends",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_vacation_patterns_analysis(
        self, 
        employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analiza patrones de vacaciones (días preferidos, duración típica, etc.).
        
        Args:
            employee_id: ID del empleado específico (opcional)
        
        Returns:
            Dict[str, Any]: Análisis de patrones
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante el análisis
        """
        try:
            self._logger.debug(f"Analizando patrones de vacaciones para empleado: {employee_id or 'todos'}")
            
            conditions = []
            if employee_id:
                conditions.append(self.model_class.employee_id == employee_id)
            
            # Análisis de duración de vacaciones
            duration_stmt = select(
                self.model_class.days_requested,
                func.count(self.model_class.id).label('frequency')
            ).where(and_(*conditions) if conditions else True).group_by(
                self.model_class.days_requested
            ).order_by(func.count(self.model_class.id).desc())
            
            duration_result = await self.session.execute(duration_stmt)
            duration_patterns = duration_result.all()
            
            # Análisis de días de la semana preferidos para inicio
            weekday_stmt = select(
                extract('dow', self.model_class.start_date).label('weekday'),
                func.count(self.model_class.id).label('frequency')
            ).where(and_(*conditions) if conditions else True).group_by(
                extract('dow', self.model_class.start_date)
            )
            
            weekday_result = await self.session.execute(weekday_stmt)
            weekday_patterns = weekday_result.all()
            
            # Análisis de meses preferidos
            month_stmt = select(
                extract('month', self.model_class.start_date).label('month'),
                func.count(self.model_class.id).label('frequency'),
                func.avg(self.model_class.days_requested).label('avg_duration')
            ).where(and_(*conditions) if conditions else True).group_by(
                extract('month', self.model_class.start_date)
            ).order_by(func.count(self.model_class.id).desc())
            
            month_result = await self.session.execute(month_stmt)
            month_patterns = month_result.all()
            
            # Estadísticas generales
            stats_stmt = select(
                func.count(self.model_class.id).label('total_vacations'),
                func.avg(self.model_class.days_requested).label('avg_duration'),
                func.min(self.model_class.days_requested).label('min_duration'),
                func.max(self.model_class.days_requested).label('max_duration')
            ).where(and_(*conditions) if conditions else True)
            
            stats_result = await self.session.execute(stats_stmt)
            general_stats = stats_result.first()
            
            # Mapeo de días de la semana
            weekday_names = {
                0: 'Domingo', 1: 'Lunes', 2: 'Martes', 3: 'Miércoles',
                4: 'Jueves', 5: 'Viernes', 6: 'Sábado'
            }
            
            # Mapeo de meses
            month_names = {
                1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
            }
            
            patterns = {
                'employee_id': employee_id,
                'general_statistics': {
                    'total_vacations': general_stats.total_vacations if general_stats else 0,
                    'average_duration': round(float(general_stats.avg_duration or 0), 2),
                    'min_duration': general_stats.min_duration if general_stats else 0,
                    'max_duration': general_stats.max_duration if general_stats else 0
                },
                'duration_patterns': [
                    {
                        'days': row.days_requested,
                        'frequency': row.frequency
                    }
                    for row in duration_patterns[:10]  # Top 10
                ],
                'preferred_start_weekdays': [
                    {
                        'weekday': weekday_names.get(int(row.weekday), f'Día {int(row.weekday)}'),
                        'frequency': row.frequency
                    }
                    for row in weekday_patterns
                ],
                'preferred_months': [
                    {
                        'month': month_names.get(int(row.month), f'Mes {int(row.month)}'),
                        'frequency': row.frequency,
                        'average_duration': round(float(row.avg_duration or 0), 2)
                    }
                    for row in month_patterns
                ]
            }
            
            self._logger.debug("Análisis de patrones completado")
            
            return patterns
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error analizando patrones: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_vacation_patterns_analysis",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado analizando patrones: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado analizando patrones: {e}",
                operation="get_vacation_patterns_analysis",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )

    async def generate_vacation_summary_report(
        self, 
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte resumen completo de vacaciones.
        
        Args:
            year: Año específico (opcional, por defecto año actual)
        
        Returns:
            Dict[str, Any]: Reporte resumen completo
        
        Raises:
            VacationRepositoryError: Si ocurre un error generando el reporte
        """
        try:
            if year is None:
                year = pendulum.now().year
            
            self._logger.debug(f"Generando reporte resumen para año {year}")
            
            # Estadísticas generales
            general_stmt = select(
                func.count(self.model_class.id).label('total_vacations'),
                func.count(case((self.model_class.status == 'APPROVED', 1))).label('approved_count'),
                func.count(case((self.model_class.status == 'PENDING', 1))).label('pending_count'),
                func.count(case((self.model_class.status == 'REJECTED', 1))).label('rejected_count'),
                func.sum(case((self.model_class.status == 'APPROVED', self.model_class.days_requested))).label('total_approved_days'),
                func.count(distinct(self.model_class.employee_id)).label('employees_with_vacations')
            ).where(extract('year', self.model_class.start_date) == year)
            
            general_result = await self.session.execute(general_stmt)
            general_stats = general_result.first()
            
            # Estadísticas por tipo
            type_stmt = select(
                self.model_class.vacation_type,
                func.count(self.model_class.id).label('count'),
                func.sum(self.model_class.days_requested).label('total_days')
            ).where(
                and_(
                    extract('year', self.model_class.start_date) == year,
                    self.model_class.status == 'APPROVED'
                )
            ).group_by(self.model_class.vacation_type)
            
            type_result = await self.session.execute(type_stmt)
            type_stats = type_result.all()
            
            # Top empleados por días de vacación
            top_employees_stmt = select(
                self.model_class.employee_id,
                func.sum(self.model_class.days_requested).label('total_days'),
                func.count(self.model_class.id).label('vacation_count')
            ).where(
                and_(
                    extract('year', self.model_class.start_date) == year,
                    self.model_class.status == 'APPROVED'
                )
            ).group_by(self.model_class.employee_id).order_by(
                func.sum(self.model_class.days_requested).desc()
            ).limit(10)
            
            top_employees_result = await self.session.execute(top_employees_stmt)
            top_employees = top_employees_result.all()
            
            # Compilar reporte
            report = {
                'year': year,
                'generated_at': pendulum.now().isoformat(),
                'general_statistics': {
                    'total_vacations': general_stats.total_vacations if general_stats else 0,
                    'approved_vacations': general_stats.approved_count if general_stats else 0,
                    'pending_vacations': general_stats.pending_count if general_stats else 0,
                    'rejected_vacations': general_stats.rejected_count if general_stats else 0,
                    'total_approved_days': general_stats.total_approved_days if general_stats else 0,
                    'employees_with_vacations': general_stats.employees_with_vacations if general_stats else 0,
                    'approval_rate': round(
                        (general_stats.approved_count / general_stats.total_vacations * 100) 
                        if general_stats and general_stats.total_vacations > 0 else 0, 2
                    )
                },
                'vacation_types': [
                    {
                        'type': row.vacation_type,
                        'count': row.count,
                        'total_days': row.total_days or 0
                    }
                    for row in type_stats
                ],
                'top_employees_by_vacation_days': [
                    {
                        'employee_id': row.employee_id,
                        'total_days': row.total_days or 0,
                        'vacation_count': row.vacation_count
                    }
                    for row in top_employees
                ]
            }
            
            self._logger.debug("Reporte resumen generado exitosamente")
            
            return report
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error generando reporte: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="generate_vacation_summary_report",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado generando reporte: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado generando reporte: {e}",
                operation="generate_vacation_summary_report",
                entity_type=self.model_class.__name__,
                original_error=e
            )