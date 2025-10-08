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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass