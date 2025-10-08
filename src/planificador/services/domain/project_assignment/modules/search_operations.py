# src/planificador/services/domain/project_assignment/modules/search_operations.py

"""
Módulo de Operaciones de Búsqueda para Asignaciones de Proyecto

Implementa operaciones especializadas de búsqueda, filtrado y consultas
complejas para asignaciones de proyecto, incluyendo filtros avanzados,
rangos de fechas, búsquedas por rol y detección de solapamientos.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import date
from decimal import Decimal
from loguru import logger
from collections import defaultdict

from planificador.schemas.assignment.assignment import ProjectAssignment
from planificador.schemas.assignment.advanced_schemas import (
    AssignmentAdvancedFilters,
    ProjectAssignmentResponseSchema
)
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.exceptions import RepositoryError, ValidationError
from ..interfaces import ISearchOperations


class SearchOperations(ISearchOperations):
    """
    Implementación de operaciones de búsqueda para asignaciones de proyecto.
    
    Proporciona métodos especializados para realizar búsquedas complejas,
    aplicar filtros avanzados, buscar por rangos de fechas, roles específicos
    y detectar solapamientos entre asignaciones.
    """
    
    def __init__(self, repository_facade: ProjectAssignmentRepositoryFacade):
        """
        Inicializa el módulo de operaciones de búsqueda.
        
        Args:
            repository_facade: Facade del repositorio de asignaciones
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="project_assignment_search_operations")
    
    async def get_assignments_with_filters(
        self, 
        filters: AssignmentAdvancedFilters
    ) -> List[ProjectAssignmentResponseSchema]:
        """
        Busca asignaciones aplicando filtros avanzados múltiples.
        
        Args:
            filters: Filtros avanzados a aplicar
            
        Returns:
            List[ProjectAssignmentResponseSchema]: Lista de asignaciones filtradas
            
        Raises:
            ValidationError: Si los filtros no son válidos
            RepositoryError: Si hay errores en la base de datos
        """
        self._logger.debug(f"Aplicando filtros avanzados: {filters}")
        
        try:
            # Validar filtros
            await self._validate_filters(filters)
            
            # Obtener todas las asignaciones base
            base_assignments = await self._repository.queries.get_all_assignments()
            
            # Aplicar filtros secuencialmente
            filtered_assignments = await self._apply_advanced_filters(base_assignments, filters)
            
            # Convertir a esquemas de respuesta
            response_assignments = []
            for assignment in filtered_assignments:
                response_schema = await self._convert_to_response_schema(assignment)
                response_assignments.append(response_schema)
            
            # Aplicar ordenamiento si se especifica
            if hasattr(filters, 'sort_by') and filters.sort_by:
                sort_order = getattr(filters, 'sort_order', 'asc')
                response_assignments = self._sort_assignments(response_assignments, filters.sort_by, sort_order)
            
            # Aplicar paginación si se especifica
            limit = getattr(filters, 'limit', None)
            offset = getattr(filters, 'offset', None)
            if limit or offset:
                response_assignments = self._paginate_assignments(
                    response_assignments, 
                    limit, 
                    offset or 0
                )
            
            self._logger.info(
                f"Filtros aplicados exitosamente: {len(response_assignments)} asignaciones encontradas"
            )
            
            return response_assignments
            
        except Exception as e:
            self._logger.error(f"Error aplicando filtros avanzados: {e}")
            if isinstance(e, (RepositoryError, ValidationError)):
                raise
            raise RepositoryError(
                message=f"Error inesperado aplicando filtros: {e}",
                operation="get_assignments_with_filters",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    async def get_assignments_by_date_range(
        self, 
        start_date: date, 
        end_date: date,
        include_partial_overlap: bool = True
    ) -> List[ProjectAssignment]:
        """
        Busca asignaciones dentro de un rango de fechas específico.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            include_partial_overlap: Si incluir asignaciones con solapamiento parcial
            
        Returns:
            List[ProjectAssignment]: Lista de asignaciones en el rango
            
        Raises:
            ValidationError: Si el rango de fechas no es válido
            RepositoryError: Si hay errores en la base de datos
        """
        self._logger.debug(
            f"Buscando asignaciones en rango: {start_date} - {end_date}, "
            f"solapamiento parcial: {include_partial_overlap}"
        )
        
        # Validar rango de fechas
        if start_date > end_date:
            raise ValidationError(
                message="La fecha de inicio debe ser anterior a la fecha de fin",
                field="date_range",
                value=f"{start_date} - {end_date}"
            )
        
        try:
            # Obtener todas las asignaciones
            all_assignments = await self._repository.queries.get_all_assignments()
            
            # Filtrar por rango de fechas
            filtered_assignments = []
            for assignment in all_assignments:
                if self._assignment_in_date_range(assignment, start_date, end_date, include_partial_overlap):
                    filtered_assignments.append(assignment)
            
            self._logger.info(
                f"Encontradas {len(filtered_assignments)} asignaciones en el rango "
                f"{start_date} - {end_date}"
            )
            
            return filtered_assignments
            
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo asignaciones por rango de fechas: {e}")
            if isinstance(e, (RepositoryError, ValidationError)):
                raise
            raise RepositoryError(
                message=f"Error inesperado obteniendo asignaciones por rango de fechas: {e}",
                operation="get_assignments_by_date_range",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    def _assignment_start_date_in_range(
        self, 
        assignment: ProjectAssignment, 
        start_date_from: Optional[date], 
        start_date_to: Optional[date]
    ) -> bool:
        """Verifica si la fecha de inicio de una asignación está dentro del rango especificado."""
        
        assignment_start = assignment.start_date
        if not assignment_start:
            return False
        
        if start_date_from and assignment_start < start_date_from:
            return False
        
        if start_date_to and assignment_start > start_date_to:
            return False
        
        return True
    
    def _assignment_end_date_in_range(
        self, 
        assignment: ProjectAssignment, 
        end_date_from: Optional[date], 
        end_date_to: Optional[date]
    ) -> bool:
        """Verifica si la fecha de fin de una asignación está dentro del rango especificado."""
        
        assignment_end = assignment.end_date
        if not assignment_end:
            # Si no tiene fecha de fin, consideramos que está activa indefinidamente
            return end_date_from is None
        
        if end_date_from and assignment_end < end_date_from:
            return False
        
        if end_date_to and assignment_end > end_date_to:
            return False
        
        return True

    async def get_assignments_by_role(
        self, 
        role: str,
        exact_match: bool = False
    ) -> List[ProjectAssignment]:
        """
        Busca asignaciones por rol específico en el proyecto.
        
        Args:
            role: Rol a buscar
            exact_match: Si buscar coincidencia exacta o parcial
            
        Returns:
            List[ProjectAssignment]: Lista de asignaciones con el rol especificado
            
        Raises:
            ValidationError: Si el rol no es válido
            RepositoryError: Si hay errores en la base de datos
        """
        self._logger.debug(f"Buscando asignaciones por rol: '{role}', exacto: {exact_match}")
        
        # Validar rol
        if not role or not role.strip():
            raise ValidationError(
                message="El rol no puede estar vacío",
                field="role",
                value=role
            )
        
        role = role.strip()
        
        try:
            # Obtener todas las asignaciones
            all_assignments = await self._repository.queries.get_all_assignments()
            
            # Filtrar por rol
            filtered_assignments = []
            for assignment in all_assignments:
                if self._assignment_matches_role(assignment, role, exact_match):
                    filtered_assignments.append(assignment)
            
            self._logger.info(
                f"Encontradas {len(filtered_assignments)} asignaciones con rol '{role}'"
            )
            
            return filtered_assignments
            
        except Exception as e:
            self._logger.error(f"Error buscando asignaciones por rol: {e}")
            if isinstance(e, (RepositoryError, ValidationError)):
                raise
            raise RepositoryError(
                message=f"Error inesperado buscando por rol: {e}",
                operation="get_assignments_by_role",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    async def get_overlapping_assignments(
        self, 
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None,
        threshold_percentage: float = 100.0
    ) -> List[Dict[str, Any]]:
        """
        Detecta asignaciones que se solapan temporalmente.
        
        Args:
            employee_id: ID del empleado (opcional, para filtrar)
            project_id: ID del proyecto (opcional, para filtrar)
            threshold_percentage: Umbral de solapamiento para considerar conflicto
            
        Returns:
            List[Dict[str, Any]]: Lista de grupos de asignaciones solapadas
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay errores en la base de datos
        """
        self._logger.debug(
            f"Detectando solapamientos - empleado: {employee_id}, "
            f"proyecto: {project_id}, umbral: {threshold_percentage}%"
        )
        
        # Validar parámetros
        if threshold_percentage < 0 or threshold_percentage > 200:
            raise ValidationError(
                message="El umbral de solapamiento debe estar entre 0 y 200%",
                field="threshold_percentage",
                value=threshold_percentage
            )
        
        try:
            # Obtener asignaciones base
            base_assignments = await self._get_assignments_for_overlap_detection(
                employee_id, project_id
            )
            
            # Detectar solapamientos
            overlapping_groups = await self._detect_overlapping_assignments(
                base_assignments, threshold_percentage
            )
            
            self._logger.info(
                f"Detectados {len(overlapping_groups)} grupos de asignaciones solapadas"
            )
            
            return overlapping_groups
            
        except Exception as e:
            self._logger.error(f"Error detectando solapamientos: {e}")
            if isinstance(e, (RepositoryError, ValidationError)):
                raise
            raise RepositoryError(
                message=f"Error inesperado detectando solapamientos: {e}",
                operation="get_overlapping_assignments",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE VALIDACIÓN Y FILTRADO
    # ============================================================================
    
    async def _validate_filters(self, filters: AssignmentAdvancedFilters) -> None:
        """Valida los filtros avanzados."""
        
        # Validar rango de fechas de inicio
        if filters.start_date_from and filters.start_date_to:
            if filters.start_date_from > filters.start_date_to:
                raise ValidationError(
                    message="La fecha de inicio 'desde' debe ser anterior a la fecha de inicio 'hasta'",
                    field="start_date_range",
                    value=f"{filters.start_date_from} - {filters.start_date_to}"
                )
        
        # Validar rango de fechas de fin
        if filters.end_date_from and filters.end_date_to:
            if filters.end_date_from > filters.end_date_to:
                raise ValidationError(
                    message="La fecha de fin 'desde' debe ser anterior a la fecha de fin 'hasta'",
                    field="end_date_range",
                    value=f"{filters.end_date_from} - {filters.end_date_to}"
                )
        
        # Validar porcentajes
        if filters.min_allocation_percentage is not None:
            if filters.min_allocation_percentage < 0 or filters.min_allocation_percentage > 100:
                raise ValidationError(
                    message="El porcentaje mínimo de asignación debe estar entre 0 y 100",
                    field="min_allocation_percentage",
                    value=filters.min_allocation_percentage
                )
        
        if filters.max_allocation_percentage is not None:
            if filters.max_allocation_percentage < 0 or filters.max_allocation_percentage > 100:
                raise ValidationError(
                    message="El porcentaje máximo de asignación debe estar entre 0 y 100",
                    field="max_allocation_percentage",
                    value=filters.max_allocation_percentage
                )
        
        # Validar coherencia de porcentajes
        if (filters.min_allocation_percentage is not None and 
            filters.max_allocation_percentage is not None):
            if filters.min_allocation_percentage > filters.max_allocation_percentage:
                raise ValidationError(
                    message="El porcentaje mínimo no puede ser mayor que el máximo",
                    field="allocation_percentage_range",
                    value=f"{filters.min_allocation_percentage} - {filters.max_allocation_percentage}"
                )
        
        # Validar horas
        if filters.min_hours_per_day is not None and filters.min_hours_per_day < 0:
            raise ValidationError(
                message="Las horas mínimas por día no pueden ser negativas",
                field="min_hours_per_day",
                value=filters.min_hours_per_day
            )
        
        if filters.max_hours_per_day is not None and filters.max_hours_per_day < 0:
            raise ValidationError(
                message="Las horas máximas por día no pueden ser negativas",
                field="max_hours_per_day",
                value=filters.max_hours_per_day
            )
    
    async def _apply_advanced_filters(
        self, 
        assignments: List[ProjectAssignment], 
        filters: AssignmentAdvancedFilters
    ) -> List[ProjectAssignment]:
        """Aplica los filtros avanzados a la lista de asignaciones."""
        
        filtered = assignments
        
        # Filtro por empleado
        if filters.employee_ids:
            filtered = [a for a in filtered if a.employee_id in filters.employee_ids]
        
        # Filtro por proyecto
        if filters.project_ids:
            filtered = [a for a in filtered if a.project_id in filters.project_ids]
        
        # Filtro por estado activo
        if filters.is_active is not None:
            filtered = [a for a in filtered if a.is_active == filters.is_active]
        
        # Filtro por rango de fechas de inicio
        if filters.start_date_from or filters.start_date_to:
            filtered = [
                a for a in filtered 
                if self._assignment_start_date_in_range(a, filters.start_date_from, filters.start_date_to)
            ]
        
        # Filtro por rango de fechas de fin
        if filters.end_date_from or filters.end_date_to:
            filtered = [
                a for a in filtered 
                if self._assignment_end_date_in_range(a, filters.end_date_from, filters.end_date_to)
            ]
        
        # Filtro por roles
        if filters.roles:
            filtered = [
                a for a in filtered 
                if a.role_in_project and a.role_in_project in filters.roles
            ]
        
        # Filtro por porcentaje de asignación
        if filters.min_allocation_percentage is not None:
            filtered = [
                a for a in filtered 
                if (a.percentage_allocation or 0) >= filters.min_allocation_percentage
            ]
        
        if filters.max_allocation_percentage is not None:
            filtered = [
                a for a in filtered 
                if (a.percentage_allocation or 0) <= filters.max_allocation_percentage
            ]
        
        # Filtro por horas por día
        if filters.min_hours_per_day is not None:
            filtered = [
                a for a in filtered 
                if (a.allocated_hours_per_day or 0) >= filters.min_hours_per_day
            ]
        
        if filters.max_hours_per_day is not None:
            filtered = [
                a for a in filtered 
                if (a.allocated_hours_per_day or 0) <= filters.max_hours_per_day
            ]
        
        # Filtro por texto en descripción o notas
        if filters.include_notes_search:
            search_text = filters.include_notes_search.lower()
            filtered = [
                a for a in filtered 
                if (a.notes and search_text in a.notes.lower()) or
                   (a.role_in_project and search_text in a.role_in_project.lower())
            ]
        
        return filtered
    
    def _assignment_in_date_range(
        self, 
        assignment: ProjectAssignment, 
        start_date: Optional[date], 
        end_date: Optional[date],
        include_partial_overlap: bool = True
    ) -> bool:
        """Verifica si una asignación está dentro del rango de fechas."""
        
        assignment_start = assignment.start_date
        assignment_end = assignment.end_date
        
        # Si no hay fecha de fin en la asignación, considerar como abierta
        if assignment_end is None:
            assignment_end = date.max
        
        # Si no se especifica rango, incluir todas
        if start_date is None and end_date is None:
            return True
        
        # Si solo se especifica fecha de inicio
        if start_date is not None and end_date is None:
            return assignment_end >= start_date
        
        # Si solo se especifica fecha de fin
        if start_date is None and end_date is not None:
            return assignment_start <= end_date
        
        # Rango completo especificado
        if include_partial_overlap:
            # Incluir si hay cualquier solapamiento
            return not (assignment_end < start_date or assignment_start > end_date)
        else:
            # Incluir solo si está completamente dentro del rango
            return assignment_start >= start_date and assignment_end <= end_date
    
    def _assignment_matches_role(
        self, 
        assignment: ProjectAssignment, 
        role: str, 
        exact_match: bool = False
    ) -> bool:
        """Verifica si una asignación coincide con el rol especificado."""
        
        if not assignment.role_in_project:
            return False
        
        assignment_role = assignment.role_in_project.strip()
        search_role = role.strip()
        
        if exact_match:
            return assignment_role.lower() == search_role.lower()
        else:
            return search_role.lower() in assignment_role.lower()
    
    async def _convert_to_response_schema(
        self, 
        assignment: ProjectAssignment
    ) -> ProjectAssignmentResponseSchema:
        """Convierte una asignación a esquema de respuesta con información adicional."""
        
        # Obtener información adicional del empleado y proyecto
        employee_info = await self._repository.queries.get_employee_basic_info(assignment.employee_id)
        project_info = await self._repository.queries.get_project_basic_info(assignment.project_id)
        
        return ProjectAssignmentResponseSchema(
            id=assignment.id,
            employee_id=assignment.employee_id,
            employee_name=employee_info.get("name", f"Empleado {assignment.employee_id}"),
            project_id=assignment.project_id,
            project_name=project_info.get("name", f"Proyecto {assignment.project_id}"),
            role_in_project=assignment.role_in_project,
            start_date=assignment.start_date,
            end_date=assignment.end_date,
            percentage_allocation=assignment.percentage_allocation,
            allocated_hours_per_day=assignment.allocated_hours_per_day,
            is_active=assignment.is_active,
            notes=assignment.notes,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at
        )
    
    def _sort_assignments(
        self, 
        assignments: List[ProjectAssignmentResponseSchema], 
        sort_by: str,
        sort_order: str = "asc"
    ) -> List[ProjectAssignmentResponseSchema]:
        """Ordena las asignaciones según el criterio especificado."""
        
        reverse = sort_order.lower() == "desc"
        
        if sort_by == "start_date":
            return sorted(assignments, key=lambda x: x.start_date, reverse=reverse)
        elif sort_by == "end_date":
            return sorted(assignments, key=lambda x: x.end_date or date.max, reverse=reverse)
        elif sort_by == "employee_name":
            return sorted(assignments, key=lambda x: x.employee_name, reverse=reverse)
        elif sort_by == "project_name":
            return sorted(assignments, key=lambda x: x.project_name, reverse=reverse)
        elif sort_by == "percentage_allocation":
            return sorted(assignments, key=lambda x: x.percentage_allocation or 0, reverse=reverse)
        elif sort_by == "allocated_hours_per_day":
            return sorted(assignments, key=lambda x: x.allocated_hours_per_day or 0, reverse=reverse)
        elif sort_by == "role_in_project":
            return sorted(assignments, key=lambda x: x.role_in_project or "", reverse=reverse)
        else:
            # Por defecto, ordenar por ID
            return sorted(assignments, key=lambda x: x.id, reverse=reverse)
    
    def _paginate_assignments(
        self, 
        assignments: List[ProjectAssignmentResponseSchema], 
        limit: Optional[int],
        offset: int = 0
    ) -> List[ProjectAssignmentResponseSchema]:
        """Aplica paginación a la lista de asignaciones."""
        
        start_index = offset
        
        if limit is not None:
            end_index = start_index + limit
            return assignments[start_index:end_index]
        else:
            return assignments[start_index:]
    
    # ============================================================================
    # MÉTODOS PRIVADOS PARA DETECCIÓN DE SOLAPAMIENTOS
    # ============================================================================
    
    async def _get_assignments_for_overlap_detection(
        self, 
        employee_id: Optional[int], 
        project_id: Optional[int]
    ) -> List[ProjectAssignment]:
        """Obtiene las asignaciones base para la detección de solapamientos."""
        
        if employee_id:
            # Obtener asignaciones del empleado específico
            assignments = await self._repository.queries.get_assignments_by_employee(employee_id)
        elif project_id:
            # Obtener asignaciones del proyecto específico
            assignments = await self._repository.queries.get_assignments_by_project(project_id)
        else:
            # Obtener todas las asignaciones activas
            assignments = await self._repository.queries.get_all_assignments(active_only=True)
        
        return assignments
    
    async def _detect_overlapping_assignments(
        self, 
        assignments: List[ProjectAssignment], 
        threshold_percentage: float
    ) -> List[Dict[str, Any]]:
        """Detecta grupos de asignaciones que se solapan."""
        
        overlapping_groups = []
        
        # Agrupar por empleado para detectar solapamientos
        employee_assignments = defaultdict(list)
        for assignment in assignments:
            employee_assignments[assignment.employee_id].append(assignment)
        
        # Detectar solapamientos por empleado
        for employee_id, emp_assignments in employee_assignments.items():
            if len(emp_assignments) < 2:
                continue
            
            # Ordenar por fecha de inicio
            emp_assignments.sort(key=lambda x: x.start_date)
            
            # Buscar solapamientos
            for i in range(len(emp_assignments)):
                for j in range(i + 1, len(emp_assignments)):
                    assignment1 = emp_assignments[i]
                    assignment2 = emp_assignments[j]
                    
                    overlap_info = self._calculate_assignment_overlap(
                        assignment1, assignment2, threshold_percentage
                    )
                    
                    if overlap_info["has_overlap"]:
                        # Buscar si ya existe un grupo con estas asignaciones
                        existing_group = None
                        for group in overlapping_groups:
                            if (assignment1.id in [a["assignment_id"] for a in group["assignments"]] or
                                assignment2.id in [a["assignment_id"] for a in group["assignments"]]):
                                existing_group = group
                                break
                        
                        if existing_group:
                            # Agregar a grupo existente
                            assignment_ids = [a["assignment_id"] for a in existing_group["assignments"]]
                            if assignment1.id not in assignment_ids:
                                existing_group["assignments"].append(
                                    self._assignment_to_overlap_dict(assignment1)
                                )
                            if assignment2.id not in assignment_ids:
                                existing_group["assignments"].append(
                                    self._assignment_to_overlap_dict(assignment2)
                                )
                            
                            # Actualizar métricas del grupo
                            existing_group["total_overlap_percentage"] = max(
                                existing_group["total_overlap_percentage"],
                                overlap_info["overlap_percentage"]
                            )
                        else:
                            # Crear nuevo grupo
                            overlapping_groups.append({
                                "employee_id": employee_id,
                                "overlap_type": overlap_info["overlap_type"],
                                "total_overlap_percentage": overlap_info["overlap_percentage"],
                                "overlap_period": overlap_info["overlap_period"],
                                "conflict_severity": self._determine_conflict_severity(
                                    overlap_info["overlap_percentage"]
                                ),
                                "assignments": [
                                    self._assignment_to_overlap_dict(assignment1),
                                    self._assignment_to_overlap_dict(assignment2)
                                ],
                                "recommendations": self._generate_overlap_recommendations(
                                    assignment1, assignment2, overlap_info
                                )
                            })
        
        return overlapping_groups
    
    def _calculate_assignment_overlap(
        self, 
        assignment1: ProjectAssignment, 
        assignment2: ProjectAssignment,
        threshold_percentage: float
    ) -> Dict[str, Any]:
        """Calcula el solapamiento entre dos asignaciones."""
        
        # Obtener fechas de las asignaciones
        start1, end1 = assignment1.start_date, assignment1.end_date or date.max
        start2, end2 = assignment2.start_date, assignment2.end_date or date.max
        
        # Calcular período de solapamiento
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        
        # Verificar si hay solapamiento temporal
        has_temporal_overlap = overlap_start <= overlap_end
        
        if not has_temporal_overlap:
            return {
                "has_overlap": False,
                "overlap_type": "none",
                "overlap_percentage": 0.0,
                "overlap_period": None
            }
        
        # Calcular porcentaje de solapamiento de recursos
        allocation1 = float(assignment1.percentage_allocation or 0)
        allocation2 = float(assignment2.percentage_allocation or 0)
        total_allocation = allocation1 + allocation2
        
        # Determinar tipo de solapamiento
        if total_allocation > threshold_percentage:
            overlap_type = "resource_conflict"
        elif assignment1.project_id == assignment2.project_id:
            overlap_type = "same_project"
        else:
            overlap_type = "different_projects"
        
        return {
            "has_overlap": total_allocation > threshold_percentage,
            "overlap_type": overlap_type,
            "overlap_percentage": total_allocation,
            "overlap_period": {
                "start_date": overlap_start,
                "end_date": overlap_end if overlap_end != date.max else None,
                "duration_days": (overlap_end - overlap_start).days if overlap_end != date.max else None
            }
        }
    
    def _assignment_to_overlap_dict(self, assignment: ProjectAssignment) -> Dict[str, Any]:
        """Convierte una asignación a diccionario para reporte de solapamiento."""
        return {
            "assignment_id": assignment.id,
            "project_id": assignment.project_id,
            "role_in_project": assignment.role_in_project,
            "start_date": assignment.start_date,
            "end_date": assignment.end_date,
            "percentage_allocation": float(assignment.percentage_allocation or 0),
            "allocated_hours_per_day": float(assignment.allocated_hours_per_day or 0),
            "is_active": assignment.is_active
        }
    
    def _determine_conflict_severity(self, overlap_percentage: float) -> str:
        """Determina la severidad del conflicto basado en el porcentaje de solapamiento."""
        if overlap_percentage <= 100:
            return "low"
        elif overlap_percentage <= 150:
            return "medium"
        else:
            return "high"
    
    def _generate_overlap_recommendations(
        self, 
        assignment1: ProjectAssignment, 
        assignment2: ProjectAssignment,
        overlap_info: Dict[str, Any]
    ) -> List[str]:
        """Genera recomendaciones para resolver solapamientos."""
        recommendations = []
        
        overlap_percentage = overlap_info["overlap_percentage"]
        
        if overlap_percentage > 100:
            recommendations.append(
                f"Reducir la asignación total del empleado en {overlap_percentage - 100:.1f}%"
            )
        
        if assignment1.project_id != assignment2.project_id:
            recommendations.append(
                "Considerar reasignar una de las tareas a otro empleado"
            )
            recommendations.append(
                "Evaluar la posibilidad de ajustar las fechas de las asignaciones"
            )
        
        if overlap_info["overlap_type"] == "resource_conflict":
            recommendations.append(
                "Revisar la prioridad de los proyectos involucrados"
            )
            recommendations.append(
                "Considerar dividir las responsabilidades entre múltiples empleados"
            )
        
        return recommendations