"""
Módulo de operaciones de búsqueda y filtrado para el dominio de asignaciones de proyecto.

Este módulo implementa las operaciones especializadas de búsqueda, filtrado y consultas
complejas para asignaciones de proyecto, incluyendo búsquedas por criterios múltiples,
rangos de fechas, roles específicos y detección de solapamientos.

Métodos implementados según PROJECT_ASSIGNMENT_DOMAIN_SERVICE_METHODS.md:
- search_assignments_by_criteria: Búsqueda con criterios múltiples
- get_assignments_by_date_range: Obtiene asignaciones en rango de fechas
- get_assignments_by_role: Busca asignaciones por rol específico
- get_overlapping_assignments: Detecta solapamientos entre asignaciones
"""

from typing import List, Optional, Dict, Any
from datetime import date
from loguru import logger
from collections import defaultdict

from planificador.schemas import ProjectAssignment
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.exceptions import RepositoryError, ValidationError
from ..interfaces import ISearchOperations


class SearchOperations(ISearchOperations):
    """
    Implementa operaciones de búsqueda y filtrado para asignaciones de proyecto.
    
    Esta clase proporciona métodos especializados para realizar búsquedas complejas,
    aplicar filtros, buscar por rangos de fechas, roles específicos y detectar
    solapamientos entre asignaciones.
    """
    
    def __init__(self, repository_facade: ProjectAssignmentRepositoryFacade):
        """Inicializa el módulo de operaciones de búsqueda."""
        self._repository = repository_facade
        self._logger = logger.bind(module="search_operations")
    
    # ============================================================================
    # MÉTODOS DOCUMENTADOS OFICIALMENTE
    # ============================================================================
    
    async def search_assignments_by_criteria(
        self, 
        criteria: Dict[str, Any]
    ) -> List[ProjectAssignment]:
        """
        Busca asignaciones aplicando criterios múltiples de filtrado.
        
        Args:
            criteria: Diccionario con criterios de búsqueda
                - employee_id: ID del empleado (opcional)
                - project_id: ID del proyecto (opcional)
                - role_in_project: Rol en el proyecto (opcional)
                - is_active: Estado activo (opcional)
                - start_date_from: Fecha inicio desde (opcional)
                - start_date_to: Fecha inicio hasta (opcional)
                - end_date_from: Fecha fin desde (opcional)
                - end_date_to: Fecha fin hasta (opcional)
                - min_percentage: Porcentaje mínimo de asignación (opcional)
                - max_percentage: Porcentaje máximo de asignación (opcional)
                
        Returns:
            List[ProjectAssignment]: Lista de asignaciones que cumplen los criterios
            
        Raises:
            ValidationError: Si los criterios no son válidos
            RepositoryError: Si hay errores en la consulta
        """
        try:
            self._logger.info(f"Buscando asignaciones con criterios: {criteria}")
            
            # Validar criterios
            await self._validate_search_criteria(criteria)
            
            # Obtener todas las asignaciones base
            all_assignments = await self._repository.queries.get_all_assignments()
            
            # Aplicar filtros secuencialmente
            filtered_assignments = await self._apply_search_criteria(all_assignments, criteria)
            
            self._logger.info(
                f"Búsqueda completada: {len(filtered_assignments)} asignaciones encontradas"
            )
            
            return filtered_assignments
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error en búsqueda por criterios: {e}")
            raise RepositoryError(
                message=f"Error en búsqueda por criterios: {e}",
                operation="search_assignments_by_criteria",
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
        Obtiene asignaciones que se encuentran en un rango de fechas específico.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            include_partial_overlap: Si incluir asignaciones con solapamiento parcial
            
        Returns:
            List[ProjectAssignment]: Lista de asignaciones en el rango
            
        Raises:
            ValidationError: Si las fechas no son válidas
            RepositoryError: Si hay errores en la consulta
        """
        try:
            self._logger.info(
                f"Obteniendo asignaciones en rango {start_date} - {end_date} "
                f"(solapamiento parcial: {include_partial_overlap})"
            )
            
            # Validar fechas
            if start_date >= end_date:
                raise ValidationError(
                    message="La fecha de inicio debe ser anterior a la fecha de fin",
                    field="date_range",
                    value=f"{start_date} - {end_date}"
                )
            
            # Obtener todas las asignaciones
            all_assignments = await self._repository.queries.get_all_assignments()
            
            # Filtrar por rango de fechas
            assignments_in_range = []
            for assignment in all_assignments:
                if self._assignment_in_date_range(
                    assignment, start_date, end_date, include_partial_overlap
                ):
                    assignments_in_range.append(assignment)
            
            self._logger.info(
                f"Se encontraron {len(assignments_in_range)} asignaciones en el rango"
            )
            
            return assignments_in_range
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener asignaciones por rango de fechas: {e}")
            raise RepositoryError(
                message=f"Error al obtener asignaciones por rango de fechas: {e}",
                operation="get_assignments_by_date_range",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    async def get_assignments_by_role(
        self, 
        role: str,
        exact_match: bool = False
    ) -> List[ProjectAssignment]:
        """
        Busca asignaciones por rol específico en el proyecto.
        
        Args:
            role: Rol a buscar
            exact_match: Si realizar coincidencia exacta o parcial
            
        Returns:
            List[ProjectAssignment]: Lista de asignaciones con el rol especificado
            
        Raises:
            ValidationError: Si el rol no es válido
            RepositoryError: Si hay errores en la consulta
        """
        try:
            self._logger.info(
                f"Buscando asignaciones por rol '{role}' "
                f"(coincidencia exacta: {exact_match})"
            )
            
            # Validar rol
            if not role or not role.strip():
                raise ValidationError(
                    message="El rol no puede estar vacío",
                    field="role",
                    value=role
                )
            
            role = role.strip()
            
            # Obtener todas las asignaciones
            all_assignments = await self._repository.queries.get_all_assignments()
            
            # Filtrar por rol
            role_assignments = []
            for assignment in all_assignments:
                if self._assignment_matches_role(assignment, role, exact_match):
                    role_assignments.append(assignment)
            
            self._logger.info(
                f"Se encontraron {len(role_assignments)} asignaciones con rol '{role}'"
            )
            
            return role_assignments
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al buscar asignaciones por rol: {e}")
            raise RepositoryError(
                message=f"Error al buscar asignaciones por rol: {e}",
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
        Detecta solapamientos entre asignaciones que pueden causar conflictos.
        
        Args:
            employee_id: ID del empleado para filtrar (opcional)
            project_id: ID del proyecto para filtrar (opcional)
            threshold_percentage: Umbral de porcentaje para considerar solapamiento
            
        Returns:
            List[Dict[str, Any]]: Lista de solapamientos detectados con detalles
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay errores en la detección
        """
        try:
            self._logger.info(
                f"Detectando solapamientos (empleado: {employee_id}, "
                f"proyecto: {project_id}, umbral: {threshold_percentage}%)"
            )
            
            # Validar parámetros
            if threshold_percentage < 0 or threshold_percentage > 200:
                raise ValidationError(
                    message="El umbral de porcentaje debe estar entre 0 y 200",
                    field="threshold_percentage",
                    value=threshold_percentage
                )
            
            if employee_id is not None and employee_id <= 0:
                raise ValidationError(
                    message="El ID del empleado debe ser un número positivo",
                    field="employee_id",
                    value=employee_id
                )
            
            if project_id is not None and project_id <= 0:
                raise ValidationError(
                    message="El ID del proyecto debe ser un número positivo",
                    field="project_id",
                    value=project_id
                )
            
            # Obtener asignaciones para análisis
            assignments = await self._get_assignments_for_overlap_detection(
                employee_id, project_id
            )
            
            # Detectar solapamientos
            overlaps = await self._detect_overlapping_assignments(
                assignments, threshold_percentage
            )
            
            self._logger.info(f"Se detectaron {len(overlaps)} solapamientos")
            
            return overlaps
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al detectar solapamientos: {e}")
            raise RepositoryError(
                message=f"Error al detectar solapamientos: {e}",
                operation="get_overlapping_assignments",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE VALIDACIÓN Y FILTRADO
    # ============================================================================
    
    async def _validate_search_criteria(self, criteria: Dict[str, Any]) -> None:
        """Valida los criterios de búsqueda."""
        if not isinstance(criteria, dict):
            raise ValidationError(
                message="Los criterios deben ser un diccionario",
                field="criteria",
                value=type(criteria).__name__
            )
        
        # Validar IDs si están presentes
        for id_field in ["employee_id", "project_id"]:
            if id_field in criteria and criteria[id_field] is not None:
                if not isinstance(criteria[id_field], int) or criteria[id_field] <= 0:
                    raise ValidationError(
                        message=f"El {id_field} debe ser un número entero positivo",
                        field=id_field,
                        value=criteria[id_field]
                    )
        
        # Validar fechas si están presentes
        date_fields = ["start_date_from", "start_date_to", "end_date_from", "end_date_to"]
        for date_field in date_fields:
            if date_field in criteria and criteria[date_field] is not None:
                if not isinstance(criteria[date_field], date):
                    raise ValidationError(
                        message=f"El campo {date_field} debe ser una fecha válida",
                        field=date_field,
                        value=criteria[date_field]
                    )
        
        # Validar porcentajes si están presentes
        for pct_field in ["min_percentage", "max_percentage"]:
            if pct_field in criteria and criteria[pct_field] is not None:
                value = criteria[pct_field]
                if not isinstance(value, (int, float)) or value < 0 or value > 100:
                    raise ValidationError(
                        message=f"El {pct_field} debe estar entre 0 y 100",
                        field=pct_field,
                        value=value
                    )
    
    async def _apply_search_criteria(
        self, 
        assignments: List[ProjectAssignment], 
        criteria: Dict[str, Any]
    ) -> List[ProjectAssignment]:
        """Aplica los criterios de búsqueda a la lista de asignaciones."""
        filtered_assignments = assignments.copy()
        
        # Filtrar por employee_id
        if criteria.get("employee_id") is not None:
            filtered_assignments = [
                a for a in filtered_assignments 
                if a.employee_id == criteria["employee_id"]
            ]
        
        # Filtrar por project_id
        if criteria.get("project_id") is not None:
            filtered_assignments = [
                a for a in filtered_assignments 
                if a.project_id == criteria["project_id"]
            ]
        
        # Filtrar por rol
        if criteria.get("role_in_project"):
            role = criteria["role_in_project"]
            filtered_assignments = [
                a for a in filtered_assignments 
                if self._assignment_matches_role(a, role, exact_match=False)
            ]
        
        # Filtrar por estado activo
        if criteria.get("is_active") is not None:
            filtered_assignments = [
                a for a in filtered_assignments 
                if a.is_active == criteria["is_active"]
            ]
        
        # Filtrar por fecha de inicio
        if criteria.get("start_date_from") or criteria.get("start_date_to"):
            start_from = criteria.get("start_date_from")
            start_to = criteria.get("start_date_to")
            filtered_assignments = [
                a for a in filtered_assignments 
                if self._assignment_start_date_in_range(a, start_from, start_to)
            ]
        
        # Filtrar por fecha de fin
        if criteria.get("end_date_from") or criteria.get("end_date_to"):
            end_from = criteria.get("end_date_from")
            end_to = criteria.get("end_date_to")
            filtered_assignments = [
                a for a in filtered_assignments 
                if self._assignment_end_date_in_range(a, end_from, end_to)
            ]
        
        # Filtrar por porcentaje mínimo
        if criteria.get("min_percentage") is not None:
            min_pct = criteria["min_percentage"]
            filtered_assignments = [
                a for a in filtered_assignments 
                if a.percentage_allocation >= min_pct
            ]
        
        # Filtrar por porcentaje máximo
        if criteria.get("max_percentage") is not None:
            max_pct = criteria["max_percentage"]
            filtered_assignments = [
                a for a in filtered_assignments 
                if a.percentage_allocation <= max_pct
            ]
        
        return filtered_assignments
    
    def _assignment_start_date_in_range(
        self, 
        assignment: ProjectAssignment, 
        start_date_from: Optional[date], 
        start_date_to: Optional[date]
    ) -> bool:
        """Verifica si la fecha de inicio de la asignación está en el rango."""
        if start_date_from and assignment.start_date < start_date_from:
            return False
        if start_date_to and assignment.start_date > start_date_to:
            return False
        return True
    
    def _assignment_end_date_in_range(
        self, 
        assignment: ProjectAssignment, 
        end_date_from: Optional[date], 
        end_date_to: Optional[date]
    ) -> bool:
        """Verifica si la fecha de fin de la asignación está en el rango."""
        if end_date_from and assignment.end_date < end_date_from:
            return False
        if end_date_to and assignment.end_date > end_date_to:
            return False
        return True
    
    def _assignment_in_date_range(
        self, 
        assignment: ProjectAssignment, 
        start_date: Optional[date], 
        end_date: Optional[date],
        include_partial_overlap: bool = True
    ) -> bool:
        """Verifica si una asignación está en el rango de fechas especificado."""
        if not start_date or not end_date:
            return True
        
        if include_partial_overlap:
            # Incluir si hay cualquier solapamiento
            return not (assignment.end_date < start_date or assignment.start_date > end_date)
        else:
            # Solo incluir si está completamente dentro del rango
            return assignment.start_date >= start_date and assignment.end_date <= end_date
    
    def _assignment_matches_role(
        self, 
        assignment: ProjectAssignment, 
        role: str, 
        exact_match: bool = False
    ) -> bool:
        """Verifica si una asignación coincide con el rol especificado."""
        assignment_role = assignment.role_in_project or ""
        
        if exact_match:
            return assignment_role.lower() == role.lower()
        else:
            return role.lower() in assignment_role.lower()
    
    async def _get_assignments_for_overlap_detection(
        self, 
        employee_id: Optional[int], 
        project_id: Optional[int]
    ) -> List[ProjectAssignment]:
        """Obtiene las asignaciones relevantes para la detección de solapamientos."""
        if employee_id:
            return await self._repository.queries.get_assignments_by_employee(
                employee_id=employee_id,
                include_inactive=False
            )
        elif project_id:
            return await self._repository.queries.get_assignments_by_project(
                project_id=project_id,
                include_inactive=False
            )
        else:
            # Obtener todas las asignaciones activas
            all_assignments = await self._repository.queries.get_all_assignments()
            return [a for a in all_assignments if a.is_active]
    
    async def _detect_overlapping_assignments(
        self, 
        assignments: List[ProjectAssignment], 
        threshold_percentage: float
    ) -> List[Dict[str, Any]]:
        """Detecta solapamientos entre asignaciones."""
        overlaps = []
        
        # Agrupar por empleado para detectar solapamientos
        employee_assignments = defaultdict(list)
        for assignment in assignments:
            employee_assignments[assignment.employee_id].append(assignment)
        
        # Detectar solapamientos para cada empleado
        for employee_id, emp_assignments in employee_assignments.items():
            if len(emp_assignments) < 2:
                continue
            
            # Comparar cada par de asignaciones
            for i in range(len(emp_assignments)):
                for j in range(i + 1, len(emp_assignments)):
                    assignment1 = emp_assignments[i]
                    assignment2 = emp_assignments[j]
                    
                    overlap_info = self._calculate_assignment_overlap(
                        assignment1, assignment2, threshold_percentage
                    )
                    
                    if overlap_info["has_overlap"]:
                        overlap_detail = {
                            "employee_id": employee_id,
                            "assignment1": self._assignment_to_overlap_dict(assignment1),
                            "assignment2": self._assignment_to_overlap_dict(assignment2),
                            "overlap_info": overlap_info,
                            "conflict_severity": self._determine_conflict_severity(
                                overlap_info["overlap_percentage"]
                            ),
                            "recommendations": self._generate_overlap_recommendations(
                                assignment1, assignment2, overlap_info
                            )
                        }
                        overlaps.append(overlap_detail)
        
        return overlaps
    
    def _calculate_assignment_overlap(
        self, 
        assignment1: ProjectAssignment, 
        assignment2: ProjectAssignment,
        threshold_percentage: float
    ) -> Dict[str, Any]:
        """Calcula el solapamiento entre dos asignaciones."""
        # Verificar solapamiento temporal
        overlap_start = max(assignment1.start_date, assignment2.start_date)
        overlap_end = min(assignment1.end_date, assignment2.end_date)
        
        has_temporal_overlap = overlap_start <= overlap_end
        
        if not has_temporal_overlap:
            return {
                "has_overlap": False,
                "temporal_overlap": False,
                "overlap_days": 0,
                "overlap_percentage": 0,
                "total_allocation_percentage": 0
            }
        
        # Calcular días de solapamiento
        overlap_days = (overlap_end - overlap_start).days + 1
        
        # Calcular porcentaje total de asignación durante el solapamiento
        total_allocation = assignment1.percentage_allocation + assignment2.percentage_allocation
        
        # Determinar si excede el umbral
        exceeds_threshold = total_allocation > threshold_percentage
        
        return {
            "has_overlap": exceeds_threshold,
            "temporal_overlap": True,
            "overlap_start": overlap_start,
            "overlap_end": overlap_end,
            "overlap_days": overlap_days,
            "overlap_percentage": total_allocation,
            "total_allocation_percentage": total_allocation,
            "exceeds_threshold": exceeds_threshold,
            "threshold_percentage": threshold_percentage
        }
    
    def _assignment_to_overlap_dict(self, assignment: ProjectAssignment) -> Dict[str, Any]:
        """Convierte una asignación a diccionario para reporte de solapamiento."""
        return {
            "assignment_id": assignment.id,
            "project_id": assignment.project_id,
            "role_in_project": assignment.role_in_project,
            "start_date": assignment.start_date,
            "end_date": assignment.end_date,
            "percentage_allocation": assignment.percentage_allocation,
            "allocated_hours_per_day": assignment.allocated_hours_per_day
        }
    
    def _determine_conflict_severity(self, overlap_percentage: float) -> str:
        """Determina la severidad del conflicto basado en el porcentaje de solapamiento."""
        if overlap_percentage <= 100:
            return "none"
        elif overlap_percentage <= 120:
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
        
        total_percentage = overlap_info["total_allocation_percentage"]
        
        if total_percentage > 100:
            recommendations.append(
                f"Reducir asignación total en {total_percentage - 100}% para evitar sobreasignación"
            )
        
        if overlap_info["overlap_days"] > 30:
            recommendations.append(
                "Considerar ajustar fechas para reducir período de solapamiento"
            )
        
        if assignment1.project_id == assignment2.project_id:
            recommendations.append(
                "Consolidar roles en el mismo proyecto si es posible"
            )
        
        recommendations.append(
            "Revisar prioridades de proyecto y ajustar asignaciones según importancia"
        )
        
        return recommendations