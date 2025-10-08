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
    
    # ==========================================
    # ESTADÍSTICAS BÁSICAS (4 métodos)
    # ==========================================
    
    @abstractmethod
    async def get_total_assignments_count(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> int:
        """
        Obtiene el conteo total de asignaciones en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango (opcional)
            end_date: Fecha de fin del rango (opcional)
            
        Returns:
            int: Número total de asignaciones
            
        Raises:
            RepositoryError: Error al acceder a los datos
            ValidationError: Fechas inválidas
        """
        pass
    
    @abstractmethod
    async def get_active_assignments_count(
        self, 
        reference_date: Optional[date] = None
    ) -> int:
        """
        Obtiene el conteo de asignaciones activas en una fecha específica.
        
        Args:
            reference_date: Fecha de referencia (por defecto hoy)
            
        Returns:
            int: Número de asignaciones activas
            
        Raises:
            RepositoryError: Error al acceder a los datos
        """
        pass
    
    @abstractmethod
    async def get_assignments_by_status_count(self) -> Dict[str, int]:
        """
        Obtiene el conteo de asignaciones agrupadas por estado.
        
        Returns:
            Dict[str, int]: Diccionario con estado como clave y conteo como valor
            
        Raises:
            RepositoryError: Error al acceder a los datos
        """
        pass
    
    @abstractmethod
    async def get_assignments_by_allocation_category_count(self) -> Dict[str, int]:
        """
        Obtiene el conteo de asignaciones agrupadas por categoría de asignación.
        
        Returns:
            Dict[str, int]: Diccionario con categoría y conteo
            
        Raises:
            RepositoryError: Error al acceder a los datos
        """
        pass
    
    # ==========================================
    # ESTADÍSTICAS AVANZADAS (4 métodos)
    # ==========================================
    
    @abstractmethod
    async def get_assignment_duration_analytics(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene análisis avanzados de duración de asignaciones.
        
        Args:
            start_date: Fecha de inicio del análisis (opcional)
            end_date: Fecha de fin del análisis (opcional)
            
        Returns:
            Dict[str, Any]: Análisis de duración con métricas estadísticas
            
        Raises:
            RepositoryError: Error al acceder a los datos
            ValidationError: Fechas inválidas
        """
        pass
    
    @abstractmethod
    async def get_workload_distribution_analytics(self) -> Dict[str, Any]:
        """
        Obtiene análisis avanzados de distribución de carga de trabajo.
        
        Returns:
            Dict[str, Any]: Análisis de distribución de carga de trabajo
            
        Raises:
            RepositoryError: Error al acceder a los datos
        """
        pass
    
    @abstractmethod
    async def get_assignment_trends(
        self, 
        months_back: int = 12
    ) -> Dict[str, Any]:
        """
        Obtiene análisis de tendencias de asignaciones en el tiempo.
        
        Args:
            months_back: Número de meses hacia atrás para el análisis
            
        Returns:
            Dict[str, Any]: Análisis de tendencias temporales
            
        Raises:
            RepositoryError: Error al acceder a los datos
            ValidationError: Parámetros inválidos
        """
        pass
    
    @abstractmethod
    async def get_comprehensive_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas completas para dashboard ejecutivo.
        
        Returns:
            Dict[str, Any]: Métricas completas del dashboard
            
        Raises:
            RepositoryError: Error al acceder a los datos
        """
        pass