# -*- coding: utf-8 -*-
"""
Health Operations Interface for Client Domain Service

Define las operaciones de salud, diagnóstico y monitoreo para la entidad Client
con verificaciones de sistema y métricas de rendimiento.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from uuid import UUID


class IHealthOperations(ABC):
    """
    Interfaz para operaciones de salud y diagnóstico del dominio Client.
    
    Define métodos para monitorear la salud del sistema,
    diagnosticar problemas y generar métricas de rendimiento.
    """

    @abstractmethod
    async def check_service_health(self) -> Dict[str, Any]:
        """
        Verifica la salud general del servicio de clientes.
        
        Returns:
            Dict[str, Any]: Estado de salud con métricas y diagnósticos
        """
        pass

    @abstractmethod
    async def check_database_connectivity(self) -> Dict[str, Any]:
        """
        Verifica la conectividad con la base de datos.
        
        Returns:
            Dict[str, Any]: Estado de la conexión con métricas de rendimiento
        """
        pass

    @abstractmethod
    async def get_service_performance_metrics(
        self,
        include_historical: bool = False
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de rendimiento del servicio.
        
        Args:
            include_historical: Si incluir datos históricos
            
        Returns:
            Dict[str, Any]: Métricas detalladas de rendimiento
        """
        pass

    @abstractmethod
    async def diagnose_client_data_issues(
        self,
        client_id: Optional[UUID] = None,
        check_relationships: bool = True
    ) -> Dict[str, Any]:
        """
        Diagnostica problemas en los datos de clientes.
        
        Args:
            client_id: ID específico del cliente (None para todos)
            check_relationships: Si verificar integridad de relaciones
            
        Returns:
            Dict[str, Any]: Diagnóstico detallado con problemas encontrados
        """
        pass

    @abstractmethod
    async def get_system_resource_usage(self) -> Dict[str, Any]:
        """
        Obtiene el uso de recursos del sistema.
        
        Returns:
            Dict[str, Any]: Métricas de uso de recursos (memoria, CPU, etc.)
        """
        pass

    @abstractmethod
    async def validate_data_consistency(
        self,
        fix_issues: bool = False
    ) -> Dict[str, Any]:
        """
        Valida la consistencia de datos en el sistema.
        
        Args:
            fix_issues: Si intentar corregir problemas automáticamente
            
        Returns:
            Dict[str, Any]: Reporte de consistencia con problemas encontrados
        """
        pass

    @abstractmethod
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del cache del servicio.
        
        Returns:
            Dict[str, Any]: Métricas de cache (hits, misses, tamaño, etc.)
        """
        pass

    @abstractmethod
    async def run_maintenance_tasks(
        self,
        task_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta tareas de mantenimiento del servicio.
        
        Args:
            task_types: Tipos específicos de tareas (None = todas)
            
        Returns:
            Dict[str, Any]: Resultado de las tareas de mantenimiento
        """
        pass

    @abstractmethod
    async def generate_health_report(
        self,
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """
        Genera un reporte completo de salud del servicio.
        
        Args:
            include_recommendations: Si incluir recomendaciones de mejora
            
        Returns:
            Dict[str, Any]: Reporte completo de salud del sistema
        """
        pass

    @abstractmethod
    async def monitor_service_alerts(
        self,
        alert_level: str = "warning"
    ) -> List[Dict[str, Any]]:
        """
        Monitorea alertas del servicio.
        
        Args:
            alert_level: Nivel mínimo de alerta (info, warning, error, critical)
            
        Returns:
            List[Dict[str, Any]]: Lista de alertas activas
        """
        pass