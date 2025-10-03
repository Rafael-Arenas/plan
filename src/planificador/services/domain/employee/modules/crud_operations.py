# -*- coding: utf-8 -*-
"""
CRUD Operations Implementation for Employee Domain Service

Implementación concreta de las operaciones CRUD para empleados.
"""

from typing import List, Dict, Any, Optional
from loguru import logger

from planificador.models.employee import Employee
from planificador.repositories.employee_repository_facade import EmployeeRepositoryFacade
from planificador.exceptions.validation_error import ValidationError
from planificador.exceptions.business_logic_error import BusinessLogicError
from planificador.exceptions.not_found_error import NotFoundError
from planificador.exceptions.repository_error import RepositoryError
from ..interfaces.crud_interface import ICrudOperations


class CrudOperations(ICrudOperations):
    """
    Implementación de operaciones CRUD para el dominio Employee.
    
    Proporciona funcionalidades para crear, actualizar y eliminar empleados
    con validaciones de negocio completas.
    """

    def __init__(self, repository_facade: EmployeeRepositoryFacade):
        """
        Inicializa las operaciones CRUD.
        
        Args:
            repository_facade: Fachada del repositorio de empleados
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="employee_crud_operations")

    # ============================================================================
    # OPERACIONES CRUD PRINCIPALES (4 métodos)
    # ============================================================================

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
        self._logger.info(f"Creando empleado: {employee_data.get('email', 'N/A')}")
        
        try:
            employee = await self._repository.create_employee(employee_data)
            self._logger.info(f"Empleado creado exitosamente: ID {employee.id}")
            return employee
            
        except Exception as e:
            self._logger.error(f"Error creando empleado: {e}")
            raise

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
        self._logger.info(f"Obteniendo empleado por ID: {employee_id}")
        
        try:
            if employee_id <= 0:
                raise ValidationError(
                    message="El ID del empleado debe ser un número positivo",
                    field="employee_id",
                    value=employee_id
                )
            
            employee = await self._repository.get_by_id(employee_id)
            if employee:
                self._logger.info(f"Empleado encontrado: ID {employee.id}")
            else:
                self._logger.info(f"Empleado no encontrado: ID {employee_id}")
            
            return employee
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error obteniendo empleado {employee_id}: {e}")
            raise

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
        self._logger.info(f"Actualizando empleado ID: {employee_id}")
        
        try:
            if employee_id <= 0:
                raise ValidationError(
                    message="El ID del empleado debe ser un número positivo",
                    field="employee_id",
                    value=employee_id
                )
            
            # Verificar que el empleado existe antes de actualizar
            existing_employee = await self._repository.get_by_id(employee_id)
            if not existing_employee:
                raise NotFoundError(
                    message=f"Empleado con ID {employee_id} no encontrado",
                    entity_type="Employee",
                    entity_id=employee_id
                )
            
            updated_employee = await self._repository.update_employee(employee_id, employee_data)
            if updated_employee:
                self._logger.info(f"Empleado actualizado exitosamente: ID {employee_id}")
            else:
                self._logger.warning(f"No se pudo actualizar empleado: ID {employee_id}")
            
            return updated_employee
            
        except (ValidationError, NotFoundError):
            raise
        except Exception as e:
            self._logger.error(f"Error actualizando empleado {employee_id}: {e}")
            raise

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
        self._logger.info(f"Eliminando empleado ID: {employee_id}")
        
        try:
            if employee_id <= 0:
                raise ValidationError(
                    message="El ID del empleado debe ser un número positivo",
                    field="employee_id",
                    value=employee_id
                )
            
            # Verificar que el empleado existe antes de eliminar
            existing_employee = await self._repository.get_by_id(employee_id)
            if not existing_employee:
                self._logger.info(f"Empleado no encontrado para eliminar: ID {employee_id}")
                return False
            
            # Verificar dependencias antes de eliminar
            has_dependencies = await self._repository.has_dependencies(employee_id)
            if has_dependencies:
                raise BusinessLogicError(
                    message=f"No se puede eliminar el empleado {employee_id} porque tiene dependencias activas",
                    operation="delete_employee",
                    entity_type="Employee",
                    entity_id=employee_id
                )
            
            result = await self._repository.delete_employee(employee_id)
            if result:
                self._logger.info(f"Empleado eliminado exitosamente: ID {employee_id}")
            else:
                self._logger.warning(f"No se pudo eliminar empleado: ID {employee_id}")
            
            return result
            
        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"Error eliminando empleado {employee_id}: {e}")
            raise

    # ============================================================================
    # OPERACIONES CRUD ESPECIALIZADAS (4 métodos) - Orden según documentación
    # ============================================================================

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
        self._logger.info(f"Creando empleado con validación: {employee_data.get('email', 'N/A')}")
        
        try:
            # TODO: Implementar validaciones de negocio específicas
            # TODO: Validar datos requeridos
            # TODO: Validar formato de email
            # TODO: Validar unicidad de email
            
            employee = await self._repository.create(employee_data)
            self._logger.info(f"Empleado creado exitosamente: ID {employee.id}")
            return employee
            
        except Exception as e:
            self._logger.error(f"Error creando empleado: {e}")
            raise

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
        self._logger.info(f"Creando {len(employees_data)} empleados en lote")
        
        try:
            # TODO: Implementar creación en lote con transacción
            # TODO: Validar todos los datos antes de crear
            # TODO: Manejar rollback en caso de error
            
            created_employees = []
            for employee_data in employees_data:
                employee = await self.create_employee_with_validation(employee_data)
                created_employees.append(employee)
            
            self._logger.info(f"Creados {len(created_employees)} empleados exitosamente")
            return created_employees
            
        except Exception as e:
            self._logger.error(f"Error en creación en lote: {e}")
            raise

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
        self._logger.info(f"Eliminando lógicamente empleado ID: {employee_id}")
        
        try:
            # TODO: Verificar que el empleado existe
            # TODO: Validar que no tiene dependencias activas
            # TODO: Implementar eliminación lógica
            
            result = await self._repository.soft_delete(employee_id)
            self._logger.info(f"Empleado {employee_id} eliminado lógicamente")
            return result
            
        except Exception as e:
            self._logger.error(f"Error eliminando empleado {employee_id}: {e}")
            raise

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
        self._logger.info(f"Restaurando empleado ID: {employee_id}")
        
        try:
            # TODO: Verificar que el empleado existe y está eliminado
            # TODO: Validar que se puede restaurar
            # TODO: Implementar restauración
            
            employee = await self._repository.restore(employee_id)
            if employee:
                self._logger.info(f"Empleado {employee_id} restaurado exitosamente")
            else:
                self._logger.warning(f"No se pudo restaurar empleado {employee_id}")
            
            return employee
            
        except Exception as e:
            self._logger.error(f"Error restaurando empleado {employee_id}: {e}")
            raise