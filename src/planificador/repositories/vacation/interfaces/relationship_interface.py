# src/planificador/repositories/vacation/interfaces/relationship_interface.py

"""
Interfaz para operaciones de relaciones del repositorio Vacation.

Este módulo define la interfaz abstracta para las operaciones de
gestión de relaciones entre vacaciones, empleados y otras entidades.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para relaciones
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones de relaciones

Uso:
    ```python
    class VacationRelationshipModule(IVacationRelationshipOperations):
        async def get_vacation_with_employee(self, vacation_id: int) -> Optional[Vacation]:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.models.vacation import Vacation
from planificador.models.employee import Employee
from planificador.exceptions.repository import VacationRepositoryError


class IVacationRelationshipOperations(ABC):
    """
    Interfaz abstracta para operaciones de relaciones de vacaciones.
    
    Define los métodos para gestionar las relaciones entre vacaciones,
    empleados y otras entidades del sistema, así como la validación
    de existencia y gestión de conflictos.
    
    Métodos:
        - Gestión de relaciones (vacación con empleado, detalles completos)
        - Validación de existencia de entidades
        - Gestión de conflictos y solapamientos
        - Consultas con relaciones cargadas
    """

    @abstractmethod
    async def get_vacation_with_employee(self, vacation_id: int) -> Optional[Vacation]:
        """
        Obtiene vacación con información del empleado.
        
        Args:
            vacation_id: ID de la vacación
        
        Returns:
            Optional[Vacation]: Vacación con empleado o None si no existe
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_vacation_with_all_relations(self, vacation_id: int) -> Optional[Vacation]:
        """
        Obtiene vacación con todas las relaciones cargadas.
        
        Args:
            vacation_id: ID de la vacación
        
        Returns:
            Optional[Vacation]: Vacación con todas las relaciones o None si no existe
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_employee_vacations_with_details(
        self, 
        employee_id: int, 
        year: Optional[int] = None
    ) -> List[Vacation]:
        """
        Obtiene vacaciones de empleado con detalles completos.
        
        Args:
            employee_id: ID del empleado
            year: Año específico (opcional)
        
        Returns:
            List[Vacation]: Lista de vacaciones con detalles completos
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_team_vacations_summary(
        self, 
        team_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """
        Genera resumen de vacaciones para un equipo.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
        
        Returns:
            Dict[str, Any]: Resumen de vacaciones del equipo
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def validate_vacation_exists(self, vacation_id: int) -> Vacation:
        """
        Valida la existencia de una vacación por ID.
        
        Args:
            vacation_id: ID de la vacación
        
        Returns:
            Vacation: La vacación si existe
        
        Raises:
            VacationRepositoryError: Si la vacación no existe
        """
        pass

    @abstractmethod
    async def validate_employee_exists(self, employee_id: int) -> Employee:
        """
        Valida la existencia de un empleado por ID.
        
        Args:
            employee_id: ID del empleado
        
        Returns:
            Employee: El empleado si existe
        
        Raises:
            VacationRepositoryError: Si el empleado no existe
        """
        pass

    @abstractmethod
    async def check_vacation_overlap(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        exclude_vacation_id: Optional[int] = None
    ) -> bool:
        """
        Verifica solapamiento de vacaciones.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio de la vacación
            end_date: Fecha de fin de la vacación
            exclude_vacation_id: ID de vacación a excluir (opcional)
        
        Returns:
            bool: True si hay solapamiento, False en caso contrario
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la verificación
        """
        pass

    @abstractmethod
    async def get_vacation_conflicts(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        exclude_vacation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene información detallada sobre conflictos de vacaciones.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio de la vacación
            end_date: Fecha de fin de la vacación
            exclude_vacation_id: ID de vacación a excluir (opcional)
        
        Returns:
            Dict[str, Any]: Información detallada sobre conflictos
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass