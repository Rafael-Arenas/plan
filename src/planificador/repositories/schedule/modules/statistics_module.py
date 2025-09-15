# src/planificador/repositories/schedule/modules/statistics_module.py

from typing import Dict, Any, List, Optional, Tuple
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import func, and_, or_, case, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import select
from loguru import logger
import pendulum

from ....models.schedule import Schedule
from ....models.employee import Employee
from ....models.project import Project
from ....models.team import Team
from ....exceptions.repository_exceptions import RepositoryError
from ....exceptions.database_exceptions import convert_sqlalchemy_error
from ..interfaces.statistics_interface import IScheduleStatisticsOperations


class ScheduleStatisticsModule(IScheduleStatisticsOperations):
    """
    Módulo para operaciones de estadísticas del repositorio Schedule.
    
    Proporciona métodos para generar estadísticas, métricas y reportes
    relacionados con horarios de trabajo.
    """
    
    def __init__(self, session: AsyncSession, model_class: type = Schedule):
        """
        Inicializa el módulo de estadísticas.
        
        Args:
            session: Sesión de base de datos asíncrona
            model_class: Clase del modelo Schedule
        """
        self.session = session
        self.model_class = model_class
        self._logger = logger.bind(module="ScheduleStatisticsModule")
    
    # ==========================================
    # ESTADÍSTICAS DE HORAS TRABAJADAS
    # ==========================================
    
    async def get_total_hours_by_employee(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Decimal:
        """
        Calcula el total de horas trabajadas por un empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período (opcional)
            end_date: Fecha de fin del período (opcional)
            
        Returns:
            Total de horas trabajadas
        """
        try:
            query = select(func.sum(self.model_class.hours_worked)).where(
                self.model_class.employee_id == employee_id
            )
            
            if start_date:
                query = query.where(self.model_class.date >= start_date)
            if end_date:
                query = query.where(self.model_class.date <= end_date)
            
            result = await self.session.execute(query)
            total_hours = result.scalar() or Decimal('0')
            
            self._logger.debug(
                f"Total horas empleado {employee_id}: {total_hours}"
            )
            return total_hours
            
        except Exception as e:
            self._logger.error(
                f"Error calculando horas totales empleado {employee_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error calculando horas totales: {e}",
                operation="get_total_hours_by_employee",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )
    
    async def get_total_hours_by_project(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Decimal:
        """
        Calcula el total de horas trabajadas en un proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del período (opcional)
            end_date: Fecha de fin del período (opcional)
            
        Returns:
            Total de horas trabajadas en el proyecto
        """
        try:
            query = select(func.sum(self.model_class.hours_worked)).where(
                self.model_class.project_id == project_id
            )
            
            if start_date:
                query = query.where(self.model_class.date >= start_date)
            if end_date:
                query = query.where(self.model_class.date <= end_date)
            
            result = await self.session.execute(query)
            total_hours = result.scalar() or Decimal('0')
            
            self._logger.debug(
                f"Total horas proyecto {project_id}: {total_hours}"
            )
            return total_hours
            
        except Exception as e:
            self._logger.error(
                f"Error calculando horas totales proyecto {project_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error calculando horas totales proyecto: {e}",
                operation="get_total_hours_by_project",
                entity_type=self.model_class.__name__,
                entity_id=project_id,
                original_error=e
            )
    
    async def get_hours_summary_by_period(
        self,
        start_date: date,
        end_date: date,
        group_by: str = "day"  # day, week, month
    ) -> List[Dict[str, Any]]:
        """
        Obtiene resumen de horas trabajadas agrupadas por período.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            group_by: Tipo de agrupación (day, week, month)
            
        Returns:
            Lista de resúmenes por período
        """
        try:
            # Configurar agrupación según el tipo
            if group_by == "day":
                date_part = self.model_class.date
                date_format = "%Y-%m-%d"
            elif group_by == "week":
                date_part = func.date_trunc('week', self.model_class.date)
                date_format = "%Y-W%U"
            elif group_by == "month":
                date_part = func.date_trunc('month', self.model_class.date)
                date_format = "%Y-%m"
            else:
                raise ValueError(f"Tipo de agrupación no válido: {group_by}")
            
            query = select(
                date_part.label('period'),
                func.sum(self.model_class.hours_worked).label('total_hours'),
                func.count(self.model_class.id).label('total_schedules'),
                func.count(func.distinct(self.model_class.employee_id)).label('unique_employees')
            ).where(
                and_(
                    self.model_class.date >= start_date,
                    self.model_class.date <= end_date
                )
            ).group_by(date_part).order_by(date_part)
            
            result = await self.session.execute(query)
            rows = result.fetchall()
            
            summary = []
            for row in rows:
                period_date = row.period
                if isinstance(period_date, date):
                    period_str = period_date.strftime(date_format)
                else:
                    period_str = str(period_date)
                
                summary.append({
                    'period': period_str,
                    'total_hours': float(row.total_hours or 0),
                    'total_schedules': row.total_schedules,
                    'unique_employees': row.unique_employees
                })
            
            self._logger.debug(
                f"Resumen horas por {group_by}: {len(summary)} períodos"
            )
            return summary
            
        except Exception as e:
            self._logger.error(
                f"Error generando resumen por período: {e}"
            )
            raise RepositoryError(
                message=f"Error generando resumen por período: {e}",
                operation="get_hours_summary_by_period",
                entity_type=self.model_class.__name__,
                original_error=e
            )
    
    # ==========================================
    # MÉTRICAS DE PRODUCTIVIDAD
    # ==========================================
    
    async def get_productivity_metrics_by_employee(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Calcula métricas de productividad para un empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Dict con métricas de productividad
        """
        try:
            # Consulta principal para métricas
            query = select(
                func.sum(self.model_class.hours_worked).label('total_hours'),
                func.count(self.model_class.id).label('total_days'),
                func.avg(self.model_class.hours_worked).label('avg_hours_per_day'),
                func.min(self.model_class.hours_worked).label('min_hours'),
                func.max(self.model_class.hours_worked).label('max_hours'),
                func.count(func.distinct(self.model_class.project_id)).label('unique_projects')
            ).where(
                and_(
                    self.model_class.employee_id == employee_id,
                    self.model_class.date >= start_date,
                    self.model_class.date <= end_date
                )
            )
            
            result = await self.session.execute(query)
            row = result.fetchone()
            
            if not row or row.total_hours is None:
                return {
                    'employee_id': employee_id,
                    'period_start': start_date.isoformat(),
                    'period_end': end_date.isoformat(),
                    'total_hours': 0.0,
                    'total_days': 0,
                    'avg_hours_per_day': 0.0,
                    'min_hours': 0.0,
                    'max_hours': 0.0,
                    'unique_projects': 0,
                    'productivity_score': 0.0
                }
            
            # Calcular días laborables en el período
            period_days = (end_date - start_date).days + 1
            work_days = row.total_days
            
            # Calcular score de productividad (0-100)
            # Basado en horas promedio y consistencia
            avg_hours = float(row.avg_hours_per_day or 0)
            consistency = 1.0 - (float(row.max_hours or 0) - float(row.min_hours or 0)) / max(avg_hours, 1.0)
            productivity_score = min(100.0, (avg_hours / 8.0) * 50 + consistency * 50)
            
            metrics = {
                'employee_id': employee_id,
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'total_hours': float(row.total_hours),
                'total_days': work_days,
                'avg_hours_per_day': avg_hours,
                'min_hours': float(row.min_hours or 0),
                'max_hours': float(row.max_hours or 0),
                'unique_projects': row.unique_projects,
                'productivity_score': round(productivity_score, 2),
                'work_days_ratio': round(work_days / period_days, 2) if period_days > 0 else 0.0
            }
            
            self._logger.debug(
                f"Métricas productividad empleado {employee_id}: {metrics['productivity_score']}"
            )
            return metrics
            
        except Exception as e:
            self._logger.error(
                f"Error calculando métricas productividad empleado {employee_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error calculando métricas productividad: {e}",
                operation="get_productivity_metrics_by_employee",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )
    
    async def get_team_productivity_comparison(
        self,
        team_ids: List[int],
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Compara métricas de productividad entre equipos.
        
        Args:
            team_ids: Lista de IDs de equipos
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Lista de métricas por equipo
        """
        try:
            team_metrics = []
            
            for team_id in team_ids:
                # Consulta para métricas del equipo
                query = select(
                    func.sum(self.model_class.hours_worked).label('total_hours'),
                    func.count(self.model_class.id).label('total_schedules'),
                    func.avg(self.model_class.hours_worked).label('avg_hours'),
                    func.count(func.distinct(self.model_class.employee_id)).label('unique_employees'),
                    func.count(func.distinct(self.model_class.project_id)).label('unique_projects')
                ).where(
                    and_(
                        self.model_class.team_id == team_id,
                        self.model_class.date >= start_date,
                        self.model_class.date <= end_date
                    )
                )
                
                result = await self.session.execute(query)
                row = result.fetchone()
                
                if row and row.total_hours:
                    team_metrics.append({
                        'team_id': team_id,
                        'total_hours': float(row.total_hours),
                        'total_schedules': row.total_schedules,
                        'avg_hours_per_schedule': float(row.avg_hours or 0),
                        'unique_employees': row.unique_employees,
                        'unique_projects': row.unique_projects,
                        'hours_per_employee': float(row.total_hours) / max(row.unique_employees, 1)
                    })
                else:
                    team_metrics.append({
                        'team_id': team_id,
                        'total_hours': 0.0,
                        'total_schedules': 0,
                        'avg_hours_per_schedule': 0.0,
                        'unique_employees': 0,
                        'unique_projects': 0,
                        'hours_per_employee': 0.0
                    })
            
            # Ordenar por total de horas descendente
            team_metrics.sort(key=lambda x: x['total_hours'], reverse=True)
            
            self._logger.debug(
                f"Comparación productividad {len(team_metrics)} equipos"
            )
            return team_metrics
            
        except Exception as e:
            self._logger.error(
                f"Error comparando productividad equipos: {e}"
            )
            raise RepositoryError(
                message=f"Error comparando productividad equipos: {e}",
                operation="get_team_productivity_comparison",
                entity_type=self.model_class.__name__,
                original_error=e
            )
    
    # ==========================================
    # REPORTES DE UTILIZACIÓN
    # ==========================================
    
    async def get_resource_utilization_report(
        self,
        start_date: date,
        end_date: date,
        include_employees: bool = True,
        include_projects: bool = True
    ) -> Dict[str, Any]:
        """
        Genera reporte de utilización de recursos.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            include_employees: Incluir datos de empleados
            include_projects: Incluir datos de proyectos
            
        Returns:
            Dict con reporte de utilización
        """
        try:
            report = {
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'summary': {},
                'employees': [] if include_employees else None,
                'projects': [] if include_projects else None
            }
            
            # Resumen general
            summary_query = select(
                func.sum(self.model_class.hours_worked).label('total_hours'),
                func.count(self.model_class.id).label('total_schedules'),
                func.count(func.distinct(self.model_class.employee_id)).label('active_employees'),
                func.count(func.distinct(self.model_class.project_id)).label('active_projects')
            ).where(
                and_(
                    self.model_class.date >= start_date,
                    self.model_class.date <= end_date
                )
            )
            
            result = await self.session.execute(summary_query)
            summary_row = result.fetchone()
            
            if summary_row:
                report['summary'] = {
                    'total_hours': float(summary_row.total_hours or 0),
                    'total_schedules': summary_row.total_schedules,
                    'active_employees': summary_row.active_employees,
                    'active_projects': summary_row.active_projects,
                    'avg_hours_per_schedule': float(summary_row.total_hours or 0) / max(summary_row.total_schedules, 1)
                }
            
            # Datos por empleado
            if include_employees:
                employee_query = select(
                    self.model_class.employee_id,
                    func.sum(self.model_class.hours_worked).label('total_hours'),
                    func.count(self.model_class.id).label('total_schedules'),
                    func.avg(self.model_class.hours_worked).label('avg_hours')
                ).where(
                    and_(
                        self.model_class.date >= start_date,
                        self.model_class.date <= end_date
                    )
                ).group_by(self.model_class.employee_id).order_by(
                    func.sum(self.model_class.hours_worked).desc()
                )
                
                result = await self.session.execute(employee_query)
                employee_rows = result.fetchall()
                
                report['employees'] = [
                    {
                        'employee_id': row.employee_id,
                        'total_hours': float(row.total_hours),
                        'total_schedules': row.total_schedules,
                        'avg_hours_per_schedule': float(row.avg_hours or 0)
                    }
                    for row in employee_rows
                ]
            
            # Datos por proyecto
            if include_projects:
                project_query = select(
                    self.model_class.project_id,
                    func.sum(self.model_class.hours_worked).label('total_hours'),
                    func.count(self.model_class.id).label('total_schedules'),
                    func.count(func.distinct(self.model_class.employee_id)).label('unique_employees')
                ).where(
                    and_(
                        self.model_class.date >= start_date,
                        self.model_class.date <= end_date,
                        self.model_class.project_id.isnot(None)
                    )
                ).group_by(self.model_class.project_id).order_by(
                    func.sum(self.model_class.hours_worked).desc()
                )
                
                result = await self.session.execute(project_query)
                project_rows = result.fetchall()
                
                report['projects'] = [
                    {
                        'project_id': row.project_id,
                        'total_hours': float(row.total_hours),
                        'total_schedules': row.total_schedules,
                        'unique_employees': row.unique_employees
                    }
                    for row in project_rows
                ]
            
            self._logger.debug(
                f"Reporte utilización generado: {report['summary']['total_hours']} horas"
            )
            return report
            
        except Exception as e:
            self._logger.error(
                f"Error generando reporte utilización: {e}"
            )
            raise RepositoryError(
                message=f"Error generando reporte utilización: {e}",
                operation="get_resource_utilization_report",
                entity_type=self.model_class.__name__,
                original_error=e
            )
    
    # ==========================================
    # ANÁLISIS DE TENDENCIAS
    # ==========================================
    
    async def get_schedule_trends_analysis(
        self,
        start_date: date,
        end_date: date,
        granularity: str = "week"  # day, week, month
    ) -> Dict[str, Any]:
        """
        Analiza tendencias en los horarios de trabajo.
        
        Args:
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
            granularity: Granularidad del análisis (day, week, month)
            
        Returns:
            Dict con análisis de tendencias
        """
        try:
            # Obtener datos históricos agrupados
            historical_data = await self.get_hours_summary_by_period(
                start_date, end_date, granularity
            )
            
            if len(historical_data) < 2:
                return {
                    'period_start': start_date.isoformat(),
                    'period_end': end_date.isoformat(),
                    'granularity': granularity,
                    'trend_analysis': 'Datos insuficientes para análisis',
                    'growth_rate': 0.0,
                    'periods_analyzed': len(historical_data)
                }
            
            # Calcular tendencias
            total_hours_trend = []
            schedules_trend = []
            
            for period_data in historical_data:
                total_hours_trend.append(period_data['total_hours'])
                schedules_trend.append(period_data['total_schedules'])
            
            # Calcular tasa de crecimiento
            first_period = total_hours_trend[0]
            last_period = total_hours_trend[-1]
            
            if first_period > 0:
                growth_rate = ((last_period - first_period) / first_period) * 100
            else:
                growth_rate = 0.0
            
            # Determinar tendencia
            if growth_rate > 5:
                trend_direction = "Crecimiento"
            elif growth_rate < -5:
                trend_direction = "Decrecimiento"
            else:
                trend_direction = "Estable"
            
            # Calcular promedios
            avg_hours = sum(total_hours_trend) / len(total_hours_trend)
            avg_schedules = sum(schedules_trend) / len(schedules_trend)
            
            analysis = {
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'granularity': granularity,
                'periods_analyzed': len(historical_data),
                'trend_direction': trend_direction,
                'growth_rate': round(growth_rate, 2),
                'avg_hours_per_period': round(avg_hours, 2),
                'avg_schedules_per_period': round(avg_schedules, 2),
                'peak_hours_period': max(historical_data, key=lambda x: x['total_hours'])['period'],
                'peak_hours_value': max(total_hours_trend),
                'min_hours_period': min(historical_data, key=lambda x: x['total_hours'])['period'],
                'min_hours_value': min(total_hours_trend),
                'historical_data': historical_data
            }
            
            self._logger.debug(
                f"Análisis tendencias: {trend_direction}, crecimiento {growth_rate}%"
            )
            return analysis
            
        except Exception as e:
            self._logger.error(
                f"Error analizando tendencias: {e}"
            )
            raise RepositoryError(
                message=f"Error analizando tendencias: {e}",
                operation="get_schedule_trends_analysis",
                entity_type=self.model_class.__name__,
                original_error=e
            )