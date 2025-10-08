"""
Interfaz para Operaciones de Estadísticas de Horas del Servicio de Dominio Schedule.

Define los contratos para cálculos estadísticos, análisis de horas trabajadas,
reportes de tiempo y métricas de utilización de recursos.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.schemas.schedule.schedule import Schedule
from planificador.schemas.response.response_schemas import ScheduleSearchResponse


class IScheduleDomainStatisticsOperations(ABC):
    """
    Interfaz para operaciones de estadísticas de horas del servicio de dominio Schedule.
    
    Define los métodos para cálculos estadísticos, análisis de horas
    y reportes de tiempo con métricas de utilización.
    """

    @abstractmethod
    async def calculate_total_hours_by_employee(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> ScheduleSearchResponse:
        """
        Calcula estadísticas completas de horas trabajadas por empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            ScheduleSearchResponse: Estadísticas detalladas de horas
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def calculate_total_hours_by_project(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> ScheduleSearchResponse:
        """
        Calcula estadísticas completas de horas asignadas por proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            ScheduleSearchResponse: Estadísticas detalladas de horas del proyecto
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def generate_weekly_hours_report(
        self,
        week_start_date: date,
        employee_ids: Optional[List[int]] = None
    ) -> ScheduleSearchResponse:
        """
        Genera reporte semanal de horas con análisis comparativo.
        
        Args:
            week_start_date: Fecha de inicio de la semana
            employee_ids: IDs de empleados a incluir (opcional, todos si es None)
            
        Returns:
            ScheduleSearchResponse: Reporte semanal completo
            
        Raises:
            ValidationError: Si la fecha no es válida
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def generate_monthly_hours_report(
        self,
        year: int,
        month: int,
        include_breakdown: bool = True
    ) -> ScheduleSearchResponse:
        """
        Genera reporte mensual de horas con desglose detallado.
        
        Args:
            year: Año del reporte
            month: Mes del reporte (1-12)
            include_breakdown: Si incluir desglose por empleado/proyecto
            
        Returns:
            ScheduleSearchResponse: Reporte mensual completo
            
        Raises:
            ValidationError: Si el año/mes no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def analyze_employee_hours_distribution(
        self,
        employee_id: int,
        analysis_period_months: int = 3
    ) -> ScheduleSearchResponse:
        """
        Analiza la distribución de horas de un empleado en un período.
        
        Args:
            employee_id: ID del empleado
            analysis_period_months: Número de meses hacia atrás a analizar
            
        Returns:
            ScheduleSearchResponse: Análisis de distribución de horas
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_project_hours_distribution(
        self,
        project_id: int,
        include_team_breakdown: bool = True
    ) -> ScheduleSearchResponse:
        """
        Obtiene la distribución de horas por proyecto con desglose de equipo.
        
        Args:
            project_id: ID del proyecto
            include_team_breakdown: Si incluir desglose por miembros del equipo
            
        Returns:
            ScheduleSearchResponse: Distribución de horas del proyecto
            
        Raises:
            ValidationError: Si el project_id no es válido
            RepositoryError: Si hay error en la consulta
        """
        pass