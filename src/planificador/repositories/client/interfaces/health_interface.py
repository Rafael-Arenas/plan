"""Interface para operaciones de salud del sistema de clientes.

Define el contrato que deben cumplir las implementaciones de operaciones
de monitoreo y salud del sistema para el repositorio de clientes.
"""

from abc import ABC, abstractmethod
from typing import Any


class IHealthOperations(ABC):
    """Interface para operaciones de salud del sistema."""

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Realiza una verificación de salud del repositorio.
        
        Returns:
            Diccionario con información de salud del sistema
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la verificación
        """
        pass

    @abstractmethod
    async def get_module_info(self) -> dict[str, Any]:
        """Obtiene información del módulo y sus capacidades.
        
        Returns:
            Diccionario con información del módulo
            
        Raises:
            ClientRepositoryError: Si ocurre un error obteniendo la información
        """
        pass