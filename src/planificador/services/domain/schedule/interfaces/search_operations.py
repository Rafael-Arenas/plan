"""
Interfaz para Operaciones de Búsqueda y Filtrado del Servicio de Dominio Schedule.

Define los contratos para búsquedas avanzadas, filtrado por múltiples criterios
y consultas complejas con paginación y ordenamiento.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date, time

from planificador.schemas.schedule.schedule import (
    Schedule,
    ScheduleSearchFilter
)
from planificador.schemas.response.response_schemas import (
    ScheduleListResponse,
    ScheduleSearchResponse
)
from planificador.schemas.common_schemas import PaginationSchema


class IScheduleDomainSearchOperations(ABC):
    """
    Interfaz para operaciones de búsqueda y filtrado del servicio de dominio Schedule.
    
    Define los métodos para búsquedas avanzadas y filtrado por múltiples
    criterios con soporte para paginación y ordenamiento.
    """

    @abstractmethod
    async def search_schedules_by_criteria(
        self,
        criteria: ScheduleSearchFilter,
        pagination: Optional[PaginationSchema] = None
    ) -> ScheduleSearchResponse:
        """
        Busca horarios usando criterios múltiples con paginación y ordenamiento.
        
        Args:
            criteria: Criterios de búsqueda y filtrado
            pagination: Configuración de paginación (opcional)
            
        Returns:
            ScheduleSearchResponse: Resultados paginados con metadatos
            
        Raises:
            ValidationError: Si los criterios no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def find_schedules_by_date_range(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[int]] = None,
        project_ids: Optional[List[int]] = None
    ) -> List[ScheduleSearchResponse]:
        """
        Encuentra horarios en un rango de fechas con filtros opcionales.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            employee_ids: IDs de empleados a filtrar (opcional)
            project_ids: IDs de proyectos a filtrar (opcional)
            
        Returns:
            List[ScheduleSearchResponse]: Lista de horarios encontrados
            
        Raises:
            ValidationError: Si el rango de fechas no es válido
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def find_schedules_by_time_range(
        self,
        start_time: time,
        end_time: time,
        target_date: Optional[date] = None
    ) -> List[ScheduleSearchResponse]:
        """
        Encuentra horarios que se superponen con un rango de tiempo específico.
        
        Args:
            start_time: Hora de inicio del rango
            end_time: Hora de fin del rango
            target_date: Fecha específica a consultar (opcional, por defecto hoy)
            
        Returns:
            List[ScheduleSearchResponse]: Lista de horarios en el rango de tiempo
            
        Raises:
            ValidationError: Si el rango de tiempo no es válido
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def search_schedules_with_advanced_filters(
        self,
        filters: ScheduleSearchFilter,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc"
    ) -> List[ScheduleSearchResponse]:
        """
        Realiza búsqueda avanzada con filtros dinámicos y ordenamiento personalizado.
        
        Args:
            filters: Diccionario de filtros dinámicos
            sort_by: Campo por el cual ordenar (opcional)
            sort_order: Orden de clasificación: 'asc' o 'desc' (opcional)
            
        Returns:
            List[ScheduleSearchResponse]: Lista de horarios filtrados y ordenados
            
        Raises:
            ValidationError: Si los filtros o criterios de ordenamiento no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass