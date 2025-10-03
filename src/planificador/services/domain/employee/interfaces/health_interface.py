# -*- coding: utf-8 -*-
"""
Health Operations Interface for Employee Domain Service

Define las operaciones de salud y diagnóstico del servicio de empleados.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IHealthOperations(ABC):
    """
    Interfaz para operaciones de salud del dominio Employee.
    
    Define métodos para verificar el estado de salud del servicio
    y realizar diagnósticos del sistema.
    """

    @abstractmethod
    async def check_service_health(self) -> Dict[str, Any]:
        """
        Verifica el estado de salud del servicio de empleados.
        
        Returns:
            Dict[str, Any]: Estado de salud con métricas del servicio
        """
        pass

    @abstractmethod
    async def get_service_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas operacionales del servicio.
        
        Returns:
            Dict[str, Any]: Métricas de rendimiento y uso del servicio
        """
        pass