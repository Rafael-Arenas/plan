"""Módulo de operaciones de validación para clientes.

Este módulo implementa funcionalidades especializadas para validación
de datos de clientes, incluyendo validaciones de unicidad, formato
y reglas de negocio específicas.

Características principales:
- Validación de unicidad de campos clave
- Validación de formatos (email, teléfono, etc.)
- Validación de reglas de negocio
- Validación de integridad referencial
- Manejo robusto de errores con logging estructurado
- Operaciones asíncronas optimizadas

Autor: Sistema de Repositorios
Versión: 2.0.0
"""

import re
from typing import Any, Coroutine, Dict, Optional

from loguru import logger

from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository.client_repository_exceptions import (
    ClientDuplicateError,
    ClientValidationError,
)
from planificador.models.client import Client
from planificador.repositories.client.interfaces.validation_interface import (
    IValidationOperations,
)


class ValidationOperations(BaseRepository[Client], IValidationOperations):
    """Implementación de operaciones de validación para clientes.

    Esta clase proporciona métodos especializados para validar datos
    de clientes antes de operaciones de creación y actualización.
    """

    def __init__(self, session_factory: Coroutine) -> None:
        """Inicializa las operaciones de validación.

        Args:
            session_factory: Factoría de sesiones de base de datos asíncrona
        """
        super().__init__(session_factory, Client)
        self._logger = logger.bind(component="ValidationOperations")

        # Patrones de validación
        self.email_pattern = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        self.phone_pattern = re.compile(r"^[\+]?[1-9]?[0-9]{7,15}$")

        self._logger.debug("ValidationOperations inicializado")

    async def validate_unique_fields(
        self, client_data: Dict[str, Any], exclude_id: Optional[int] = None
    ) -> None:
        """Valida que los campos únicos no estén duplicados.

        Args:
            client_data: Datos del cliente a validar
            exclude_id: ID del cliente a excluir de la validación (para updates)

        Raises:
            ClientDuplicateError: Si se encuentra un campo duplicado
        """
        self._logger.debug(f"Validando campos únicos (exclude_id: {exclude_id})")

        unique_fields = {
            "email": client_data.get("email"),
            "code": client_data.get("code"),
            "name": client_data.get("name"),
        }

        for field_name, field_value in unique_fields.items():
            if field_value is None:
                continue

            await self._check_field_uniqueness(field_name, field_value, exclude_id)

        self._logger.debug("Validación de campos únicos completada")

    async def _check_field_uniqueness(
        self, field_name: str, field_value: Any, exclude_id: Optional[int]
    ) -> None:
        """Verifica la unicidad de un campo específico.

        Args:
            field_name: Nombre del campo a verificar
            field_value: Valor del campo
            exclude_id: ID a excluir de la verificación

        Raises:
            ClientDuplicateError: Si el campo ya existe
        """
        criteria = {field_name: field_value}
        if await self.exists(criteria, exclude_id):
            self._logger.warning(
                f"Campo duplicado encontrado: {field_name} = '{field_value}'"
            )
            raise ClientDuplicateError(
                message=f"Ya existe un cliente con {field_name}: {field_value}",
                field=field_name,
                value=field_value,
            )

    def validate_email_format(self, email: str) -> None:
        """Valida el formato del email.

        Args:
            email: Email a validar

        Raises:
            ClientValidationError: Si el formato es inválido
        """
        if not email:
            return

        if not self.email_pattern.match(email):
            self._logger.warning(f"Formato de email inválido: {email}")
            raise ClientValidationError(
                message=f"Formato de email inválido: {email}",
                field="email",
                value=email,
            )

    def validate_phone_format(self, phone: str) -> None:
        """Valida el formato del teléfono.

        Args:
            phone: Teléfono a validar

        Raises:
            ClientValidationError: Si el formato es inválido
        """
        if not phone:
            return

        clean_phone = re.sub(r"[\s\-\(\)]", "", phone)

        if not self.phone_pattern.match(clean_phone):
            self._logger.warning(f"Formato de teléfono inválido: {phone}")
            raise ClientValidationError(
                message=f"Formato de teléfono inválido: {phone}",
                field="phone",
                value=phone,
            )

    def validate_required_fields(self, client_data: Dict[str, Any]) -> None:
        """Valida que los campos requeridos estén presentes.

        Args:
            client_data: Datos del cliente a validar

        Raises:
            ClientValidationError: Si falta un campo requerido
        """
        required_fields = ["name", "code", "email"]
        missing_fields = [
            field for field in required_fields if not client_data.get(field)
        ]

        if missing_fields:
            self._logger.warning(f"Campos requeridos faltantes: {missing_fields}")
            raise ClientValidationError(
                message=f"Los siguientes campos son requeridos: {', '.join(missing_fields)}",
                field=", ".join(missing_fields),
            )

    async def validate_all(self, client_data: Dict[str, Any], exclude_id: Optional[int] = None) -> None:
        """Ejecuta todas las validaciones para un cliente.

        Args:
            client_data: Datos del cliente a validar
            exclude_id: ID del cliente a excluir (para actualizaciones)
        """
        self._logger.debug("Ejecutando todas las validaciones para el cliente")
        
        self.validate_required_fields(client_data)
        self.validate_email_format(client_data.get("email", ""))
        self.validate_phone_format(client_data.get("phone", ""))
        await self.validate_unique_fields(client_data, exclude_id)
        
        self._logger.info("Todas las validaciones se completaron exitosamente")