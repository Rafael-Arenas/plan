"""Interface para operaciones de validación de clientes.

Define el contrato que deben cumplir las implementaciones de operaciones
de validación para la entidad Cliente.
"""

from abc import ABC, abstractmethod


class IValidationOperations(ABC):
    """Interface para operaciones de validación de clientes."""

    @abstractmethod
    async def validate_client_name_unique(
        self, name: str, exclude_id: int | None = None
    ) -> bool:
        """Valida que el nombre del cliente sea único.
        
        Args:
            name: Nombre del cliente a validar
            exclude_id: ID del cliente a excluir de la validación (para updates)
            
        Returns:
            True si el nombre es único, False en caso contrario
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la validación
        """
        pass

    @abstractmethod
    async def validate_client_code_unique(
        self, code: str, exclude_id: int | None = None
    ) -> bool:
        """Valida que el código del cliente sea único.
        
        Args:
            code: Código del cliente a validar
            exclude_id: ID del cliente a excluir de la validación (para updates)
            
        Returns:
            True si el código es único, False en caso contrario
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la validación
        """
        pass

    @abstractmethod
    async def validate_client_deletion(self, client_id: int) -> bool:
        """Valida si un cliente puede ser eliminado.
        
        Args:
            client_id: ID del cliente a validar
            
        Returns:
            True si el cliente puede ser eliminado, False en caso contrario
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la validación
        """
        pass