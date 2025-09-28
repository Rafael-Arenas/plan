# src/planificador/repositories/team_membership/interfaces/statistics_interface.py

"""
Interfaz para operaciones estadísticas del repositorio TeamMembership.

Este módulo define la interfaz abstracta para las operaciones de
análisis estadístico y métricas relacionadas con membresías de equipos.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para estadísticas
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones estadísticas

Uso:
    ```python
    class TeamMembershipStatisticsModule(ITeamMembershipStatisticsOperations):
        async def count_total_memberships(self) -> int:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import date
from enum import Enum

from planificador.models.team_membership import MembershipRole, MembershipStatus


class StatisticsPeriod(Enum):
    """Períodos para análisis estadísticos."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ITeamMembershipStatisticsOperations(ABC):
    """
    Interfaz abstracta para operaciones estadísticas de membresías.
    
    Define los métodos para generar estadísticas, métricas y análisis
    relacionados con las membresías de equipos.
    
    Métodos:
        - Conteos y distribuciones
        - Análisis de tendencias temporales
        - Métricas de rotación y retención
        - Estadísticas por roles y equipos
    """
    
    @abstractmethod
    async def count_total_memberships(
        self,
        active_only: bool = False,
        as_of_date: Optional[date] = None
    ) -> int:
        """
        Cuenta el total de membresías en el sistema.
        
        Args:
            active_only: Si solo contar membresías activas
            as_of_date: Fecha de referencia (opcional)
        
        Returns:
            int: Número total de membresías
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el conteo
        """
        pass
    
    @abstractmethod
    async def count_memberships_by_status(
        self,
        as_of_date: Optional[date] = None
    ) -> Dict[MembershipStatus, int]:
        """
        Cuenta membresías agrupadas por estado.
        
        Args:
            as_of_date: Fecha de referencia (opcional)
        
        Returns:
            Dict[MembershipStatus, int]: Conteo por estado
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el conteo
        """
        pass
    
    @abstractmethod
    async def count_memberships_by_role(
        self,
        active_only: bool = True,
        as_of_date: Optional[date] = None
    ) -> Dict[MembershipRole, int]:
        """
        Cuenta membresías agrupadas por rol.
        
        Args:
            active_only: Si solo contar membresías activas
            as_of_date: Fecha de referencia (opcional)
        
        Returns:
            Dict[MembershipRole, int]: Conteo por rol
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el conteo
        """
        pass
    
    @abstractmethod
    async def get_membership_duration_statistics(
        self,
        completed_only: bool = True
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de duración de membresías.
        
        Args:
            completed_only: Si solo incluir membresías completadas
        
        Returns:
            Dict[str, Any]: Estadísticas de duración (promedio, mediana, etc.)
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el cálculo
        """
        pass
    
    @abstractmethod
    async def get_team_size_distribution(
        self,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene distribución de tamaños de equipos.
        
        Args:
            as_of_date: Fecha de referencia (opcional)
        
        Returns:
            Dict[str, Any]: Distribución de tamaños de equipos
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el cálculo
        """
        pass
    
    @abstractmethod
    async def get_employee_participation_stats(
        self,
        employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de participación de empleados.
        
        Args:
            employee_id: ID del empleado específico (opcional)
        
        Returns:
            Dict[str, Any]: Estadísticas de participación
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el cálculo
        """
        pass
    
    @abstractmethod
    async def get_membership_trends(
        self,
        period: StatisticsPeriod,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Obtiene tendencias de membresías por período.
        
        Args:
            period: Período de agrupación
            start_date: Fecha de inicio
            end_date: Fecha de fin
        
        Returns:
            List[Dict[str, Any]]: Tendencias por período
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el cálculo
        """
        pass
    
    @abstractmethod
    async def get_turnover_rate(
        self,
        team_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calcula la tasa de rotación de membresías.
        
        Args:
            team_id: ID del equipo específico (opcional)
            start_date: Fecha de inicio del período (opcional)
            end_date: Fecha de fin del período (opcional)
        
        Returns:
            Dict[str, Any]: Métricas de rotación
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el cálculo
        """
        pass
    
    @abstractmethod
    async def get_retention_rate(
        self,
        team_id: Optional[int] = None,
        months_threshold: int = 12
    ) -> Dict[str, Any]:
        """
        Calcula la tasa de retención de membresías.
        
        Args:
            team_id: ID del equipo específico (opcional)
            months_threshold: Umbral en meses para considerar retención
        
        Returns:
            Dict[str, Any]: Métricas de retención
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el cálculo
        """
        pass
    
    @abstractmethod
    async def get_role_transition_matrix(
        self,
        team_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene matriz de transiciones entre roles.
        
        Args:
            team_id: ID del equipo específico (opcional)
        
        Returns:
            Dict[str, Any]: Matriz de transiciones de roles
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el cálculo
        """
        pass
    
    @abstractmethod
    async def get_membership_overlap_statistics(
        self,
        employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de solapamiento de membresías.
        
        Args:
            employee_id: ID del empleado específico (opcional)
        
        Returns:
            Dict[str, Any]: Estadísticas de solapamiento
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el cálculo
        """
        pass
    
    @abstractmethod
    async def get_team_stability_metrics(
        self,
        team_id: int,
        analysis_period_months: int = 12
    ) -> Dict[str, Any]:
        """
        Calcula métricas de estabilidad de un equipo.
        
        Args:
            team_id: ID del equipo
            analysis_period_months: Período de análisis en meses
        
        Returns:
            Dict[str, Any]: Métricas de estabilidad del equipo
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el cálculo
        """
        pass
    
    @abstractmethod
    async def get_leadership_statistics(
        self,
        team_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de liderazgo.
        
        Args:
            team_id: ID del equipo específico (opcional)
        
        Returns:
            Dict[str, Any]: Estadísticas de liderazgo
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el cálculo
        """
        pass
    
    @abstractmethod
    async def get_membership_summary_report(
        self,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte resumen de membresías.
        
        Args:
            as_of_date: Fecha de referencia (opcional)
        
        Returns:
            Dict[str, Any]: Reporte resumen completo
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la generación
        """
        pass
    
    @abstractmethod
    async def get_team_composition_analysis(
        self,
        team_id: int,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Analiza la composición de un equipo específico.
        
        Args:
            team_id: ID del equipo
            as_of_date: Fecha de referencia (opcional)
        
        Returns:
            Dict[str, Any]: Análisis de composición del equipo
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el análisis
        """
        pass
    
    @abstractmethod
    async def get_cross_team_participation(
        self,
        employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analiza la participación cruzada entre equipos.
        
        Args:
            employee_id: ID del empleado específico (opcional)
        
        Returns:
            Dict[str, Any]: Análisis de participación cruzada
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el análisis
        """
        pass