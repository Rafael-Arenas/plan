"""
Interfaz para las operaciones de estadísticas de proyectos.

Esta interfaz define el contrato para la generación de estadísticas, métricas
y análisis de rendimiento de proyectos.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import date

from planificador.schemas.project.statistics import (
    ProjectStatusSummary,
    OverdueProjectSummary,
    ProjectPerformanceStats,
    ProjectWorkloadStats,
    ProjectDurationStats,
    ProjectDashboardSummary
)


class IProjectStatisticsOperations(ABC):
    """
    Interfaz abstracta para las operaciones de estadísticas de proyectos.
    
    Define el contrato para la generación de todas las estadísticas, métricas
    y análisis de rendimiento relacionados con proyectos.
    """

    # ==========================================
    # ESTADÍSTICAS GENERALES
    # ==========================================

    @abstractmethod
    async def get_project_status_summary(
        self,
        client_id: Optional[int] = None,
        date_range: Optional[tuple[date, date]] = None
    ) -> ProjectStatusSummary:
        """
        Obtiene resumen de estadísticas por estado de proyectos.
        
        Args:
            client_id (int, optional): Filtrar por cliente específico
            date_range (tuple[date, date], optional): Rango de fechas
            
        Returns:
            ProjectStatusSummary: Resumen de estadísticas por estado
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_overdue_projects_summary(
        self,
        client_id: Optional[int] = None
    ) -> OverdueProjectSummary:
        """
        Obtiene resumen de proyectos vencidos.
        
        Args:
            client_id (int, optional): Filtrar por cliente específico
            
        Returns:
            OverdueProjectSummary: Resumen de proyectos vencidos
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_project_performance_stats(
        self,
        date_range: Optional[tuple[date, date]] = None,
        client_id: Optional[int] = None
    ) -> ProjectPerformanceStats:
        """
        Obtiene estadísticas de rendimiento de proyectos.
        
        Args:
            date_range (tuple[date, date], optional): Rango de fechas
            client_id (int, optional): Filtrar por cliente específico
            
        Returns:
            ProjectPerformanceStats: Estadísticas de rendimiento
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_project_workload_stats(
        self,
        date_range: Optional[tuple[date, date]] = None
    ) -> ProjectWorkloadStats:
        """
        Obtiene estadísticas de carga de trabajo de proyectos.
        
        Args:
            date_range (tuple[date, date], optional): Rango de fechas
            
        Returns:
            ProjectWorkloadStats: Estadísticas de carga de trabajo
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_project_duration_stats(
        self,
        client_id: Optional[int] = None,
        date_range: Optional[tuple[date, date]] = None
    ) -> ProjectDurationStats:
        """
        Obtiene estadísticas de duración de proyectos.
        
        Args:
            client_id (int, optional): Filtrar por cliente específico
            date_range (tuple[date, date], optional): Rango de fechas
            
        Returns:
            ProjectDurationStats: Estadísticas de duración
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_dashboard_summary(
        self,
        user_id: Optional[int] = None,
        client_id: Optional[int] = None
    ) -> ProjectDashboardSummary:
        """
        Obtiene resumen para dashboard principal.
        
        Args:
            user_id (int, optional): Filtrar por usuario específico
            client_id (int, optional): Filtrar por cliente específico
            
        Returns:
            ProjectDashboardSummary: Resumen para dashboard
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # ESTADÍSTICAS POR CLIENTE
    # ==========================================

    @abstractmethod
    async def get_client_project_statistics(self, client_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas completas de proyectos por cliente.
        
        Args:
            client_id (int): ID del cliente
            
        Returns:
            Dict[str, Any]: Estadísticas del cliente
            
        Raises:
            NotFoundError: Si el cliente no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_client_performance_comparison(self) -> Dict[str, Any]:
        """
        Obtiene comparación de rendimiento entre clientes.
        
        Returns:
            Dict[str, Any]: Comparación de rendimiento por cliente
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_client_project_trends(
        self,
        client_id: int,
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Obtiene tendencias de proyectos de un cliente.
        
        Args:
            client_id (int): ID del cliente
            months (int): Número de meses para análisis
            
        Returns:
            Dict[str, Any]: Tendencias de proyectos del cliente
            
        Raises:
            NotFoundError: Si el cliente no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # ESTADÍSTICAS TEMPORALES
    # ==========================================

    @abstractmethod
    async def get_monthly_project_statistics(
        self,
        year: int,
        month: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas mensuales de proyectos.
        
        Args:
            year (int): Año para análisis
            month (int, optional): Mes específico (si no se proporciona, todo el año)
            
        Returns:
            Dict[str, Any]: Estadísticas mensuales
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_quarterly_project_statistics(self, year: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas trimestrales de proyectos.
        
        Args:
            year (int): Año para análisis
            
        Returns:
            Dict[str, Any]: Estadísticas trimestrales
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_yearly_project_statistics(
        self,
        years: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas anuales de proyectos.
        
        Args:
            years (List[int], optional): Años específicos para análisis
            
        Returns:
            Dict[str, Any]: Estadísticas anuales
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_project_timeline_statistics(
        self,
        date_range: tuple[date, date]
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de línea de tiempo de proyectos.
        
        Args:
            date_range (tuple[date, date]): Rango de fechas para análisis
            
        Returns:
            Dict[str, Any]: Estadísticas de línea de tiempo
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # ESTADÍSTICAS DE RECURSOS Y EQUIPOS
    # ==========================================

    @abstractmethod
    async def get_employee_project_statistics(
        self,
        employee_id: int,
        date_range: Optional[tuple[date, date]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de proyectos por empleado.
        
        Args:
            employee_id (int): ID del empleado
            date_range (tuple[date, date], optional): Rango de fechas
            
        Returns:
            Dict[str, Any]: Estadísticas del empleado
            
        Raises:
            NotFoundError: Si el empleado no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_team_project_statistics(
        self,
        team_id: int,
        date_range: Optional[tuple[date, date]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de proyectos por equipo.
        
        Args:
            team_id (int): ID del equipo
            date_range (tuple[date, date], optional): Rango de fechas
            
        Returns:
            Dict[str, Any]: Estadísticas del equipo
            
        Raises:
            NotFoundError: Si el equipo no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_resource_utilization_statistics(
        self,
        date_range: Optional[tuple[date, date]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de utilización de recursos.
        
        Args:
            date_range (tuple[date, date], optional): Rango de fechas
            
        Returns:
            Dict[str, Any]: Estadísticas de utilización de recursos
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # ESTADÍSTICAS DE PRODUCTIVIDAD
    # ==========================================

    @abstractmethod
    async def get_productivity_metrics(
        self,
        date_range: Optional[tuple[date, date]] = None,
        group_by: str = "month"
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de productividad de proyectos.
        
        Args:
            date_range (tuple[date, date], optional): Rango de fechas
            group_by (str): Agrupación (day, week, month, quarter, year)
            
        Returns:
            Dict[str, Any]: Métricas de productividad
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_efficiency_statistics(
        self,
        client_id: Optional[int] = None,
        date_range: Optional[tuple[date, date]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de eficiencia de proyectos.
        
        Args:
            client_id (int, optional): Filtrar por cliente específico
            date_range (tuple[date, date], optional): Rango de fechas
            
        Returns:
            Dict[str, Any]: Estadísticas de eficiencia
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_quality_metrics(
        self,
        date_range: Optional[tuple[date, date]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de calidad de proyectos.
        
        Args:
            date_range (tuple[date, date], optional): Rango de fechas
            
        Returns:
            Dict[str, Any]: Métricas de calidad
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # ESTADÍSTICAS COMPARATIVAS
    # ==========================================

    @abstractmethod
    async def get_comparative_project_analysis(
        self,
        project_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Obtiene análisis comparativo entre proyectos específicos.
        
        Args:
            project_ids (List[int]): IDs de proyectos a comparar
            
        Returns:
            Dict[str, Any]: Análisis comparativo
            
        Raises:
            NotFoundError: Si algún proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_benchmark_statistics(
        self,
        category: str = "all"
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de benchmark del sistema.
        
        Args:
            category (str): Categoría de benchmark (all, performance, quality, efficiency)
            
        Returns:
            Dict[str, Any]: Estadísticas de benchmark
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # ESTADÍSTICAS PREDICTIVAS
    # ==========================================

    @abstractmethod
    async def get_project_forecast_statistics(
        self,
        forecast_months: int = 6
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de pronóstico de proyectos.
        
        Args:
            forecast_months (int): Meses hacia adelante para pronóstico
            
        Returns:
            Dict[str, Any]: Estadísticas de pronóstico
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_trend_analysis_statistics(
        self,
        metric: str = "completion_rate",
        periods: int = 12
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de análisis de tendencias.
        
        Args:
            metric (str): Métrica para análisis de tendencias
            periods (int): Número de períodos para análisis
            
        Returns:
            Dict[str, Any]: Estadísticas de tendencias
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # EXPORTACIÓN DE ESTADÍSTICAS
    # ==========================================

    @abstractmethod
    async def export_statistics_report(
        self,
        report_type: str,
        format_type: str = "json",
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Exporta reporte de estadísticas en formato específico.
        
        Args:
            report_type (str): Tipo de reporte (summary, detailed, comparative)
            format_type (str): Formato de exportación (json, csv, excel)
            filters (Dict[str, Any], optional): Filtros para el reporte
            
        Returns:
            Dict[str, Any]: Datos del reporte exportado
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def generate_custom_statistics_report(
        self,
        metrics: List[str],
        dimensions: List[str],
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Genera reporte personalizado de estadísticas.
        
        Args:
            metrics (List[str]): Métricas a incluir en el reporte
            dimensions (List[str]): Dimensiones para agrupación
            filters (Dict[str, Any], optional): Filtros para el reporte
            
        Returns:
            Dict[str, Any]: Reporte personalizado
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass