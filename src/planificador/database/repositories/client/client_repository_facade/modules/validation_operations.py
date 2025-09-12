"""Módulo de operaciones de validación para clientes.

Este módulo implementa la interfaz IValidationOperations y proporciona
funcionalidades especializadas para validación de datos de clientes.

Clases:
    ValidationOperations: Implementación de operaciones de validación

Ejemplo:
    ```python
    validation_ops = ValidationOperations(session, validator, exception_handler)
    is_unique = await validation_ops.validate_client_name_unique("Empresa ABC")
    ```
"""

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from ..interfaces.validation_interface import IValidationOperations
from ..client_validator import ClientValidator
from ..client_exception_handler import ClientExceptionHandler


class ValidationOperations(IValidationOperations):
    """Implementación de operaciones de validación para clientes.
    
    Esta clase proporciona métodos especializados para validar datos
    de clientes, incluyendo unicidad de nombres y códigos, y validación
    de eliminación.
    
    Attributes:
        session: Sesión de base de datos SQLAlchemy
        validator: Validador de datos de clientes
        exception_handler: Manejador de excepciones del repositorio
    """
    
    def __init__(
        self,
        session: AsyncSession,
        validator: ClientValidator,
        exception_handler: ClientExceptionHandler,
    ) -> None:
        """Inicializa las operaciones de validación.
        
        Args:
            session: Sesión de base de datos activa
            validator: Validador de datos de clientes
            exception_handler: Manejador de excepciones
        """
        self.session = session
        self.validator = validator
        self.exception_handler = exception_handler
        self._logger = logger.bind(module="ValidationOperations")
    
    async def validate_client_name_unique(
        self, name: str, exclude_id: int | None = None
    ) -> bool:
        """Valida que el nombre del cliente sea único.
        
        Args:
            name: Nombre a validar
            exclude_id: ID a excluir de la validación (para actualizaciones)
            
        Returns:
            True si el nombre es único, False en caso contrario
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la validación
        """
        self._logger.info(
            f"Validando unicidad de nombre: {name} (excluir ID: {exclude_id})"
        )
        
        try:
            return await self.validator.validate_name_unique(name, exclude_id)
        except Exception as e:
            self._logger.error(f"Error validando unicidad de nombre: {e}")
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="validate_client_name_unique",
                additional_context={"name": name, "exclude_id": exclude_id},
            )
            return False
    
    async def validate_client_code_unique(
        self, code: str, exclude_id: int | None = None
    ) -> bool:
        """Valida que el código del cliente sea único.
        
        Args:
            code: Código a validar
            exclude_id: ID a excluir de la validación (para actualizaciones)
            
        Returns:
            True si el código es único, False en caso contrario
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la validación
        """
        self._logger.info(
            f"Validando unicidad de código: {code} (excluir ID: {exclude_id})"
        )
        
        try:
            return await self.validator.validate_code_unique(code, exclude_id)
        except Exception as e:
            self._logger.error(f"Error validando unicidad de código: {e}")
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="validate_client_code_unique",
                additional_context={"code": code, "exclude_id": exclude_id},
            )
            return False
    
    async def validate_client_deletion(self, client_id: int) -> bool:
        """Valida si un cliente puede ser eliminado.
        
        Args:
            client_id: ID del cliente a validar
            
        Returns:
            True si puede ser eliminado, False en caso contrario
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la validación
        """
        self._logger.info(f"Validando eliminación de cliente ID: {client_id}")
        
        try:
            return await self.validator.validate_client_deletion(client_id)
        except Exception as e:
            self._logger.error(f"Error validando eliminación: {e}")
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="validate_client_deletion",
                additional_context={"client_id": client_id},
            )
    
    async def validate_email_format(self, email: str) -> bool:
        """Valida el formato de un email.
        
        Args:
            email: Email a validar
            
        Returns:
            True si el formato es válido, False en caso contrario
        """
        self._logger.debug(f"Validando formato de email: {email}")
        
        try:
            return self.validator.validate_email_format(email)
        except Exception as e:
            self._logger.error(f"Error validando formato de email: {e}")
            return False
    
    async def validate_phone_format(self, phone: str) -> bool:
        """Valida el formato de un teléfono.
        
        Args:
            phone: Teléfono a validar
            
        Returns:
            True si el formato es válido, False en caso contrario
        """
        self._logger.debug(f"Validando formato de teléfono: {phone}")
        
        try:
            return self.validator.validate_phone_format(phone)
        except Exception as e:
            self._logger.error(f"Error validando formato de teléfono: {e}")
            return False
    
    async def validate_client_data_integrity(self, client_data: dict) -> bool:
        """Valida la integridad de los datos de un cliente.
        
        Args:
            client_data: Datos del cliente a validar
            
        Returns:
            True si los datos son válidos, False en caso contrario
        """
        self._logger.info("Validando integridad de datos de cliente")
        
        try:
            # Validar datos usando el validador
            validated_data = self.validator.validate_client_data(client_data)
            return validated_data is not None
        except Exception as e:
            self._logger.error(f"Error validando integridad de datos: {e}")
            return False