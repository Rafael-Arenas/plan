# -*- coding: utf-8 -*-
"""
Relationship Operations Interface for Employee Domain Service

Define las operaciones para gestionar relaciones entre empleados y otras entidades.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from planificador.models.employee import Employee


class IRelationshipOperations(ABC):
    """
    Interfaz para operaciones de relaciones del dominio Employee.
    
    Define métodos para gestionar las relaciones entre empleados
    y otras entidades del sistema.
    """

    @abstractmethod
    async def get_employee_subordinates(self, manager_id: int) -> List[Employee]:
        """
        Obtiene los subordinados directos de un empleado.
        
        Args:
            manager_id: ID del empleado manager
            
        Returns:
            List[Employee]: Lista de empleados subordinados
        """
        pass

    @abstractmethod
    async def get_employee_manager(self, employee_id: int) -> Optional[Employee]:
        """
        Obtiene el manager directo de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Optional[Employee]: El manager del empleado o None
        """
        pass

    @abstractmethod
    async def get_employees_in_hierarchy(self, root_employee_id: int) -> List[Employee]:
        """
        Obtiene todos los empleados en la jerarquía de un empleado.
        
        Args:
            root_employee_id: ID del empleado raíz de la jerarquía
            
        Returns:
            List[Employee]: Lista de empleados en la jerarquía
        """
        pass

    @abstractmethod
    async def assign_manager_to_employee(
        self,
        employee_id: int,
        manager_id: int
    ) -> bool:
        """
        Asigna un manager a un empleado.
        
        Args:
            employee_id: ID del empleado
            manager_id: ID del nuevo manager
            
        Returns:
            bool: True si la asignación fue exitosa
            
        Raises:
            ValidationError: Si la asignación no es válida
            BusinessLogicError: Si viola reglas de negocio
        """
        pass