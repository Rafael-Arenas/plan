# src/planificador/repositories/workload/interfaces/statistics_interface.py

"""
Interfaz para operaciones de estadísticas del repositorio Workload.

Este módulo define la interfaz abstracta para las operaciones de análisis,
métricas y estadísticas de cargas de trabajo.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para estadísticas
    - Analytics Focus: Definición de métricas y análisis especializados
    - Single Responsibility: Solo operaciones de estadísticas y análisis

Uso:
    ```python
    class WorkloadStatisticsModule(IWorkloadStatisticsOperations):
        async def get_employee_total_hours(self, employee_id: int, start_date: date, end_date: date) -> float:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import date

from planificador.exceptions.repository import WorkloadRepositoryError


class IWorkloadStatisticsOperations(ABC):
    """
    Interfaz abstracta para operaciones de estadísticas de cargas de trabajo.
    
    Define los métodos de análisis y estadísticas que debe implementar cualquier
    módulo que maneje métricas, análisis y reportes de cargas de trabajo.
    
    Incluye estadísticas por empleado, proyecto, equipo y análisis avanzados
    como distribución de carga y tendencias temporales.
    """

    # Estadísticas por Empleado
    @abstractmethod
    async def get_employee_total_hours(self, employee_id: int, start_date: date, end_date: date) -> float:
        """
        Calcula el total de horas trabajadas por un empleado en un período.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
        
        Returns:
            float: Total de horas trabajadas
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el cálculo
        """
        pass

    @abstractmethod
    async def get_employee_average_hours(self, employee_id: int, start_date: date, end_date: date) -> float:
        """
        Calcula el promedio de horas diarias trabajadas por un empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
        
        Returns:
            float: Promedio de horas diarias
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el cálculo
        """
        pass

    @abstractmethod
    async def get_employee_workload_distribution(self, employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Obtiene la distribución de carga de trabajo de un empleado por proyectos.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
        
        Returns:
            Dict[str, Any]: Distribución de horas por proyecto
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el análisis
        """
        pass

    # Estadísticas por Proyecto
    @abstractmethod
    async def get_project_total_hours(self, project_id: int, start_date: date, end_date: date) -> float:
        """
        Calcula el total de horas invertidas en un proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
        
        Returns:
            float: Total de horas del proyecto
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el cálculo
        """
        pass

    @abstractmethod
    async def get_project_employee_distribution(self, project_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Obtiene la distribución de horas por empleado en un proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
        
        Returns:
            Dict[str, Any]: Distribución de horas por empleado
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el análisis
        """
        pass

    # Estadísticas por Equipo
    @abstractmethod
    async def get_team_total_hours(self, team_id: int, start_date: date, end_date: date) -> float:
        """
        Calcula el total de horas trabajadas por un equipo.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
        
        Returns:
            float: Total de horas del equipo
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el cálculo
        """
        pass

    @abstractmethod
    async def get_team_average_hours(self, team_id: int, start_date: date, end_date: date) -> float:
        """
        Calcula el promedio de horas diarias trabajadas por un equipo.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
        
        Returns:
            float: Promedio de horas diarias del equipo
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el cálculo
        """
        pass

    @abstractmethod
    async def get_team_workload_distribution(self, team_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Obtiene la distribución de carga de trabajo de un equipo.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
        
        Returns:
            Dict[str, Any]: Distribución de carga por empleado y proyecto
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el análisis
        """
        pass

    # Análisis Avanzado
    @abstractmethod
    async def get_workload_trends(self, start_date: date, end_date: date, granularity: str = "daily") -> List[Dict[str, Any]]:
        """
        Analiza tendencias de carga de trabajo en el tiempo.
        
        Args:
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
            granularity: Granularidad del análisis ("daily", "weekly", "monthly")
        
        Returns:
            List[Dict[str, Any]]: Datos de tendencias por período
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el análisis
        """
        pass

    @abstractmethod
    async def get_capacity_utilization(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Calcula la utilización de capacidad general.
        
        Args:
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
        
        Returns:
            Dict[str, Any]: Métricas de utilización de capacidad
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el cálculo
        """
        pass

    @abstractmethod
    async def get_peak_workload_periods(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        Identifica períodos de mayor carga de trabajo.
        
        Args:
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
        
        Returns:
            List[Dict[str, Any]]: Períodos de pico con métricas
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el análisis
        """
        pass