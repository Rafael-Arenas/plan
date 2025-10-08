"""
Interfaz para Operaciones de Diagnóstico del Servicio de Dominio Schedule.

Define los contratos para diagnósticos del sistema, análisis de salud de datos,
detección de anomalías y reportes de estado del sistema de horarios.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.schemas.schedule.schedule import Schedule
from planificador.schemas.response.response_schemas import ScheduleSearchResponse


class IScheduleDomainDiagnosticOperations(ABC):
    """
    Interfaz para operaciones de diagnóstico del servicio de dominio Schedule.
    
    Define los métodos para diagnósticos del sistema, análisis de salud
    de datos y detección de anomalías en el sistema de horarios.
    """

    @abstractmethod
    async def generate_system_health_report(
        self,
        include_performance_metrics: bool = True,
        include_data_quality_metrics: bool = True
    ) -> ScheduleSearchResponse:
        """
        Genera un reporte completo de salud del sistema de horarios.
        
        Args:
            include_performance_metrics: Si incluir métricas de rendimiento
            include_data_quality_metrics: Si incluir métricas de calidad de datos
            
        Returns:
            ScheduleSearchResponse: Reporte completo de salud del sistema
            
        Raises:
            RepositoryError: Si hay error en la consulta del sistema
        """
        pass

    @abstractmethod
    async def detect_schedule_anomalies(
        self,
        detection_period_start: date,
        detection_period_end: date,
        anomaly_types: Optional[List[str]] = None
    ) -> ScheduleSearchResponse:
        """
        Detecta anomalías en los datos de horarios durante un período específico.
        
        Args:
            detection_period_start: Inicio del período de detección
            detection_period_end: Fin del período de detección
            anomaly_types: Tipos específicos de anomalías a detectar (opcional)
            
        Returns:
            ScheduleSearchResponse: Reporte de anomalías detectadas
            
        Raises:
            ValidationError: Si el período no es válido
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def run_comprehensive_system_diagnostic(
        self,
        diagnostic_scope: str = "full",  # 'full', 'performance', 'data_integrity'
        include_recommendations: bool = True
    ) -> ScheduleSearchResponse:
        """
        Ejecuta un diagnóstico completo del sistema de horarios con recomendaciones.
        
        Args:
            diagnostic_scope: Alcance del diagnóstico ('full', 'performance', 'data_integrity')
            include_recommendations: Si incluir recomendaciones de mejora
            
        Returns:
            ScheduleSearchResponse: Diagnóstico completo del sistema
            
        Raises:
            ValidationError: Si el alcance no es válido
            RepositoryError: Si hay error en el diagnóstico
        """
        pass