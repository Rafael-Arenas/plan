"""
Interfaz para Operaciones de Búsqueda y Filtrado del Servicio de Dominio Schedule.

Define los métodos de búsqueda avanzada y filtrado según la documentación oficial.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

from planificador.schemas.response.response_schemas import ScheduleResponseSchema
from planificador.schemas.schedule.schedule_advanced_filters import ScheduleAdvancedFilters


class IScheduleDomainSearchOperations(ABC):
    """
    Interfaz para operaciones de búsqueda y filtrado del servicio de dominio Schedule.
    
    Define los métodos de búsqueda según la documentación oficial.
    """

    @abstractmethod
    async def get_schedules_by_date(
        self,
        target_date: date,
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None
    ) -> List[ScheduleResponseSchema]:
        """
        Obtiene horarios para una fecha específica con filtros opcionales.
        
        Args:
            target_date: Fecha objetivo para la búsqueda
            employee_id: ID del empleado (opcional)
            project_id: ID del proyecto (opcional)
            
        Returns:
            List[ScheduleResponseSchema]: Lista de horarios encontrados
            
        Raises:
            ValidationError: Si la fecha no es válida
            RepositoryError: Si hay error en la base de datos
        """
        pass

    @abstractmethod
    async def get_confirmed_schedules(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        employee_id: Optional[int] = None
    ) -> List[ScheduleResponseSchema]:
        """
        Obtiene horarios confirmados con filtros opcionales de fecha y empleado.
        
        Args:
            date_from: Fecha de inicio del rango (opcional)
            date_to: Fecha de fin del rango (opcional)
            employee_id: ID del empleado (opcional)
            
        Returns:
            List[ScheduleResponseSchema]: Lista de horarios confirmados
            
        Raises:
            ValidationError: Si el rango de fechas no es válido
            RepositoryError: Si hay error en la base de datos
        """
        pass

    @abstractmethod
    async def search_schedules_advanced(
        self,
        filters: ScheduleAdvancedFilters
    ) -> List[ScheduleResponseSchema]:
        """
        Realiza búsqueda avanzada de horarios con filtros complejos.
        
        Args:
            filters: Filtros avanzados para la búsqueda
            
        Returns:
            List[ScheduleResponseSchema]: Lista de horarios encontrados
            
        Raises:
            ValidationError: Si los filtros no son válidos
            RepositoryError: Si hay error en la base de datos
        """
        pass