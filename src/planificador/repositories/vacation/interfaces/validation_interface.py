# src/planificador/repositories/vacation/interfaces/validation_interface.py

"""
Interfaz para operaciones de validación del repositorio Vacation.

Este módulo define la interfaz abstracta para las operaciones de
validación de datos, reglas de negocio y consistencia de vacaciones.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para validaciones
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones de validación

Uso:
    ```python
    class VacationValidationModule(IVacationValidationOperations):
        async def validate_create_data(self, data: Dict[str, Any]) -> None:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import date

from planificador.enums.vacation_type import VacationType
from planificador.exceptions.repository import VacationRepositoryError


class IVacationValidationOperations(ABC):
    """
    Interfaz abstracta para operaciones de validación de vacaciones.
    
    Define los métodos para validar datos de vacaciones, reglas de negocio,
    consistencia de datos y restricciones del dominio.
    
    Métodos:
        - Validación de datos para crear/actualizar vacaciones
        - Validación de solicitudes de vacación
        - Validación de IDs y existencia de entidades
        - Validaciones de reglas de negocio específicas
    """

    @abstractmethod
    async def validate_create_data(self, data: Dict[str, Any]) -> None:
        """
        Valida los datos para crear una nueva vacación.
        
        Args:
            data: Diccionario con los datos de la vacación
        
        Raises:
            VacationRepositoryError: Si los datos no son válidos
        """
        pass

    @abstractmethod
    async def validate_update_data(self, data: Dict[str, Any]) -> None:
        """
        Valida los datos para actualizar una vacación.
        
        Args:
            data: Diccionario con los datos a actualizar
        
        Raises:
            VacationRepositoryError: Si los datos no son válidos
        """
        pass

    @abstractmethod
    async def validate_vacation_request(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        vacation_type: VacationType,
        exclude_vacation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Valida una solicitud de vacación completa.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio de la vacación
            end_date: Fecha de fin de la vacación
            vacation_type: Tipo de vacación
            exclude_vacation_id: ID de vacación a excluir de la validación (opcional)
        
        Returns:
            Dict[str, Any]: Resultado de la validación con detalles
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la validación
        """
        pass

    @abstractmethod
    async def validate_vacation_id(self, vacation_id: int) -> None:
        """
        Valida el ID de una vacación.
        
        Args:
            vacation_id: ID de la vacación a validar
        
        Raises:
            VacationRepositoryError: Si el ID no es válido
        """
        pass