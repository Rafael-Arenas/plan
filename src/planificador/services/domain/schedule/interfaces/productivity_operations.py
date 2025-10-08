"""
Interfaz para Operaciones de Análisis de Productividad del Servicio de Dominio Schedule.

Define los contratos para análisis de eficiencia, métricas de rendimiento,
evaluación de carga de trabajo y optimización de recursos.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.schemas.schedule.schedule import Schedule
from planificador.schemas.response.response_schemas import ScheduleSearchResponse


class IScheduleDomainProductivityOperations(ABC):
    """
    Interfaz para operaciones de análisis de productividad del servicio de dominio Schedule.
    
    Define los métodos para análisis de eficiencia, métricas de rendimiento
    y optimización de recursos con evaluación de carga de trabajo.
    """

    @abstractmethod
    async def analyze_employee_productivity(
        self,
        employee_id: int,
        analysis_start_date: date,
        analysis_end_date: date,
        include_comparisons: bool = True
    ) -> ScheduleSearchResponse:
        """
        Analiza la productividad de un empleado con métricas detalladas y comparaciones.
        
        Args:
            employee_id: ID del empleado
            analysis_start_date: Fecha de inicio del análisis
            analysis_end_date: Fecha de fin del análisis
            include_comparisons: Si incluir comparaciones con promedios del equipo
            
        Returns:
            ScheduleSearchResponse: Análisis completo de productividad
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def analyze_team_workload_distribution(
        self,
        team_id: int,
        analysis_date: date,
        include_recommendations: bool = True
    ) -> ScheduleSearchResponse:
        """
        Analiza la distribución de carga de trabajo del equipo con recomendaciones.
        
        Args:
            team_id: ID del equipo
            analysis_date: Fecha para el análisis
            include_recommendations: Si incluir recomendaciones de optimización
            
        Returns:
            ScheduleSearchResponse: Análisis de distribución de carga de trabajo
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def calculate_efficiency_metrics(
        self,
        entity_type: str,  # 'employee', 'team', 'project'
        entity_id: int,
        metrics_period_days: int = 30
    ) -> ScheduleSearchResponse:
        """
        Calcula métricas de eficiencia para empleados, equipos o proyectos.
        
        Args:
            entity_type: Tipo de entidad ('employee', 'team', 'project')
            entity_id: ID de la entidad
            metrics_period_days: Período en días para el cálculo de métricas
            
        Returns:
            ScheduleSearchResponse: Métricas de eficiencia calculadas
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def generate_resource_optimization_recommendations(
        self,
        scope: str,  # 'department', 'project', 'team'
        scope_id: int,
        optimization_period_start: date,
        optimization_period_end: date
    ) -> ScheduleSearchResponse:
        """
        Genera recomendaciones de optimización de recursos basadas en análisis de datos.
        
        Args:
            scope: Alcance del análisis ('department', 'project', 'team')
            scope_id: ID del alcance
            optimization_period_start: Inicio del período de optimización
            optimization_period_end: Fin del período de optimización
            
        Returns:
            ScheduleSearchResponse: Recomendaciones de optimización
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass