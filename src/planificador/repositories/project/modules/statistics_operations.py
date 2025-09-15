from collections import Counter
from typing import Any, Dict, List, Optional

import pendulum
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from planificador.repositories.base_repository import BaseRepository
from planificador.models.project import Project
from planificador.exceptions.repository.base_repository_exceptions import RepositoryError, convert_sqlalchemy_error
from planificador.exceptions.repository.project_repository_exceptions import ProjectRepositoryError


class StatisticsOperations(BaseRepository[Project]):
    """
    Módulo para calcular estadísticas de proyectos.
    """

    def __init__(self, session, query_builder):
        super().__init__(session, Project)
        self.query_builder = query_builder
        self._logger = logger.bind(module="project_statistics_operations")
    
    async def get_by_unique_field(self, field_name: str, field_value: Any) -> Optional[Project]:
        """
        Obtiene un proyecto por un campo único específico.
        
        Args:
            field_name: Nombre del campo único
            field_value: Valor del campo único
            
        Returns:
            Optional[Project]: El proyecto encontrado o None
            
        Raises:
            RepositoryError: Si ocurre un error durante la consulta
        """
        try:
            if not hasattr(Project, field_name):
                raise ValueError(f"El campo '{field_name}' no existe en el modelo Project")
            
            field_attr = getattr(Project, field_name)
            query = select(Project).where(field_attr == field_value)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al buscar proyecto por {field_name}={field_value}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_unique_field",
                entity_type="Project",
                entity_id=str(field_value)
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar proyecto por {field_name}={field_value}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al buscar proyecto por {field_name}={field_value}: {e}",
                operation="get_by_unique_field",
                entity_type="Project",
                entity_id=str(field_value),
                original_error=e
            )

    async def get_status_summary(self) -> Dict[str, int]:
        """
        Calcula un resumen del número de proyectos por estado.
        """
        try:
            query = select(Project.status, func.count(Project.id)).group_by(
                Project.status
            )
            result = await self.session.execute(query)
            return {status: count for status, count in result.all()}
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener el resumen de estados: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_status_summary",
                entity_type="Project",
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener el resumen de estados: {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado al obtener el resumen de estados: {e}",
                operation="get_status_summary",
                entity_type="Project",
                original_error=e,
             )

    async def get_project_duration_stats(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de duración de un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Dict[str, Any]: Estadísticas de duración del proyecto
        """
        try:
            query = select(Project).where(Project.id == project_id)
            result = await self.session.execute(query)
            project = result.scalar_one_or_none()
            
            if not project:
                raise ProjectRepositoryError(
                    message=f"Proyecto con ID {project_id} no encontrado",
                    operation="get_project_duration_stats",
                    entity_type="Project",
                )
            
            # Calcular estadísticas de duración
            planned_duration_days = 0
            actual_duration_days = 0
            remaining_days = 0
            
            if project.start_date and project.end_date:
                planned_duration_days = (project.end_date - project.start_date).days
                
                current_date = pendulum.now().date()
                if project.status in ["Completed", "Archived"]:
                    # Si está completado, usar la fecha de finalización real o actual
                    actual_duration_days = planned_duration_days
                else:
                    # Si está en progreso, calcular días transcurridos
                    if current_date >= project.start_date:
                        actual_duration_days = (current_date - project.start_date).days
                    
                    # Calcular días restantes
                    if current_date < project.end_date:
                        remaining_days = (project.end_date - current_date).days
            
            return {
                "project_id": project_id,
                "project_name": project.name,
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "end_date": project.end_date.isoformat() if project.end_date else None,
                "planned_duration_days": planned_duration_days,
                "actual_duration_days": actual_duration_days,
                "remaining_days": remaining_days,
                "is_overdue": remaining_days < 0 if project.end_date else False,
                "completion_percentage": (
                    (actual_duration_days / planned_duration_days * 100) 
                    if planned_duration_days > 0 else 0
                )
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener estadísticas de duración del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_duration_stats",
                entity_type="Project",
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de duración del proyecto {project_id}: {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado al obtener estadísticas de duración: {str(e)}",
                operation="get_project_duration_stats",
                entity_type="Project",
                original_error=e,
            )

    async def get_monthly_project_stats(self, year: int, month: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas mensuales de proyectos.
        
        Args:
            year: Año
            month: Mes (1-12)
            
        Returns:
            Dict[str, Any]: Estadísticas mensuales de proyectos
        """
        try:
            # Crear fechas de inicio y fin del mes
            start_of_month = pendulum.datetime(year, month, 1).date()
            end_of_month = start_of_month.add(months=1).subtract(days=1)
            
            # Proyectos que inician en el mes
            query_starting = (
                select(func.count(Project.id))
                .where(
                    Project.start_date >= start_of_month,
                    Project.start_date <= end_of_month
                )
            )
            result_starting = await self.session.execute(query_starting)
            projects_starting = result_starting.scalar() or 0
            
            # Proyectos que terminan en el mes
            query_ending = (
                select(func.count(Project.id))
                .where(
                    Project.end_date >= start_of_month,
                    Project.end_date <= end_of_month
                )
            )
            result_ending = await self.session.execute(query_ending)
            projects_ending = result_ending.scalar() or 0
            
            # Proyectos activos durante el mes
            query_active = (
                select(func.count(Project.id))
                .where(
                    Project.start_date <= end_of_month,
                    or_(
                        Project.end_date >= start_of_month,
                        Project.end_date.is_(None)
                    )
                )
            )
            result_active = await self.session.execute(query_active)
            projects_active = result_active.scalar() or 0
            
            return {
                "year": year,
                "month": month,
                "month_name": pendulum.datetime(year, month, 1).format("MMMM"),
                "projects_starting": projects_starting,
                "projects_ending": projects_ending,
                "projects_active": projects_active,
                "period": {
                    "start_date": start_of_month.isoformat(),
                    "end_date": end_of_month.isoformat()
                }
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener estadísticas mensuales para {year}-{month}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_monthly_project_stats",
                entity_type="Project",
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas mensuales para {year}-{month}: {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado al obtener estadísticas mensuales: {str(e)}",
                operation="get_monthly_project_stats",
                entity_type="Project",
                original_error=e,
            )

    async def get_client_project_stats(self, client_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de proyectos de un cliente específico.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Dict[str, Any]: Estadísticas de proyectos del cliente
        """
        try:
            # Total de proyectos del cliente
            query_total = (
                select(func.count(Project.id))
                .where(Project.client_id == client_id)
            )
            result_total = await self.session.execute(query_total)
            total_projects = result_total.scalar() or 0
            
            # Proyectos por estado
            query_by_status = (
                select(Project.status, func.count(Project.id))
                .where(Project.client_id == client_id)
                .group_by(Project.status)
            )
            result_by_status = await self.session.execute(query_by_status)
            projects_by_status = dict(result_by_status.all())
            
            # Proyectos activos
            active_projects = projects_by_status.get("Active", 0)
            
            # Proyectos completados
            completed_projects = projects_by_status.get("Completed", 0)
            
            return {
                "client_id": client_id,
                "total_projects": total_projects,
                "active_projects": active_projects,
                "completed_projects": completed_projects,
                "projects_by_status": projects_by_status,
                "completion_rate": (
                    (completed_projects / total_projects * 100) 
                    if total_projects > 0 else 0
                )
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener estadísticas de proyectos del cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_project_stats",
                entity_type="Project",
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de proyectos del cliente {client_id}: {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado al obtener estadísticas del cliente: {str(e)}",
                operation="get_client_project_stats",
                entity_type="Project",
                original_error=e,
            )

    async def get_overdue_projects_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de proyectos atrasados.
        
        Returns:
            Dict[str, Any]: Estadísticas de proyectos atrasados
        """
        try:
            current_date = pendulum.now().date()
            
            # Total de proyectos vencidos
            query_overdue = (
                select(func.count(Project.id))
                .where(
                    Project.end_date < current_date,
                    Project.status.notin_(["Completed", "Archived"])
                )
            )
            result_overdue = await self.session.execute(query_overdue)
            total_overdue = result_overdue.scalar() or 0
            
            # Promedio de días de retraso
            query_avg_delay = (
                select(func.avg(func.julianday(current_date) - func.julianday(Project.end_date)))
                .where(
                    Project.end_date < current_date,
                    Project.status.notin_(["Completed", "Archived"])
                )
            )
            result_avg_delay = await self.session.execute(query_avg_delay)
            avg_delay_days = result_avg_delay.scalar() or 0
            
            # Total de proyectos activos
            query_active = (
                select(func.count(Project.id))
                .where(Project.status.notin_(["Completed", "Archived"]))
            )
            result_active = await self.session.execute(query_active)
            total_active = result_active.scalar() or 0
            
            return {
                "total_overdue_projects": total_overdue,
                "total_active_projects": total_active,
                "overdue_percentage": (
                    (total_overdue / total_active * 100) 
                    if total_active > 0 else 0
                ),
                "average_delay_days": round(float(avg_delay_days), 2),
                "analysis_date": current_date.isoformat()
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener estadísticas de proyectos atrasados: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_overdue_projects_stats",
                entity_type="Project",
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de proyectos atrasados: {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado al obtener estadísticas de proyectos atrasados: {str(e)}",
                operation="get_overdue_projects_stats",
                entity_type="Project",
                original_error=e,
            )

    async def get_overdue_projects_summary(self) -> List[Dict[str, Any]]:
        """
        Obtiene un resumen de proyectos vencidos con información detallada.
        
        Returns:
            List[Dict[str, Any]]: Lista de proyectos vencidos con detalles como:
                - id: ID del proyecto
                - name: Nombre del proyecto
                - reference: Referencia del proyecto
                - end_date: Fecha de finalización
                - days_overdue: Días de retraso
                - client_name: Nombre del cliente
        """
        try:
            current_date = pendulum.now().date()
            
            # Consulta base con joins necesarios
            query = (
                self.query_builder._base_query()
                .where(Project.end_date < current_date)
                .where(Project.status.notin_(["Completed", "Archived"]))
            )
            
            result = await self.session.execute(query)
            overdue_projects = result.scalars().all()
            
            summary = []
            for project in overdue_projects:
                days_overdue = (current_date - project.end_date).days
                summary.append({
                    "id": project.id,
                    "name": project.name,
                    "reference": getattr(project, 'reference', None),
                    "end_date": project.end_date.isoformat() if project.end_date else None,
                    "days_overdue": days_overdue,
                    "client_name": getattr(project.client, 'name', 'Sin cliente') if hasattr(project, 'client') and project.client else "Sin cliente",
                })
            
            return summary
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener el resumen de proyectos vencidos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_overdue_projects_summary",
                entity_type="Project",
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado al obtener el resumen de proyectos vencidos: {e}"
            )
            raise ProjectRepositoryError(
                message=f"Error inesperado al obtener el resumen de proyectos vencidos: {e}",
                operation="get_overdue_projects_summary",
                entity_type="Project",
                original_error=e,
            )

    async def get_project_performance_stats(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de rendimiento de un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Dict[str, Any]: Estadísticas de rendimiento del proyecto
        """
        try:
            # Obtener el proyecto básico
            query = select(Project).where(Project.id == project_id)
            result = await self.session.execute(query)
            project = result.scalar_one_or_none()
            
            if not project:
                raise ProjectRepositoryError(
                    message=f"Proyecto con ID {project_id} no encontrado",
                    operation="get_project_performance_stats",
                    entity_type="Project",
                )
            
            # Calcular progreso del proyecto
            progress_percentage = 0
            if project.start_date and project.end_date:
                current_date = pendulum.now().date()
                total_days = (project.end_date - project.start_date).days
                elapsed_days = (current_date - project.start_date).days
                if total_days > 0:
                    progress_percentage = min(100, max(0, (elapsed_days / total_days) * 100))
            
            return {
                "project_id": project_id,
                "project_name": project.name,
                "progress_percentage": round(progress_percentage, 2),
                "status": project.status,
                "priority": getattr(project, 'priority', None),
                "is_overdue": (
                    project.end_date < pendulum.now().date() 
                    if project.end_date and project.status not in ["Completed", "Archived"]
                    else False
                )
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener estadísticas de rendimiento del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_performance_stats",
                entity_type="Project",
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de rendimiento del proyecto {project_id}: {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado al obtener estadísticas de rendimiento: {str(e)}",
                operation="get_project_performance_stats",
                entity_type="Project",
                original_error=e,
            )

    async def get_projects_by_status_summary(self) -> Dict[str, int]:
        """
        Obtiene un resumen de proyectos agrupados por estado.
        
        Returns:
            Dict[str, int]: Diccionario con el conteo de proyectos por estado
        """
        return await self.get_status_summary()

    async def get_project_workload_stats(
        self,
        project_id: int,
        start_date: Any = None,
        end_date: Any = None,
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de carga de trabajo de un proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del período (opcional)
            end_date: Fecha de fin del período (opcional)
            
        Returns:
            Dict[str, Any]: Estadísticas de carga de trabajo
        """
        try:
            query = select(Project).where(Project.id == project_id)
            result = await self.session.execute(query)
            project = result.scalar_one_or_none()
            
            if not project:
                raise ProjectRepositoryError(
                    message=f"Proyecto con ID {project_id} no encontrado",
                    operation="get_project_workload_stats",
                    entity_type="Project",
                )
            
            return {
                "project_id": project_id,
                "project_name": project.name,
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                },
                "total_hours": 0.0,
                "total_assignments": 0,
                "average_hours_per_assignment": 0.0,
                "employee_workload": {}
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener estadísticas de carga de trabajo del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_workload_stats",
                entity_type="Project",
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de carga de trabajo del proyecto {project_id}: {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado al obtener estadísticas de carga de trabajo: {str(e)}",
                operation="get_project_workload_stats",
                entity_type="Project",
                original_error=e,
            )