# src/planificador/repositories/vacation/interfaces/statistics_interface.py

"""
Interfaz para operaciones de estadísticas del repositorio Vacation.

Este módulo define la interfaz abstracta para las operaciones de
cálculo de estadísticas, métricas y análisis de vacaciones.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para estadísticas
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones de análisis y estadísticas

Uso:
    ```python
    class VacationStatisticsModule(IVacationStatisticsOperations):
        async def get_vacation_summary_by_employee(self, employee_id: int, year: int) -> Dict[str, Any]:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import date

from planificador.exceptions.repository import VacationRepositoryError


class IVacationStatisticsOperations(ABC):
    """
    Interfaz abstracta para operaciones de estadísticas de vacaciones.
    
    Define los métodos para generar estadísticas, métricas y análisis
    relacionados con vacaciones, balances y patrones de uso.
    
    Métodos:
        - Estadísticas por empleado (resúmenes, tendencias)
        - Estadísticas por equipo (métricas grupales)
        - Análisis avanzado (balances, patrones)
        - Reportes y métricas de uso
    """

    @abstractmethod
    async def get_vacation_summary_by_employee(
        self, 
        employee_id: int, 
        year: int
    ) -> Dict[str, Any]:
        """
        Obtiene resumen estadístico de vacaciones por empleado.
        
        Args:
            employee_id: ID del empleado
            year: Año para el análisis
        
        Returns:
            Dict[str, Any]: Resumen estadístico de vacaciones
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante el cálculo
        """
        pass

    @abstractmethod
    async def get_vacation_trends_by_employee(
        self, 
        employee_id: int, 
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Obtiene tendencias de uso de vacaciones por empleado.
        
        Args:
            employee_id: ID del empleado
            months: Número de meses hacia atrás para el análisis
        
        Returns:
            List[Dict[str, Any]]: Lista de tendencias por período
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante el cálculo
        """
        pass

    @abstractmethod
    async def get_team_vacation_statistics(
        self, 
        employee_ids: List[int], 
        year: int
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de vacaciones para un equipo.
        
        Args:
            employee_ids: Lista de IDs de empleados del equipo
            year: Año para el análisis
        
        Returns:
            Dict[str, Any]: Estadísticas del equipo
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante el cálculo
        """
        pass

    @abstractmethod
    async def get_team_vacation_summary(
        self, 
        employee_ids: List[int], 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """
        Obtiene resumen de vacaciones para un equipo en un período específico.
        
        Args:
            employee_ids: Lista de IDs de empleados del equipo
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
        
        Returns:
            Dict[str, Any]: Resumen de vacaciones del equipo
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante el cálculo
        """
        pass

    @abstractmethod
    async def get_vacation_balance_analysis(
        self, 
        employee_id: int, 
        reference_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Analiza balances de vacaciones de empleados.
        
        Args:
            employee_id: ID del empleado
            reference_date: Fecha de referencia (opcional, por defecto hoy)
        
        Returns:
            Dict[str, Any]: Análisis de balance de vacaciones
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante el análisis
        """
        pass

    @abstractmethod
    async def get_vacation_patterns_analysis(
        self,
        employee_ids: Optional[List[int]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Analiza patrones de uso de vacaciones en un período.
        
        Args:
            employee_ids: Lista de IDs de empleados (opcional)
            start_date: Fecha de inicio del análisis (opcional)
            end_date: Fecha de fin del análisis (opcional)
        
        Returns:
            Dict[str, Any]: Análisis de patrones de uso
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante el análisis
        """
        pass