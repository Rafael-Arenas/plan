"""
Módulo de consultas de proyectos para asignaciones de proyecto.

Este módulo implementa la interfaz IProjectQueries proporcionando
funcionalidades para consultas centradas en proyectos, incluyendo
análisis de equipos, recursos y planificación temporal.
"""

from typing import Dict, List, Any, Optional
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
        self._repository = repository_facade
        self._logger = logger.bind(module="project_queries")
    
    async def get_assignments_by_project(self, project_id: int) -> List[ProjectAssignment]:
        """
        Obtiene todas las asignaciones de un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Lista de asignaciones del proyecto
            
        Raises:
            ValidationError: Si el project_id es inválido
            RepositoryError: Si hay error al acceder a los datos
        """
        try:
            # Validar parámetros
            if not isinstance(project_id, int) or project_id <= 0:
                raise ValidationError(
                    message="ID de proyecto inválido",
                    field="project_id",
                    value=project_id
                )
            
            self._logger.info(f"Obteniendo asignaciones para proyecto {project_id}")
            
            # Obtener asignaciones del proyecto
            assignments = await self._repository.get_assignments_by_project(project_id)
            
            self._logger.info(
                f"Encontradas {len(assignments)} asignaciones para proyecto {project_id}"
            )
            
            return assignments
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener asignaciones del proyecto {project_id}: {e}")
            raise RepositoryError(
                message=f"Error al obtener asignaciones del proyecto: {e}",
                operation="get_assignments_by_project",
                entity_type="ProjectAssignment",
                entity_id=project_id,
                original_error=e
            )
    
    async def get_project_team_summary(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene un resumen completo del equipo asignado al proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Diccionario con resumen del equipo del proyecto
            
        Raises:
            ValidationError: Si el project_id es inválido
            RepositoryError: Si hay error al acceder a los datos
        """
        try:
            # Validar parámetros
            if not isinstance(project_id, int) or project_id <= 0:
                raise ValidationError(
                    message="ID de proyecto inválido",
                    field="project_id",
                    value=project_id
                )
            
            self._logger.info(f"Generando resumen de equipo para proyecto {project_id}")
            
            # Obtener asignaciones del proyecto
            assignments = await self._repository.get_assignments_by_project(project_id)
            
            if not assignments:
                return {
                    "project_id": project_id,
                    "team_size": 0,
                    "active_members": 0,
                    "roles_distribution": {},
                    "allocation_summary": {
                        "total_allocation": 0.0,
                        "average_allocation": 0.0,
                        "max_allocation": 0.0,
                        "min_allocation": 0.0
                    },
                    "timeline": {
                        "earliest_start": None,
                        "latest_end": None,
                        "project_duration_days": 0
                    },
                    "team_members": []
                }
            
            # Calcular métricas del equipo
            team_metrics = await self._calculate_team_metrics(assignments)
            
            # Generar resumen completo
            team_summary = {
                "project_id": project_id,
                "team_size": len(assignments),
                "active_members": len([a for a in assignments if a.is_active]),
                "roles_distribution": team_metrics["roles_distribution"],
                "allocation_summary": team_metrics["allocation_summary"],
                "timeline": team_metrics["timeline"],
                "team_members": team_metrics["team_members"]
            }
            
            self._logger.info(
                f"Resumen de equipo generado para proyecto {project_id} - "
                f"Tamaño: {team_summary['team_size']}, Activos: {team_summary['active_members']}"
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
    
    async def get_project_resource_allocation(self, project_id: int) -> Dict[str, Any]:
        """
        Calcula la distribución de recursos del proyecto por roles y tiempo.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Diccionario con distribución de recursos del proyecto
            
        Raises:
            ValidationError: Si el project_id es inválido
            RepositoryError: Si hay error al acceder a los datos
        """
        try:
            # Validar parámetros
            if not isinstance(project_id, int) or project_id <= 0:
                raise ValidationError(
                    message="ID de proyecto inválido",
                    field="project_id",
                    value=project_id
                )
            
            self._logger.info(f"Calculando distribución de recursos para proyecto {project_id}")
            
            # Obtener asignaciones del proyecto
            assignments = await self._repository.get_assignments_by_project(project_id)
            
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
    
    async def get_project_assignment_timeline(
        self, 
        project_id: int,
        include_milestones: bool = True
    ) -> Dict[str, Any]:
        """
        Genera una línea de tiempo visual de las asignaciones del proyecto.
        
        Args:
            project_id: ID del proyecto
            include_milestones: Si incluir hitos importantes en la línea de tiempo
            
        Returns:
            Diccionario con línea de tiempo del proyecto
            
        Raises:
            ValidationError: Si el project_id es inválido
            RepositoryError: Si hay error al acceder a los datos
        """
        try:
            # Validar parámetros
            if not isinstance(project_id, int) or project_id <= 0:
                raise ValidationError(
                    message="ID de proyecto inválido",
                    field="project_id",
                    value=project_id
                )
            
            self._logger.info(f"Generando línea de tiempo para proyecto {project_id}")
            
            # Obtener asignaciones del proyecto
            assignments = await self._repository.get_assignments_by_project(project_id)
            
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
            timeline_data = await self._generate_project_timeline(assignments, include_milestones)
            
            self._logger.info(
                f"Línea de tiempo generada para proyecto {project_id} - "
                f"Duración: {timeline_data['project_span']['duration_days']} días"
            )
            
            return timeline_data
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al generar línea de tiempo para proyecto {project_id}: {e}")
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
            role = assignment.role or "Sin rol"
            roles_distribution[role] = roles_distribution.get(role, 0) + 1
            
            # Recopilar asignaciones para cálculos
            if assignment.allocation_percentage:
                allocations.append(assignment.allocation_percentage)
            
            # Fechas para timeline
            if assignment.start_date:
                start_dates.append(assignment.start_date)
            if assignment.end_date:
                end_dates.append(assignment.end_date)
            
            # Información de miembros del equipo
            team_members.append({
                "assignment_id": assignment.id,
                "employee_id": assignment.employee_id,
                "role": assignment.role,
                "allocation_percentage": assignment.allocation_percentage,
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
            role = assignment.role or "Sin rol"
            if role not in by_role:
                by_role[role] = {"count": 0, "total_allocation": 0.0}
            by_role[role]["count"] += 1
            by_role[role]["total_allocation"] += assignment.allocation_percentage or 0.0
            
            # Por nivel de asignación
            allocation = assignment.allocation_percentage or 0.0
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
                "role": assignment.role,
                "start_date": assignment.start_date.isoformat(),
                "end_date": assignment.end_date.isoformat() if assignment.end_date else None,
                "allocation_percentage": assignment.allocation_percentage,
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
                "task": f"Empleado {a.employee_id} - {a.role or 'Sin rol'}",
                "start": a.start_date.isoformat(),
                "end": a.end_date.isoformat() if a.end_date else project_end.isoformat(),
                "allocation": a.allocation_percentage
            }
            for a in sorted_assignments
        ]
        
        resource_chart_data = []
        current_date = project_start
        while current_date <= (project_end or project_start):
            active_count = sum(
                1 for a in sorted_assignments 
                if a.start_date <= current_date and (not a.end_date or a.end_date >= current_date)
            )
            resource_chart_data.append({
                "date": current_date.isoformat(),
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