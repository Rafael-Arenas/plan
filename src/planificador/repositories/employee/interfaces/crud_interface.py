from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.models.employee import Employee, EmployeeStatus


class IEmployeeCrudOperations(ABC):
    """
    Interfaz para operaciones CRUD básicas de empleados.
    
    Define los métodos fundamentales para crear, leer, actualizar y eliminar empleados,
    así como operaciones de búsqueda básicas por identificadores únicos.
    """
    
    @abstractmethod
    async def create_employee(self, employee_data: Dict[str, Any]) -> Employee:
        """
        Crea un nuevo empleado con validaciones.
        
        Args:
            employee_data: Datos del empleado
            
        Returns:
            Empleado creado
            
        Raises:
            EmployeeValidationRepositoryError: Si los datos no son válidos
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    @abstractmethod
    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[Employee]:
        """
        Obtiene un empleado por un campo único.

        Args:
            field_name: Nombre del campo único
            value: Valor del campo

        Returns:
            Empleado o None si no se encuentra
        """
        pass
    
    @abstractmethod
    async def update_employee(self, employee_id: int, update_data: Dict[str, Any]) -> Optional[Employee]:
        """
        Actualiza un empleado existente.
        
        Args:
            employee_id: ID del empleado a actualizar
            update_data: Datos a actualizar
            
        Returns:
            Empleado actualizado o None si no existe
            
        Raises:
            EmployeeValidationRepositoryError: Si los datos no son válidos
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    @abstractmethod
    async def delete_employee(self, employee_id: int) -> bool:
        """
        Elimina un empleado por su ID.
        
        Args:
            employee_id: ID del empleado a eliminar
            
        Returns:
            True si se eliminó correctamente, False si no existía
        """
        pass
