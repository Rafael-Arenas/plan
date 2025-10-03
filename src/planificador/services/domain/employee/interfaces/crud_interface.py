# -*- coding: utf-8 -*-
"""
CRUD Operations Interface for Employee Domain Service

Define las operaciones básicas de creación, lectura, actualización y eliminación
para la entidad Employee a nivel de dominio.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from planificador.models.employee import Employee


class ICrudOperations(ABC):
    """
    Interfaz para operaciones CRUD del dominio Employee.
    
    Define los métodos básicos para gestionar el ciclo de vida
    de los empleados con validaciones de negocio.
    """

    # ============================================================================
    # OPERACIONES CRUD PRINCIPALES (4 métodos)
    # ============================================================================

    @abstractmethod
    async def create_employee(self, employee_data: Dict[str, Any]) -> Employee:
        """
        Crea un nuevo empleado.
        
        Args:
            employee_data: Datos del empleado a crear
            
        Returns:
            Employee: El empleado creado
            
        Raises:
            ValidationError: Si los datos no son válidos
            RepositoryError: Si falla la operación de base de datos
        """
        pass

    @abstractmethod
    async def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """
        Obtiene un empleado por su ID.
        
        Args:
            employee_id: ID del empleado a buscar
            
        Returns:
            Optional[Employee]: El empleado encontrado o None
            
        Raises:
            ValidationError: Si el ID no es válido
            RepositoryError: Si falla la operación de base de datos
        """
        pass

    @abstractmethod
    async def update_employee(
        self, 
        employee_id: int, 
        employee_data: Dict[str, Any]
    ) -> Optional[Employee]:
        """
        Actualiza un empleado existente.
        
        Args:
            employee_id: ID del empleado a actualizar
            employee_data: Datos de actualización del empleado
            
        Returns:
            Optional[Employee]: El empleado actualizado o None si no existe
            
        Raises:
            ValidationError: Si los datos no son válidos
            NotFoundError: Si el empleado no existe
            RepositoryError: Si falla la operación de base de datos
        """
        pass

    @abstractmethod
    async def delete_employee(self, employee_id: int) -> bool:
        """
        Elimina un empleado.
        
        Args:
            employee_id: ID del empleado a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False si no existe
            
        Raises:
            ValidationError: Si el ID no es válido
            BusinessLogicError: Si tiene dependencias activas
            RepositoryError: Si falla la operación de base de datos
        """
        pass

    # ============================================================================
    # OPERACIONES CRUD ESPECIALIZADAS (4 métodos)
    # ============================================================================

    @abstractmethod
    async def create_employee_with_validation(
        self,
        employee_data: Dict[str, Any],
        validate_business_rules: bool = True
    ) -> Employee:
        """
        Crea un nuevo empleado con validaciones completas de negocio.
        
        Args:
            employee_data: Datos del empleado a crear
            validate_business_rules: Si aplicar validaciones de negocio
            
        Returns:
            Employee: El empleado creado
            
        Raises:
            ValidationError: Si los datos no son válidos
            BusinessLogicError: Si viola reglas de negocio
        """
        pass

    @abstractmethod
    async def bulk_create_employees(
        self,
        employees_data: List[Dict[str, Any]]
    ) -> List[Employee]:
        """
        Crea múltiples empleados en una operación transaccional.
        
        Args:
            employees_data: Lista de datos de empleados
            
        Returns:
            List[Employee]: Lista de empleados creados
            
        Raises:
            ValidationError: Si algún dato no es válido
            RepositoryError: Si falla la operación de base de datos
        """
        pass

    @abstractmethod
    async def soft_delete_employee(self, employee_id: int) -> bool:
        """
        Realiza eliminación lógica de un empleado.
        
        Args:
            employee_id: ID del empleado a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            NotFoundError: Si el empleado no existe
            BusinessLogicError: Si tiene dependencias activas
        """
        pass

    @abstractmethod
    async def restore_employee(self, employee_id: int) -> Optional[Employee]:
        """
        Restaura un empleado eliminado lógicamente.
        
        Args:
            employee_id: ID del empleado a restaurar
            
        Returns:
            Optional[Employee]: El empleado restaurado o None
            
        Raises:
            NotFoundError: Si el empleado no existe
            ValidationError: Si no se puede restaurar
        """
        pass