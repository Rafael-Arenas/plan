from abc import ABC, abstractmethod
from typing import Dict, Any

class IValidationOperations(ABC):
    """
    Interfaz para operaciones de validación de clientes.
    """

    @abstractmethod
    def validate_create_data(self, data: Dict[str, Any]) -> None:
        """
        Valida los datos para crear un nuevo cliente.
        """
        pass

    @abstractmethod
    def validate_update_data(self, data: Dict[str, Any]) -> None:
        """
        Valida los datos para actualizar un cliente existente.
        """
        pass

    @abstractmethod
    def validate_client_id(self, client_id: int) -> None:
        """
        Valida que un ID de cliente sea válido.
        """
        pass