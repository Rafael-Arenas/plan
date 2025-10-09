"""
Interfaz para Operaciones de Diagnóstico del Servicio de Dominio Schedule.

Define los contratos para diagnósticos del sistema, análisis de salud de datos,
detección de anomalías y reportes de estado del sistema de horarios.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IScheduleDomainDiagnosticOperations(ABC):
    """
    Interfaz para operaciones de diagnóstico del servicio de dominio Schedule.
    
    Define los métodos para diagnósticos del sistema, análisis de salud
    de datos y detección de anomalías en el sistema de horarios.
    """

    @abstractmethod
    async def check_service_health(self) -> Dict[str, Any]:
        """
        Verifica el estado de salud del servicio de horarios y sus dependencias.
        
        Returns:
            Dict[str, Any]: Diccionario con información del estado de salud del servicio
            
        Raises:
            RepositoryError: Si hay error en la verificación del sistema
        """
        pass