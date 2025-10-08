# src/planificador/services/domain/project_assignment/interfaces/statistics_operations_interface.py

"""
Interfaz para Operaciones Estadísticas de Asignaciones de Proyecto

Define el contrato para operaciones estadísticas básicas y avanzadas,
incluyendo métricas de rendimiento, análisis temporal y tendencias.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import date

from planificador.schemas import ProjectAssignment


class IStatisticsOperations(ABC):
    """
    Interfaz para operaciones estadísticas de asignaciones de proyecto.
    
    Proporciona métodos para generar estadísticas básicas y avanzadas,
    análisis de tendencias y métricas de rendimiento.
    """
    
    # ============================================================================
    # ESTADÍSTICAS BÁSICAS (4 métodos)
    # ============================================================================
    
    @abstractmethod
    async def get_assignment_count_by_status(self) -> Dict[str, int]:
        """
        Cuenta asignaciones agrupadas por estado (activo/inactivo).
        
        Returns:
            Dict con conteos por estado:
            - active: Número de asignaciones activas
            - inactive: Número de asignaciones inactivas
            - total: Total de asignaciones
            - active_percentage: Porcentaje de asignaciones activas
            - inactive_percentage: Porcentaje de asignaciones inactivas
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_assignment_distribution_by_role(self) -> Dict[str, Any]:
        """
        Analiza la distribución de asignaciones por rol.
        
        Returns:
            Dict con distribución por rol:
            - role_counts: Conteo de asignaciones por rol
            - role_percentages: Porcentajes por rol
            - most_common_role: Rol más común
            - least_common_role: Rol menos común
            - role_diversity_index: Índice de diversidad de roles (0.0-1.0)
            - total_roles: Número total de roles únicos
            - total_assignments: Total de asignaciones analizadas
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_average_allocation_metrics(self) -> Dict[str, float]:
        """
        Calcula métricas promedio de asignación de recursos.
        
        Returns:
            Dict con métricas promedio:
            - average_percentage_allocation: Asignación promedio en porcentaje
            - average_hours_per_day: Horas promedio por día
            - median_percentage_allocation: Mediana de asignación en porcentaje
            - median_hours_per_day: Mediana de horas por día
            - std_dev_percentage: Desviación estándar de porcentajes
            - std_dev_hours: Desviación estándar de horas
            - min_allocation: Asignación mínima
            - max_allocation: Asignación máxima
            - allocation_range: Rango de asignaciones
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_assignment_duration_statistics(self) -> Dict[str, Any]:
        """
        Analiza estadísticas de duración de asignaciones.
        
        Returns:
            Dict con estadísticas de duración:
            - average_duration_days: Duración promedio en días
            - median_duration_days: Mediana de duración en días
            - shortest_assignment_days: Asignación más corta
            - longest_assignment_days: Asignación más larga
            - duration_std_dev: Desviación estándar de duraciones
            - duration_distribution: Distribución de duraciones por rangos
            - assignments_by_duration_category: Categorización por duración
            - duration_trends: Tendencias de duración a lo largo del tiempo
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    # ============================================================================
    # ESTADÍSTICAS AVANZADAS (4 métodos)
    # ============================================================================
    
    @abstractmethod
    async def get_temporal_assignment_trends(
        self, 
        start_date: date, 
        end_date: date, 
        granularity: str = "monthly"
    ) -> Dict[str, Any]:
        """
        Analiza tendencias temporales de asignaciones en un período.
        
        Args:
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
            granularity: Granularidad del análisis ("daily", "weekly", "monthly", "quarterly")
            
        Returns:
            Dict con análisis temporal:
            - period_analyzed: Período analizado
            - granularity: Granularidad utilizada
            - assignment_trends: Tendencias de asignaciones por período
            - creation_trends: Tendencias de creación de asignaciones
            - completion_trends: Tendencias de finalización
            - peak_periods: Períodos de mayor actividad
            - low_activity_periods: Períodos de menor actividad
            - seasonal_patterns: Patrones estacionales identificados
            - trend_analysis: Análisis de tendencias (creciente/decreciente)
            - forecast_indicators: Indicadores para pronósticos
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_resource_utilization_analysis(
        self, 
        analysis_period_days: int = 90
    ) -> Dict[str, Any]:
        """
        Análisis avanzado de utilización de recursos en el período especificado.
        
        Args:
            analysis_period_days: Días hacia atrás para el análisis (default: 90)
            
        Returns:
            Dict con análisis de utilización:
            - analysis_period: Período analizado
            - overall_utilization_rate: Tasa general de utilización
            - utilization_by_employee: Utilización detallada por empleado
            - utilization_by_project: Utilización por proyecto
            - utilization_by_role: Utilización por rol
            - peak_utilization_periods: Períodos de máxima utilización
            - underutilization_analysis: Análisis de subutilización
            - overallocation_risks: Riesgos de sobreasignación
            - utilization_efficiency_score: Puntuación de eficiencia (0.0-1.0)
            - optimization_opportunities: Oportunidades de optimización
            
        Raises:
            ValidationError: Si el período no es válido
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_project_assignment_performance_metrics(
        self, 
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Métricas avanzadas de rendimiento de asignaciones por proyecto.
        
        Args:
            project_id: ID del proyecto específico (None para todos los proyectos)
            
        Returns:
            Dict con métricas de rendimiento:
            - scope: Alcance del análisis (proyecto específico o global)
            - assignment_efficiency_score: Puntuación de eficiencia de asignaciones
            - team_stability_index: Índice de estabilidad del equipo
            - resource_allocation_balance: Balance de asignación de recursos
            - assignment_completion_rate: Tasa de finalización de asignaciones
            - average_assignment_lifecycle: Ciclo de vida promedio
            - role_distribution_effectiveness: Efectividad de distribución de roles
            - workload_balance_score: Puntuación de balance de carga
            - assignment_quality_indicators: Indicadores de calidad
            - performance_benchmarks: Benchmarks de rendimiento
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_predictive_assignment_insights(self) -> Dict[str, Any]:
        """
        Insights predictivos basados en patrones históricos de asignaciones.
        
        Returns:
            Dict con insights predictivos:
            - historical_patterns: Patrones históricos identificados
            - seasonal_predictions: Predicciones estacionales
            - resource_demand_forecast: Pronóstico de demanda de recursos
            - capacity_planning_insights: Insights para planificación de capacidad
            - risk_indicators: Indicadores de riesgo identificados
            - optimization_recommendations: Recomendaciones de optimización
            - trend_predictions: Predicciones de tendencias futuras
            - workload_projections: Proyecciones de carga de trabajo
            - assignment_lifecycle_predictions: Predicciones de ciclo de vida
            - strategic_insights: Insights estratégicos para toma de decisiones
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass