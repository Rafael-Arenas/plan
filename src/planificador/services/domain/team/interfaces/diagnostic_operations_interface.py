# src/planificador/services/domain/team/interfaces/diagnostic_operations.py

"""
Interfaz para operaciones de diagnóstico del servicio de dominio de Team.

Define los métodos para filtros temporales específicos y monitoreo
de salud del servicio y sus dependencias críticas.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import pendulum

from .....schemas.team.team import Team
from .....schemas.team.team_advanced_schemas import TeamSchema


class ITeamDomainDiagnosticOperations(ABC):
    """
    Interfaz para operaciones de diagnóstico del servicio de dominio de Team.
    
    Define los métodos para diagnóstico del sistema, filtros temporales
    y monitoreo de salud del servicio.
    """

    @abstractmethod
    async def get_teams_by_creation_date(
        self,
        target_date: datetime,
        tolerance_hours: int = 24
    ) -> List[TeamSchema]:
        """
        Obtiene equipos creados en una fecha específica con tolerancia.
        
        Args:
            target_date: Fecha objetivo para buscar equipos
            tolerance_hours: Tolerancia en horas para la búsqueda
            
        Returns:
            List[TeamSchema]: Lista de equipos encontrados
            
        Raises:
            ValidationError: Si los parámetros son inválidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def check_service_health(self) -> Dict[str, Any]:
        """
        Verifica el estado de salud del servicio de equipos y dependencias.
        
        Returns:
            Dict[str, Any]: Estado de salud detallado del servicio
            
        Raises:
            RepositoryError: Si hay error en la verificación
        """
        pass