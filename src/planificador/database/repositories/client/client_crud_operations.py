"""Módulo especializado para operaciones CRUD de clientes.

Este módulo contiene todas las operaciones básicas de creación, lectura,
actualizacion y eliminación de clientes, extraídas del ClientRepository
original para mejorar la modularidad y mantenibilidad.

Autor: Sistema de Modularización
Fecha: 21 de agosto de 2025
"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import pendulum

from planificador.models.client import Client
from planificador.exceptions.client_exceptions import (
    ClientNotFoundError,
    ClientValidationError,
    create_client_validation_error
)
from planificador.exceptions.repository_exceptions import (
    RepositoryError,
    convert_sqlalchemy_error
)
from planificador.database.repositories.client.client_validator import ClientValidator


class ClientCRUDOperations:
    """Clase especializada para operaciones CRUD de clientes.
    
    Esta clase encapsula todas las operaciones básicas de creación, lectura,
    actualización y eliminación de clientes, proporcionando una interfaz
    limpia y bien definida para estas operaciones fundamentales.
    
    Attributes:
        session: Sesión asíncrona de SQLAlchemy
        validator: Instancia del validador de clientes
        _logger: Logger estructurado para la clase
    """
    
    def __init__(self, session: AsyncSession, validator: ClientValidator):
        """Inicializa las operaciones CRUD de clientes.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
            validator: Instancia del validador de clientes
        """
        self.session = session
        self.validator = validator
        self._logger = logger.bind(component="ClientCRUDOperations")
        
    async def create_client(self, client_data: Dict[str, Any]) -> Client:
        """Crea un nuevo cliente en la base de datos.
        
        Args:
            client_data: Diccionario con los datos del cliente
            
        Returns:
            Cliente creado con ID asignado
            
        Raises:
            ClientValidationError: Si los datos no son válidos
            RepositoryError: Si hay errores en la base de datos
        """
        try:
            # Validar datos del cliente
            await self.validator.validate_client_data(client_data)
            
            # Crear instancia del cliente
            client = Client(**client_data)
            
            # Persistir en base de datos
            self.session.add(client)
            await self.session.commit()
            await self.session.refresh(client)
            
            self._logger.info(f"Cliente creado exitosamente con ID: {client.id}")
            return client
            
        except ClientValidationError:
            # Re-lanzar errores de validación directamente
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            await self.session.rollback()
            self._logger.error(f"Error de base de datos creando cliente: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_client",
                entity_type="Client"
            )
        except Exception as e:
            # Manejar errores inesperados
            await self.session.rollback()
            self._logger.error(f"Error inesperado creando cliente: {e}")
            raise RepositoryError(
                message=f"Error inesperado creando cliente: {e}",
                operation="create_client",
                entity_type="Client",
                original_error=e
            )
    
    async def update_client(self, client_id: int, update_data: Dict[str, Any]) -> Client:
        """Actualiza un cliente existente.
        
        Args:
            client_id: ID del cliente a actualizar
            update_data: Diccionario con los datos a actualizar
            
        Returns:
            Cliente actualizado
            
        Raises:
            ClientNotFoundError: Si el cliente no existe
            ClientValidationError: Si los datos no son válidos
            RepositoryError: Si hay errores en la base de datos
        """
        try:
            # Buscar cliente existente
            client = await self.session.get(Client, client_id)
            if not client:
                raise ClientNotFoundError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    client_id=client_id
                )
            
            # Validar datos de actualización
            await self.validator.validate_update_data(update_data, client_id)
            
            # Aplicar actualizaciones
            for field, value in update_data.items():
                if hasattr(client, field):
                    setattr(client, field, value)
            
            # Actualizar timestamp de modificación
            client.updated_at = pendulum.now()
            
            # Persistir cambios
            await self.session.commit()
            await self.session.refresh(client)
            
            self._logger.info(f"Cliente {client_id} actualizado exitosamente")
            return client
            
        except (ClientNotFoundError, ClientValidationError):
            # Re-lanzar errores específicos directamente
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            await self.session.rollback()
            self._logger.error(f"Error de base de datos actualizando cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="update_client",
                entity_type="Client",
                entity_id=str(client_id)
            )
        except Exception as e:
            # Manejar errores inesperados
            await self.session.rollback()
            self._logger.error(f"Error inesperado actualizando cliente {client_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado actualizando cliente {client_id}: {e}",
                operation="update_client",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )
    
    async def delete_client(self, client_id: int) -> bool:
        """Elimina un cliente de la base de datos.
        
        Args:
            client_id: ID del cliente a eliminar
            
        Returns:
            True si el cliente fue eliminado exitosamente
            
        Raises:
            ClientNotFoundError: Si el cliente no existe
            RepositoryError: Si hay errores en la base de datos
        """
        try:
            # Buscar cliente existente
            client = await self.session.get(Client, client_id)
            if not client:
                raise ClientNotFoundError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    client_id=client_id
                )
            
            # Validar que se puede eliminar (sin proyectos activos)
            await self.validator.validate_client_deletion(client_id)
            
            # Eliminar cliente
            await self.session.delete(client)
            await self.session.commit()
            
            self._logger.info(f"Cliente {client_id} eliminado exitosamente")
            return True
            
        except (ClientNotFoundError, ClientValidationError):
            # Re-lanzar errores específicos directamente
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            await self.session.rollback()
            self._logger.error(f"Error de base de datos eliminando cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="delete_client",
                entity_type="Client",
                entity_id=str(client_id)
            )
        except Exception as e:
            # Manejar errores inesperados
            await self.session.rollback()
            self._logger.error(f"Error inesperado eliminando cliente {client_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado eliminando cliente {client_id}: {e}",
                operation="delete_client",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )
    
    async def create_client_with_pendulum_validation(
        self, 
        client_data: Dict[str, Any]
    ) -> Client:
        """Crea un cliente con validación avanzada de fechas usando Pendulum.
        
        Este método proporciona validación adicional para campos de fecha
        utilizando la librería Pendulum para manejo robusto de fechas y
        zonas horarias.
        
        Args:
            client_data: Diccionario con los datos del cliente
            
        Returns:
            Cliente creado con validación de fechas
            
        Raises:
            ClientValidationError: Si las fechas no son válidas
            RepositoryError: Si hay errores en la base de datos
        """
        try:
            # Validar y normalizar fechas con Pendulum
            validated_data = await self._validate_dates_with_pendulum(client_data)
            
            # Validar datos del cliente
            await self.validator.validate_client_data(validated_data)
            
            # Crear instancia del cliente
            client = Client(**validated_data)
            
            # Persistir en base de datos
            self.session.add(client)
            await self.session.commit()
            await self.session.refresh(client)
            
            self._logger.info(
                f"Cliente creado con validación Pendulum, ID: {client.id}"
            )
            return client
            
        except ClientValidationError:
            # Re-lanzar errores de validación directamente
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            await self.session.rollback()
            self._logger.error(
                f"Error de base de datos creando cliente con validación Pendulum: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_client_with_pendulum_validation",
                entity_type="Client"
            )
        except Exception as e:
            # Manejar errores inesperados
            await self.session.rollback()
            self._logger.error(
                f"Error inesperado creando cliente con validación Pendulum: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado creando cliente con validación Pendulum: {e}",
                operation="create_client_with_pendulum_validation",
                entity_type="Client",
                original_error=e
            )
    
    async def _validate_dates_with_pendulum(
        self, 
        client_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida y normaliza fechas usando Pendulum.
        
        Args:
            client_data: Datos del cliente con fechas a validar
            
        Returns:
            Datos del cliente con fechas normalizadas
            
        Raises:
            ClientValidationError: Si las fechas no son válidas
        """
        validated_data = client_data.copy()
        date_fields = ['created_at', 'updated_at', 'birth_date', 'contract_start_date']
        
        try:
            for field in date_fields:
                if field in validated_data and validated_data[field] is not None:
                    # Convertir a Pendulum para validación
                    date_value = validated_data[field]
                    if isinstance(date_value, str):
                        # Parsear string a fecha Pendulum
                        parsed_date = pendulum.parse(date_value)
                        validated_data[field] = parsed_date.to_datetime_string()
                    elif hasattr(date_value, 'isoformat'):
                        # Convertir datetime a string ISO
                        validated_data[field] = date_value.isoformat()
            
            return validated_data
            
        except Exception as e:
            self._logger.error(f"Error validando fechas con Pendulum: {e}")
            raise create_client_validation_error(
                field="date_validation",
                value=str(client_data),
                reason=f"Error en validación de fechas: {str(e)}",
                operation="validate_dates_with_pendulum"
            )
    
    async def get_client_by_id(self, client_id: int) -> Optional[Client]:
        """Obtiene un cliente por su ID.
        
        Args:
            client_id: ID del cliente a buscar
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        try:
            client = await self.session.get(Client, client_id)
            
            if client:
                self._logger.debug(f"Cliente {client_id} encontrado")
            else:
                self._logger.debug(f"Cliente {client_id} no encontrado")
            
            return client
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_by_id",
                entity_type="Client",
                entity_id=str(client_id)
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo cliente {client_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo cliente {client_id}: {e}",
                operation="get_client_by_id",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )