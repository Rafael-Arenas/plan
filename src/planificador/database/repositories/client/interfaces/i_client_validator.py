"""Interface para validación de datos de cliente.

Esta interface define los métodos de validación que deben ser implementados
por las clases de validación de cliente, permitiendo la inyección de
dependencias y evitando referencias circulares.
"""

from abc import ABC, abstractmethod
from typing import Any


class IClientValidator(ABC):
    """Interface abstracta para validación de datos de cliente.

    Define los métodos que deben implementar las clases de validación
    para garantizar la integridad de los datos de cliente.
    """

    @abstractmethod
    def validate_client_data(
        self, client_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Valida los datos de creación de un cliente.

        Args:
            client_data: Datos del cliente a validar.

        Returns:
            Datos validados y normalizados.

        Raises:
            ValidationError: Si los datos no son válidos.
        """
        pass

    @abstractmethod
    def validate_update_data(
        self, update_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Valida los datos de actualización de un cliente.

        Args:
            update_data: Datos de actualización del cliente.

        Returns:
            Datos validados y normalizados.

        Raises:
            ValidationError: Si los datos no son válidos.
        """
        pass

    @abstractmethod
    def validate_email_format(self, email: str) -> bool:
        """Valida el formato de un email.

        Args:
            email: Email a validar.

        Returns:
            True si el formato es válido, False en caso contrario.
        """
        pass

    @abstractmethod
    def validate_phone_format(self, phone: str | None) -> bool:
        """Valida el formato de un teléfono.

        Args:
            phone: Teléfono a validar (puede ser None).

        Returns:
            True si el formato es válido o es None, False en caso contrario.
        """
        pass
