# -*- coding: utf-8 -*-
"""
Validation Operations Implementation for Employee Domain Service

Implementación concreta de las operaciones de validación para empleados.
"""

from typing import Dict, Any, List
import re
from loguru import logger

from planificador.models.employee import Employee
from planificador.repositories.employee_repository_facade import EmployeeRepositoryFacade
from ..interfaces.validation_interface import IValidationOperations


class ValidationOperations(IValidationOperations):
    """
    Implementación de operaciones de validación para el dominio Employee.
    
    Proporciona funcionalidades para validar reglas de negocio específicas
    del dominio de empleados.
    """

    def __init__(self, repository_facade: EmployeeRepositoryFacade):
        """
        Inicializa las operaciones de validación.
        
        Args:
            repository_facade: Fachada del repositorio de empleados
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="employee_validation_operations")

    async def validate_employee_data(self, employee_data: Dict[str, Any]) -> List[str]:
        """
        Valida los datos de un empleado según reglas de negocio.
        
        Args:
            employee_data: Datos del empleado a validar
            
        Returns:
            List[str]: Lista de errores de validación (vacía si es válido)
        """
        self._logger.info("Validando datos de empleado")
        
        errors = []
        
        try:
            # Validar campos requeridos
            required_fields = ['first_name', 'last_name', 'email', 'department']
            for field in required_fields:
                if not employee_data.get(field):
                    errors.append(f"El campo '{field}' es requerido")
            
            # Validar formato de email
            email = employee_data.get('email')
            if email and not self._is_valid_email(email):
                errors.append("El formato del email no es válido")
            
            # Validar longitud de campos
            if employee_data.get('first_name') and len(employee_data['first_name']) > 100:
                errors.append("El nombre no puede exceder 100 caracteres")
            
            if employee_data.get('last_name') and len(employee_data['last_name']) > 100:
                errors.append("El apellido no puede exceder 100 caracteres")
            
            # Validar salario si está presente
            salary = employee_data.get('salary')
            if salary is not None:
                if not isinstance(salary, (int, float)) or salary < 0:
                    errors.append("El salario debe ser un número positivo")
            
            # Validar fecha de contratación
            hire_date = employee_data.get('hire_date')
            if hire_date:
                # TODO: Validar que la fecha no sea futura usando Pendulum
                pass
            
            self._logger.info(f"Validación completada: {len(errors)} errores encontrados")
            return errors
            
        except Exception as e:
            self._logger.error(f"Error durante validación de datos: {e}")
            return [f"Error interno durante validación: {str(e)}"]

    async def validate_unique_employee_email(self, email: str, employee_id: int = None) -> bool:
        """
        Valida que el email del empleado sea único.
        
        Args:
            email: Email a validar
            employee_id: ID del empleado (para actualizaciones)
            
        Returns:
            bool: True si el email es único
        """
        self._logger.info(f"Validando unicidad de email: {email}")
        
        try:
            existing_employee = await self._repository.get_by_email(email)
            
            # Si no existe ningún empleado con ese email, es único
            if not existing_employee:
                return True
            
            # Si existe pero es el mismo empleado (actualización), es válido
            if employee_id and existing_employee.id == employee_id:
                return True
            
            # Si existe y es diferente empleado, no es único
            self._logger.warning(f"Email {email} ya está en uso por empleado ID: {existing_employee.id}")
            return False
            
        except Exception as e:
            self._logger.error(f"Error validando unicidad de email: {e}")
            return False

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
        self._logger.info(f"Validando asignación de manager {manager_id} a empleado {employee_id}")
        
        errors = []
        
        try:
            # Validar que no sea el mismo empleado
            if employee_id == manager_id:
                errors.append("Un empleado no puede ser su propio manager")
            
            # Validar que ambos empleados existen
            employee = await self._repository.get_by_id(employee_id)
            if not employee:
                errors.append(f"Empleado con ID {employee_id} no existe")
            
            manager = await self._repository.get_by_id(manager_id)
            if not manager:
                errors.append(f"Manager con ID {manager_id} no existe")
            
            # Validar que ambos están activos
            if employee and not employee.is_active:
                errors.append("No se puede asignar manager a un empleado inactivo")
            
            if manager and not manager.is_active:
                errors.append("No se puede asignar un manager inactivo")
            
            # TODO: Validar que no se crea un ciclo en la jerarquía
            # TODO: Validar niveles jerárquicos apropiados
            
            self._logger.info(f"Validación de asignación completada: {len(errors)} errores")
            return errors
            
        except Exception as e:
            self._logger.error(f"Error validando asignación de manager: {e}")
            return [f"Error interno durante validación: {str(e)}"]

    async def validate_employee_deletion(self, employee_id: int) -> List[str]:
        """
        Valida si un empleado puede ser eliminado.
        
        Args:
            employee_id: ID del empleado a eliminar
            
        Returns:
            List[str]: Lista de errores que impiden la eliminación
        """
        self._logger.info(f"Validando eliminación de empleado ID: {employee_id}")
        
        errors = []
        
        try:
            # Validar que el empleado existe
            employee = await self._repository.get_by_id(employee_id)
            if not employee:
                errors.append(f"Empleado con ID {employee_id} no existe")
                return errors
            
            # Validar que no tiene subordinados activos
            subordinates = await self._repository.get_subordinates(employee_id)
            active_subordinates = [s for s in subordinates if s.is_active]
            
            if active_subordinates:
                errors.append(f"No se puede eliminar empleado con {len(active_subordinates)} subordinados activos")
            
            # TODO: Validar otras dependencias (proyectos, tareas, etc.)
            # TODO: Validar permisos del usuario que intenta eliminar
            
            self._logger.info(f"Validación de eliminación completada: {len(errors)} errores")
            return errors
            
        except Exception as e:
            self._logger.error(f"Error validando eliminación de empleado: {e}")
            return [f"Error interno durante validación: {str(e)}"]

    def _is_valid_email(self, email: str) -> bool:
        """
        Valida el formato de un email usando regex.
        
        Args:
            email: Email a validar
            
        Returns:
            bool: True si el formato es válido
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None