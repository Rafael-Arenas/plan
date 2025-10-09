# src/planificador/services/domain/team/interfaces/productivity_operations.py

"""
Interfaz para operaciones de análisis de productividad del servicio de dominio de Team.

Define los métodos para métricas avanzadas de rendimiento, colaboración,
benchmarking y reportes ejecutivos de equipos.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
import pendulum


class DateRange(BaseModel):
    """Modelo para rangos de fechas."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    start_date: pendulum.DateTime
    end_date: pendulum.DateTime


class TeamPerformanceMetrics(BaseModel):
    """Modelo para métricas de rendimiento de equipo."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    team_id: int
    efficiency_score: float
    collaboration_index: float
    task_completion_rate: float
    quality_metrics: Dict[str, float]
    period: DateRange


class ProductivityAnalysis(BaseModel):
    """Modelo para análisis de productividad."""
    analysis_period: str
    teams_analyzed: int
    average_productivity: float
    top_performers: List[Dict[str, Any]]
    improvement_areas: List[str]


class CollaborationMetrics(BaseModel):
    """Modelo para métricas de colaboración."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    team_synergy_score: float
    cross_team_interactions: int
    communication_effectiveness: float
    knowledge_sharing_index: float


class TeamsSummaryReport(BaseModel):
    """Modelo para reporte resumen de equipos."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    report_format: str
    generation_date: pendulum.DateTime
    total_teams: int
    active_teams: int
    performance_summary: Dict[str, Any]
    recommendations: List[str]


class ITeamDomainProductivityOperations(ABC):
    """
    Interfaz para operaciones de análisis de productividad del servicio de dominio de Team.
    
    Define los métodos para generar métricas avanzadas de rendimiento,
    análisis de colaboración y reportes ejecutivos de equipos.
    """

    @abstractmethod
    async def get_team_performance_metrics(
        self,
        team_id: int,
        date_range: DateRange
    ) -> TeamPerformanceMetrics:
        """
        Calcula métricas avanzadas de rendimiento de un equipo específico.
        
        Args:
            team_id: Identificador único del equipo
            date_range: Rango de fechas para el análisis
            
        Returns:
            TeamPerformanceMetrics: Métricas de rendimiento del equipo
            
        Raises:
            NotFoundError: Si el equipo no existe
            ValidationError: Si los parámetros son inválidos
            RepositoryError: Si hay error en el cálculo
        """
        pass

    @abstractmethod
    async def get_teams_productivity_analysis(
        self,
        date_range: DateRange
    ) -> ProductivityAnalysis:
        """
        Analiza la productividad de todos los equipos en un rango de fechas.
        
        Args:
            date_range: Rango de fechas para el análisis
            
        Returns:
            ProductivityAnalysis: Análisis de productividad de equipos
            
        Raises:
            ValidationError: Si el rango de fechas es inválido
            RepositoryError: Si hay error en el análisis
        """
        pass

    @abstractmethod
    async def get_team_collaboration_metrics(
        self,
        team_id: int,
        date_range: DateRange
    ) -> CollaborationMetrics:
        """
        Obtiene métricas de colaboración para un equipo específico.
        
        Args:
            team_id: Identificador único del equipo
            date_range: Rango de fechas para el análisis
            
        Returns:
            CollaborationMetrics: Métricas de colaboración del equipo
            
        Raises:
            NotFoundError: Si el equipo no existe
            ValidationError: Si los parámetros son inválidos
            RepositoryError: Si hay error en el cálculo
        """
        pass

    @abstractmethod
    async def generate_teams_summary_report(
        self,
        date_range: DateRange
    ) -> TeamsSummaryReport:
        """
        Genera un reporte resumen de todos los equipos.
        
        Args:
            date_range: Rango de fechas para el reporte
            
        Returns:
            TeamsSummaryReport: Reporte resumen de equipos
            
        Raises:
            ValidationError: Si los parámetros son inválidos
            RepositoryError: Si hay error en la generación
        """
        pass