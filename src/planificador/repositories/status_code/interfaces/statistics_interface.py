# src/planificador/repositories/status_code/interfaces/statistics_interface.py

"""
Interfaz para operaciones de estadísticas y análisis de códigos de estado.

Define los métodos de análisis estadístico y métricas para la entidad
StatusCode, incluyendo estadísticas de uso y análisis de distribución.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from planificador.models.status_code import StatusCode


class IStatusCodeStatisticsOperations(ABC):
    """
    Interfaz abstracta para operaciones de estadísticas de códigos de estado.
    
    Define los métodos de análisis estadístico que debe implementar cualquier
    módulo que maneje métricas, estadísticas de uso y análisis de distribución
    de códigos de estado.
    
    Métodos incluyen estadísticas generales de uso, análisis de distribución
    por características y métricas de rendimiento del sistema.
    """

    # ==========================================
    # ESTADÍSTICAS GENERALES DE USO
    # ==========================================

    @abstractmethod
    async def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de uso de los códigos de estado.
        
        Incluye métricas como:
        - Total de códigos de estado
        - Distribución por características (activos, facturables, productivos)
        - Códigos más utilizados
        - Códigos menos utilizados
        - Estadísticas de aprobación
        
        Returns:
            Dict[str, Any]: Diccionario con estadísticas de uso
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    # ==========================================
    # ANÁLISIS DE DISTRIBUCIÓN
    # ==========================================

    @abstractmethod
    async def get_distribution_by_characteristics(self) -> Dict[str, Any]:
        """
        Obtiene la distribución de códigos por características.
        
        Analiza la distribución de códigos según:
        - Estado activo/inactivo
        - Códigos facturables vs no facturables
        - Códigos productivos vs no productivos
        - Códigos que requieren aprobación
        
        Returns:
            Dict[str, Any]: Diccionario con análisis de distribución
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    @abstractmethod
    async def get_sort_order_analysis(self) -> Dict[str, Any]:
        """
        Obtiene análisis del ordenamiento de códigos.
        
        Incluye:
        - Rango de valores de sort_order
        - Gaps en la secuencia de ordenamiento
        - Códigos duplicados en sort_order
        - Sugerencias de reorganización
        
        Returns:
            Dict[str, Any]: Diccionario con análisis de ordenamiento
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    # ==========================================
    # MÉTRICAS DE RENDIMIENTO
    # ==========================================

    @abstractmethod
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas de rendimiento del sistema de códigos de estado.
        
        Incluye:
        - Tiempo promedio de consultas
        - Códigos más consultados
        - Eficiencia de filtros
        - Recomendaciones de optimización
        
        Returns:
            Dict[str, Any]: Diccionario con métricas de rendimiento
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    # ==========================================
    # ANÁLISIS DE INTEGRIDAD
    # ==========================================

    @abstractmethod
    async def get_integrity_report(self) -> Dict[str, Any]:
        """
        Obtiene reporte de integridad de códigos de estado.
        
        Verifica:
        - Códigos duplicados
        - Inconsistencias en características
        - Códigos huérfanos o no utilizados
        - Problemas de ordenamiento
        
        Returns:
            Dict[str, Any]: Diccionario con reporte de integridad
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass