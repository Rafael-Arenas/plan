# -*- coding: utf-8 -*-
"""
Validation Operations Interface for Employee Domain Service

Define las operaciones de validación de reglas de negocio para empleados.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

from planificador.models.employee import Employee


class IValidationOperations(ABC):
    """
    Interfaz para operaciones de validación del dominio Employee.
    
    Define métodos para validar reglas de negocio específicas
    del dominio de empleados.
    """

    @abstractmethod
    async def validate_employee_data(self, employee_data: Dict[str, Any]) -> List[str]:
        """
        Valida los datos de un empleado según reglas de negocio.
        
        Args:
            employee_data: Datos del empleado a validar
            
        Returns:
            List[str]: Lista de errores de validación (vacía si es válido)
        """
        pass

    @abstractmethod
    async def validate_unique_employee_email(self, email: str, employee_id: int = None) -> bool:
        """
        Valida que el email del empleado sea único.
        
        Args:
            email: Email a validar
            employee_id: ID del empleado (para actualizaciones)
            
        Returns:
            bool: True si el email es único
        """
        pass

    @abstractmethod
    async def validate_manager_assignment(
        self,
        employee_id: int,
        manager_id: int
    ) -> List[str]:
        """
        Valida la asignación de un manager a un empleado.
        
        Args:
            employee_id: ID del empleado
            manager_id: ID del manager propuesto
            
        Returns:
            List[str]: Lista de errores de validación
        """
        pass

    @abstractmethod
    async def validate_employee_deletion(self, employee_id: int) -> List[str]:
        """
        Valida si un empleado puede ser eliminado.
        
        Args:
            employee_id: ID del empleado a eliminar
            
        Returns:
            List[str]: Lista de errores que impiden la eliminación
        """
        pass