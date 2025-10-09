"""
Módulo de consultas de proyectos para asignaciones de proyecto.

Este módulo implementa la interfaz IProjectQueries proporcionando
funcionalidades para consultas centradas en proyectos, incluyendo
análisis de equipos, recursos y planificación temporal.
"""

from typing import Any, Dict, List, Optional
import pendulum
from loguru import logger

from ..interfaces.project_queries_interface import IProjectQueries
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.models.project_assignment import ProjectAssignment
from planificador.exceptions import RepositoryError, ValidationError


class ProjectQueries(IProjectQueries):
    """
    Implementación de consultas centradas en proyectos para asignaciones de proyecto.
    
    Proporciona métodos especializados para analizar la información
    de asignaciones desde la perspectiva del proyecto, incluyendo
    análisis de equipos, recursos y planificación temporal.
    """
    
    def __init__(self, repository_facade: ProjectAssignmentRepositoryFacade):
        """
        Inicializa las consultas de proyectos.
        
        Args:
            repository_facade: Fachada del repositorio para acceso a datos
        """
        self.repository_facade = repository_facade
        self._logger = logger.bind(module="project_queries")
    
    async def get_assignments_by_project(self, project_id: int) -> list[ProjectAssignment]:
        """
        Obtiene todas las asignaciones de un proyecto específico.
        """
        logger.info(f"Buscando asignaciones para el proyecto con ID: {project_id}")
        if not isinstance(project_id, int) or project_id <= 0:
            raise ValidationError("ID de proyecto debe ser un entero positivo.")

        try:
            return await self.repository_facade.project_assignment.get_assignments_by_project(
                project_id
            )
        except Exception as e:
            self._logger.error(f"Error al obtener asignaciones del proyecto {project_id}: {e}")
            raise RepositoryError(
                message=f"Error al obtener asignaciones del proyecto: {e}",
                operation="get_assignments_by_project",
                entity_type="ProjectAssignment",
                entity_id=project_id,
                original_error=e
            )
    
    async def get_project_team_summary(self, project_id: int) -> dict:
        """
        Genera un resumen del equipo asignado a un proyecto.
        """
        logger.info(f"Generando resumen del equipo para el proyecto ID: {project_id}")
        if not isinstance(project_id, int) or project_id <= 0:
            raise ValidationError("ID de proyecto debe ser un entero positivo.")

        try:
            assignments = await self.repository_facade.project_assignment.get_assignments_by_project(project_id)
            
            if not assignments:
                logger.warning(f"No se encontraron asignaciones para el proyecto ID: {project_id}")
                return {
                    "project_id": project_id,
                    "total_team_members": 0,
                    "team_composition": {
                        "roles_distribution": {},
                        "active_members": 0,
                        "inactive_members": 0,
                    },
                    "allocation_summary": {
                        "total_allocated_hours": 0.0,
                        "average_allocation_percentage": 0.0,
                    },
                }

            metrics = await self._calculate_team_metrics(assignments)

            active_members = sum(1 for m in metrics["team_members"] if m["is_active"])
            inactive_members = len(assignments) - active_members

            team_composition = {
                "roles_distribution": metrics["roles_distribution"],
                "active_members": active_members,
                "inactive_members": inactive_members,
            }

            team_summary = {
                "project_id": project_id,
                "total_team_members": len(assignments),
                "team_composition": team_composition,
                "allocation_summary": metrics["allocation_summary"],
            }

            self._logger.info(
                f"Resumen de equipo generado para proyecto {project_id} - "
                f"Tamaño: {team_summary['total_team_members']}"
            )

            return team_summary

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al generar resumen de equipo para proyecto {project_id}: {e}")
            raise RepositoryError(
                message=f"Error al generar resumen de equipo: {e}",
                operation="get_project_team_summary",
                entity_type="ProjectTeam",
                entity_id=project_id,
                original_error=e
            )
    
    async def get_project_resource_allocation(self, project_id: int) -> dict:
        """
        Obtiene la distribución de recursos para un proyecto.
        """
        logger.info(f"Obteniendo distribución de recursos para el proyecto ID: {project_id}")
        if not isinstance(project_id, int) or project_id <= 0:
            raise ValidationError("ID de proyecto debe ser un entero positivo.")

        try:
            
            self._logger.info(f"Calculando distribución de recursos para proyecto {project_id}")
            
            # Obtener asignaciones del proyecto
            assignments = await self.repository_facade.project_assignment.get_assignments_by_project(project_id)
            
            if not assignments:
                return {
                    "project_id": project_id,
                    "total_resources": 0,
                    "resource_distribution": {
                        "by_role": {},
                        "by_allocation_level": {},
                        "by_time_period": {}
                    },
                    "utilization_metrics": {
                        "total_allocated_percentage": 0.0,
                        "average_allocation_per_member": 0.0,
                        "peak_utilization_period": None,
                        "resource_efficiency_score": 0.0
                    },
                    "recommendations": []
                }
            
            # Calcular distribución de recursos
            resource_distribution = await self._calculate_resource_distribution(assignments)
            
            # Generar análisis completo
            resource_allocation = {
                "project_id": project_id,
                "total_resources": len(assignments),
                "resource_distribution": resource_distribution["distribution"],
                "utilization_metrics": resource_distribution["utilization_metrics"],
                "recommendations": resource_distribution["recommendations"]
            }
            
            self._logger.info(
                f"Distribución de recursos calculada para proyecto {project_id} - "
                f"Total recursos: {resource_allocation['total_resources']}"
            )
            
            return resource_allocation
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al calcular distribución de recursos para proyecto {project_id}: {e}")
            raise RepositoryError(
                message=f"Error al calcular distribución de recursos: {e}",
                operation="get_project_resource_allocation",
                entity_type="ProjectResourceAllocation",
                entity_id=project_id,
                original_error=e
            )
    
    async def get_project_assignment_timeline(self, project_id: int, date_range: Optional[Any] = None) -> dict:
        """
        Genera una línea de tiempo de las asignaciones de un proyecto.
        """
        logger.info(f"Generando línea de tiempo para el proyecto ID: {project_id}")
        if not isinstance(project_id, int) or project_id <= 0:
            raise ValidationError("ID de proyecto debe ser un entero positivo.")

        if date_range:
            try:
                # Asumiendo que DateRange tiene atributos start_date y end_date
                if date_range.start_date and date_range.end_date and date_range.end_date < date_range.start_date:
                    raise ValidationError(
                        message="La fecha de fin debe ser posterior a la fecha de inicio",
                        field="end_date",
                        value=date_range.end_date
                    )
            except AttributeError:
                raise ValidationError("El objeto date_range es inválido.")

        try:
            
            self._logger.info(f"Generando línea de tiempo para proyecto {project_id}")
            
            # Obtener asignaciones del proyecto
            assignments = await self.repository_facade.project_assignment.get_assignments_by_project(project_id)
            
            if not assignments:
                return {
                    "project_id": project_id,
                    "timeline_data": [],
                    "project_span": {
                        "start_date": None,
                        "end_date": None,
                        "duration_days": 0
                    },
                    "milestones": [],
                    "resource_peaks": [],
                    "timeline_visualization": {
                        "gantt_data": [],
                        "resource_chart_data": []
                    }
                }
            
            # Generar línea de tiempo
            # El parámetro include_milestones no está en la nueva firma, asumiendo True
            timeline_data = await self._generate_project_timeline(assignments, True)
            
            self._logger.info(
                f"Línea de tiempo generada para proyecto {project_id} - "
                f"Duración: {timeline_data['project_span']['duration_days']} días"
            )
            
            return timeline_data
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.exception(f"Error detallado al generar línea de tiempo para proyecto {project_id}: {e}")
            raise RepositoryError(
                message=f"Error al generar línea de tiempo: {e}",
                operation="get_project_assignment_timeline",
                entity_type="ProjectTimeline",
                entity_id=project_id,
                original_error=e
            )
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE APOYO
    # ============================================================================
    
    async def _calculate_team_metrics(self, assignments: List[ProjectAssignment]) -> Dict[str, Any]:
        """Calcula métricas del equipo del proyecto."""
        roles_distribution = {}
        allocations = []
        start_dates = []
        end_dates = []
        team_members = []
        
        for assignment in assignments:
            # Distribución por roles
            role = assignment.role_in_project or "Sin rol"
            roles_distribution[role] = roles_distribution.get(role, 0) + 1
            
            # Recopilar asignaciones para cálculos
            if assignment.percentage_allocation:
                allocations.append(assignment.percentage_allocation)
            
            # Fechas para timeline
            if assignment.start_date:
                start_dates.append(assignment.start_date)
            if assignment.end_date:
                end_dates.append(assignment.end_date)
            
            # Información de miembros del equipo
            team_members.append({
                "assignment_id": assignment.id,
                "employee_id": assignment.employee_id,
                "role": assignment.role_in_project,
                "allocation_percentage": assignment.percentage_allocation,
                "start_date": assignment.start_date.isoformat() if assignment.start_date else None,
                "end_date": assignment.end_date.isoformat() if assignment.end_date else None,
                "is_active": assignment.is_active
            })
        
        # Calcular métricas de asignación
        allocation_summary = {
            "total_allocation": sum(allocations),
            "average_allocation": sum(allocations) / len(allocations) if allocations else 0.0,
            "max_allocation": max(allocations) if allocations else 0.0,
            "min_allocation": min(allocations) if allocations else 0.0
        }
        
        # Calcular timeline
        timeline = {
            "earliest_start": min(start_dates).isoformat() if start_dates else None,
            "latest_end": max(end_dates).isoformat() if end_dates else None,
            "project_duration_days": 0
        }
        
        if start_dates and end_dates:
            duration = max(end_dates) - min(start_dates)
            timeline["project_duration_days"] = duration.days
        
        return {
            "roles_distribution": roles_distribution,
            "allocation_summary": allocation_summary,
            "timeline": timeline,
            "team_members": team_members
        }
    
    async def _calculate_resource_distribution(self, assignments: List[ProjectAssignment]) -> Dict[str, Any]:
        """Calcula la distribución de recursos del proyecto."""
        # Distribución por rol
        by_role = {}
        by_allocation_level = {"Low (0-50%)": 0, "Medium (51-80%)": 0, "High (81-100%)": 0}
        by_time_period = {}
        
        total_allocation = 0.0
        allocations = []
        
        for assignment in assignments:
            # Por rol
            role = assignment.role_in_project or "Sin rol"
            if role not in by_role:
                by_role[role] = {"count": 0, "total_allocation": 0.0}
            by_role[role]["count"] += 1
            by_role[role]["total_allocation"] += float(assignment.percentage_allocation or 0.0)
            
            # Por nivel de asignación
            allocation = float(assignment.percentage_allocation or 0.0)
            allocations.append(allocation)
            total_allocation += allocation
            
            if allocation <= 50:
                by_allocation_level["Low (0-50%)"] += 1
            elif allocation <= 80:
                by_allocation_level["Medium (51-80%)"] += 1
            else:
                by_allocation_level["High (81-100%)"] += 1
            
            # Por período de tiempo (agrupado por mes)
            if assignment.start_date:
                month_key = assignment.start_date.strftime("%Y-%m")
                by_time_period[month_key] = by_time_period.get(month_key, 0) + 1
        
        # Métricas de utilización
        utilization_metrics = {
            "total_allocated_percentage": total_allocation,
            "average_allocation_per_member": total_allocation / len(assignments) if assignments else 0.0,
            "peak_utilization_period": max(by_time_period.items(), key=lambda x: x[1])[0] if by_time_period else None,
            "resource_efficiency_score": min(100.0, (total_allocation / (len(assignments) * 100)) * 100) if assignments else 0.0
        }
        
        # Recomendaciones
        recommendations = []
        if utilization_metrics["average_allocation_per_member"] > 90:
            recommendations.append("Considerar redistribuir carga de trabajo - alta utilización promedio")
        if by_allocation_level["High (81-100%)"] > len(assignments) * 0.7:
            recommendations.append("Muchos recursos con alta asignación - riesgo de sobrecarga")
        if len(by_role) == 1:
            recommendations.append("Considerar diversificar roles en el equipo")
        
        return {
            "distribution": {
                "by_role": by_role,
                "by_allocation_level": by_allocation_level,
                "by_time_period": by_time_period
            },
            "utilization_metrics": utilization_metrics,
            "recommendations": recommendations
        }
    
    async def _generate_project_timeline(
        self, 
        assignments: List[ProjectAssignment], 
        include_milestones: bool
    ) -> Dict[str, Any]:
        """Genera la línea de tiempo del proyecto."""
        timeline_data = []
        milestones = []
        resource_peaks = []
        
        # Ordenar asignaciones por fecha de inicio
        sorted_assignments = sorted(
            [a for a in assignments if a.start_date], 
            key=lambda x: x.start_date
        )
        
        if not sorted_assignments:
            return {
                "project_id": assignments[0].project_id if assignments else None,
                "timeline_data": [],
                "project_span": {
                    "start_date": None,
                    "end_date": None,
                    "duration_days": 0
                },
                "milestones": [],
                "resource_peaks": [],
                "timeline_visualization": {
                    "gantt_data": [],
                    "resource_chart_data": []
                }
            }
        
        # Calcular span del proyecto
        project_start = min(a.start_date for a in sorted_assignments if a.start_date)
        project_end = max(a.end_date for a in sorted_assignments if a.end_date)
        
        project_span = {
            "start_date": project_start.isoformat(),
            "end_date": project_end.isoformat() if project_end else None,
            "duration_days": (project_end - project_start).days if project_end else 0
        }
        
        # Generar datos de timeline
        for assignment in sorted_assignments:
            timeline_entry = {
                "assignment_id": assignment.id,
                "employee_id": assignment.employee_id,
                "role": assignment.role_in_project,
                "start_date": assignment.start_date.isoformat(),
                "end_date": assignment.end_date.isoformat() if assignment.end_date else None,
                "allocation_percentage": assignment.percentage_allocation,
                "duration_days": (assignment.end_date - assignment.start_date).days if assignment.end_date else 0
            }
            timeline_data.append(timeline_entry)
        
        # Generar hitos si está habilitado
        if include_milestones:
            milestones = [
                {
                    "type": "project_start",
                    "date": project_start.isoformat(),
                    "description": "Inicio del proyecto"
                }
            ]
            
            if project_end:
                milestones.append({
                    "type": "project_end",
                    "date": project_end.isoformat(),
                    "description": "Fin del proyecto"
                })
            
            # Hito de pico de recursos (mes con más asignaciones activas)
            monthly_counts = {}
            for assignment in sorted_assignments:
                month_key = assignment.start_date.strftime("%Y-%m")
                monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
            
            if monthly_counts:
                peak_month = max(monthly_counts.items(), key=lambda x: x[1])
                milestones.append({
                    "type": "resource_peak",
                    "date": f"{peak_month[0]}-01",
                    "description": f"Pico de recursos ({peak_month[1]} asignaciones)"
                })
        
        # Datos para visualización
        gantt_data = [
            {
                "task": f"Empleado {a.employee_id} - {a.role_in_project or 'Sin rol'}",
                "start": a.start_date.isoformat(),
                "end": a.end_date.isoformat() if a.end_date else project_end.isoformat(),
                "allocation": a.percentage_allocation
            }
            for a in sorted_assignments
        ]
        
        resource_chart_data = []
        # Convertir project_start y project_end a objetos pendulum para manipulación
        current_date = pendulum.parse(project_start.isoformat()) if project_start else pendulum.now()
        project_end_pendulum = pendulum.parse(project_end.isoformat()) if project_end else current_date

        while current_date <= project_end_pendulum:
            # Convertir current_date a date para comparación con fechas de asignación
            current_date_as_date = current_date.date()
            active_count = sum(
                1 for a in sorted_assignments 
                if a.start_date <= current_date_as_date and (not a.end_date or a.end_date >= current_date_as_date)
            )
            resource_chart_data.append({
                "date": current_date.to_iso8601_string(),
                "active_resources": active_count
            })
            current_date = current_date.add(days=7)  # Datos semanales
        
        return {
            "project_id": assignments[0].project_id,
            "timeline_data": timeline_data,
            "project_span": project_span,
            "milestones": milestones,
            "resource_peaks": resource_peaks,
            "timeline_visualization": {
                "gantt_data": gantt_data,
                "resource_chart_data": resource_chart_data
            }
        }