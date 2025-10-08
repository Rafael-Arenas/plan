"""
Interfaz para operaciones de estadísticas de horarios.

Este módulo define la interfaz abstracta para las operaciones de estadísticas
del dominio de horarios, incluyendo cálculos de horas, reportes y análisis.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from planificador.schemas.schedule.statistics import (
    EmployeeHoursSummarySchema,
    ProjectHoursSummarySchema,
    TeamHoursSummarySchema,
    OvertimeAnalysisSchema
)


class IScheduleDomainStatisticsOperations(ABC):
    """
    Interfaz abstracta para operaciones de estadísticas de horarios.
    
    Define los métodos que deben implementar las clases concretas para
    proporcionar funcionalidades de estadísticas y análisis de horarios.
    """

    @abstractmethod
    async def get_employee_hours_summary(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> EmployeeHoursSummarySchema:
        """
        Calcula resumen completo de horas trabajadas por empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            EmployeeHoursSummarySchema: Resumen completo de horas trabajadas
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            NotFoundError: Si el empleado no existe
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_project_hours_summary(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> ProjectHoursSummarySchema:
        """
        Obtiene resumen de horas invertidas en un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            ProjectHoursSummarySchema: Resumen de horas del proyecto
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_team_hours_summary(
        self,
        team_id: int,
        start_date: date,
        end_date: date
    ) -> TeamHoursSummarySchema:
        """
        Calcula distribución de horas trabajadas por equipo.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            TeamHoursSummarySchema: Distribución de horas del equipo
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            NotFoundError: Si el equipo no existe
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_overtime_analysis(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> OvertimeAnalysisSchema:
        """
        Analiza patrones de horas extra y sobrecarga laboral.
        
        Args:
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
            employee_id: ID del empleado para filtrar (opcional)
            
        Returns:
            OvertimeAnalysisSchema: Análisis de horas extra y sobrecarga
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass