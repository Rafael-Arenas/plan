# -*- coding: utf-8 -*-
"""
Statistics Operations Interface for Client Domain Service

Define las operaciones de estadísticas y métricas para la entidad Client
con cálculos de negocio y análisis de datos.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID


class IStatisticsOperations(ABC):
    """
    Interfaz para operaciones de estadísticas del dominio Client.
    
    Define métodos para generar métricas, reportes y análisis
    estadísticos de los clientes con lógica de negocio aplicada.
    """

    @abstractmethod
    async def get_client_count_by_status(self) -> Dict[str, int]:
        """
        Obtiene el conteo de clientes agrupados por estado.
        
        Returns:
            Dict[str, int]: Diccionario con estado como clave y conteo como valor
        """
        pass

    @abstractmethod
    async def get_client_count_by_type(self) -> Dict[str, int]:
        """
        Obtiene el conteo de clientes agrupados por tipo.
        
        Returns:
            Dict[str, int]: Diccionario con tipo como clave y conteo como valor
        """
        pass

    @abstractmethod
    async def get_total_clients_count(
        self,
        include_inactive: bool = False
    ) -> int:
        """
        Obtiene el conteo total de clientes.
        
        Args:
            include_inactive: Si incluir clientes inactivos en el conteo
            
        Returns:
            int: Número total de clientes
        """
        pass

    @abstractmethod
    async def get_clients_growth_statistics(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: str = "month"
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de crecimiento de clientes en un período.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            group_by: Agrupación temporal (day, week, month, year)
            
        Returns:
            Dict[str, Any]: Estadísticas de crecimiento con métricas detalladas
        """
        pass

    @abstractmethod
    async def get_client_activity_metrics(
        self,
        client_id: Optional[UUID] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de actividad de clientes.
        
        Args:
            client_id: ID específico del cliente (None para todos)
            days_back: Días hacia atrás para el análisis
            
        Returns:
            Dict[str, Any]: Métricas de actividad detalladas
        """
        pass

    @abstractmethod
    async def get_client_distribution_by_region(self) -> Dict[str, int]:
        """
        Obtiene la distribución de clientes por región geográfica.
        
        Returns:
            Dict[str, int]: Diccionario con región como clave y conteo como valor
        """
        pass

    @abstractmethod
    async def calculate_client_retention_rate(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """
        Calcula la tasa de retención de clientes en un período.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Dict[str, float]: Métricas de retención detalladas
        """
        pass

    @abstractmethod
    async def get_client_engagement_score(
        self,
        client_id: UUID,
        calculation_period_days: int = 90
    ) -> Dict[str, Any]:
        """
        Calcula el score de engagement de un cliente específico.
        
        Args:
            client_id: ID del cliente
            calculation_period_days: Período de cálculo en días
            
        Returns:
            Dict[str, Any]: Score de engagement con detalles del cálculo
        """
        pass

    @abstractmethod
    async def get_top_clients_by_activity(
        self,
        limit: int = 10,
        activity_metric: str = "projects_count",
        period_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Obtiene los clientes más activos según una métrica específica.
        
        Args:
            limit: Número máximo de clientes a retornar
            activity_metric: Métrica de actividad a usar
            period_days: Período de análisis en días
            
        Returns:
            List[Dict[str, Any]]: Lista de clientes top con sus métricas
        """
        pass

    @abstractmethod
    async def generate_client_summary_report(
        self,
        include_trends: bool = True,
        include_predictions: bool = False
    ) -> Dict[str, Any]:
        """
        Genera un reporte resumen completo de clientes.
        
        Args:
            include_trends: Si incluir análisis de tendencias
            include_predictions: Si incluir predicciones básicas
            
        Returns:
            Dict[str, Any]: Reporte completo con todas las métricas
        """
        pass