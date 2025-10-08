# src/planificador/services/domain/project_assignment/interfaces/resource_management_interface.py

"""
Interfaz para Gestión de Recursos de Asignaciones de Proyecto

Define el contrato para operaciones de gestión de recursos,
incluyendo capacidades, optimización y balanceado de cargas.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date

from planificador.schemas import ProjectAssignment


class IResourceManagement(ABC):
    """
    Interfaz para gestión de recursos en asignaciones de proyecto.
    
    Proporciona métodos para asignación de empleados, reasignación
    y cálculo de utilización según la documentación oficial.
    """
    
    # ============================================================================
    # OPERACIONES DE GESTIÓN DE RECURSOS (3 métodos)
    # ============================================================================
    
    @abstractmethod
    async def assign_employee_to_project(
        self,
        employee_id: int,
        project_id: int,
        assignment_data: Dict[str, Any]
    ) -> ProjectAssignment:
        """
        Asigna un empleado a un proyecto específico.
        
        Args:
            employee_id: ID del empleado a asignar
            project_id: ID del proyecto de destino
            assignment_data: Datos de la asignación (rol, fechas, etc.)
            
        Returns:
            ProjectAssignment: La asignación creada
            
        Raises:
            RepositoryError: Error al acceder a los datos
            ValidationError: Parámetros de entrada inválidos
            BusinessLogicError: Error en la lógica de asignación
        """
        pass
    
    @abstractmethod
    async def reassign_employee(
        self,
        assignment_id: int,
        new_project_id: int,
        reassignment_data: Optional[Dict[str, Any]] = None
    ) -> ProjectAssignment:
        """
        Reasigna un empleado de un proyecto a otro.
        
        Args:
            assignment_id: ID de la asignación actual
            new_project_id: ID del nuevo proyecto
            reassignment_data: Datos opcionales para la reasignación
            
        Returns:
            ProjectAssignment: La asignación actualizada
            
        Raises:
            RepositoryError: Error al acceder a los datos
            ValidationError: Parámetros de entrada inválidos
            BusinessLogicError: Error en la lógica de reasignación
        """
        pass
    
    @abstractmethod
    async def calculate_employee_utilization(
        self,
        employee_id: int,
        date_range: Optional[Dict[str, date]] = None
    ) -> Dict[str, Any]:
        """
        Calcula la utilización de un empleado en un rango de fechas.
        
        Args:
            employee_id: ID del empleado
            date_range: Rango de fechas opcional (start_date, end_date)
            
        Returns:
            Dict con métricas de utilización del empleado:
            - employee_id: ID del empleado
            - period: Período analizado
            - total_assignments: Número total de asignaciones
            - active_assignments: Número de asignaciones activas
            - total_allocation_percentage: Porcentaje total de asignación
            - utilization_status: Estado de utilización (underutilized, optimal, overallocated)
            - assignments_detail: Detalle de asignaciones por proyecto
            - recommendations: Recomendaciones basadas en utilización
            
        Raises:
            RepositoryError: Error al acceder a los datos
            ValidationError: Parámetros de entrada inválidos
            BusinessLogicError: Error en el cálculo de utilización
        """
        pass