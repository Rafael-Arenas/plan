# src/planificador/database/repositories/project/project_statistics.py

from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from ....models.project import Project, ProjectStatus, ProjectPriority
from ....models.project_assignment import ProjectAssignment
from ....models.workload import Workload
from ....models.employee import Employee
from ....utils.date_utils import get_current_time
from ....exceptions.repository.base_repository_exceptions import convert_sqlalchemy_error
from ....exceptions.repository.project_repository_exceptions import create_project_statistics_error
from .project_query_builder import ProjectQueryBuilder


class ProjectStatistics:
    """
    Calculador de estadísticas para proyectos.
    
    Centraliza todos los cálculos estadísticos relacionados con proyectos,
    incluyendo métricas de rendimiento, análisis temporal y reportes.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.query_builder = ProjectQueryBuilder(session)
        self._logger = logging.getLogger(__name__)
    
    # ==========================================
    # ESTADÍSTICAS GENERALES
    # ==========================================
    
    async def get_project_summary_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de todos los proyectos.
        
        Returns:
            Diccionario con estadísticas generales
        """
        try:
            # Estadísticas por estado
            status_query = select(
                Project.status,
                func.count(Project.id).label('count')
            ).group_by(Project.status)
            
            status_result = await self.session.execute(status_query)
            status_stats = {row.status.value: row.count for row in status_result}
            
            # Estadísticas por prioridad
            priority_query = select(
                Project.priority,
                func.count(Project.id).label('count')
            ).group_by(Project.priority)
            
            priority_result = await self.session.execute(priority_query)
            priority_stats = {row.priority.value: row.count for row in priority_result}
            
            # Estadísticas generales
            general_query = select(
                func.count(Project.id).label('total_projects'),
                func.count(Project.id.filter(Project.is_archived == False)).label('active_projects'),
                func.count(Project.id.filter(Project.is_archived == True)).label('archived_projects'),
                func.avg(Project.budget).label('avg_budget'),
                func.sum(Project.budget).label('total_budget')
            )
            
            general_result = await self.session.execute(general_query)
            general_stats = general_result.first()
            
            return {
                'general': {
                    'total_projects': general_stats.total_projects or 0,
                    'active_projects': general_stats.active_projects or 0,
                    'archived_projects': general_stats.archived_projects or 0,
                    'avg_budget': float(general_stats.avg_budget or 0),
                    'total_budget': float(general_stats.total_budget or 0)
                },
                'by_status': status_stats,
                'by_priority': priority_stats
            }
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos obteniendo estadísticas generales de proyectos: {e}",
                extra={"operation": "get_project_summary_stats"}
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_summary_stats",
                entity_type="Project"
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo estadísticas generales de proyectos: {e}",
                extra={"operation": "get_project_summary_stats", "error_type": type(e).__name__}
            )
            raise create_project_statistics_error(
                statistic_type="summary_stats",
                parameters={},
                reason=f"Error inesperado: {str(e)}"
            )

    async def get_overdue_projects_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de proyectos atrasados.
        
        Returns:
            Diccionario con estadísticas de proyectos atrasados
        """
        try:
            current_date = get_current_time().date()
            
            # Proyectos atrasados por severidad
            overdue_query = select(
                case(
                    (Project.end_date < current_date - timedelta(days=30), 'critical'),
                    (Project.end_date < current_date - timedelta(days=7), 'high'),
                    else_='medium'
                ).label('severity'),
                func.count(Project.id).label('count')
            ).where(
                and_(
                    Project.end_date < current_date,
                    Project.status.in_([
                        ProjectStatus.PLANNED,
                        ProjectStatus.IN_PROGRESS,
                        ProjectStatus.ON_HOLD
                    ])
                )
            ).group_by('severity')
            
            overdue_result = await self.session.execute(overdue_query)
            overdue_stats = {row.severity: row.count for row in overdue_result}
            
            # Total de proyectos atrasados
            total_overdue_query = select(func.count(Project.id)).where(
                and_(
                    Project.end_date < current_date,
                    Project.status.in_([
                        ProjectStatus.PLANNED,
                        ProjectStatus.IN_PROGRESS,
                        ProjectStatus.ON_HOLD
                    ])
                )
            )
            total_overdue_result = await self.session.execute(total_overdue_query)
            total_overdue = total_overdue_result.scalar() or 0
            
            return {
                'total_overdue': total_overdue,
                'by_severity': overdue_stats,
                'reference_date': current_date.isoformat()
            }
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener estadísticas de proyectos atrasados: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_overdue_projects_stats",
                entity_type="Project"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de proyectos atrasados: {e}")
            raise create_project_statistics_error(
                message=f"Error inesperado al obtener estadísticas de proyectos atrasados: {e}",
                operation="get_overdue_projects_stats",
                original_error=e
            )
    
    # ==========================================
    # ESTADÍSTICAS ESPECÍFICAS DE PROYECTO
    # ==========================================
    
    async def get_project_performance_stats(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de rendimiento de un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Diccionario con estadísticas de rendimiento
        """
        try:
            # Estadísticas de workload
            workload_query = select(
                func.count(Workload.id).label('total_records'),
                func.sum(Workload.planned_hours).label('total_planned_hours'),
                func.sum(Workload.actual_hours).label('total_actual_hours'),
                func.avg(Workload.planned_hours).label('avg_planned_hours'),
                func.avg(Workload.actual_hours).label('avg_actual_hours')
            ).where(Workload.project_id == project_id)
            
            workload_result = await self.session.execute(workload_query)
            workload_stats = workload_result.first()
            
            # Estadísticas de asignaciones
            assignment_query = select(
                func.count(ProjectAssignment.id).label('total_assignments'),
                func.count(
                    ProjectAssignment.id.filter(ProjectAssignment.is_active == True)
                ).label('active_assignments'),
                func.sum(ProjectAssignment.allocated_hours_per_day).label('total_allocated_hours')
            ).where(ProjectAssignment.project_id == project_id)
            
            assignment_result = await self.session.execute(assignment_query)
            assignment_stats = assignment_result.first()
            
            # Calcular métricas derivadas
            total_planned = float(workload_stats.total_planned_hours or 0)
            total_actual = float(workload_stats.total_actual_hours or 0)
            
            efficiency_rate = 0.0
            if total_planned > 0:
                efficiency_rate = (total_actual / total_planned) * 100
            
            utilization_rate = 0.0
            total_allocated = float(assignment_stats.total_allocated_hours or 0)
            if total_allocated > 0:
                utilization_rate = (total_actual / total_allocated) * 100
            
            return {
                'workload': {
                    'total_records': workload_stats.total_records or 0,
                    'total_planned_hours': total_planned,
                    'total_actual_hours': total_actual,
                    'avg_planned_hours': float(workload_stats.avg_planned_hours or 0),
                    'avg_actual_hours': float(workload_stats.avg_actual_hours or 0)
                },
                'assignments': {
                    'total_assignments': assignment_stats.total_assignments or 0,
                    'active_assignments': assignment_stats.active_assignments or 0,
                    'total_allocated_hours': total_allocated
                },
                'performance': {
                    'efficiency_rate': round(efficiency_rate, 2),
                    'utilization_rate': round(utilization_rate, 2)
                }
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener estadísticas de rendimiento del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_performance_stats",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de rendimiento del proyecto {project_id}: {e}")
            raise create_project_statistics_error(
                message=f"Error inesperado al obtener estadísticas de rendimiento del proyecto {project_id}: {e}",
                operation="get_project_performance_stats",
                project_id=project_id,
                original_error=e
            )
            
    async def get_project_timeline_stats(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de línea de tiempo de un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Diccionario con estadísticas de línea de tiempo
        """
        try:
            # Obtener el proyecto
            project_query = select(Project).where(Project.id == project_id)
            project_result = await self.session.execute(project_query)
            project = project_result.scalar_one_or_none()
            
            if not project:
                return {}
            
            current_date = get_current_time().date()
            
            # Calcular duración planificada
            planned_duration = (project.end_date - project.start_date).days
            
            # Calcular progreso temporal
            if current_date < project.start_date:
                progress_percentage = 0.0
                days_elapsed = 0
                days_remaining = (project.start_date - current_date).days
            elif current_date > project.end_date:
                progress_percentage = 100.0
                days_elapsed = (current_date - project.start_date).days
                days_remaining = 0
            else:
                days_elapsed = (current_date - project.start_date).days
                progress_percentage = (days_elapsed / planned_duration) * 100 if planned_duration > 0 else 0
                days_remaining = (project.end_date - current_date).days
            
            # Determinar estado del cronograma
            schedule_status = 'on_time'
            if project.status == ProjectStatus.COMPLETED:
                schedule_status = 'completed'
            elif current_date > project.end_date and project.status != ProjectStatus.COMPLETED:
                schedule_status = 'overdue'
            elif days_remaining <= 7 and project.status == ProjectStatus.IN_PROGRESS:
                schedule_status = 'at_risk'
            
            return {
                'timeline': {
                    'start_date': project.start_date.isoformat(),
                    'end_date': project.end_date.isoformat(),
                    'planned_duration_days': planned_duration,
                    'days_elapsed': days_elapsed,
                    'days_remaining': days_remaining,
                    'progress_percentage': round(progress_percentage, 2)
                },
                'schedule': {
                    'status': schedule_status,
                    'is_overdue': current_date > project.end_date and project.status != ProjectStatus.COMPLETED,
                    'is_at_risk': days_remaining <= 7 and project.status == ProjectStatus.IN_PROGRESS
                }
            }
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener estadísticas de cronograma del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_timeline_stats",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de cronograma del proyecto {project_id}: {e}")
            raise create_project_statistics_error(
                message=f"Error inesperado al obtener estadísticas de cronograma del proyecto: {e}",
                operation="get_project_timeline_stats",
                project_id=project_id,
                original_error=e
            )

    async def get_project_workload_stats(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de carga de trabajo para un proyecto en un período.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del período (opcional)
            end_date: Fecha de fin del período (opcional)
            
        Returns:
            Diccionario con estadísticas de carga de trabajo
        """
        try:
            # Construir consulta base
            query = select(
                func.count(Workload.id).label('total_records'),
                func.sum(Workload.planned_hours).label('total_planned_hours'),
                func.sum(Workload.actual_hours).label('total_actual_hours'),
                func.avg(Workload.planned_hours).label('average_planned_hours'),
                func.avg(Workload.actual_hours).label('average_actual_hours')
            ).where(Workload.project_id == project_id)
            
            # Aplicar filtros de fecha si se proporcionan
            if start_date:
                query = query.where(Workload.date >= start_date)
            if end_date:
                query = query.where(Workload.date <= end_date)
            
            result = await self.session.execute(query)
            stats = result.first()
            
            # Calcular métricas derivadas
            total_planned = float(stats.total_planned_hours or 0)
            total_actual = float(stats.total_actual_hours or 0)
            
            efficiency_rate = 0.0
            if total_planned > 0:
                efficiency_rate = (total_actual / total_planned) * 100
            
            average_utilization = 0.0
            if stats.average_planned_hours and stats.average_planned_hours > 0:
                average_utilization = (float(stats.average_actual_hours or 0) / float(stats.average_planned_hours)) * 100
            
            return {
                'total_records': stats.total_records or 0,
                'total_planned_hours': total_planned,
                'total_actual_hours': total_actual,
                'average_planned_hours': float(stats.average_planned_hours or 0),
                'average_actual_hours': float(stats.average_actual_hours or 0),
                'efficiency_rate': round(efficiency_rate, 2),
                'average_utilization': round(average_utilization, 2),
                'period': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                }
            }
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener estadísticas de carga de trabajo del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_workload_stats",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de carga de trabajo del proyecto {project_id}: {e}")
            raise create_project_statistics_error(
                message=f"Error inesperado al obtener estadísticas de carga de trabajo del proyecto {project_id}: {e}",
                operation="get_project_workload_stats",
                project_id=project_id,
                original_error=e
            )

    # ==========================================
    # ESTADÍSTICAS TEMPORALES Y POR CLIENTE
    # ==========================================
    
    async def get_monthly_project_stats(self, year: int, month: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de proyectos para un mes específico.
        
        Args:
            year: Año
            month: Mes
            
        Returns:
            Diccionario con estadísticas mensuales
        """
        try:
            from calendar import monthrange
            
            # Calcular fechas del mes
            start_date = date(year, month, 1)
            _, last_day = monthrange(year, month)
            end_date = date(year, month, last_day)
            
            # Proyectos que inician en el mes
            starting_query = select(func.count(Project.id)).where(
                and_(
                    Project.start_date >= start_date,
                    Project.start_date <= end_date
                )
            )
            starting_result = await self.session.execute(starting_query)
            projects_starting = starting_result.scalar() or 0
            
            # Proyectos que terminan en el mes
            ending_query = select(func.count(Project.id)).where(
                and_(
                    Project.end_date >= start_date,
                    Project.end_date <= end_date
                )
            )
            ending_result = await self.session.execute(ending_query)
            projects_ending = ending_result.scalar() or 0
            
            # Proyectos activos durante el mes
            active_query = select(func.count(Project.id)).where(
                and_(
                    Project.start_date <= end_date,
                    Project.end_date >= start_date,
                    Project.status.in_([ProjectStatus.PLANNED, ProjectStatus.IN_PROGRESS])
                )
            )
            active_result = await self.session.execute(active_query)
            projects_active = active_result.scalar() or 0
            
            # Workload del mes
            workload_query = select(
                func.sum(Workload.planned_hours).label('total_planned'),
                func.sum(Workload.actual_hours).label('total_actual'),
                func.count(Workload.id).label('total_records')
            ).where(
                and_(
                    Workload.date >= start_date,
                    Workload.date <= end_date
                )
            )
            workload_result = await self.session.execute(workload_query)
            workload_stats = workload_result.first()
        
            return {
                'period': {
                    'year': year,
                    'month': month,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'projects': {
                    'starting': projects_starting,
                    'ending': projects_ending,
                    'active': projects_active
                },
                'workload': {
                    'total_planned_hours': float(workload_stats.total_planned or 0),
                    'total_actual_hours': float(workload_stats.total_actual or 0),
                    'total_records': workload_stats.total_records or 0
                }
            }
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener estadísticas mensuales de proyectos para {year}-{month}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_monthly_project_stats",
                entity_type="Project"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas mensuales de proyectos para {year}-{month}: {e}")
            raise create_project_statistics_error(
                message=f"Error inesperado al obtener estadísticas mensuales de proyectos: {e}",
                operation="get_monthly_project_stats",
                original_error=e
            )
    
    async def get_client_project_stats(self, client_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de proyectos para un cliente específico.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con estadísticas del cliente
        """
        try:
            # Estadísticas generales por cliente
            general_query = select(
                func.count(Project.id).label('total_projects'),
                func.count(
                    Project.id.filter(Project.status == ProjectStatus.COMPLETED)
                ).label('completed_projects'),
                func.count(
                    Project.id.filter(Project.status == ProjectStatus.IN_PROGRESS)
                ).label('active_projects'),
                func.sum(Project.budget).label('total_budget'),
                func.avg(Project.budget).label('avg_budget')
            ).where(Project.client_id == client_id)
            
            general_result = await self.session.execute(general_query)
            general_stats = general_result.first()
            
            # Estadísticas por estado
            status_query = select(
                Project.status,
                func.count(Project.id).label('count')
            ).where(Project.client_id == client_id).group_by(Project.status)
            
            status_result = await self.session.execute(status_query)
            status_stats = {row.status.value: row.count for row in status_result}
            
            # Estadísticas de workload del cliente
            workload_query = select(
                func.sum(Workload.planned_hours).label('total_planned'),
                func.sum(Workload.actual_hours).label('total_actual')
            ).join(
                Project, Workload.project_id == Project.id
            ).where(Project.client_id == client_id)
            
            workload_result = await self.session.execute(workload_query)
            workload_stats = workload_result.first()
            
            return {
                'general': {
                    'total_projects': general_stats.total_projects or 0,
                    'completed_projects': general_stats.completed_projects or 0,
                    'active_projects': general_stats.active_projects or 0,
                    'total_budget': float(general_stats.total_budget or 0),
                    'avg_budget': float(general_stats.avg_budget or 0)
                },
                'by_status': status_stats,
                'workload': {
                    'total_planned_hours': float(workload_stats.total_planned or 0),
                    'total_actual_hours': float(workload_stats.total_actual or 0)
                }
            }
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener estadísticas de proyectos del cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_project_stats",
                entity_type="Project",
                entity_id=client_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de proyectos del cliente {client_id}: {e}")
            raise create_project_statistics_error(
                message=f"Error inesperado al obtener estadísticas de proyectos del cliente: {e}",
                operation="get_client_project_stats",
                client_id=client_id,
                original_error=e
            )
    
