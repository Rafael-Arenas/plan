# src/planificador/services/domain/project_assignment/modules/employee_queries.py

"""
Módulo de consultas centradas en empleados para el dominio de asignaciones de proyecto.

Este módulo implementa las operaciones de consulta específicas para empleados,
proporcionando funcionalidades para obtener información detallada sobre las
asignaciones de empleados, su carga de trabajo, historial y asignación actual.

Métodos implementados según PROJECT_ASSIGNMENT_DOMAIN_SERVICE_METHODS.md:
- get_assignments_by_employee: Obtiene todas las asignaciones de un empleado
- get_active_assignments_by_employee: Obtiene asignaciones activas de un empleado
- get_employee_workload_summary: Genera resumen de carga de trabajo
- get_employee_assignment_history: Obtiene historial cronológico de asignaciones
- get_employee_current_allocation: Obtiene asignación actual detallada
"""

from typing import List, Optional, Dict, Any
from datetime import date
from loguru import logger

from planificador.schemas import ProjectAssignment
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.exceptions import RepositoryError, ValidationError
from ..interfaces import IEmployeeQueries


class EmployeeQueries(IEmployeeQueries):
    """
    Implementa operaciones de consulta centradas en empleados.
    
    Esta clase proporciona métodos especializados para consultar información
    relacionada con empleados y sus asignaciones de proyecto.
    """
    
    def __init__(self, repository_facade: ProjectAssignmentRepositoryFacade):
        """Inicializa el módulo de consultas de empleados."""
        self._repository = repository_facade
        self._logger = logger.bind(module="employee_queries")
    
    # ============================================================================
    # MÉTODOS DOCUMENTADOS OFICIALMENTE
    # ============================================================================
    
    async def get_assignments_by_employee(
        self, 
        employee_id: int, 
        include_inactive: bool = False
    ) -> List[ProjectAssignment]:
        """
        Obtiene todas las asignaciones de un empleado específico.
        
        Args:
            employee_id: ID del empleado
            include_inactive: Si incluir asignaciones inactivas
            
        Returns:
            List[ProjectAssignment]: Lista de asignaciones del empleado
            
        Raises:
            ValidationError: Si el employee_id no es válido
            RepositoryError: Si hay errores en la consulta
        """
        try:
            self._logger.info(
                f"Obteniendo asignaciones del empleado {employee_id} "
                f"(incluir inactivas: {include_inactive})"
            )
            
            # Validar employee_id
            if employee_id <= 0:
                raise ValidationError(
                    message="El ID del empleado debe ser un número positivo",
                    field="employee_id",
                    value=employee_id
                )
            
            # Obtener asignaciones
            assignments = await self._repository.queries.get_assignments_by_employee(
                employee_id=employee_id,
                include_inactive=include_inactive
            )
            
            self._logger.info(
                f"Se encontraron {len(assignments)} asignaciones para el empleado {employee_id}"
            )
            return assignments
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(
                f"Error al obtener asignaciones del empleado {employee_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error al obtener asignaciones del empleado: {e}",
                operation="get_assignments_by_employee",
                entity_type="ProjectAssignment",
                entity_id=employee_id,
                original_error=e
            )
    
    async def get_active_assignments_by_employee(
        self, 
        employee_id: int, 
        reference_date: Optional[date] = None
    ) -> List[ProjectAssignment]:
        """
        Obtiene las asignaciones activas de un empleado en una fecha específica.
        
        Args:
            employee_id: ID del empleado
            reference_date: Fecha de referencia (por defecto: fecha actual)
            
        Returns:
            List[ProjectAssignment]: Lista de asignaciones activas
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay errores en la consulta
        """
        try:
            if reference_date is None:
                from pendulum import now
                reference_date = now().date()
            
            self._logger.info(
                f"Obteniendo asignaciones activas del empleado {employee_id} "
                f"para la fecha {reference_date}"
            )
            
            # Validar employee_id
            if employee_id <= 0:
                raise ValidationError(
                    message="El ID del empleado debe ser un número positivo",
                    field="employee_id",
                    value=employee_id
                )
            
            # Obtener asignaciones activas
            active_assignments = await self._repository.queries.get_active_assignments_by_employee(
                employee_id=employee_id,
                reference_date=reference_date
            )
            
            self._logger.info(
                f"Se encontraron {len(active_assignments)} asignaciones activas "
                f"para el empleado {employee_id} en {reference_date}"
            )
            return active_assignments
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(
                f"Error al obtener asignaciones activas del empleado {employee_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error al obtener asignaciones activas del empleado: {e}",
                operation="get_active_assignments_by_employee",
                entity_type="ProjectAssignment",
                entity_id=employee_id,
                original_error=e
            )
    
    async def get_employee_workload_summary(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """
        Genera un resumen completo de la carga de trabajo de un empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Dict[str, Any]: Resumen detallado de carga de trabajo
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay errores en el cálculo
        """
        try:
            self._logger.info(
                f"Generando resumen de carga de trabajo para empleado {employee_id} "
                f"del {start_date} al {end_date}"
            )
            
            # Validaciones
            if employee_id <= 0:
                raise ValidationError(
                    message="El ID del empleado debe ser un número positivo",
                    field="employee_id",
                    value=employee_id
                )
            
            if start_date >= end_date:
                raise ValidationError(
                    message="La fecha de inicio debe ser anterior a la fecha de fin",
                    field="date_range",
                    value=f"{start_date} - {end_date}"
                )
            
            # Obtener asignaciones en el período
            assignments = await self._repository.queries.get_assignments_by_date_range(
                employee_id=employee_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Calcular métricas de carga de trabajo
            workload_summary = await self._calculate_workload_metrics(
                assignments, start_date, end_date
            )
            
            # Agregar información del empleado
            workload_summary.update({
                "employee_id": employee_id,
                "period_start": start_date,
                "period_end": end_date,
                "total_assignments": len(assignments)
            })
            
            self._logger.info(
                f"Resumen de carga de trabajo generado para empleado {employee_id}: "
                f"{workload_summary['total_assignments']} asignaciones, "
                f"{workload_summary.get('total_allocated_percentage', 0)}% asignación total"
            )
            
            return workload_summary
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(
                f"Error al generar resumen de carga de trabajo para empleado {employee_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error al generar resumen de carga de trabajo: {e}",
                operation="get_employee_workload_summary",
                entity_type="ProjectAssignment",
                entity_id=employee_id,
                original_error=e
            )
    
    async def get_employee_assignment_history(
        self, 
        employee_id: int, 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene el historial cronológico de asignaciones de un empleado.
        
        Args:
            employee_id: ID del empleado
            limit: Límite de registros a retornar (opcional)
            
        Returns:
            List[Dict[str, Any]]: Historial cronológico de asignaciones
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay errores en la consulta
        """
        try:
            self._logger.info(
                f"Obteniendo historial de asignaciones del empleado {employee_id} "
                f"(límite: {limit or 'sin límite'})"
            )
            
            # Validar employee_id
            if employee_id <= 0:
                raise ValidationError(
                    message="El ID del empleado debe ser un número positivo",
                    field="employee_id",
                    value=employee_id
                )
            
            # Validar límite si se proporciona
            if limit is not None and limit <= 0:
                raise ValidationError(
                    message="El límite debe ser un número positivo",
                    field="limit",
                    value=limit
                )
            
            # Obtener todas las asignaciones del empleado
            all_assignments = await self._repository.queries.get_assignments_by_employee(
                employee_id=employee_id,
                include_inactive=True
            )
            
            # Ordenar por fecha de inicio (más reciente primero)
            sorted_assignments = sorted(
                all_assignments,
                key=lambda x: x.start_date,
                reverse=True
            )
            
            # Aplicar límite si se especifica
            if limit:
                sorted_assignments = sorted_assignments[:limit]
            
            # Generar historial enriquecido
            history = []
            for assignment in sorted_assignments:
                history_entry = {
                    "assignment_id": assignment.id,
                    "project_id": assignment.project_id,
                    "role_in_project": assignment.role_in_project,
                    "start_date": assignment.start_date,
                    "end_date": assignment.end_date,
                    "percentage_allocation": assignment.percentage_allocation,
                    "allocated_hours_per_day": assignment.allocated_hours_per_day,
                    "is_active": assignment.is_active,
                    "duration_days": (assignment.end_date - assignment.start_date).days,
                    "created_at": assignment.created_at,
                    "updated_at": assignment.updated_at,
                    "notes": assignment.notes
                }
                history.append(history_entry)
            
            self._logger.info(
                f"Historial generado para empleado {employee_id}: {len(history)} registros"
            )
            return history
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(
                f"Error al obtener historial del empleado {employee_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error al obtener historial del empleado: {e}",
                operation="get_employee_assignment_history",
                entity_type="ProjectAssignment",
                entity_id=employee_id,
                original_error=e
            )
    
    async def get_employee_current_allocation(self, employee_id: int) -> Dict[str, Any]:
        """
        Obtiene la asignación actual detallada de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Dict[str, Any]: Información detallada de asignación actual
            
        Raises:
            ValidationError: Si el employee_id no es válido
            RepositoryError: Si hay errores en el cálculo
        """
        try:
            from pendulum import now
            current_date = now().date()
            
            self._logger.info(
                f"Obteniendo asignación actual del empleado {employee_id} "
                f"para la fecha {current_date}"
            )
            
            # Validar employee_id
            if employee_id <= 0:
                raise ValidationError(
                    message="El ID del empleado debe ser un número positivo",
                    field="employee_id",
                    value=employee_id
                )
            
            # Obtener asignaciones activas actuales
            current_assignments = await self.get_active_assignments_by_employee(
                employee_id=employee_id,
                reference_date=current_date
            )
            
            # Calcular métricas de asignación actual
            total_percentage = sum(
                assignment.percentage_allocation for assignment in current_assignments
            )
            total_hours_per_day = sum(
                assignment.allocated_hours_per_day for assignment in current_assignments
            )
            
            # Agrupar por proyecto
            projects_allocation = {}
            for assignment in current_assignments:
                project_id = assignment.project_id
                if project_id not in projects_allocation:
                    projects_allocation[project_id] = {
                        "project_id": project_id,
                        "assignments": [],
                        "total_percentage": 0,
                        "total_hours_per_day": 0
                    }
                
                projects_allocation[project_id]["assignments"].append({
                    "assignment_id": assignment.id,
                    "role_in_project": assignment.role_in_project,
                    "percentage_allocation": assignment.percentage_allocation,
                    "allocated_hours_per_day": assignment.allocated_hours_per_day,
                    "start_date": assignment.start_date,
                    "end_date": assignment.end_date
                })
                projects_allocation[project_id]["total_percentage"] += assignment.percentage_allocation
                projects_allocation[project_id]["total_hours_per_day"] += assignment.allocated_hours_per_day
            
            # Determinar estado de capacidad
            capacity_status = self._determine_capacity_status(total_percentage)
            
            current_allocation = {
                "employee_id": employee_id,
                "reference_date": current_date,
                "total_active_assignments": len(current_assignments),
                "total_percentage_allocation": total_percentage,
                "total_hours_per_day": total_hours_per_day,
                "capacity_status": capacity_status,
                "projects_allocation": list(projects_allocation.values()),
                "availability_percentage": max(0, 100 - total_percentage),
                "is_overallocated": total_percentage > 100,
                "is_fully_allocated": total_percentage >= 100,
                "has_capacity": total_percentage < 100
            }
            
            self._logger.info(
                f"Asignación actual calculada para empleado {employee_id}: "
                f"{total_percentage}% asignado en {len(current_assignments)} proyectos"
            )
            
            return current_allocation
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(
                f"Error al obtener asignación actual del empleado {employee_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error al obtener asignación actual del empleado: {e}",
                operation="get_employee_current_allocation",
                entity_type="ProjectAssignment",
                entity_id=employee_id,
                original_error=e
            )
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE CÁLCULO
    # ============================================================================
    
    async def _calculate_workload_metrics(
        self, 
        assignments: List[ProjectAssignment], 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Calcula métricas detalladas de carga de trabajo."""
        if not assignments:
            return {
                "total_allocated_percentage": 0,
                "total_allocated_hours_per_day": 0,
                "average_allocation_percentage": 0,
                "peak_allocation_percentage": 0,
                "projects_count": 0,
                "roles_distribution": {},
                "allocation_periods": []
            }
        
        # Calcular métricas básicas
        total_percentage = sum(assignment.percentage_allocation for assignment in assignments)
        total_hours = sum(assignment.allocated_hours_per_day for assignment in assignments)
        average_percentage = total_percentage / len(assignments)
        peak_percentage = max(assignment.percentage_allocation for assignment in assignments)
        
        # Distribución por roles
        roles_distribution = {}
        for assignment in assignments:
            role = assignment.role_in_project
            if role not in roles_distribution:
                roles_distribution[role] = {
                    "count": 0,
                    "total_percentage": 0,
                    "total_hours": 0
                }
            roles_distribution[role]["count"] += 1
            roles_distribution[role]["total_percentage"] += assignment.percentage_allocation
            roles_distribution[role]["total_hours"] += assignment.allocated_hours_per_day
        
        # Períodos de asignación
        allocation_periods = []
        for assignment in assignments:
            allocation_periods.append({
                "assignment_id": assignment.id,
                "project_id": assignment.project_id,
                "start_date": assignment.start_date,
                "end_date": assignment.end_date,
                "percentage_allocation": assignment.percentage_allocation,
                "role_in_project": assignment.role_in_project
            })
        
        return {
            "total_allocated_percentage": total_percentage,
            "total_allocated_hours_per_day": total_hours,
            "average_allocation_percentage": round(average_percentage, 2),
            "peak_allocation_percentage": peak_percentage,
            "projects_count": len(set(assignment.project_id for assignment in assignments)),
            "roles_distribution": roles_distribution,
            "allocation_periods": allocation_periods
        }
    
    def _determine_capacity_status(self, total_percentage: float) -> str:
        """Determina el estado de capacidad basado en el porcentaje total."""
        if total_percentage == 0:
            return "available"
        elif total_percentage < 50:
            return "low_utilization"
        elif total_percentage < 80:
            return "moderate_utilization"
        elif total_percentage < 100:
            return "high_utilization"
        elif total_percentage == 100:
            return "fully_allocated"
        else:
            return "overallocated"