from uuid import UUID
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from ..interfaces.crud_interface import IEmployeeCrudOperations
from ....models.employee import Employee
from ....exceptions.repository import (
    convert_sqlalchemy_error,
    EmployeeRepositoryError,
    create_employee_validation_repository_error
)
from .validation_operations import ValidationOperations as EmployeeValidator
from planificador.repositories.base_repository import BaseRepository


class CrudOperations(BaseRepository[Employee], IEmployeeCrudOperations):
    """
    Implementación de operaciones CRUD para empleados.
    
    Esta clase maneja todas las operaciones básicas de creación, lectura,
    actualización y eliminación de empleados, incluyendo validaciones
    de negocio y manejo robusto de errores.
    
    Attributes:
        validator: Instancia del validador de empleados
        logger: Logger para registro de operaciones
    """
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa las operaciones CRUD.
        
        Args:
            session: Sesión de base de datos SQLAlchemy
        """
        super().__init__(Employee, session)
        self.validator = EmployeeValidator()
        self.logger = logger.bind(component="EmployeeCrudOperations")
    
    async def create_employee(self, employee_data: Dict[str, Any]) -> Employee:
        """
        Crea un nuevo empleado con validaciones.
        
        Args:
            employee_data: Datos del empleado a crear
            
        Returns:
            Employee: Empleado creado
            
        Raises:
            EmployeeValidationRepositoryError: Si los datos no son válidos
            EmployeeRepositoryError: Si ocurre un error inesperado
        """
        try:
            # Validar datos de creación
            await self.validator.validate_create_data(employee_data)
            
            # Crear empleado usando el método heredado de BaseRepository
            employee = await self.create(employee_data)
            self.logger.info(f"Empleado creado exitosamente: {employee.full_name} (ID: {employee.id})")
            return employee
            
        except ValueError as e:
            await self.session.rollback()
            raise create_employee_validation_repository_error(
                field="employee_data",
                value=str(employee_data),
                reason=f"Error de validación: {str(e)}",
                operation="create_employee"
            )
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_employee",
                entity_type="Employee"
            )
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error inesperado creando empleado: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado creando empleado: {e}",
                operation="create_employee",
                entity_type="Employee",
                original_error=e
            )
    
    async def update_employee(self, employee_id: int, update_data: Dict[str, Any]) -> Optional[Employee]:
        """
        Actualiza un empleado con validaciones.
        
        Args:
            employee_id: ID del empleado a actualizar
            update_data: Datos a actualizar
            
        Returns:
            Optional[Employee]: Empleado actualizado o None si no existe
            
        Raises:
            EmployeeValidationRepositoryError: Si los datos no son válidos
            EmployeeRepositoryError: Si ocurre un error inesperado
        """
        try:
            # Validar datos de actualización
            await self.validator.validate_update_data(update_data, employee_id)
            
            # Actualizar empleado usando el método heredado de BaseRepository
            employee = await self.update(employee_id, update_data)
            if employee:
                self.logger.info(f"Empleado actualizado exitosamente: {employee.full_name} (ID: {employee.id})")
            return employee
            
        except ValueError as e:
            await self.session.rollback()
            raise create_employee_validation_repository_error(
                field="update_data",
                value=str(update_data),
                reason=f"Error de validación: {str(e)}",
                operation="update_employee"
            )
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="update_employee",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error inesperado actualizando empleado {employee_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado actualizando empleado: {e}",
                operation="update_employee",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[Employee]:
        """
        Obtiene un empleado por un campo único (DNI o email).

        Args:
            field_name: Nombre del campo único ('dni' o 'email').
            value: Valor a buscar.

        Returns:
            El empleado encontrado o None si no existe.
        
        Raises:
            RepositoryError: Si el campo no es válido o si ocurre un error.
        """
        if field_name not in ["dni", "email"]:
            raise RepositoryError(
                message=f"Campo '{field_name}' no es un campo único válido para buscar.",
                operation="get_by_unique_field",
                entity_type=self.model_class.__name__
            )
        
        return await super().get_by_unique_field(field_name, value)

    async def delete_employee(self, employee_id: UUID) -> bool:
        """
        Elimina un empleado por ID.
        
        Args:
            employee_id: ID del empleado a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente, False si no existía
            
        Raises:
            EmployeeRepositoryError: Si ocurre un error durante la eliminación
        """
        try:
            # Usar el método heredado de BaseRepository
            result = await self.delete(employee_id)
            if result:
                self.logger.info(f"Empleado eliminado exitosamente (ID: {employee_id})")
            return result
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="delete_employee",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error inesperado eliminando empleado {employee_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado eliminando empleado: {e}",
                operation="delete_employee",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    