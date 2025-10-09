"""
Interfaz para Operaciones de Proyecto del Servicio de Dominio Schedule.

Define los contratos para consultas y análisis centrados en proyectos específicos
con líneas de tiempo y gestión de equipos de proyecto.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

from planificador.schemas.schedule.schedule import Schedule
from planificador.schemas.response.response_schemas import ScheduleListResponse, ScheduleSearchResponse


class IScheduleDomainProjectOperations(ABC):
    """
    Interfaz para operaciones de proyecto del servicio de dominio Schedule.
    
    Define los métodos para consultas y análisis centrados en proyectos
    específicos con gestión de equipos y líneas de tiempo.
    """

    @abstractmethod
    async def get_project_schedules(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[ScheduleListResponse]:
        """
        Obtiene todos los horarios asociados a un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del rango (opcional)
            end_date: Fecha de fin del rango (opcional)
            
        Returns:
            List[ScheduleListResponse]: Lista de horarios del proyecto
            
        Raises:
            ValidationError: Si el project_id no es válido
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_project_team_schedules(
        self,
        project_id: int,
        include_employee_details: bool = True
    ) -> ScheduleListResponse:
        """
        Obtiene horarios completos del equipo asignado al proyecto.
        
        Args:
            project_id: ID del proyecto
            include_employee_details: Si incluir detalles de empleados
            
        Returns:
            ScheduleListResponse: Horarios del equipo con detalles
            
        Raises:
            ValidationError: Si el project_id no es válido
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_project_schedule_timeline(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> ScheduleSearchResponse:
        """
        Genera una línea de tiempo visual de horarios del proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio de la línea de tiempo
            end_date: Fecha de fin de la línea de tiempo
            
        Returns:
            ScheduleSearchResponse: Línea de tiempo del proyecto
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass