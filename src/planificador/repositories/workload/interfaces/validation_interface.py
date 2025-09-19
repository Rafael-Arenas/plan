# src/planificador/repositories/workload/interfaces/validation_interface.py

"""
Interfaz para operaciones de validación del repositorio Workload.

Este módulo define la interfaz abstracta para las operaciones de validación
de datos y reglas de negocio para cargas de trabajo.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para validaciones
    - Business Rules: Definición de reglas de negocio claras
    - Single Responsibility: Solo operaciones de validación

Uso:
    ```python
    class WorkloadValidationModule(IWorkloadValidationOperations):
        async def validate_create_data(self, data: Dict[str, Any]) -> None:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import date

from planificador.exceptions.repository import WorkloadRepositoryError
from planificador.exceptions.validation import ValidationError


class IWorkloadValidationOperations(ABC):
    """
    Interfaz abstracta para operaciones de validación de cargas de trabajo.
    
    Define los métodos de validación que debe implementar cualquier módulo
    que maneje validaciones de datos y reglas de negocio para cargas de trabajo.
    
    Incluye validaciones para creación, actualización, rangos de fechas,
    umbrales de horas y consistencia de datos.
    """

    # Funciones Públicas de Validación
    @abstractmethod
    async def validate_create_data(self, data: Dict[str, Any]) -> None:
        """
        Valida los datos para crear una nueva carga de trabajo.
        
        Args:
            data: Diccionario con los datos de la carga de trabajo
        
        Raises:
            ValidationError: Si los datos no son válidos
            WorkloadRepositoryError: Si ocurre un error durante la validación
        """
        pass

    @abstractmethod
    async def validate_update_data(self, data: Dict[str, Any], workload_id: Optional[int] = None) -> None:
        """
        Valida los datos para actualizar una carga de trabajo.
        
        Args:
            data: Diccionario con los datos a actualizar
            workload_id: ID de la carga de trabajo (opcional)
        
        Raises:
            ValidationError: Si los datos no son válidos
            WorkloadRepositoryError: Si ocurre un error durante la validación
        """
        pass

    @abstractmethod
    async def validate_date_range(self, start_date: date, end_date: date) -> None:
        """
        Valida un rango de fechas.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
        
        Raises:
            ValidationError: Si el rango de fechas no es válido
        """
        pass

    @abstractmethod
    async def validate_threshold_hours(self, threshold_hours: float) -> None:
        """
        Valida un umbral de horas.
        
        Args:
            threshold_hours: Umbral de horas a validar
        
        Raises:
            ValidationError: Si el umbral no es válido
        """
        pass

    @abstractmethod
    async def validate_team_id(self, team_id: int) -> None:
        """
        Valida el ID del equipo.
        
        Args:
            team_id: ID del equipo a validar
        
        Raises:
            ValidationError: Si el ID del equipo no es válido
            WorkloadRepositoryError: Si el equipo no existe
        """
        pass

    @abstractmethod
    async def validate_workload_id(self, workload_id: int) -> None:
        """
        Valida el ID de la carga de trabajo.
        
        Args:
            workload_id: ID de la carga de trabajo a validar
        
        Raises:
            ValidationError: Si el ID no es válido
            WorkloadRepositoryError: Si la carga de trabajo no existe
        """
        pass

    # Validación de Consistencia
    @abstractmethod
    async def check_employee_project_consistency(self, workload_id: int, employee_id: int, project_id: int) -> bool:
        """
        Verifica consistencia entre empleado y proyecto asignados.
        
        Args:
            workload_id: ID de la carga de trabajo
            employee_id: ID del empleado
            project_id: ID del proyecto
        
        Returns:
            bool: True si la consistencia es válida
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la verificación
        """
        pass