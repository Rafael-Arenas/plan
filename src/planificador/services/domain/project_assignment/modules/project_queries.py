# src/planificador/services/domain/project_assignment/modules/project_queries.py

"""
Módulo de Consultas de Proyectos para Asignaciones de Proyecto

Implementa consultas especializadas centradas en proyectos,
incluyendo análisis de equipos, distribución de recursos,
líneas de tiempo y métricas de proyecto.
"""

from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal
from loguru import logger
from collections import defaultdict
import statistics
import pendulum

from planificador.schemas.assignment.assignment import ProjectAssignment
from planificador.schemas.assignment.advanced_schemas import (
    ProjectTeamSummarySchema,
    ProjectResourceAllocationSchema,
    ProjectTimelineSchema
)
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.exceptions import RepositoryError, ValidationError, NotFoundError
from ..interfaces import IProjectQueries


class ProjectQueries(IProjectQueries):
    """
    Implementación de consultas centradas en proyectos para asignaciones de proyecto.
    
    Proporciona métodos especializados para analizar la información
    de asignaciones desde la perspectiva del proyecto, incluyendo
    análisis de equipos, recursos y planificación temporal.
    """
    
    def __init__(self, repository_facade: ProjectAssignmentRepositoryFacade):
        """
        Inicializa el módulo de consultas de proyectos.
        
        Args:
            repository_facade: Facade del repositorio de asignaciones
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="project_assignment_project_queries")
    
    async def get_assignments_by_project(
        self, 
        project_id: int, 
        include_inactive: bool = True
    ) -> List[ProjectAssignment]:
        """
        Obtiene todas las asignaciones de un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            include_inactive: Si incluir asignaciones inactivas
            
        Returns:
            List[ProjectAssignment]: Lista de asignaciones del proyecto
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
            ValidationError: Si el ID del proyecto es inválido
        """
        self._logger.debug(f"Obteniendo asignaciones para proyecto {project_id}")
        
        # Validar entrada
        self._validate_project_id(project_id)
        
        try:
            # Obtener asignaciones del proyecto
            assignments = await self._repository.get_assignments_by_project(
                project_id=project_id
            )
            
            # Filtrar por estado si es necesario
            if not include_inactive:
                assignments = [a for a in assignments if a.is_active]
            
            self._logger.info(
                f"Obtenidas {len(assignments)} asignaciones para proyecto {project_id}"
            )
            
            return assignments
            
        except Exception as e:
            self._logger.error(f"Error obteniendo asignaciones del proyecto {project_id}: {e}")
            if isinstance(e, (RepositoryError, ValidationError)):
                raise
            raise RepositoryError(
                message=f"Error inesperado obteniendo asignaciones del proyecto: {e}",
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
            Dict[str, Any]: Resumen del equipo del proyecto
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        self._logger.debug(f"Generando resumen del equipo para proyecto {project_id}")
        
        try:
            # Obtener asignaciones activas del proyecto
            assignments = await self._repository.get_assignments_by_project(
                project_id=project_id,
                active_only=True
            )
            
            if not assignments:
                # Verificar si el proyecto existe
                project_exists = await self._repository.project_exists(project_id)
                if not project_exists:
                    raise NotFoundError(
                        entity_type="Project",
                        entity_id=project_id,
                        message=f"Proyecto con ID {project_id} no encontrado"
                    )
            
            # Obtener información del proyecto
            project_info = await self._repository.get_project_basic_info(project_id)
            project_name = project_info.get("name", f"Proyecto {project_id}")
            
            # Calcular métricas del equipo
            team_summary = await self._calculate_team_metrics(assignments, project_id, project_name)
            
            # Convertir a diccionario para cumplir con la interfaz
            result = {
                "project_id": team_summary.project_id,
                "project_name": team_summary.project_name,
                "total_members": team_summary.total_team_members,
                "active_assignments": team_summary.active_assignments,
                "total_allocation": float(team_summary.total_allocation_percentage),
                "average_allocation": float(team_summary.average_allocation_per_member),
                "roles_distribution": team_summary.roles_distribution,
                "team_capacity_status": team_summary.team_capacity_status,
                "team_composition": team_summary.team_members,
                "project_timeline": team_summary.project_timeline
            }
            
            self._logger.info(
                f"Resumen del equipo generado para proyecto {project_id}: "
                f"{result['total_members']} miembros"
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error generando resumen del equipo para proyecto {project_id}: {e}")
            if isinstance(e, (RepositoryError, ValidationError, NotFoundError)):
                raise
            raise RepositoryError(
                message=f"Error inesperado generando resumen del equipo: {e}",
                operation="get_project_team_summary",
                entity_type="Project",
                entity_id=project_id,
                original_error=e
            )
    
    async def get_project_resource_allocation(self, project_id: int) -> Dict[str, Any]:
        """
        Calcula la distribución de recursos del proyecto por roles y tiempo.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Dict[str, Any]: Distribución de recursos del proyecto con las siguientes claves:
                - project_id: ID del proyecto
                - total_resources: Número total de recursos asignados
                - allocation_by_role: Distribución de horas por rol
                - allocation_by_period: Distribución temporal de recursos
                - resource_utilization: Utilización de recursos por empleado
                - peak_allocation_periods: Períodos de mayor asignación
                - resource_gaps: Períodos con baja asignación de recursos
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        self._logger.debug(f"Calculando distribución de recursos para proyecto {project_id}")
        
        try:
            # Obtener todas las asignaciones del proyecto (activas e inactivas)
            assignments = await self._repository.get_assignments_by_project(
                project_id=project_id,
                include_inactive=True
            )
            
            if not assignments:
                # Verificar si el proyecto existe
                project_exists = await self._repository.project_exists(project_id)
                if not project_exists:
                    raise NotFoundError(
                        entity_type="Project",
                        entity_id=project_id,
                        message=f"Proyecto con ID {project_id} no encontrado"
                    )
            
            # Obtener información del proyecto
            project_info = await self._repository.get_project_basic_info(project_id)
            project_name = project_info.get("name", f"Proyecto {project_id}")
            
            # Calcular distribución de recursos
            resource_allocation = await self._calculate_resource_distribution(
                assignments, project_id, project_name
            )
            
            self._logger.info(
                f"Distribución de recursos calculada para proyecto {project_id}: "
                f"{resource_allocation.total_allocated_hours_per_day} horas/día totales"
            )
            
            # Convertir el schema a diccionario según la interfaz
            return {
                "project_id": resource_allocation.project_id,
                "project_name": resource_allocation.project_name,
                "total_resources": len(assignments),
                "total_allocation": float(resource_allocation.total_allocation_percentage),
                "resource_distribution": resource_allocation.resource_distribution_by_role,
                "allocation_by_role": resource_allocation.resource_distribution_by_role,
                "allocation_by_period": resource_allocation.resource_distribution_by_time,
                "resource_utilization": resource_allocation.capacity_analysis,
                "peak_allocation_periods": resource_allocation.resource_distribution_by_time,
                "resource_gaps": [],  # Se puede calcular basado en períodos de baja asignación
                "efficiency_metrics": resource_allocation.efficiency_metrics,
                "total_allocated_hours_per_day": float(resource_allocation.total_allocated_hours_per_day)
            }
            
        except Exception as e:
            self._logger.error(f"Error calculando distribución de recursos para proyecto {project_id}: {e}")
            if isinstance(e, (RepositoryError, ValidationError, NotFoundError)):
                raise
            raise RepositoryError(
                message=f"Error inesperado calculando distribución de recursos: {e}",
                operation="get_project_resource_allocation",
                entity_type="Project",
                entity_id=project_id,
                original_error=e
            )
    
    async def get_project_assignment_timeline(
        self, 
        project_id: int, 
        start_date: Optional[pendulum.Date] = None,
        end_date: Optional[pendulum.Date] = None
    ) -> Dict[str, Any]:
        """
        Genera una línea de tiempo visual de las asignaciones del proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio opcional para filtrar asignaciones
            end_date: Fecha de fin opcional para filtrar asignaciones
            
        Returns:
            Dict[str, Any]: Diccionario con línea de tiempo del proyecto conteniendo:
                - project_id: ID del proyecto
                - project_start_date: Fecha de inicio del proyecto
                - project_end_date: Fecha de fin del proyecto
                - timeline_events: Lista de eventos de asignación ordenados
                - concurrent_assignments: Asignaciones concurrentes por período
                - resource_peaks: Picos de recursos en la línea de tiempo
                - milestone_assignments: Asignaciones asociadas a hitos
                - timeline_visualization_data: Datos para visualización gráfica
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
            ValidationError: Si el rango de fechas es inválido
        """
        self._logger.debug(f"Generando línea de tiempo para proyecto {project_id}")
        
        # Validar rango de fechas si se proporcionan ambas
        if start_date and end_date:
            self._validate_date_range(start_date, end_date)
        
        try:
            # Obtener todas las asignaciones del proyecto
            assignments = await self._repository.get_assignments_by_project(
                project_id=project_id,
                include_inactive=True
            )
            
            if not assignments:
                # Verificar si el proyecto existe
                project_exists = await self._repository.project_exists(project_id)
                if not project_exists:
                    raise NotFoundError(
                        entity_type="Project",
                        entity_id=project_id,
                        message=f"Proyecto con ID {project_id} no encontrado"
                    )
            
            # Obtener información del proyecto
            project_info = await self._repository.get_project_basic_info(project_id)
            project_name = project_info.get("name", f"Proyecto {project_id}")
            
            # Generar línea de tiempo
            timeline = await self._generate_project_timeline(
                assignments, project_id, project_name
            )
            
            self._logger.info(
                f"Línea de tiempo generada para proyecto {project_id}: "
                f"{len(timeline.timeline_events)} eventos"
            )
            
            # Convertir el esquema a diccionario para cumplir con la interfaz
            return {
                "project_id": timeline.project_id,
                "project_name": timeline.project_name,
                "project_start_date": timeline.project_start_date,
                "project_end_date": timeline.project_end_date,
                "timeline_events": timeline.timeline_events,
                "phases": timeline.phases,
                "milestones": timeline.milestones,
                "resource_timeline": timeline.resource_timeline,
                "critical_path": timeline.critical_path,
                # Campos adicionales requeridos por la interfaz
                "concurrent_assignments": [],  # Se puede implementar más adelante
                "resource_peaks": [],  # Se puede implementar más adelante
                "milestone_assignments": [],  # Se puede implementar más adelante
                "timeline_visualization_data": {}  # Se puede implementar más adelante
            }
            
        except Exception as e:
            self._logger.error(f"Error generando línea de tiempo para proyecto {project_id}: {e}")
            if isinstance(e, (RepositoryError, ValidationError, NotFoundError)):
                raise
            raise RepositoryError(
                message=f"Error inesperado generando línea de tiempo: {e}",
                operation="get_project_assignment_timeline",
                entity_type="Project",
                entity_id=project_id,
                original_error=e
            )
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE CÁLCULO
    # ============================================================================
    
    async def _calculate_team_metrics(
        self, 
        assignments: List[ProjectAssignment], 
        project_id: int, 
        project_name: str
    ) -> ProjectTeamSummarySchema:
        """Calcula las métricas del equipo del proyecto."""
        
        # Agrupar por empleado
        employees = {}
        roles_count = defaultdict(int)
        total_allocation = Decimal('0')
        
        for assignment in assignments:
            employee_id = assignment.employee_id
            
            if employee_id not in employees:
                # Obtener información del empleado
                employee_info = await self._repository.get_employee_basic_info(employee_id)
                employees[employee_id] = {
                    "employee_id": employee_id,
                    "employee_name": employee_info.get("name", f"Empleado {employee_id}"),
                    "assignments": [],
                    "total_allocation": Decimal('0'),
                    "total_hours": Decimal('0'),
                    "roles": set()
                }
            
            employees[employee_id]["assignments"].append({
                "assignment_id": assignment.id,
                "role": assignment.role_in_project,
                "allocation_percentage": assignment.percentage_allocation or Decimal('0'),
                "hours_per_day": assignment.allocated_hours_per_day or Decimal('0'),
                "start_date": assignment.start_date,
                "end_date": assignment.end_date,
                "is_active": assignment.is_active
            })
            
            employees[employee_id]["total_allocation"] += assignment.percentage_allocation or Decimal('0')
            employees[employee_id]["total_hours"] += assignment.allocated_hours_per_day or Decimal('0')
            
            if assignment.role_in_project:
                employees[employee_id]["roles"].add(assignment.role_in_project)
                roles_count[assignment.role_in_project] += 1
            
            total_allocation += assignment.percentage_allocation or Decimal('0')
        
        # Convertir sets a listas para serialización
        team_members = []
        for emp_data in employees.values():
            emp_data["roles"] = list(emp_data["roles"])
            team_members.append(emp_data)
        
        # Determinar estado de capacidad del equipo
        avg_allocation = total_allocation / len(employees) if employees else Decimal('0')
        if avg_allocation < 60:
            capacity_status = "underutilized"
        elif avg_allocation > 90:
            capacity_status = "overallocated"
        else:
            capacity_status = "optimal"
        
        # Calcular fechas del proyecto
        project_dates = self._calculate_project_dates(assignments)
        
        return ProjectTeamSummarySchema(
            project_id=project_id,
            project_name=project_name,
            total_team_members=len(employees),
            active_assignments=len([a for a in assignments if a.is_active]),
            total_allocation_percentage=total_allocation,
            average_allocation_per_member=avg_allocation,
            roles_distribution=dict(roles_count),
            team_capacity_status=capacity_status,
            team_members=team_members,
            project_timeline=project_dates
        )
    
    async def _calculate_resource_distribution(
        self, 
        assignments: List[ProjectAssignment], 
        project_id: int, 
        project_name: str
    ) -> ProjectResourceAllocationSchema:
        """Calcula la distribución de recursos del proyecto."""
        
        total_hours = Decimal('0')
        total_percentage = Decimal('0')
        
        # Distribución por rol
        role_distribution = defaultdict(lambda: {
            "count": 0,
            "total_hours": Decimal('0'),
            "total_percentage": Decimal('0'),
            "employees": []
        })
        
        # Distribución temporal
        time_distribution = []
        
        for assignment in assignments:
            hours = assignment.allocated_hours_per_day or Decimal('0')
            percentage = assignment.percentage_allocation or Decimal('0')
            
            total_hours += hours
            total_percentage += percentage
            
            # Por rol
            role = assignment.role_in_project or "Sin rol definido"
            role_distribution[role]["count"] += 1
            role_distribution[role]["total_hours"] += hours
            role_distribution[role]["total_percentage"] += percentage
            role_distribution[role]["employees"].append({
                "employee_id": assignment.employee_id,
                "assignment_id": assignment.id,
                "hours": float(hours),
                "percentage": float(percentage)
            })
            
            # Distribución temporal
            time_distribution.append({
                "assignment_id": assignment.id,
                "employee_id": assignment.employee_id,
                "role": role,
                "start_date": assignment.start_date,
                "end_date": assignment.end_date,
                "hours_per_day": float(hours),
                "percentage": float(percentage),
                "is_active": assignment.is_active
            })
        
        # Convertir defaultdict a dict regular
        role_dist_dict = {}
        for role, data in role_distribution.items():
            role_dist_dict[role] = {
                "count": data["count"],
                "total_hours": float(data["total_hours"]),
                "total_percentage": float(data["total_percentage"]),
                "average_hours_per_employee": float(data["total_hours"] / data["count"]) if data["count"] > 0 else 0,
                "employees": data["employees"]
            }
        
        # Análisis de capacidad
        capacity_analysis = {
            "total_assignments": len(assignments),
            "active_assignments": len([a for a in assignments if a.is_active]),
            "unique_employees": len(set(a.employee_id for a in assignments)),
            "unique_roles": len(role_distribution),
            "average_allocation_per_assignment": float(total_percentage / len(assignments)) if assignments else 0,
            "resource_utilization_score": min(100, float(total_percentage / len(assignments)) * 1.2) if assignments else 0
        }
        
        # Métricas de eficiencia
        efficiency_metrics = {
            "role_diversity_index": len(role_distribution) / len(assignments) if assignments else 0,
            "allocation_balance_score": self._calculate_allocation_balance(assignments),
            "resource_optimization_score": self._calculate_resource_optimization(role_dist_dict)
        }
        
        return ProjectResourceAllocationSchema(
            project_id=project_id,
            project_name=project_name,
            total_allocated_hours_per_day=total_hours,
            total_allocation_percentage=total_percentage,
            resource_distribution_by_role=role_dist_dict,
            resource_distribution_by_time=time_distribution,
            capacity_analysis=capacity_analysis,
            efficiency_metrics=efficiency_metrics
        )
    
    async def _generate_project_timeline(
        self, 
        assignments: List[ProjectAssignment], 
        project_id: int, 
        project_name: str
    ) -> ProjectTimelineSchema:
        """Genera la línea de tiempo del proyecto."""
        
        # Calcular fechas del proyecto
        project_dates = self._calculate_project_dates(assignments)
        
        # Generar eventos de la línea de tiempo
        timeline_events = []
        for assignment in assignments:
            # Evento de inicio
            timeline_events.append({
                "event_type": "assignment_start",
                "date": assignment.start_date,
                "employee_id": assignment.employee_id,
                "assignment_id": assignment.id,
                "role": assignment.role_in_project,
                "description": f"Inicio de asignación - {assignment.role_in_project or 'Sin rol'}",
                "allocation_percentage": float(assignment.percentage_allocation or 0),
                "hours_per_day": float(assignment.allocated_hours_per_day or 0)
            })
            
            # Evento de fin (si existe)
            if assignment.end_date:
                timeline_events.append({
                    "event_type": "assignment_end",
                    "date": assignment.end_date,
                    "employee_id": assignment.employee_id,
                    "assignment_id": assignment.id,
                    "role": assignment.role_in_project,
                    "description": f"Fin de asignación - {assignment.role_in_project or 'Sin rol'}",
                    "allocation_percentage": float(assignment.percentage_allocation or 0),
                    "hours_per_day": float(assignment.allocated_hours_per_day or 0)
                })
        
        # Ordenar eventos por fecha
        timeline_events.sort(key=lambda x: x["date"])
        
        # Generar fases del proyecto
        phases = self._generate_project_phases(assignments)
        
        # Generar hitos
        milestones = self._generate_project_milestones(assignments)
        
        # Generar línea de tiempo de recursos
        resource_timeline = self._generate_resource_timeline(assignments)
        
        # Generar ruta crítica
        critical_path = self._generate_critical_path(assignments)
        
        return ProjectTimelineSchema(
            project_id=project_id,
            project_name=project_name,
            project_start_date=project_dates.get("start_date"),
            project_end_date=project_dates.get("end_date"),
            timeline_events=timeline_events,
            phases=phases,
            milestones=milestones,
            resource_timeline=resource_timeline,
            critical_path=critical_path
        )
    
    def _calculate_project_dates(self, assignments: List[ProjectAssignment]) -> Dict[str, Any]:
        """Calcula las fechas del proyecto basadas en las asignaciones."""
        if not assignments:
            return {"start_date": None, "end_date": None, "duration_days": 0}
        
        start_dates = [a.start_date for a in assignments]
        end_dates = [a.end_date for a in assignments if a.end_date]
        
        project_start = min(start_dates)
        project_end = max(end_dates) if end_dates else None
        
        duration = (project_end - project_start).days if project_end else None
        
        return {
            "start_date": project_start,
            "end_date": project_end,
            "duration_days": duration,
            "has_open_assignments": len(end_dates) < len(assignments)
        }
    
    def _calculate_allocation_balance(self, assignments: List[ProjectAssignment]) -> float:
        """Calcula el balance de asignación del proyecto."""
        if not assignments:
            return 0.0
        
        allocations = [float(a.percentage_allocation or 0) for a in assignments]
        if not allocations:
            return 0.0
        
        # Calcular desviación estándar como medida de balance
        mean_allocation = statistics.mean(allocations)
        if len(allocations) > 1:
            std_dev = statistics.stdev(allocations)
            # Convertir a score (menor desviación = mejor balance)
            balance_score = max(0, 100 - (std_dev / mean_allocation * 100)) if mean_allocation > 0 else 0
        else:
            balance_score = 100.0
        
        return balance_score
    
    def _calculate_resource_optimization(self, role_distribution: Dict[str, Any]) -> float:
        """Calcula el score de optimización de recursos."""
        if not role_distribution:
            return 0.0
        
        # Factores de optimización
        role_count = len(role_distribution)
        total_assignments = sum(data["count"] for data in role_distribution.values())
        
        # Score basado en diversidad de roles y distribución
        diversity_score = min(100, role_count * 20)  # Máximo 5 roles diferentes
        
        # Score de distribución equilibrada
        role_counts = [data["count"] for data in role_distribution.values()]
        if len(role_counts) > 1:
            distribution_score = self._calculate_allocation_balance(
                [type('obj', (object,), {'percentage_allocation': count * 100 / total_assignments})() 
                 for count in role_counts]
            )
        else:
            distribution_score = 100.0
        
        return (diversity_score + distribution_score) / 2
    
    def _generate_project_phases(self, assignments: List[ProjectAssignment]) -> List[Dict[str, Any]]:
        """Genera las fases del proyecto basadas en las asignaciones."""
        # Agrupar asignaciones por períodos temporales
        phases = []
        
        if not assignments:
            return phases
        
        # Ordenar por fecha de inicio
        sorted_assignments = sorted(assignments, key=lambda x: x.start_date)
        
        # Crear fases basadas en cambios significativos en el equipo
        current_phase = {
            "phase_name": "Fase Inicial",
            "start_date": sorted_assignments[0].start_date,
            "end_date": None,
            "team_size": 0,
            "assignments": []
        }
        
        for assignment in sorted_assignments:
            current_phase["assignments"].append({
                "assignment_id": assignment.id,
                "employee_id": assignment.employee_id,
                "role": assignment.role_in_project
            })
        
        # Simplificación: crear una fase única por ahora
        if sorted_assignments:
            end_dates = [a.end_date for a in sorted_assignments if a.end_date]
            current_phase["end_date"] = max(end_dates) if end_dates else None
            current_phase["team_size"] = len(set(a.employee_id for a in sorted_assignments))
        
        phases.append(current_phase)
        
        return phases
    
    def _generate_project_milestones(self, assignments: List[ProjectAssignment]) -> List[Dict[str, Any]]:
        """Genera hitos del proyecto."""
        milestones = []
        
        if not assignments:
            return milestones
        
        # Hito de inicio del proyecto
        start_date = min(a.start_date for a in assignments)
        milestones.append({
            "milestone_name": "Inicio del Proyecto",
            "date": start_date,
            "description": "Inicio de las primeras asignaciones del proyecto",
            "milestone_type": "start"
        })
        
        # Hito de máxima capacidad
        active_assignments = [a for a in assignments if a.is_active]
        if active_assignments:
            milestones.append({
                "milestone_name": "Máxima Capacidad",
                "date": start_date,  # Simplificación
                "description": f"Proyecto con {len(active_assignments)} asignaciones activas",
                "milestone_type": "peak"
            })
        
        # Hito de finalización (si hay fechas de fin)
        end_dates = [a.end_date for a in assignments if a.end_date]
        if end_dates:
            end_date = max(end_dates)
            milestones.append({
                "milestone_name": "Finalización Planificada",
                "date": end_date,
                "description": "Finalización de las últimas asignaciones",
                "milestone_type": "end"
            })
        
        return milestones
    
    def _generate_resource_timeline(self, assignments: List[ProjectAssignment]) -> List[Dict[str, Any]]:
        """Genera la línea de tiempo de recursos."""
        resource_timeline = []
        
        # Agrupar por empleado y crear entradas de timeline
        employee_assignments = defaultdict(list)
        for assignment in assignments:
            employee_assignments[assignment.employee_id].append(assignment)
        
        for employee_id, emp_assignments in employee_assignments.items():
            for assignment in emp_assignments:
                resource_timeline.append({
                    "employee_id": employee_id,
                    "assignment_id": assignment.id,
                    "start_date": assignment.start_date,
                    "end_date": assignment.end_date,
                    "role": assignment.role_in_project,
                    "allocation_percentage": float(assignment.percentage_allocation or 0),
                    "hours_per_day": float(assignment.allocated_hours_per_day or 0),
                    "is_active": assignment.is_active
                })
        
        # Ordenar por fecha de inicio
        resource_timeline.sort(key=lambda x: x["start_date"])
        
        return resource_timeline
    
    def _generate_critical_path(self, assignments: List[ProjectAssignment]) -> List[Dict[str, Any]]:
        """Genera la ruta crítica del proyecto."""
        critical_path = []
        
        if not assignments:
            return critical_path
        
        # Simplificación: identificar asignaciones críticas por duración y rol
        for assignment in assignments:
            # Considerar críticas las asignaciones de larga duración o roles clave
            duration = None
            if assignment.end_date:
                duration = (assignment.end_date - assignment.start_date).days
            
            is_critical = (
                duration and duration > 30 or  # Asignaciones largas
                assignment.percentage_allocation and assignment.percentage_allocation > 80 or  # Alta dedicación
                assignment.role_in_project and any(keyword in assignment.role_in_project.lower() 
                                                 for keyword in ['lead', 'manager', 'architect', 'senior'])
            )
            
            if is_critical:
                critical_path.append({
                    "assignment_id": assignment.id,
                    "employee_id": assignment.employee_id,
                    "role": assignment.role_in_project,
                    "start_date": assignment.start_date,
                    "end_date": assignment.end_date,
                    "duration_days": duration,
                    "allocation_percentage": float(assignment.percentage_allocation or 0),
                    "criticality_reason": self._determine_criticality_reason(assignment, duration)
                })
        
        # Ordenar por fecha de inicio
        critical_path.sort(key=lambda x: x["start_date"])
        
        return critical_path
    
    def _determine_criticality_reason(self, assignment: ProjectAssignment, duration: Optional[int]) -> str:
        """Determina la razón de criticidad de una asignación."""
        reasons = []
        
        if duration and duration > 30:
            reasons.append("Larga duración")
        
        if assignment.percentage_allocation and assignment.percentage_allocation > 80:
            reasons.append("Alta dedicación")
        
        if assignment.role_in_project:
            role_lower = assignment.role_in_project.lower()
            if any(keyword in role_lower for keyword in ['lead', 'manager', 'architect', 'senior']):
                reasons.append("Rol clave")
        
        return ", ".join(reasons) if reasons else "Asignación crítica"
    
    def _validate_project_id(self, project_id: int) -> None:
        """
        Valida que el ID del proyecto sea válido.
        
        Args:
            project_id: ID del proyecto a validar
            
        Raises:
            ValidationError: Si el ID no es válido
        """
        if not isinstance(project_id, int) or project_id <= 0:
            raise ValidationError(
                message="ID de proyecto debe ser positivo",
                field="project_id",
                value=project_id
            )
    
    def _validate_date_range(self, start_date, end_date) -> None:
        """
        Valida que el rango de fechas sea válido.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Raises:
            ValidationError: Si el rango de fechas no es válido
        """
        if start_date and end_date and start_date > end_date:
            raise ValidationError(
                message="La fecha de fin debe ser posterior a la fecha de inicio",
                field="date_range",
                value=f"{start_date} - {end_date}"
            )