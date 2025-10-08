# src/planificador/services/domain/project_assignment/interfaces/validation_operations_interface.py

"""
Interfaz para Operaciones de Validación y Reglas de Negocio

Define el contrato para validaciones complejas, verificación de reglas
de negocio y análisis de integridad de asignaciones de proyecto.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import date

from planificador.schemas import ProjectAssignmentCreate, ProjectAssignmentUpdate


class IValidationOperations(ABC):
    """
    Interfaz para operaciones de validación y reglas de negocio.
    
    Proporciona métodos para validar asignaciones, verificar reglas
    de negocio y mantener la integridad de los datos.
    """
    
    # ==========================================
    # OPERACIONES DE VALIDACIÓN Y REGLAS DE NEGOCIO (5 métodos)
    # ==========================================
    
    @abstractmethod
    async def validate_assignment_business_rules(
        self, 
        assignment_data: Dict[str, Any], 
        exclude_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Valida todas las reglas de negocio para asignaciones.
        
        Args:
            assignment_data: Datos de la asignación a validar
            exclude_id: ID de asignación a excluir de validaciones (para actualizaciones)
            
        Returns:
            Dict con resultado de validación y detalles de errores si los hay
            
        Raises:
            ValidationError: Si los datos no cumplen las reglas de negocio
            RepositoryError: Si hay errores de acceso a datos
        """
        pass
    
    @abstractmethod
    async def validate_no_overlapping_assignments(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date, 
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Valida que no existan solapamientos de asignaciones.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            exclude_id: ID de asignación a excluir de la validación
            
        Returns:
            True si no hay solapamientos, False si los hay
            
        Raises:
            ValidationError: Si hay errores en la validación
            RepositoryError: Si hay errores de acceso a datos
        """
        pass
    
    @abstractmethod
    async def validate_workload_limits(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date, 
        allocation_percentage: float
    ) -> bool:
        """
        Valida que la carga de trabajo no exceda límites establecidos.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            allocation_percentage: Porcentaje de asignación a validar
            
        Returns:
            True si la carga está dentro de límites, False si los excede
            
        Raises:
            ValidationError: Si hay errores en la validación
            RepositoryError: Si hay errores de acceso a datos
        """
        pass
    
    @abstractmethod
    async def validate_assignment_deletion(self, assignment_id: int) -> Dict[str, Any]:
        """
        Valida si una asignación puede ser eliminada sin impacto crítico.
        
        Args:
            assignment_id: ID de la asignación a validar para eliminación
            
        Returns:
            Dict con resultado de validación y detalles del impacto
            
        Raises:
            ValidationError: Si hay errores en la validación
            RepositoryError: Si hay errores de acceso a datos
        """
        pass
    
    @abstractmethod
    async def validate_employee_availability(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """
        Valida la disponibilidad del empleado para nuevas asignaciones.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Dict con información de disponibilidad y capacidad restante
            
        Raises:
            ValidationError: Si hay errores en la validación
            RepositoryError: Si hay errores de acceso a datos
        """
        pass