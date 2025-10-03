# -*- coding: utf-8 -*-
"""
Statistics Operations Interface for Employee Domain Service

Define las operaciones para generar estadísticas y métricas de empleados.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

from planificador.models.employee import EmployeeStatus


class IStatisticsOperations(ABC):
    """
    Interfaz para operaciones de estadísticas del dominio Employee.
    
    Define métodos para generar estadísticas, métricas y reportes
    sobre la información de empleados.
    """

    @abstractmethod
    async def get_employee_count_by_status(self) -> Dict[EmployeeStatus, int]:
        """
        Obtiene el conteo de empleados por estado.
        
        Returns:
            Dict[EmployeeStatus, int]: Conteo de empleados por cada estado
        """
        pass

    @abstractmethod
    async def get_employee_count_by_department(self) -> Dict[str, int]:
        """
        Obtiene el conteo de empleados por departamento.
        
        Returns:
            Dict[str, int]: Conteo de empleados por departamento
        """
        pass

    @abstractmethod
    async def get_salary_statistics(self) -> Dict[str, float]:
        """
        Obtiene estadísticas salariales de los empleados.
        
        Returns:
            Dict[str, float]: Estadísticas salariales (promedio, mediana, etc.)
        """
        pass

    @abstractmethod
    async def get_tenure_distribution(self) -> Dict[str, int]:
        """
        Obtiene la distribución de antigüedad de empleados.
        
        Returns:
            Dict[str, int]: Distribución por rangos de antigüedad
        """
        pass

    @abstractmethod
    async def generate_employee_summary_report(self) -> Dict[str, Any]:
        """
        Genera un reporte resumen completo de empleados.
        
        Returns:
            Dict[str, Any]: Reporte con métricas generales de empleados
        """
        pass