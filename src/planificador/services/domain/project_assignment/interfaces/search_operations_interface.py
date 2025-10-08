# src/planificador/services/domain/project_assignment/interfaces/search_operations_interface.py

"""
Interfaz para Operaciones de Búsqueda y Filtrado de Asignaciones

Define el contrato para operaciones de búsqueda avanzada, filtrado
y detección de conflictos en asignaciones de proyecto.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.schemas import ProjectAssignment


class ISearchOperations(ABC):
    """
    Interfaz para operaciones de búsqueda y filtrado de asignaciones.
    
    Proporciona métodos para realizar búsquedas complejas, aplicar
    filtros avanzados y detectar conflictos de asignación.
    """
    
    # ============================================================================
    # OPERACIONES DE BÚSQUEDA Y FILTRADO (4 métodos)
    # ============================================================================
    
    @abstractmethod
    async def get_assignments_with_filters(self, filters: Dict[str, Any]) -> List[ProjectAssignment]:
        """
        Búsqueda avanzada con múltiples filtros complejos.
        
        Args:
            filters: Diccionario con criterios de filtrado que puede incluir:
                - employee_ids: Lista de IDs de empleados
                - project_ids: Lista de IDs de proyectos
                - roles: Lista de roles a filtrar
                - start_date_from: Fecha de inicio desde
                - start_date_to: Fecha de inicio hasta
                - end_date_from: Fecha de fin desde
                - end_date_to: Fecha de fin hasta
                - is_active: Estado activo/inactivo
                - min_allocation: Asignación mínima en porcentaje
                - max_allocation: Asignación máxima en porcentaje
                - has_notes: Filtrar por presencia de notas
                
        Returns:
            List[ProjectAssignment]: Lista de asignaciones que cumplen los filtros
            
        Raises:
            ValidationError: Si los filtros no son válidos
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_assignments_by_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[ProjectAssignment]:
        """
        Obtiene asignaciones que se superponen con un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            
        Returns:
            List[ProjectAssignment]: Asignaciones que se superponen con el rango
            
        Raises:
            ValidationError: Si el rango de fechas no es válido
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_assignments_by_role(self, role: str) -> List[ProjectAssignment]:
        """
        Obtiene asignaciones filtradas por rol específico.
        
        Args:
            role: Rol a filtrar (ej: "Developer", "Project Manager", "Analyst")
            
        Returns:
            List[ProjectAssignment]: Asignaciones con el rol especificado
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_overlapping_assignments(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date, 
        exclude_id: Optional[int] = None
    ) -> List[ProjectAssignment]:
        """
        Detecta asignaciones superpuestas para validación de conflictos.
        
        Args:
            employee_id: ID del empleado a verificar
            start_date: Fecha de inicio del período a verificar
            end_date: Fecha de fin del período a verificar
            exclude_id: ID de asignación a excluir de la búsqueda (útil para actualizaciones)
            
        Returns:
            List[ProjectAssignment]: Asignaciones que se superponen con el período
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay errores en la consulta
        """
        pass