"""
Interfaz para Operaciones de Análisis de Productividad del Servicio de Dominio Schedule.

Define los contratos para análisis de productividad, reportes de utilización
y análisis de distribución de horarios según la documentación oficial.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.schemas.schedule.schedule import (
    ProductivityMetricsSchema,
    UtilizationReportSchema,
    ScheduleDistributionSchema
)


class IScheduleDomainProductivityOperations(ABC):
    """
    Interfaz para operaciones de análisis de productividad del servicio de dominio Schedule.
    
    Define los métodos para análisis de métricas de productividad, reportes de utilización
    y análisis de distribución de horarios según la documentación oficial.
    """

    @abstractmethod
    async def get_productivity_metrics(
        self,
        employee_id: Optional[int] = None,
        team_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        include_trends: bool = False
    ) -> ProductivityMetricsSchema:
        """
        Obtiene métricas de productividad para empleados o equipos.
        
        Calcula métricas detalladas de productividad incluyendo horas trabajadas,
        eficiencia, cumplimiento de objetivos y tendencias históricas.
        
        Args:
            employee_id: ID del empleado (opcional)
            team_id: ID del equipo (opcional)
            start_date: Fecha de inicio del período de análisis (opcional)
            end_date: Fecha de fin del período de análisis (opcional)
            include_trends: Si incluir análisis de tendencias históricas
            
        Returns:
            ProductivityMetricsSchema: Métricas de productividad calculadas
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta de datos
            BusinessLogicError: Si la lógica de negocio no se cumple
        """
        pass

    @abstractmethod
    async def get_utilization_report(
        self,
        resource_type: str,  # 'employee', 'team', 'department'
        resource_id: int,
        period_start: date,
        period_end: date,
        include_breakdown: bool = True
    ) -> UtilizationReportSchema:
        """
        Genera reporte de utilización de recursos.
        
        Analiza la utilización de empleados, equipos o departamentos durante
        un período específico, incluyendo desglose por proyectos y actividades.
        
        Args:
            resource_type: Tipo de recurso ('employee', 'team', 'department')
            resource_id: ID del recurso
            period_start: Fecha de inicio del período
            period_end: Fecha de fin del período
            include_breakdown: Si incluir desglose detallado por actividades
            
        Returns:
            UtilizationReportSchema: Reporte de utilización del recurso
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta de datos
            BusinessLogicError: Si la lógica de negocio no se cumple
        """
        pass

    @abstractmethod
    async def get_schedule_distribution_analysis(
        self,
        analysis_scope: str,  # 'department', 'team', 'project'
        scope_id: int,
        analysis_date: date,
        include_recommendations: bool = False
    ) -> ScheduleDistributionSchema:
        """
        Analiza la distribución de horarios y carga de trabajo.
        
        Examina cómo se distribuyen los horarios y la carga de trabajo
        en departamentos, equipos o proyectos, identificando patrones
        y oportunidades de optimización.
        
        Args:
            analysis_scope: Alcance del análisis ('department', 'team', 'project')
            scope_id: ID del alcance a analizar
            analysis_date: Fecha de referencia para el análisis
            include_recommendations: Si incluir recomendaciones de optimización
            
        Returns:
            ScheduleDistributionSchema: Análisis de distribución de horarios
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta de datos
            BusinessLogicError: Si la lógica de negocio no se cumple
        """
        pass