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
Versión: 1.0.0
"""

import re
from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.exceptions.repository.client_repository_exceptions import (
    ClientRepositoryError,
    ClientValidationError,
    ClientDuplicateError,
)
from planificador.models.client import Client
from ..interfaces.validation_interface import IValidationOperations


class ValidationOperations(IValidationOperations):
    """Implementación de operaciones de validación para clientes.
    
    Esta clase proporciona métodos especializados para validar datos
    de clientes antes de operaciones de creación y actualización.
    
    Attributes:
        session: Sesión asíncrona de SQLAlchemy
        _logger: Logger estructurado para la clase
    """

    def __init__(self, session: AsyncSession):
        """Inicializa las operaciones de validación.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        self.session = session
        self._logger = logger.bind(component="ValidationOperations")
        
        # Patrones de validación
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        self.phone_pattern = re.compile(
            r'^[\+]?[1-9]?[0-9]{7,15}$'
        )
        
        self._logger.debug("ValidationOperations inicializado")

    async def validate_unique_fields(
        self, 
        client_data: Dict[str, Any], 
        exclude_id: Optional[int] = None
    ) -> None:
        """Valida que los campos únicos no estén duplicados.
        
        Args:
            client_data: Datos del cliente a validar
            exclude_id: ID del cliente a excluir de la validación (para updates)
            
        Raises:
            ClientDuplicateError: Si se encuentra un campo duplicado
            ClientRepositoryError: Si ocurre un error en la validación
        """
        try:
            self._logger.debug(
                f"Validando campos únicos (exclude_id: {exclude_id})"
            )
            
            # Campos únicos a validar
            unique_fields = {
                'email': client_data.get('email'),
                'code': client_data.get('code'),
                'name': client_data.get('name')  # Asumiendo que el nombre debe ser único
            }
            
            for field_name, field_value in unique_fields.items():
                if field_value is None:
                    continue
                    
                await self._check_field_uniqueness(
                    field_name, field_value, exclude_id
                )
                
            self._logger.debug("Validación de campos únicos completada")
            
        except ClientDuplicateError:
            raise
        except Exception as e:
            self._logger.error(f"Error en validación de campos únicos: {e}")
            raise ClientRepositoryError(
                message=f"Error en validación de unicidad: {e}",
                operation="validate_unique_fields",
                entity_type="Client",
                original_error=e
            )

    async def _check_field_uniqueness(
        self, 
        field_name: str, 
        field_value: Any, 
        exclude_id: Optional[int]
    ) -> None:
        """Verifica la unicidad de un campo específico.
        
        Args:
            field_name: Nombre del campo a verificar
            field_value: Valor del campo
            exclude_id: ID a excluir de la verificación
            
        Raises:
            ClientDuplicateError: Si el campo ya existe
        """
        if not hasattr(Client, field_name):
            return
            
        field_attr = getattr(Client, field_name)
        
        # Construir consulta de verificación
        stmt = select(func.count(Client.id)).where(field_attr == field_value)
        
        if exclude_id is not None:
            stmt = stmt.where(Client.id != exclude_id)
        
        result = await self.session.execute(stmt)
        count = result.scalar()
        
        if count > 0:
            self._logger.warning(
                f"Campo duplicado encontrado: {field_name} = '{field_value}'"
            )
            raise ClientDuplicateError(
                message=f"Ya existe un cliente con {field_name}: {field_value}",
                field=field_name,
                value=field_value
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
                value=email
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
            
        # Limpiar espacios y caracteres especiales para validación
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        if not self.phone_pattern.match(clean_phone):
            self._logger.warning(f"Formato de teléfono inválido: {phone}")
            raise ClientValidationError(
                message=f"Formato de teléfono inválido: {phone}",
                field="phone",
                value=phone
            )

    def validate_required_fields(self, client_data: Dict[str, Any]) -> None:
        """Valida que los campos requeridos estén presentes.
        
        Args:
            client_data: Datos del cliente a validar
            
        Raises:
            ClientValidationError: Si falta un campo requerido
        """
        required_fields = ['name', 'email']  # Campos mínimos requeridos
        
        for field in required_fields:
            value = client_data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                self._logger.warning(f"Campo requerido faltante: {field}")
                raise ClientValidationError(
                    message=f"El campo '{field}' es requerido",
                    field=field,
                    value=value
                )

    def validate_field_lengths(self, client_data: Dict[str, Any]) -> None:
        """Valida las longitudes de los campos de texto.
        
        Args:
            client_data: Datos del cliente a validar
            
        Raises:
            ClientValidationError: Si un campo excede la longitud máxima
        """
        # Definir longitudes máximas (basadas en el modelo)
        max_lengths = {
            'name': 200,
            'email': 100,
            'phone': 20,
            'address': 500,
            'code': 50,
            'description': 1000
        }
        
        for field, max_length in max_lengths.items():
            value = client_data.get(field)
            if value and isinstance(value, str) and len(value) > max_length:
                self._logger.warning(
                    f"Campo '{field}' excede longitud máxima: {len(value)} > {max_length}"
                )
                raise ClientValidationError(
                    message=f"El campo '{field}' no puede exceder {max_length} caracteres",
                    field=field,
                    value=value
                )

    async def validate_client_data(
        self, 
        client_data: Dict[str, Any], 
        exclude_id: Optional[int] = None,
        validate_uniqueness: bool = True
    ) -> None:
        """Valida completamente los datos de un cliente.
        
        Args:
            client_data: Datos del cliente a validar
            exclude_id: ID del cliente a excluir (para updates)
            validate_uniqueness: Si validar unicidad de campos
            
        Raises:
            ClientValidationError: Si los datos son inválidos
            ClientDuplicateError: Si hay campos duplicados
            ClientRepositoryError: Si ocurre un error en la validación
        """
        try:
            self._logger.debug("Iniciando validación completa de datos del cliente")
            
            # Validaciones básicas
            self.validate_required_fields(client_data)
            self.validate_field_lengths(client_data)
            
            # Validaciones de formato
            if 'email' in client_data:
                self.validate_email_format(client_data['email'])
                
            if 'phone' in client_data:
                self.validate_phone_format(client_data['phone'])
            
            # Validación de unicidad (si se solicita)
            if validate_uniqueness:
                await self.validate_unique_fields(client_data, exclude_id)
            
            self._logger.info("Validación completa de datos del cliente exitosa")
            
        except (ClientValidationError, ClientDuplicateError):
            raise
        except Exception as e:
            self._logger.error(f"Error en validación completa: {e}")
            raise ClientRepositoryError(
                message=f"Error en validación de datos: {e}",
                operation="validate_client_data",
                entity_type="Client",
                original_error=e
            )

    def validate_code_format(self, code: str) -> None:
        """Valida el formato del código del cliente.
        
        Args:
            code: Código a validar
            
        Raises:
            ClientValidationError: Si el formato es inválido
        """
        if not code:
            return
            
        # Validar que el código solo contenga caracteres alfanuméricos y guiones
        code_pattern = re.compile(r'^[A-Za-z0-9\-_]+$')
        
        if not code_pattern.match(code):
            self._logger.warning(f"Formato de código inválido: {code}")
            raise ClientValidationError(
                message=f"El código solo puede contener letras, números, guiones y guiones bajos: {code}",
                field="code",
                value=code
            )

    async def validate_business_rules(
        self, 
        client_data: Dict[str, Any], 
        exclude_id: Optional[int] = None
    ) -> None:
        """Valida reglas de negocio específicas.
        
        Args:
            client_data: Datos del cliente a validar
            exclude_id: ID del cliente a excluir
            
        Raises:
            ClientValidationError: Si se viola una regla de negocio
        """
        try:
            self._logger.debug("Validando reglas de negocio")
            
            # Validar formato de código si está presente
            if 'code' in client_data:
                self.validate_code_format(client_data['code'])
            
            # Aquí se pueden agregar más reglas de negocio específicas
            # Por ejemplo:
            # - Validar que el cliente tenga al menos un contacto
            # - Validar rangos de fechas
            # - Validar dependencias con otras entidades
            
            self._logger.debug("Validación de reglas de negocio completada")
            
        except ClientValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error en validación de reglas de negocio: {e}")
            raise ClientRepositoryError(
                message=f"Error en validación de reglas de negocio: {e}",
                operation="validate_business_rules",
                entity_type="Client",
                original_error=e
            )

    async def validate_client_name_unique(
        self, name: str, exclude_id: Optional[int] = None
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
        try:
            self._logger.debug(f"Validando unicidad del nombre: {name}")
            
            query = select(func.count(Client.id)).where(Client.name == name)
            
            if exclude_id is not None:
                query = query.where(Client.id != exclude_id)
            
            result = await self.session.execute(query)
            count = result.scalar()
            
            is_unique = count == 0
            self._logger.debug(f"Nombre único: {is_unique}")
            
            return is_unique
            
        except Exception as e:
            self._logger.error(f"Error validando unicidad del nombre: {e}")
            raise ClientRepositoryError(
                message=f"Error validando unicidad del nombre: {e}",
                operation="validate_client_name_unique",
                entity_type="Client",
                original_error=e
            )

    async def validate_client_code_unique(
        self, code: str, exclude_id: Optional[int] = None
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
        try:
            self._logger.debug(f"Validando unicidad del código: {code}")
            
            query = select(func.count(Client.id)).where(Client.code == code)
            
            if exclude_id is not None:
                query = query.where(Client.id != exclude_id)
            
            result = await self.session.execute(query)
            count = result.scalar()
            
            is_unique = count == 0
            self._logger.debug(f"Código único: {is_unique}")
            
            return is_unique
            
        except Exception as e:
            self._logger.error(f"Error validando unicidad del código: {e}")
            raise ClientRepositoryError(
                message=f"Error validando unicidad del código: {e}",
                operation="validate_client_code_unique",
                entity_type="Client",
                original_error=e
            )

    async def validate_client_deletion(self, client_id: int) -> bool:
        """Valida si un cliente puede ser eliminado.
        
        Args:
            client_id: ID del cliente a validar
            
        Returns:
            True si el cliente puede ser eliminado, False en caso contrario
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la validación
        """
        try:
            self._logger.debug(f"Validando eliminación del cliente: {client_id}")
            
            # Verificar que el cliente existe
            query = select(func.count(Client.id)).where(Client.id == client_id)
            result = await self.session.execute(query)
            count = result.scalar()
            
            if count == 0:
                self._logger.warning(f"Cliente no encontrado: {client_id}")
                return False
            
            # Aquí se pueden agregar validaciones adicionales:
            # - Verificar si tiene proyectos asociados
            # - Verificar si tiene transacciones pendientes
            # - Verificar reglas de negocio específicas
            
            # Por ahora, permitir eliminación si el cliente existe
            can_delete = True
            self._logger.debug(f"Cliente puede ser eliminado: {can_delete}")
            
            return can_delete
            
        except Exception as e:
            self._logger.error(f"Error validando eliminación del cliente: {e}")
            raise ClientRepositoryError(
                message=f"Error validando eliminación del cliente: {e}",
                operation="validate_client_deletion",
                entity_type="Client",
                entity_id=client_id,
                original_error=e
            )