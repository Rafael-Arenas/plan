"""Módulo de operaciones de estadísticas para asignaciones de proyectos.

Este módulo implementa la interfaz IStatisticsOperations y proporciona
funcionalidades para generar estadísticas y métricas sobre las asignaciones.

Versión: 1.0.0
"""

from typing import Any
from datetime import date, timedelta
from collections import Counter

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from planificador.models.project_assignment import ProjectAssignment
from planificador.repositories.base_repository import BaseRepository
from ..interfaces.statistics_interface import IStatisticsOperations


class StatisticsOperations(BaseRepository[ProjectAssignment], IStatisticsOperations):
    """Implementación de operaciones de estadísticas para asignaciones de proyectos.

    Hereda de BaseRepository y se especializa en generar estadísticas
    y métricas sobre las asignaciones de proyectos.
    """

    def __init__(self, session: AsyncSession):
        """Inicializa las operaciones de estadísticas.

        Args:
            session: Sesión asíncrona de SQLAlchemy.
        """
        super().__init__(session, ProjectAssignment)
        self._logger = self._logger.bind(component="ProjectAssignmentStatisticsOperations")
        self._logger.debug("StatisticsOperations para ProjectAssignment inicializado")

    async def get_total_assignments_count(self) -> int:
        """Obtiene el número total de asignaciones.
        
        Returns:
            Número total de asignaciones
        """
        self._logger.debug("Obteniendo conteo total de asignaciones")
        return await self.count()

    async def get_active_assignments_count(self) -> int:
        """Obtiene el número de asignaciones activas.
        
        Returns:
            Número de asignaciones activas
        """
        self._logger.debug("Obteniendo conteo de asignaciones activas")
        return await self.count_by_criteria({"is_active": True})

    async def get_assignments_by_status(self) -> dict[str, int]:
        """Obtiene el conteo de asignaciones por estado.
        
        Returns:
            Diccionario con conteos por estado
        """
        self._logger.debug("Obteniendo estadísticas por estado")
        
        active_count = await self.count_by_criteria({"is_active": True})
        inactive_count = await self.count_by_criteria({"is_active": False})
        
        return {
            "active": active_count,
            "inactive": inactive_count,
            "total": active_count + inactive_count
        }

    async def get_assignments_by_allocation_category(self) -> dict[str, int]:
        """Obtiene el conteo de asignaciones por categoría de asignación.
        
        Returns:
            Diccionario con conteos por categoría de asignación
        """
        self._logger.debug("Obteniendo estadísticas por categoría de asignación")
        
        assignments = await self.get_all()
        
        categories = {
            "low": 0,      # 0-25%
            "medium": 0,   # 26-50%
            "high": 0,     # 51-75%
            "full": 0      # 76-100%
        }
        
        for assignment in assignments:
            allocation = assignment.allocation_percentage or 0
            if allocation <= 25:
                categories["low"] += 1
            elif allocation <= 50:
                categories["medium"] += 1
            elif allocation <= 75:
                categories["high"] += 1
            else:
                categories["full"] += 1
        
        return categories

    async def get_employee_assignment_stats(self, employee_id: int) -> dict[str, Any]:
        """Obtiene estadísticas de asignaciones para un empleado específico.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Diccionario con estadísticas del empleado
        """
        self._logger.debug(f"Obteniendo estadísticas para empleado {employee_id}")
        
        assignments = await self.find_by_criteria({"employee_id": employee_id})
        
        total_count = len(assignments)
        active_count = len([a for a in assignments if a.is_active])
        total_allocation = sum(a.allocation_percentage or 0 for a in assignments)
        avg_allocation = total_allocation / total_count if total_count > 0 else 0
        
        projects = list(set(a.project_id for a in assignments))
        roles = [a.role for a in assignments if a.role]
        role_counts = Counter(roles)
        
        return {
            "employee_id": employee_id,
            "total_assignments": total_count,
            "active_assignments": active_count,
            "inactive_assignments": total_count - active_count,
            "total_allocation_percentage": total_allocation,
            "average_allocation_percentage": round(avg_allocation, 2),
            "unique_projects": len(projects),
            "role_distribution": dict(role_counts),
            "most_common_role": role_counts.most_common(1)[0][0] if role_counts else None
        }

    async def get_project_assignment_stats(self, project_id: int) -> dict[str, Any]:
        """Obtiene estadísticas de asignaciones para un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Diccionario con estadísticas del proyecto
        """
        self._logger.debug(f"Obteniendo estadísticas para proyecto {project_id}")
        
        assignments = await self.find_by_criteria({"project_id": project_id})
        
        total_count = len(assignments)
        active_count = len([a for a in assignments if a.is_active])
        total_allocation = sum(a.allocation_percentage or 0 for a in assignments)
        avg_allocation = total_allocation / total_count if total_count > 0 else 0
        
        employees = list(set(a.employee_id for a in assignments))
        roles = [a.role for a in assignments if a.role]
        role_counts = Counter(roles)
        
        return {
            "project_id": project_id,
            "total_assignments": total_count,
            "active_assignments": active_count,
            "inactive_assignments": total_count - active_count,
            "total_allocation_percentage": total_allocation,
            "average_allocation_percentage": round(avg_allocation, 2),
            "unique_employees": len(employees),
            "role_distribution": dict(role_counts),
            "team_size": len(employees)
        }

    async def get_assignment_duration_stats(self) -> dict[str, Any]:
        """Obtiene estadísticas de duración de asignaciones.
        
        Returns:
            Diccionario con estadísticas de duración
        """
        self._logger.debug("Obteniendo estadísticas de duración")
        
        assignments = await self.get_all()
        durations = []
        
        for assignment in assignments:
            if assignment.start_date and assignment.end_date:
                duration = (assignment.end_date - assignment.start_date).days
                durations.append(duration)
        
        if not durations:
            return {
                "total_assignments_with_dates": 0,
                "average_duration_days": 0,
                "min_duration_days": 0,
                "max_duration_days": 0,
                "median_duration_days": 0
            }
        
        durations.sort()
        count = len(durations)
        median = durations[count // 2] if count % 2 == 1 else (durations[count // 2 - 1] + durations[count // 2]) / 2
        
        return {
            "total_assignments_with_dates": count,
            "average_duration_days": round(sum(durations) / count, 2),
            "min_duration_days": min(durations),
            "max_duration_days": max(durations),
            "median_duration_days": round(median, 2)
        }

    async def get_workload_distribution(self) -> dict[str, Any]:
        """Obtiene la distribución de carga de trabajo por empleado.
        
        Returns:
            Diccionario con distribución de carga de trabajo
        """
        self._logger.debug("Obteniendo distribución de carga de trabajo")
        
        assignments = await self.find_by_criteria({"is_active": True})
        
        employee_workloads = {}
        for assignment in assignments:
            employee_id = assignment.employee_id
            allocation = assignment.allocation_percentage or 0
            
            if employee_id not in employee_workloads:
                employee_workloads[employee_id] = {
                    "total_allocation": 0,
                    "assignment_count": 0
                }
            
            employee_workloads[employee_id]["total_allocation"] += allocation
            employee_workloads[employee_id]["assignment_count"] += 1
        
        # Categorizar empleados por carga de trabajo
        categories = {
            "underutilized": 0,  # < 50%
            "balanced": 0,       # 50-100%
            "overallocated": 0   # > 100%
        }
        
        for workload in employee_workloads.values():
            total = workload["total_allocation"]
            if total < 50:
                categories["underutilized"] += 1
            elif total <= 100:
                categories["balanced"] += 1
            else:
                categories["overallocated"] += 1
        
        return {
            "employee_workloads": employee_workloads,
            "workload_categories": categories,
            "total_active_employees": len(employee_workloads)
        }

    async def get_assignment_trends(self, days: int = 30) -> dict[str, Any]:
        """Obtiene tendencias de asignaciones en los últimos días.
        
        Args:
            days: Número de días hacia atrás para analizar
            
        Returns:
            Diccionario con tendencias de asignaciones
        """
        self._logger.debug(f"Obteniendo tendencias de los últimos {days} días")
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Asignaciones creadas en el período
        recent_assignments = await self.find_by_criteria({
            "created_at": {"operator": ">=", "value": start_date}
        })
        
        # Asignaciones que terminan en el período
        ending_assignments = await self.find_by_criteria({
            "end_date": {"operator": ">=", "value": start_date},
            "end_date": {"operator": "<=", "value": end_date}
        })
        
        return {
            "period_days": days,
            "start_date": start_date,
            "end_date": end_date,
            "new_assignments": len(recent_assignments),
            "ending_assignments": len(ending_assignments),
            "net_change": len(recent_assignments) - len(ending_assignments)
        }

    async def get_overlap_statistics(self) -> dict[str, Any]:
        """Obtiene estadísticas de superposición de asignaciones.
        
        Returns:
            Diccionario con estadísticas de superposición
        """
        self._logger.debug("Obteniendo estadísticas de superposición")
        
        active_assignments = await self.find_by_criteria({"is_active": True})
        
        # Agrupar por empleado
        employee_assignments = {}
        for assignment in active_assignments:
            employee_id = assignment.employee_id
            if employee_id not in employee_assignments:
                employee_assignments[employee_id] = []
            employee_assignments[employee_id].append(assignment)
        
        overlap_count = 0
        employees_with_overlaps = 0
        
        for employee_id, assignments in employee_assignments.items():
            if len(assignments) > 1:
                # Verificar superposiciones
                has_overlap = False
                for i, assignment1 in enumerate(assignments):
                    for assignment2 in assignments[i+1:]:
                        if (assignment1.start_date <= assignment2.end_date and 
                            assignment1.end_date >= assignment2.start_date):
                            overlap_count += 1
                            has_overlap = True
                
                if has_overlap:
                    employees_with_overlaps += 1
        
        return {
            "total_overlapping_assignments": overlap_count,
            "employees_with_overlaps": employees_with_overlaps,
            "total_active_employees": len(employee_assignments),
            "overlap_percentage": round(
                (employees_with_overlaps / len(employee_assignments)) * 100, 2
            ) if employee_assignments else 0
        }

    async def get_role_distribution(self) -> dict[str, int]:
        """Obtiene la distribución de asignaciones por rol.
        
        Returns:
            Diccionario con conteos por rol
        """
        self._logger.debug("Obteniendo distribución por roles")
        
        assignments = await self.get_all()
        roles = [a.role for a in assignments if a.role]
        role_counts = Counter(roles)
        
        return dict(role_counts)

    async def get_dashboard_metrics(self) -> dict[str, Any]:
        """Obtiene métricas principales para dashboard.
        
        Returns:
            Diccionario con métricas principales
        """
        self._logger.debug("Obteniendo métricas para dashboard")
        
        total_assignments = await self.get_total_assignments_count()
        active_assignments = await self.get_active_assignments_count()
        status_stats = await self.get_assignments_by_status()
        allocation_stats = await self.get_assignments_by_allocation_category()
        workload_stats = await self.get_workload_distribution()
        overlap_stats = await self.get_overlap_statistics()
        
        return {
            "summary": {
                "total_assignments": total_assignments,
                "active_assignments": active_assignments,
                "inactive_assignments": total_assignments - active_assignments,
                "activity_rate": round(
                    (active_assignments / total_assignments) * 100, 2
                ) if total_assignments > 0 else 0
            },
            "allocation_distribution": allocation_stats,
            "workload_summary": {
                "total_employees": workload_stats["total_active_employees"],
                "overallocated_employees": workload_stats["workload_categories"]["overallocated"],
                "balanced_employees": workload_stats["workload_categories"]["balanced"],
                "underutilized_employees": workload_stats["workload_categories"]["underutilized"]
            },
            "overlap_summary": {
                "overlapping_assignments": overlap_stats["total_overlapping_assignments"],
                "employees_with_overlaps": overlap_stats["employees_with_overlaps"],
                "overlap_rate": overlap_stats["overlap_percentage"]
            }
        }

    async def get_assignment_count(self) -> int:
        """Obtiene el número total de asignaciones.
        
        Returns:
            Número total de asignaciones
        """
        self._logger.debug("Obteniendo conteo total de asignaciones")
        return await self.get_total_assignments_count()

    async def get_active_assignment_count(self) -> int:
        """Obtiene el número de asignaciones activas.
        
        Returns:
            Número de asignaciones activas
        """
        self._logger.debug("Obteniendo conteo de asignaciones activas")
        return await self.get_active_assignments_count()

    async def get_comprehensive_dashboard_metrics(self) -> dict[str, Any]:
        """Obtiene métricas completas para dashboard.
        
        Returns:
            Diccionario con métricas completas
        """
        self._logger.debug("Obteniendo métricas completas para dashboard")
        return await self.get_dashboard_metrics()

    async def get_by_unique_field(self, field_name: str, value: Any) -> ProjectAssignment | None:
        """Obtiene una asignación por un campo único delegando en el repositorio base.
        
        Args:
            field_name: Nombre del campo único
            value: Valor del campo
            
        Returns:
            Asignación encontrada o None si no existe
        """
        self._logger.debug(f"Obteniendo asignación por {field_name}: {value}")
        return await self.get_by_field(field_name, value)