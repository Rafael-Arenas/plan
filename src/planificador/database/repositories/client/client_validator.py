# src/planificador/database/repositories/client/client_validator.py

import re
from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ....exceptions import ValidationError
from ....exceptions.repository import (
    convert_sqlalchemy_error,
    create_client_validation_repository_error,
)
from ....models.client import Client
from ....utils.date_utils import get_current_time, is_business_day
from .interfaces.i_client_validator import IClientValidator


class ClientValidator(IClientValidator):
    """
    Validador de datos de clientes.

    Encapsula toda la lógica de validación para datos de clientes,
    incluyendo validaciones de formato, contenido y reglas de negocio.
    """

    def __init__(self, session: AsyncSession | None = None):
        self.session = session
        self._logger = logger.bind(component="ClientValidator")

    # Configuraciones de validación
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 200
    MIN_CODE_LENGTH = 2
    MAX_CODE_LENGTH = 50
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_CONTACT_INFO_LENGTH = 500

    # Patrones de validación
    NAME_PATTERN = re.compile(r"^[a-zA-Z0-9\s\-_.,&()]+$")
    CODE_PATTERN = re.compile(r"^[A-Z0-9\-_]+$")
    EMAIL_PATTERN = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    PHONE_PATTERN = re.compile(r"^[+]?[0-9\s\-()]{7,20}$")

    # ============================================================================
    # VALIDACIONES PRINCIPALES (3 funciones)
    # ============================================================================

    def validate_client_data(
        self, client_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Valida los datos de un cliente antes de crear o actualizar.

        Args:
            client_data: Diccionario con los datos del cliente

        Returns:
            Diccionario con los datos validados y normalizados

        Raises:
            ValidationError: Si alguna validación falla
        """
        try:
            validated_data = client_data.copy()

            # Validar campos requeridos
            self._validate_required_fields(validated_data)

            # Validar y normalizar nombre
            if "name" in validated_data:
                validated_data["name"] = self._validate_name(
                    validated_data["name"]
                )

            # Validar y normalizar código
            if "code" in validated_data:
                validated_data["code"] = self._validate_code(
                    validated_data["code"]
                )

            # Validar descripción
            if validated_data.get("description"):
                validated_data["description"] = self._validate_description(
                    validated_data["description"]
                )

            # Validar información de contacto
            if validated_data.get("contact_info"):
                validated_data["contact_info"] = self._validate_contact_info(
                    validated_data["contact_info"]
                )

            # Validar email si se proporciona
            if validated_data.get("email"):
                validated_data["email"] = self._validate_email(
                    validated_data["email"]
                )

            # Validar teléfono si se proporciona
            if validated_data.get("phone"):
                validated_data["phone"] = self._validate_phone(
                    validated_data["phone"]
                )

            # Validar estado activo
            if "is_active" in validated_data:
                validated_data["is_active"] = self._validate_is_active(
                    validated_data["is_active"]
                )

            # Aplicar reglas de negocio
            self._apply_business_rules(validated_data)

            self._logger.debug(

                    f"Datos de cliente validados exitosamente: "
                    f"{validated_data.get('name', 'N/A')}"

            )
            return validated_data

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(
                f"Error inesperado validando datos de cliente: {e}"
            )
            raise ValidationError(f"Error de validación: {e!s}")

    def validate_bulk_data(
        self, clients_data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Valida una lista de datos de clientes para operaciones en lote.

        Args:
            clients_data: Lista de diccionarios con datos de clientes

        Returns:
            Lista de datos validados

        Raises:
            ValidationError: Si alguna validación falla
        """
        if not isinstance(clients_data, list):
            raise ValidationError("Los datos deben ser una lista")

        if not clients_data:
            raise ValidationError("La lista de clientes no puede estar vacía")

        if len(clients_data) > 100:  # Límite para operaciones en lote
            raise ValidationError(
                "No se pueden procesar más de 100 clientes a la vez"
            )

        validated_clients = []
        errors = []

        for i, client_data in enumerate(clients_data):
            try:
                validated_client = self.validate_client_data(client_data)
                validated_clients.append(validated_client)
            except ValidationError as e:
                errors.append(f"Cliente {i + 1}: {e!s}")

        if errors:
            raise ValidationError(
                f"Errores de validación en lote: {'; '.join(errors)}"
            )

        # Validar nombres únicos dentro del lote
        names = [
            client.get("name", "").lower() for client in validated_clients
        ]
        if len(names) != len(set(names)):
            raise ValidationError(
                "Hay nombres duplicados en el lote de clientes"
            )

        # Validar códigos únicos dentro del lote
        codes = [
            client.get("code", "").upper()
            for client in validated_clients
            if client.get("code")
        ]
        if len(codes) != len(set(codes)):
            raise ValidationError(
                "Hay códigos duplicados en el lote de clientes"
            )

        self._logger.debug(
            f"Validados {len(validated_clients)} clientes en lote"
        )
        return validated_clients

    def validate_update_data(
        self, update_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Valida datos para actualización de cliente.

        Args:
            update_data: Datos a actualizar

        Returns:
            Datos validados para actualización

        Raises:
            ValidationError: Si alguna validación falla
        """
        if not isinstance(update_data, dict):
            raise ValidationError(
                "Los datos de actualización deben ser un diccionario"
            )

        if not update_data:
            raise ValidationError("No se proporcionaron datos para actualizar")

        # Para actualizaciones, los campos no son requeridos
        # Solo validamos los campos que se proporcionan
        validated_data = {}

        for field, value in update_data.items():
            if field == "name" and value is not None:
                validated_data["name"] = self._validate_name(value)
            elif field == "code" and value is not None:
                validated_data["code"] = self._validate_code(value)
            elif field == "description" and value is not None:
                validated_data["description"] = self._validate_description(
                    value
                )
            elif field == "contact_info" and value is not None:
                validated_data["contact_info"] = self._validate_contact_info(
                    value
                )
            elif field == "email" and value is not None:
                validated_data["email"] = self._validate_email(value)
            elif field == "phone" and value is not None:
                validated_data["phone"] = self._validate_phone(value)
            elif field == "is_active" and value is not None:
                validated_data["is_active"] = self._validate_is_active(value)
            else:
                # Permitir otros campos sin validación específica
                validated_data[field] = value

        self._logger.debug(
            f"Datos de actualización validados: {list(validated_data.keys())}"
        )
        return validated_data

    # ============================================================================
    # VALIDACIONES DE REGLAS DE NEGOCIO (1 función)
    # ============================================================================

    def validate_creation_business_day(
        self, validate_business_day: bool = False
    ) -> None:
        """
        Valida que la creación sea en día laborable si se requiere.

        Args:
            validate_business_day: Si validar que sea día laborable

        Raises:
            ValidationError: Si no es día laborable y se requiere validación
        """
        if validate_business_day:
            current_time = get_current_time()
            if not is_business_day(current_time.date()):
                raise ValidationError(
                    f"Los clientes solo pueden crearse en días laborables. "
                    f"Hoy es {current_time.format('dddd')}"
                )

    # ============================================================================
    # VALIDACIONES ASÍNCRONAS DE EXISTENCIA (3 funciones)
    # ============================================================================

    async def validate_name_exists(
        self, name: str, exclude_id: int | None = None
    ) -> bool:
        """
        Valida si existe un cliente con el nombre dado.

        Args:
            name: Nombre a verificar
            exclude_id: ID de cliente a excluir de la búsqueda

        Returns:
            True si el nombre existe, False en caso contrario
        """
        if not self.session:
            raise ValidationError(
                "Sesión de base de datos requerida para validación"
            )

        try:
            query = select(Client).where(Client.name == name)
            if exclude_id:
                query = query.where(Client.id != exclude_id)

            result = await self.session.execute(query)
            return result.scalar_one_or_none() is not None

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de BD validando existencia de nombre de cliente: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_name_exists",
                entity_type="Client",
                entity_id=exclude_id,
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado validando existencia de nombre de cliente: {e}"
            )
            raise create_client_validation_repository_error(
                message=f"Error inesperado validando nombre: {e}",
                details={
                    "name": name,
                    "exclude_id": exclude_id,
                    "original_error": str(e),
                },
            )

    async def validate_code_exists(
        self, code: str, exclude_id: int | None = None
    ) -> bool:
        """
        Valida si existe un cliente con el código dado.

        Args:
            code: Código a verificar
            exclude_id: ID de cliente a excluir de la búsqueda

        Returns:
            True si el código existe, False en caso contrario
        """
        if not self.session:
            raise ValidationError(
                "Sesión de base de datos requerida para validación"
            )

        try:
            query = select(Client).where(Client.code == code)
            if exclude_id:
                query = query.where(Client.id != exclude_id)

            result = await self.session.execute(query)
            return result.scalar_one_or_none() is not None

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de BD validando existencia de código de cliente: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_code_exists",
                entity_type="Client",
                entity_id=exclude_id,
            ) from e
        except Exception as e:
            self._logger.error(
                f"Error inesperado validando existencia de código de cliente: {e}"
            )
            raise create_client_validation_repository_error(
                message=f"Error inesperado validando código: {e}",
                details={
                    "code": code,
                    "exclude_id": exclude_id,
                    "original_error": str(e),
                },
            ) from e

    async def validate_client_update_data(
        self, update_data: dict[str, Any], client_id: int
    ) -> dict[str, Any]:
        """
        Valida datos para actualización de cliente con validaciones de base de datos.

        Args:
            update_data: Datos a actualizar
            client_id: ID del cliente a actualizar

        Returns:
            Datos validados para actualización

        Raises:
            ValidationError: Si alguna validación falla
        """
        # Primero validar los datos básicos
        validated_data = self.validate_update_data(update_data)

        # Validar unicidad de nombre si se está actualizando
        if "name" in validated_data and self.session:
            name_exists = await self.validate_name_exists(
                validated_data["name"], client_id
            )
            if name_exists:
                raise ValidationError(
                    f"Ya existe un cliente con el nombre '{validated_data['name']}'"
                )

        # Validar unicidad de código si se está actualizando
        if "code" in validated_data and self.session:
            code_exists = await self.validate_code_exists(
                validated_data["code"], client_id
            )
            if code_exists:
                raise ValidationError(
                    f"Ya existe un cliente con el código '{validated_data['code']}'"
                )

        return validated_data

    # ============================================================================
    # VALIDACIONES INTERNAS - CAMPOS REQUERIDOS (1 función)
    # ============================================================================

    def _validate_required_fields(self, data: dict[str, Any]) -> None:
        """
        Valida que los campos requeridos estén presentes.

        Args:
            data: Datos del cliente

        Raises:
            ValidationError: Si falta algún campo requerido
        """
        required_fields = ["name"]

        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(f"El campo '{field}' es requerido")

    # ============================================================================
    # VALIDACIONES INTERNAS - FORMATO DE DATOS (8 funciones)
    # ============================================================================

    def _validate_name(self, name: str) -> str:
        """
        Valida y normaliza el nombre del cliente.

        Args:
            name: Nombre del cliente

        Returns:
            Nombre normalizado

        Raises:
            ValidationError: Si el nombre no es válido
        """
        if not isinstance(name, str):
            raise ValidationError("El nombre debe ser una cadena de texto")

        # Normalizar espacios
        name = " ".join(name.split())

        # Validar longitud
        if len(name) < self.MIN_NAME_LENGTH:
            raise ValidationError(
                f"El nombre debe tener al menos {self.MIN_NAME_LENGTH} caracteres"
            )

        if len(name) > self.MAX_NAME_LENGTH:
            raise ValidationError(
                f"El nombre no puede exceder {self.MAX_NAME_LENGTH} caracteres"
            )

        # Validar formato
        if not self.NAME_PATTERN.match(name):
            raise ValidationError(
                "El nombre contiene caracteres no válidos. "
                "Solo se permiten letras, números, espacios y los caracteres: -_.,&()"
            )

        # Capitalizar primera letra de cada palabra
        name = " ".join(word.capitalize() for word in name.split())

        return name

    def _validate_code(self, code: str) -> str:
        """
        Valida y normaliza el código del cliente.

        Args:
            code: Código del cliente

        Returns:
            Código normalizado

        Raises:
            ValidationError: Si el código no es válido
        """
        if not isinstance(code, str):
            raise ValidationError("El código debe ser una cadena de texto")

        # Normalizar a mayúsculas y quitar espacios
        code = code.upper().strip()

        # Validar longitud
        if len(code) < self.MIN_CODE_LENGTH:
            raise ValidationError(
                f"El código debe tener al menos {self.MIN_CODE_LENGTH} caracteres"
            )

        if len(code) > self.MAX_CODE_LENGTH:
            raise ValidationError(
                f"El código no puede exceder {self.MAX_CODE_LENGTH} caracteres"
            )

        # Validar formato
        if not self.CODE_PATTERN.match(code):
            raise ValidationError(
                "El código contiene caracteres no válidos. "
                "Solo se permiten letras mayúsculas, números, guiones y guiones bajos"
            )

        return code

    def _validate_description(self, description: str) -> str:
        """
        Valida y normaliza la descripción del cliente.

        Args:
            description: Descripción del cliente

        Returns:
            Descripción normalizada

        Raises:
            ValidationError: Si la descripción no es válida
        """
        if not isinstance(description, str):
            raise ValidationError(
                "La descripción debe ser una cadena de texto"
            )

        # Normalizar espacios
        description = " ".join(description.split())

        # Validar longitud
        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            raise ValidationError(
                f"La descripción no puede exceder {self.MAX_DESCRIPTION_LENGTH} caracteres"
            )

        return description

    def _validate_contact_info(self, contact_info: str) -> str:
        """
        Valida y normaliza la información de contacto.

        Args:
            contact_info: Información de contacto

        Returns:
            Información de contacto normalizada

        Raises:
            ValidationError: Si la información de contacto no es válida
        """
        if not isinstance(contact_info, str):
            raise ValidationError(
                "La información de contacto debe ser una cadena de texto"
            )

        # Normalizar espacios
        contact_info = " ".join(contact_info.split())

        # Validar longitud
        if len(contact_info) > self.MAX_CONTACT_INFO_LENGTH:
            raise ValidationError(
                f"La información de contacto no puede exceder {self.MAX_CONTACT_INFO_LENGTH} caracteres"
            )

        return contact_info

    def _validate_email(self, email: str) -> str:
        """
        Valida y normaliza el email del cliente.

        Args:
            email: Email del cliente

        Returns:
            Email normalizado

        Raises:
            ValidationError: Si el email no es válido
        """
        if not isinstance(email, str):
            raise ValidationError("El email debe ser una cadena de texto")

        # Normalizar a minúsculas y quitar espacios
        email = email.lower().strip()

        # Validar formato
        if not self.EMAIL_PATTERN.match(email):
            raise ValidationError("El formato del email no es válido")

        return email

    def _validate_phone(self, phone: str) -> str:
        """
        Valida y normaliza el teléfono del cliente.

        Args:
            phone: Teléfono del cliente

        Returns:
            Teléfono normalizado

        Raises:
            ValidationError: Si el teléfono no es válido
        """
        if not isinstance(phone, str):
            raise ValidationError("El teléfono debe ser una cadena de texto")

        # Quitar espacios
        phone = phone.strip()

        # Validar formato
        if not self.PHONE_PATTERN.match(phone):
            raise ValidationError(
                "El formato del teléfono no es válido. "
                "Debe contener entre 7 y 20 dígitos, puede incluir +, espacios, guiones y paréntesis"
            )

        return phone

    def _validate_is_active(self, is_active: Any) -> bool:
        """
        Valida y normaliza el estado activo del cliente.

        Args:
            is_active: Estado activo del cliente

        Returns:
            Estado activo normalizado

        Raises:
            ValidationError: Si el estado no es válido
        """
        if isinstance(is_active, bool):
            return is_active

        if isinstance(is_active, str):
            if is_active.lower() in ["true", "1", "yes", "sí", "si"]:
                return True
            elif is_active.lower() in ["false", "0", "no"]:
                return False

        if isinstance(is_active, int):
            return bool(is_active)

        raise ValidationError(
            "El estado activo debe ser un valor booleano (true/false)"
        )

    def _apply_business_rules(self, data: dict[str, Any]) -> None:
        """
        Aplica reglas de negocio específicas.

        Args:
            data: Datos del cliente

        Raises:
            ValidationError: Si alguna regla de negocio falla
        """
        # Regla: El código debe ser único (se valida en el repositorio)
        # Regla: El nombre debe ser único (se valida en el repositorio)

        # Regla: Si se proporciona email, debe ser válido
        if data.get("email") and (not isinstance(data["email"], str) or "@" not in data["email"]):
            raise ValidationError("El email proporcionado no es válido")

        # Regla: Los clientes inactivos no pueden tener proyectos activos
        # (Esta regla se implementaría en el servicio de negocio)
        pass

    def validate_email_format(self, email: str) -> bool:
        """Valida el formato de un email.

        Args:
            email: Email a validar.

        Returns:
            True si el formato es válido, False en caso contrario.
        """
        if not isinstance(email, str):
            return False
        
        # Normalizar a minúsculas y quitar espacios
        email = email.lower().strip()
        
        # Validar formato
        return bool(self.EMAIL_PATTERN.match(email))

    def validate_phone_format(self, phone: str | None) -> bool:
        """Valida el formato de un teléfono.

        Args:
            phone: Teléfono a validar (puede ser None).

        Returns:
            True si el formato es válido o es None, False en caso contrario.
        """
        if phone is None:
            return True
            
        if not isinstance(phone, str):
            return False
        
        # Quitar espacios
        phone = phone.strip()
        
        # Validar formato
        return bool(self.PHONE_PATTERN.match(phone))
