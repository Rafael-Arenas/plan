"""
Interfaz para Operaciones de Equipo del Servicio de Dominio Schedule.

Define los contratos para consultas y análisis centrados en equipos específicos
con coordinación de horarios y análisis de disponibilidad grupal.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

from planificador.schemas.schedule.schedule import Schedule
from planificador.schemas.response.response_schemas import ScheduleListResponse, ScheduleSearchResponse


class IScheduleDomainTeamOperations(ABC):
    """
    Interfaz para operaciones de equipo del servicio de dominio Schedule.
    
    Define los métodos para consultas y análisis centrados en equipos
    específicos con coordinación y disponibilidad grupal.
    """

    @abstractmethod
    async def get_team_schedules(
        self,
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[ScheduleListResponse]:
        """
        Obtiene todos los horarios de los miembros de un equipo específico.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del rango (opcional)
            end_date: Fecha de fin del rango (opcional)
            
        Returns:
            List[ScheduleListResponse]: Lista de horarios del equipo
            
        Raises:
            ValidationError: Si el team_id no es válido
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_team_schedule_coordination(
        self,
        team_id: int,
        coordination_date: date
    ) -> ScheduleSearchResponse:
        """
        Analiza la coordinación de horarios del equipo para una fecha específica.
        
        Args:
            team_id: ID del equipo
            coordination_date: Fecha para análisis de coordinación
            
        Returns:
            ScheduleSearchResponse: Análisis de coordinación del equipo
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_team_availability_analysis(
        self,
        team_id: int,
        analysis_period_start: date,
        analysis_period_end: date
    ) -> ScheduleSearchResponse:
        """
        Realiza análisis completo de disponibilidad del equipo en un período.
        
        Args:
            team_id: ID del equipo
            analysis_period_start: Inicio del período de análisis
            analysis_period_end: Fin del período de análisis
            
        Returns:
            ScheduleSearchResponse: Análisis de disponibilidad del equipo
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass