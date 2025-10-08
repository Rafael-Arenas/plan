# src/planificador/services/domain/project_assignment/interfaces/employee_queries_interface.py

"""
Interfaz para Consultas por Empleado de Asignaciones de Proyecto

Define el contrato para operaciones de consulta centradas en empleados,
incluyendo cargas de trabajo, historiales y análisis de asignación.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.schemas import ProjectAssignment


class IEmployeeQueries(ABC):
    """
    Interfaz para consultas de asignaciones centradas en empleados.
    
    Proporciona métodos para obtener información detallada sobre
    las asignaciones de empleados específicos, incluyendo análisis
    de carga de trabajo y disponibilidad.
    """
    
    # ============================================================================
    # OPERACIONES DE CONSULTA POR EMPLEADO (5 métodos)
    # ============================================================================
    
    @abstractmethod
    async def get_assignments_by_employee(
        self, 
        employee_id: int, 
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todas las asignaciones de un empleado específico.
        
        Args:
            employee_id: ID del empleado
            include_inactive: Si incluir asignaciones inactivas
            
        Returns:
            List[ProjectAssignment]: Lista de todas las asignaciones del empleado
            
        Raises:
            ValidationError: Si el employee_id no es válido
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_active_assignments_by_employee(
        self, 
        employee_id: int, 
        reference_date: Optional[date] = None
    ) -> List[ProjectAssignment]:
        """
        Obtiene solo las asignaciones activas de un empleado.
        
        Args:
            employee_id: ID del empleado
            reference_date: Fecha de referencia (por defecto: fecha actual)
            
        Returns:
            List[ProjectAssignment]: Lista de asignaciones activas del empleado
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_employee_workload_summary(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """
        Calcula un resumen completo de la carga de trabajo del empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Dict con resumen de carga de trabajo incluyendo:
            - employee_id: ID del empleado
            - period_start: Fecha de inicio del período
            - period_end: Fecha de fin del período
            - total_assignments: Número total de asignaciones
            - total_allocated_percentage: Porcentaje total de asignación
            - workload_distribution: Distribución de carga por proyecto
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay errores en el cálculo
        """
        pass
    
    @abstractmethod
    async def get_employee_assignment_history(
        self, 
        employee_id: int, 
        limit: Optional[int] = None
    ) -> List[ProjectAssignment]:
        """
        Obtiene el historial completo de asignaciones de un empleado.
        
        Args:
            employee_id: ID del empleado
            limit: Límite opcional de registros a retornar
            
        Returns:
            List[ProjectAssignment]: Historial de asignaciones ordenado por fecha
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_employee_current_allocation(self, employee_id: int) -> Dict[str, Any]:
        """
        Calcula la asignación actual total del empleado en porcentaje.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Dict con información de asignación actual:
            - employee_id: ID del empleado
            - total_allocation_percentage: Porcentaje total de asignación
            - available_capacity: Capacidad disponible restante
            - is_overallocated: Indica si está sobre-asignado
            - current_projects_count: Número de proyectos actuales
            - allocation_by_project: Desglose por proyecto
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass