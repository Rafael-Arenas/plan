# src/planificador/repositories/vacation/interfaces/query_interface.py

"""
Interfaz para operaciones de consulta del repositorio Vacation.

Este módulo define la interfaz abstracta para las operaciones de
búsqueda y consulta de vacaciones en el sistema.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para consultas
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones de consulta

Uso:
    ```python
    class VacationQueryModule(IVacationQueryOperations):
        async def get_by_employee_id(self, employee_id: int) -> List[Vacation]:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.models.vacation import Vacation
from planificador.enums.vacation_status import VacationStatus
from planificador.enums.vacation_type import VacationType
from planificador.exceptions.repository import VacationRepositoryError


class IVacationQueryOperations(ABC):
    """
    Interfaz abstracta para operaciones de consulta de vacaciones.
    
    Define los métodos de búsqueda y consulta que debe implementar
    cualquier módulo que maneje la recuperación de datos de vacaciones.
    
    Métodos:
        - Consultas básicas por empleado, estado, tipo, fechas
        - Búsquedas con filtros múltiples
        - Consultas especializadas (pendientes, solapamientos, etc.)
        - Consultas con relaciones cargadas
    """

    @abstractmethod
    async def get_by_employee_id(self, employee_id: int) -> List[Vacation]:
        """
        Obtiene todas las vacaciones de un empleado.
        
        Args:
            employee_id: ID del empleado
        
        Returns:
            List[Vacation]: Lista de vacaciones del empleado
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_by_status(self, status: VacationStatus) -> List[Vacation]:
        """
        Obtiene vacaciones por estado específico.
        
        Args:
            status: Estado de las vacaciones a buscar
        
        Returns:
            List[Vacation]: Lista de vacaciones con el estado especificado
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_by_type(self, vacation_type: VacationType) -> List[Vacation]:
        """
        Obtiene vacaciones por tipo específico.
        
        Args:
            vacation_type: Tipo de vacaciones a buscar
        
        Returns:
            List[Vacation]: Lista de vacaciones del tipo especificado
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_by_date_range(self, start_date: date, end_date: date) -> List[Vacation]:
        """
        Obtiene vacaciones en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
        
        Returns:
            List[Vacation]: Lista de vacaciones en el rango especificado
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_by_employee_and_date_range(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date
    ) -> List[Vacation]:
        """
        Obtiene vacaciones de un empleado en un rango de fechas específico.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
        
        Returns:
            List[Vacation]: Lista de vacaciones del empleado en el rango
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def search_vacations(
        self,
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[VacationStatus] = None,
        vacation_type: Optional[VacationType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Vacation]:
        """
        Busca vacaciones con múltiples filtros.
        
        Args:
            employee_id: ID del empleado (opcional)
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            status: Estado de la vacación (opcional)
            vacation_type: Tipo de vacación (opcional)
            limit: Límite de resultados
            offset: Desplazamiento para paginación
        
        Returns:
            List[Vacation]: Lista de vacaciones que coinciden con los filtros
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la búsqueda
        """
        pass

    @abstractmethod
    async def get_employee_vacations(
        self, 
        employee_id: int, 
        year: Optional[int] = None
    ) -> List[Vacation]:
        """
        Obtiene vacaciones de un empleado por año.
        
        Args:
            employee_id: ID del empleado
            year: Año específico (opcional, por defecto año actual)
        
        Returns:
            List[Vacation]: Lista de vacaciones del empleado en el año
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_pending_approvals(self, limit: int = 50) -> List[Vacation]:
        """
        Obtiene todas las vacaciones pendientes de aprobación.
        
        Args:
            limit: Límite de resultados
        
        Returns:
            List[Vacation]: Lista de vacaciones pendientes de aprobación
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_overlapping_vacations(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> List[Vacation]:
        """
        Obtiene vacaciones que se solapan con un período específico.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            employee_id: ID del empleado (opcional, para filtrar por empleado)
        
        Returns:
            List[Vacation]: Lista de vacaciones que se solapan
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_current_month_vacations(self) -> List[Vacation]:
        """
        Obtiene vacaciones del mes actual.
        
        Returns:
            List[Vacation]: Lista de vacaciones del mes actual
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_upcoming_vacations(self, days_ahead: int = 30) -> List[Vacation]:
        """
        Obtiene vacaciones próximas en los siguientes días.
        
        Args:
            days_ahead: Número de días hacia adelante a considerar
        
        Returns:
            List[Vacation]: Lista de vacaciones próximas
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_with_relations(self, vacation_id: int) -> Optional[Vacation]:
        """
        Obtiene vacación con todas las relaciones cargadas.
        
        Args:
            vacation_id: ID de la vacación
        
        Returns:
            Optional[Vacation]: Vacación con relaciones o None si no existe
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass