# src/planificador/repositories/workload/modules/statistics_module.py

"""
Módulo de estadísticas para operaciones analíticas del repositorio Workload.

Este módulo implementa las operaciones de análisis estadístico y métricas
para cargas de trabajo, incluyendo estadísticas por empleado, proyecto y equipo.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de análisis y estadísticas
    - Performance Optimization: Uso de agregaciones SQL eficientes
    - Data Analysis: Métricas avanzadas para toma de decisiones

Uso:
    ```python
    stats_module = WorkloadStatisticsModule(session)
    employee_stats = await stats_module.get_employee_workload_statistics(employee_id)
    project_stats = await stats_module.get_project_workload_statistics(project_id)
    team_stats = await stats_module.get_team_workload_statistics(team_id)
    ```
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import select, func, and_, or_, case, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.workload import Workload
from planificador.repositories.workload.interfaces.statistics_interface import IWorkloadStatisticsOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    WorkloadRepositoryError,
    convert_sqlalchemy_error
)


class WorkloadStatisticsModule(BaseRepository[Workload], IWorkloadStatisticsOperations):
    """
    Módulo para operaciones de estadísticas del repositorio Workload.
    
    Implementa las operaciones de análisis estadístico y métricas avanzadas
    para cargas de trabajo, incluyendo estadísticas por empleado, proyecto,
    equipo y análisis de tendencias.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Workload
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de estadísticas para cargas de trabajo.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Workload)
        self._logger = self._logger.bind(component="WorkloadStatisticsModule")
        self._logger.debug("WorkloadStatisticsModule inicializado")

    async def get_employee_workload_statistics(
        self, 
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de carga de trabajo para un empleado específico.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período (opcional)
            end_date: Fecha de fin del período (opcional)
        
        Returns:
            Dict[str, Any]: Estadísticas del empleado
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el análisis
        """
        self._logger.debug(f"Obteniendo estadísticas para empleado {employee_id}")
        
        try:
            # Construir condiciones base
            conditions = [self.model_class.employee_id == employee_id]
            
            if start_date:
                conditions.append(self.model_class.workload_date >= start_date)
            if end_date:
                conditions.append(self.model_class.workload_date <= end_date)
            
            # Consulta principal de estadísticas
            stmt = select(
                func.count(self.model_class.id).label('total_workloads'),
                func.sum(self.model_class.hours).label('total_hours'),
                func.avg(self.model_class.hours).label('average_hours'),
                func.min(self.model_class.hours).label('min_hours'),
                func.max(self.model_class.hours).label('max_hours'),
                func.count(func.distinct(self.model_class.project_id)).label('unique_projects'),
                func.min(self.model_class.workload_date).label('first_workload_date'),
                func.max(self.model_class.workload_date).label('last_workload_date')
            ).where(and_(*conditions))
            
            result = await self.session.execute(stmt)
            stats_row = result.first()
            
            # Estadísticas por estado
            status_stmt = select(
                self.model_class.status,
                func.count(self.model_class.id).label('count'),
                func.sum(self.model_class.hours).label('hours')
            ).where(and_(*conditions)).group_by(self.model_class.status)
            
            status_result = await self.session.execute(status_stmt)
            status_stats = {row.status: {'count': row.count, 'hours': float(row.hours or 0)} 
                          for row in status_result}
            
            # Estadísticas por proyecto
            project_stmt = select(
                self.model_class.project_id,
                func.count(self.model_class.id).label('count'),
                func.sum(self.model_class.hours).label('hours')
            ).where(and_(*conditions)).group_by(self.model_class.project_id)
            
            project_result = await self.session.execute(project_stmt)
            project_stats = {row.project_id: {'count': row.count, 'hours': float(row.hours or 0)} 
                           for row in project_result}
            
            # Construir respuesta
            statistics = {
                'employee_id': employee_id,
                'period': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                },
                'summary': {
                    'total_workloads': stats_row.total_workloads or 0,
                    'total_hours': float(stats_row.total_hours or 0),
                    'average_hours': float(stats_row.average_hours or 0),
                    'min_hours': float(stats_row.min_hours or 0),
                    'max_hours': float(stats_row.max_hours or 0),
                    'unique_projects': stats_row.unique_projects or 0,
                    'first_workload_date': stats_row.first_workload_date.isoformat() if stats_row.first_workload_date else None,
                    'last_workload_date': stats_row.last_workload_date.isoformat() if stats_row.last_workload_date else None
                },
                'by_status': status_stats,
                'by_project': project_stats
            }
            
            self._logger.debug(f"Estadísticas obtenidas para empleado {employee_id}")
            return statistics
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener estadísticas de empleado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_workload_statistics",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de empleado: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al obtener estadísticas de empleado: {e}",
                operation="get_employee_workload_statistics",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )

    async def get_project_workload_statistics(
        self, 
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de carga de trabajo para un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del período (opcional)
            end_date: Fecha de fin del período (opcional)
        
        Returns:
            Dict[str, Any]: Estadísticas del proyecto
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el análisis
        """
        self._logger.debug(f"Obteniendo estadísticas para proyecto {project_id}")
        
        try:
            # Construir condiciones base
            conditions = [self.model_class.project_id == project_id]
            
            if start_date:
                conditions.append(self.model_class.workload_date >= start_date)
            if end_date:
                conditions.append(self.model_class.workload_date <= end_date)
            
            # Consulta principal de estadísticas
            stmt = select(
                func.count(self.model_class.id).label('total_workloads'),
                func.sum(self.model_class.hours).label('total_hours'),
                func.avg(self.model_class.hours).label('average_hours'),
                func.count(func.distinct(self.model_class.employee_id)).label('unique_employees'),
                func.min(self.model_class.workload_date).label('first_workload_date'),
                func.max(self.model_class.workload_date).label('last_workload_date')
            ).where(and_(*conditions))
            
            result = await self.session.execute(stmt)
            stats_row = result.first()
            
            # Estadísticas por empleado
            employee_stmt = select(
                self.model_class.employee_id,
                func.count(self.model_class.id).label('count'),
                func.sum(self.model_class.hours).label('hours')
            ).where(and_(*conditions)).group_by(self.model_class.employee_id)
            
            employee_result = await self.session.execute(employee_stmt)
            employee_stats = {row.employee_id: {'count': row.count, 'hours': float(row.hours or 0)} 
                            for row in employee_result}
            
            # Estadísticas por estado
            status_stmt = select(
                self.model_class.status,
                func.count(self.model_class.id).label('count'),
                func.sum(self.model_class.hours).label('hours')
            ).where(and_(*conditions)).group_by(self.model_class.status)
            
            status_result = await self.session.execute(status_stmt)
            status_stats = {row.status: {'count': row.count, 'hours': float(row.hours or 0)} 
                          for row in status_result}
            
            # Construir respuesta
            statistics = {
                'project_id': project_id,
                'period': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                },
                'summary': {
                    'total_workloads': stats_row.total_workloads or 0,
                    'total_hours': float(stats_row.total_hours or 0),
                    'average_hours': float(stats_row.average_hours or 0),
                    'unique_employees': stats_row.unique_employees or 0,
                    'first_workload_date': stats_row.first_workload_date.isoformat() if stats_row.first_workload_date else None,
                    'last_workload_date': stats_row.last_workload_date.isoformat() if stats_row.last_workload_date else None
                },
                'by_employee': employee_stats,
                'by_status': status_stats
            }
            
            self._logger.debug(f"Estadísticas obtenidas para proyecto {project_id}")
            return statistics
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener estadísticas de proyecto: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_workload_statistics",
                entity_type=self.model_class.__name__,
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de proyecto: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al obtener estadísticas de proyecto: {e}",
                operation="get_project_workload_statistics",
                entity_type=self.model_class.__name__,
                entity_id=project_id,
                original_error=e
            )

    async def get_team_workload_statistics(
        self, 
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de carga de trabajo para un equipo específico.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del período (opcional)
            end_date: Fecha de fin del período (opcional)
        
        Returns:
            Dict[str, Any]: Estadísticas del equipo
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el análisis
        """
        self._logger.debug(f"Obteniendo estadísticas para equipo {team_id}")
        
        try:
            # Nota: Asumiendo que existe una relación con empleados y equipos
            # Esta implementación puede necesitar ajustes según el modelo de datos real
            
            # Por ahora, implementamos estadísticas básicas
            # En una implementación real, se haría JOIN con tabla de empleados/equipos
            
            conditions = []
            if start_date:
                conditions.append(self.model_class.workload_date >= start_date)
            if end_date:
                conditions.append(self.model_class.workload_date <= end_date)
            
            # Consulta básica (necesitaría JOIN real con tabla de equipos)
            base_condition = and_(*conditions) if conditions else True
            
            stmt = select(
                func.count(self.model_class.id).label('total_workloads'),
                func.sum(self.model_class.hours).label('total_hours'),
                func.avg(self.model_class.hours).label('average_hours'),
                func.count(func.distinct(self.model_class.employee_id)).label('unique_employees'),
                func.count(func.distinct(self.model_class.project_id)).label('unique_projects')
            ).where(base_condition)
            
            result = await self.session.execute(stmt)
            stats_row = result.first()
            
            # Construir respuesta básica
            statistics = {
                'team_id': team_id,
                'period': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                },
                'summary': {
                    'total_workloads': stats_row.total_workloads or 0,
                    'total_hours': float(stats_row.total_hours or 0),
                    'average_hours': float(stats_row.average_hours or 0),
                    'unique_employees': stats_row.unique_employees or 0,
                    'unique_projects': stats_row.unique_projects or 0
                },
                'note': 'Estadísticas básicas - requiere implementación de relación empleado-equipo'
            }
            
            self._logger.debug(f"Estadísticas obtenidas para equipo {team_id}")
            return statistics
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener estadísticas de equipo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_workload_statistics",
                entity_type=self.model_class.__name__,
                entity_id=team_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de equipo: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al obtener estadísticas de equipo: {e}",
                operation="get_team_workload_statistics",
                entity_type=self.model_class.__name__,
                entity_id=team_id,
                original_error=e
            )

    async def get_workload_trends_analysis(
        self,
        start_date: date,
        end_date: date,
        group_by: str = 'week'
    ) -> Dict[str, Any]:
        """
        Analiza tendencias de carga de trabajo en un período específico.
        
        Args:
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
            group_by: Agrupación temporal ('day', 'week', 'month')
        
        Returns:
            Dict[str, Any]: Análisis de tendencias
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el análisis
        """
        self._logger.debug(f"Analizando tendencias de {start_date} a {end_date}, agrupado por {group_by}")
        
        try:
            # Determinar función de agrupación temporal
            if group_by == 'day':
                date_trunc = func.date(self.model_class.workload_date)
            elif group_by == 'week':
                # SQLite no tiene date_trunc, usamos strftime
                date_trunc = func.strftime('%Y-%W', self.model_class.workload_date)
            elif group_by == 'month':
                date_trunc = func.strftime('%Y-%m', self.model_class.workload_date)
            else:
                raise ValueError(f"group_by inválido: {group_by}")
            
            # Consulta de tendencias
            stmt = select(
                date_trunc.label('period'),
                func.count(self.model_class.id).label('workload_count'),
                func.sum(self.model_class.hours).label('total_hours'),
                func.avg(self.model_class.hours).label('average_hours'),
                func.count(func.distinct(self.model_class.employee_id)).label('active_employees'),
                func.count(func.distinct(self.model_class.project_id)).label('active_projects')
            ).where(
                and_(
                    self.model_class.workload_date >= start_date,
                    self.model_class.workload_date <= end_date
                )
            ).group_by(date_trunc).order_by(date_trunc)
            
            result = await self.session.execute(stmt)
            trends_data = []
            
            for row in result:
                trends_data.append({
                    'period': row.period,
                    'workload_count': row.workload_count,
                    'total_hours': float(row.total_hours or 0),
                    'average_hours': float(row.average_hours or 0),
                    'active_employees': row.active_employees,
                    'active_projects': row.active_projects
                })
            
            # Calcular métricas de tendencia
            if len(trends_data) >= 2:
                first_period = trends_data[0]
                last_period = trends_data[-1]
                
                hours_growth = ((last_period['total_hours'] - first_period['total_hours']) / 
                              first_period['total_hours'] * 100) if first_period['total_hours'] > 0 else 0
                
                workload_growth = ((last_period['workload_count'] - first_period['workload_count']) / 
                                 first_period['workload_count'] * 100) if first_period['workload_count'] > 0 else 0
            else:
                hours_growth = 0
                workload_growth = 0
            
            analysis = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'group_by': group_by
                },
                'trends': trends_data,
                'summary': {
                    'total_periods': len(trends_data),
                    'hours_growth_percentage': round(hours_growth, 2),
                    'workload_growth_percentage': round(workload_growth, 2),
                    'average_hours_per_period': round(sum(p['total_hours'] for p in trends_data) / len(trends_data), 2) if trends_data else 0,
                    'average_workloads_per_period': round(sum(p['workload_count'] for p in trends_data) / len(trends_data), 2) if trends_data else 0
                }
            }
            
            self._logger.debug("Análisis de tendencias completado")
            return analysis
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al analizar tendencias: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_workload_trends_analysis",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al analizar tendencias: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al analizar tendencias: {e}",
                operation="get_workload_trends_analysis",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_workload_distribution_analysis(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Analiza la distribución de cargas de trabajo por diferentes dimensiones.
        
        Args:
            start_date: Fecha de inicio del análisis (opcional)
            end_date: Fecha de fin del análisis (opcional)
        
        Returns:
            Dict[str, Any]: Análisis de distribución
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el análisis
        """
        self._logger.debug("Analizando distribución de cargas de trabajo")
        
        try:
            conditions = []
            if start_date:
                conditions.append(self.model_class.workload_date >= start_date)
            if end_date:
                conditions.append(self.model_class.workload_date <= end_date)
            
            base_condition = and_(*conditions) if conditions else True
            
            # Distribución por rangos de horas
            hours_distribution_stmt = select(
                case(
                    (self.model_class.hours <= 2, '0-2 horas'),
                    (self.model_class.hours <= 4, '2-4 horas'),
                    (self.model_class.hours <= 6, '4-6 horas'),
                    (self.model_class.hours <= 8, '6-8 horas'),
                    else_='8+ horas'
                ).label('hours_range'),
                func.count(self.model_class.id).label('count'),
                func.sum(self.model_class.hours).label('total_hours')
            ).where(base_condition).group_by('hours_range')
            
            hours_result = await self.session.execute(hours_distribution_stmt)
            hours_distribution = {row.hours_range: {'count': row.count, 'total_hours': float(row.total_hours or 0)} 
                                for row in hours_result}
            
            # Distribución por día de la semana
            weekday_stmt = select(
                func.strftime('%w', self.model_class.workload_date).label('weekday'),
                func.count(self.model_class.id).label('count'),
                func.sum(self.model_class.hours).label('total_hours')
            ).where(base_condition).group_by('weekday')
            
            weekday_result = await self.session.execute(weekday_stmt)
            weekday_names = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
            weekday_distribution = {}
            
            for row in weekday_result:
                day_name = weekday_names[int(row.weekday)]
                weekday_distribution[day_name] = {
                    'count': row.count, 
                    'total_hours': float(row.total_hours or 0)
                }
            
            # Distribución por estado
            status_stmt = select(
                self.model_class.status,
                func.count(self.model_class.id).label('count'),
                func.sum(self.model_class.hours).label('total_hours')
            ).where(base_condition).group_by(self.model_class.status)
            
            status_result = await self.session.execute(status_stmt)
            status_distribution = {row.status: {'count': row.count, 'total_hours': float(row.total_hours or 0)} 
                                 for row in status_result}
            
            analysis = {
                'period': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                },
                'distribution': {
                    'by_hours_range': hours_distribution,
                    'by_weekday': weekday_distribution,
                    'by_status': status_distribution
                }
            }
            
            self._logger.debug("Análisis de distribución completado")
            return analysis
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al analizar distribución: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_workload_distribution_analysis",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al analizar distribución: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al analizar distribución: {e}",
                operation="get_workload_distribution_analysis",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_productivity_metrics(
        self,
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calcula métricas de productividad para empleados o proyectos.
        
        Args:
            employee_id: ID del empleado (opcional)
            project_id: ID del proyecto (opcional)
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
        
        Returns:
            Dict[str, Any]: Métricas de productividad
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el cálculo
        """
        self._logger.debug("Calculando métricas de productividad")
        
        try:
            conditions = []
            
            if employee_id:
                conditions.append(self.model_class.employee_id == employee_id)
            if project_id:
                conditions.append(self.model_class.project_id == project_id)
            if start_date:
                conditions.append(self.model_class.workload_date >= start_date)
            if end_date:
                conditions.append(self.model_class.workload_date <= end_date)
            
            base_condition = and_(*conditions) if conditions else True
            
            # Métricas básicas
            basic_metrics_stmt = select(
                func.count(self.model_class.id).label('total_workloads'),
                func.sum(self.model_class.hours).label('total_hours'),
                func.avg(self.model_class.hours).label('average_hours_per_workload'),
                func.count(case((self.model_class.status == 'completed', 1))).label('completed_workloads'),
                func.count(case((self.model_class.status == 'in_progress', 1))).label('in_progress_workloads'),
                func.count(case((self.model_class.status == 'pending', 1))).label('pending_workloads')
            ).where(base_condition)
            
            result = await self.session.execute(basic_metrics_stmt)
            metrics_row = result.first()
            
            # Calcular métricas derivadas
            total_workloads = metrics_row.total_workloads or 0
            completed_workloads = metrics_row.completed_workloads or 0
            
            completion_rate = (completed_workloads / total_workloads * 100) if total_workloads > 0 else 0
            
            # Métricas por día (si hay rango de fechas)
            daily_metrics = {}
            if start_date and end_date:
                days_in_period = (end_date - start_date).days + 1
                total_hours = float(metrics_row.total_hours or 0)
                
                daily_metrics = {
                    'average_hours_per_day': total_hours / days_in_period if days_in_period > 0 else 0,
                    'average_workloads_per_day': total_workloads / days_in_period if days_in_period > 0 else 0,
                    'days_in_period': days_in_period
                }
            
            metrics = {
                'filters': {
                    'employee_id': employee_id,
                    'project_id': project_id,
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                },
                'basic_metrics': {
                    'total_workloads': total_workloads,
                    'total_hours': float(metrics_row.total_hours or 0),
                    'average_hours_per_workload': float(metrics_row.average_hours_per_workload or 0),
                    'completed_workloads': completed_workloads,
                    'in_progress_workloads': metrics_row.in_progress_workloads or 0,
                    'pending_workloads': metrics_row.pending_workloads or 0
                },
                'derived_metrics': {
                    'completion_rate_percentage': round(completion_rate, 2),
                    'efficiency_score': round(completion_rate * 0.7 + (float(metrics_row.average_hours_per_workload or 0) / 8 * 30), 2)
                },
                'daily_metrics': daily_metrics
            }
            
            self._logger.debug("Métricas de productividad calculadas")
            return metrics
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al calcular métricas de productividad: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_productivity_metrics",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al calcular métricas de productividad: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al calcular métricas de productividad: {e}",
                operation="get_productivity_metrics",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    # Métodos alias para compatibilidad con la interfaz
    async def analyze_employee_workload(
        self, 
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Alias para get_employee_workload_statistics."""
        return await self.get_employee_workload_statistics(employee_id, start_date, end_date)

    async def analyze_project_workload(
        self, 
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Alias para get_project_workload_statistics."""
        return await self.get_project_workload_statistics(project_id, start_date, end_date)

    async def analyze_team_workload(
        self, 
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Alias para get_team_workload_statistics."""
        return await self.get_team_workload_statistics(team_id, start_date, end_date)