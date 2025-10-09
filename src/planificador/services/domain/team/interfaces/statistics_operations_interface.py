# src/planificador/services/domain/team/interfaces/statistics_operations.py

"""
Interfaz para operaciones de estadísticas del servicio de dominio de Team.

Define los métodos para análisis cuantitativos de equipos, conteos,
tendencias temporales y métricas básicas de gestión.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime
from pydantic import BaseModel

from .search_operations import TeamStatus


class TeamCreationTrend(BaseModel):
    """Modelo para tendencias de creación de equipos."""
    period: str
    count: int
    percentage_change: float


class ITeamDomainStatisticsOperations(ABC):
    """
    Interfaz para operaciones de estadísticas del servicio de dominio de Team.
    
    Define los métodos para generar estadísticas básicas, conteos y análisis
    cuantitativos de equipos y sus tendencias temporales.
    """

    @abstractmethod
    async def get_team_member_count(
        self,
        team_id: int
    ) -> int:
        """
        Obtiene el número total de miembros de un equipo.
        
        Args:
            team_id: Identificador único del equipo
            
        Returns:
            int: Número de miembros del equipo
            
        Raises:
            NotFoundError: Si el equipo no existe
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_teams_count_by_status(self) -> Dict[str, int]:
        """
        Obtiene el conteo de equipos agrupados por estado.
        
        Returns:
            Dict[str, int]: Conteo de equipos por estado
            
        Raises:
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_average_team_size(self) -> float:
        """
        Calcula el tamaño promedio de los equipos en el sistema.
        
        Returns:
            float: Tamaño promedio de equipos
            
        Raises:
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_team_creation_trends(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[TeamCreationTrend]:
        """
        Obtiene tendencias de creación de equipos por período.
        
        Args:
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
            
        Returns:
            List[TeamCreationTrend]: Lista de tendencias por período
            
        Raises:
            ValidationError: Si las fechas son inválidas
            RepositoryError: Si hay error en la consulta
        """
        pass