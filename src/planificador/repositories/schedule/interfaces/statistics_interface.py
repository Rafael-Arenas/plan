# src/planificador/repositories/schedule/interfaces/statistics_interface.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import date
from decimal import Decimal


class IScheduleStatisticsOperations(ABC):
    """
    Interface para operaciones de estadísticas del repositorio Schedule.
    
    Define los métodos para generar estadísticas, métricas y reportes
    relacionados con los horarios de empleados, proyectos y equipos.
    """
    
    @abstractmethod
    async def get_employee_hours_summary(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Obtiene resumen de horas trabajadas por empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Dict con estadísticas de horas del empleado
        """
        pass
    
    @abstractmethod
    async def get_project_hours_summary(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Obtiene resumen de horas por proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Dict con estadísticas de horas del proyecto
        """
        pass
    
    @abstractmethod
    async def get_team_hours_summary(
        self,
        team_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Obtiene resumen de horas por equipo.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Dict con estadísticas de horas del equipo
        """
        pass
    
    @abstractmethod
    async def get_schedule_counts_by_status(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Obtiene conteo de horarios por estado.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            employee_id: ID del empleado (opcional)
            
        Returns:
            Dict con conteos por estado
        """
        pass
    
    @abstractmethod
    async def get_productivity_metrics(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de productividad.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            employee_id: ID del empleado (opcional)
            project_id: ID del proyecto (opcional)
            
        Returns:
            Dict con métricas de productividad
        """
        pass
    
    @abstractmethod
    async def get_utilization_report(
        self,
        start_date: date,
        end_date: date,
        group_by: str = "employee"  # "employee", "project", "team"
    ) -> List[Dict[str, Any]]:
        """
        Obtiene reporte de utilización de tiempo.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            group_by: Criterio de agrupación
            
        Returns:
            Lista de diccionarios con datos de utilización
        """
        pass
    
    @abstractmethod
    async def get_confirmation_statistics(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de confirmación de horarios.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Dict con estadísticas de confirmación
        """
        pass
    
    @abstractmethod
    async def get_overtime_analysis(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene análisis de horas extra.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            employee_id: ID del empleado (opcional)
            
        Returns:
            Dict con análisis de horas extra
        """
        pass
    
    @abstractmethod
    async def get_schedule_distribution(
        self,
        start_date: date,
        end_date: date,
        distribution_type: str = "daily"  # "daily", "weekly", "monthly"
    ) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de horarios en el tiempo.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            distribution_type: Tipo de distribución temporal
            
        Returns:
            Lista con distribución de horarios
        """
        pass
    
    @abstractmethod
    async def get_top_performers(
        self,
        start_date: date,
        end_date: date,
        metric: str = "hours",  # "hours", "efficiency", "consistency"
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtiene ranking de mejores performers.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            metric: Métrica para el ranking
            limit: Número máximo de resultados
            
        Returns:
            Lista ordenada de performers
        """
        pass