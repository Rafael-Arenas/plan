"""Interface para operaciones de validación de asignaciones de proyectos.

Define el contrato para validaciones de negocio y reglas específicas
de la entidad ProjectAssignment.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class IValidationOperations(ABC):
    """Interface para operaciones de validación de asignaciones de proyectos."""

    @abstractmethod
    async def validate_assignment_data(
        self, 
        assignment_data: dict[str, Any], 
        exclude_id: int | None = None
    ) -> None:
        """Valida los datos de una asignación.
        
        Args:
            assignment_data: Datos de la asignación a validar
            exclude_id: ID a excluir de validaciones de unicidad
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        pass

    @abstractmethod
    def validate_required_fields(self, assignment_data: dict[str, Any]) -> None:
        """Valida que los campos requeridos estén presentes.
        
        Args:
            assignment_data: Datos de la asignación
            
        Raises:
            ValidationError: Si faltan campos requeridos
        """
        pass

    @abstractmethod
    def validate_date_range(self, start_date: date, end_date: date | None) -> None:
        """Valida que el rango de fechas sea válido.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin (opcional)
            
        Raises:
            ValidationError: Si el rango de fechas no es válido
        """
        pass

    @abstractmethod
    def validate_allocation_percentage(self, percentage: float | None) -> None:
        """Valida que el porcentaje de dedicación sea válido.
        
        Args:
            percentage: Porcentaje de dedicación
            
        Raises:
            ValidationError: Si el porcentaje no es válido
        """
        pass

    @abstractmethod
    def validate_hours_per_day(self, hours: float | None) -> None:
        """Valida que las horas por día sean válidas.
        
        Args:
            hours: Horas por día
            
        Raises:
            ValidationError: Si las horas no son válidas
        """
        pass

    @abstractmethod
    async def validate_employee_exists(self, employee_id: int) -> None:
        """Valida que el empleado exista.
        
        Args:
            employee_id: ID del empleado
            
        Raises:
            ValidationError: Si el empleado no existe
        """
        pass

    @abstractmethod
    async def validate_project_exists(self, project_id: int) -> None:
        """Valida que el proyecto exista.
        
        Args:
            project_id: ID del proyecto
            
        Raises:
            ValidationError: Si el proyecto no existe
        """
        pass

    @abstractmethod
    async def validate_no_overlapping_assignments(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date | None,
        exclude_id: int | None = None
    ) -> None:
        """Valida que no haya asignaciones superpuestas para un empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio de la nueva asignación
            end_date: Fecha de fin de la nueva asignación
            exclude_id: ID de asignación a excluir de la validación
            
        Raises:
            ValidationError: Si hay asignaciones superpuestas
        """
        pass

    @abstractmethod
    async def validate_workload_limits(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date | None,
        percentage_allocation: float | None,
        exclude_id: int | None = None
    ) -> None:
        """Valida que la carga de trabajo no exceda los límites.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio
            end_date: Fecha de fin
            percentage_allocation: Porcentaje de dedicación
            exclude_id: ID de asignación a excluir
            
        Raises:
            ValidationError: Si la carga de trabajo excede los límites
        """
        pass

    @abstractmethod
    async def validate_assignment_deletion(self, assignment_id: int) -> None:
        """Valida que una asignación pueda ser eliminada.
        
        Args:
            assignment_id: ID de la asignación
            
        Raises:
            ValidationError: Si la asignación no puede ser eliminada
        """
        pass

    @abstractmethod
    async def validate_business_rules(
        self, 
        assignment_data: dict[str, Any], 
        exclude_id: int | None = None
    ) -> None:
        """Valida reglas de negocio específicas.
        
        Args:
            assignment_data: Datos de la asignación
            exclude_id: ID a excluir de validaciones
            
        Raises:
            ValidationError: Si no se cumplen las reglas de negocio
        """
        pass