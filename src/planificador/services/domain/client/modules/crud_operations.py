# src/planificador/services/domain/client/modules/crud_operations.py

"""
Módulo de operaciones CRUD para el servicio de dominio de cliente.

Este módulo implementa las operaciones básicas de Crear, Leer, Actualizar y Eliminar
para la entidad Cliente, aplicando reglas de negocio específicas del dominio.
"""

from typing import List, Optional, Any, Dict
from uuid import UUID

from loguru import logger

from planificador.exceptions import (
    RepositoryError,
    ValidationError,
    NotFoundError,
    BusinessLogicError,
)
from planificador.repositories.client.client_repository_facade import ClientRepositoryFacade
from planificador.schemas import ClientCreate, ClientUpdate, Client
from planificador.services.domain.client.interfaces.crud_interface import ICrudOperations


class CrudOperations(ICrudOperations):
    """
    Implementación de operaciones CRUD para el dominio de cliente.
    
    Esta clase encapsula la lógica de negocio específica para las operaciones
    básicas de cliente, delegando las operaciones de persistencia al repositorio
    y aplicando validaciones de dominio.
    """

    def __init__(self, client_repository: 'ClientRepositoryFacade'):
        """
        Inicializa el módulo de operaciones CRUD.
        
        Args:
            client_repository: Instancia del repositorio de cliente
        """
        self._client_repository = client_repository
        self._logger = logger

    async def create_client(
        self,
        client_data: ClientCreate,
        validate_business_rules: bool = True
    ) -> Client:
        """
        Crea un nuevo cliente aplicando validaciones de dominio.
        
        Args:
            client_data: Datos del cliente a crear
            validate_business_rules: Si aplicar validaciones de negocio
            
        Returns:
            Client: Cliente creado
            
        Raises:
            ValidationError: Si los datos no cumplen las reglas de negocio
            BusinessLogicError: Si viola reglas específicas del dominio
        """
        try:
            self._logger.info(f"Iniciando creación de cliente: {client_data.name}")
            
            # Validaciones de dominio
            if validate_business_rules:
                await self._validate_client_creation(client_data)
            
            # Crear cliente a través del repositorio
            created_client = await self._client_repository.create_client(client_data)
            
            self._logger.info(f"Cliente creado exitosamente: ID {created_client.id}")
            return Client.model_validate(created_client)
            
        except Exception as e:
            self._logger.error(f"Error al crear cliente {client_data.name}: {e}")
            if isinstance(e, (ValidationError, BusinessLogicError)):
                raise
            raise RepositoryError(
                message=f"Error inesperado al crear cliente: {e}",
                operation="create_client",
                entity_type="Client",
                original_error=e
            )

    async def get_client_by_id(self, client_id: int) -> Optional[Client]:
        """
        Obtiene un cliente por su ID.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Optional[Client]: Cliente encontrado o None
        """
        try:
            self._logger.debug(f"Buscando cliente por ID: {client_id}")
            
            client = await self._client_repository.get_client_by_id(client_id)
            
            if client:
                return Client.model_validate(client)
            return None
            
        except Exception as e:
            self._logger.error(f"Error al buscar cliente ID {client_id}: {e}")
            raise RepositoryError(
                message=f"Error al buscar cliente: {e}",
                operation="get_client_by_id",
                entity_type="Client",
                original_error=e
            )

    async def update_client(
        self,
        client_id: int,
        client_data: ClientUpdate,
        validate_business_rules: bool = True
    ) -> Client:
        """
        Actualiza un cliente existente con validaciones de dominio.
        
        Args:
            client_id: ID del cliente a actualizar
            client_data: Datos de actualización
            validate_business_rules: Si aplicar validaciones de negocio
            
        Returns:
            Client: Cliente actualizado
            
        Raises:
            NotFoundError: Si el cliente no existe
            ValidationError: Si los datos no son válidos
            BusinessLogicError: Si no se puede eliminar por reglas de negocio
            RepositoryError: Si hay errores en la persistencia
            BusinessRuleViolationError: Si no se puede eliminar por reglas de negocio
        """
        try:
            self._logger.info(f"Iniciando actualización de cliente ID: {client_id}")
            
            # Verificar que el cliente existe
            existing_client = await self._client_repository.get_client_by_id(client_id)
            if not existing_client:
                raise NotFoundError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    entity_type="Client",
                    entity_id=str(client_id)
                )
            
            # Validaciones de dominio
            if validate_business_rules:
                await self._validate_client_update(client_id, client_data)
            
            # Actualizar cliente a través del repositorio
            updated_client = await self._client_repository.update_client(client_id, client_data)
            
            if not updated_client:
                raise RepositoryError(
                    message=f"Error al actualizar cliente ID {client_id}",
                    operation="update_client",
                    entity_type="Client",
                    original_error=None
                )
            
            self._logger.info(f"Cliente actualizado exitosamente: ID {client_id}")
            return Client.model_validate(updated_client)
            
        except Exception as e:
            self._logger.error(f"Error al actualizar cliente ID {client_id}: {e}")
            if isinstance(e, (NotFoundError, ValidationError, BusinessLogicError)):
                raise
            raise RepositoryError(
                message=f"Error inesperado al actualizar cliente: {e}",
                operation="update_client",
                entity_type="Client",
                original_error=e
            )

    async def get_all_clients(
        self,
        include_inactive: bool = False,
        include_relationships: bool = False
    ) -> List[Client]:
        """
        Obtiene todos los clientes del sistema.
        
        Args:
            include_inactive: Si incluir clientes inactivos
            include_relationships: Si incluir relaciones
            
        Returns:
            List[Client]: Lista de todos los clientes
        """
        try:
            self._logger.debug(f"Obteniendo todos los clientes (include_inactive={include_inactive})")
            
            clients = await self._client_repository.get_all_clients()
            
            result = [Client.model_validate(client) for client in clients]
            self._logger.debug(f"Obtenidos {len(result)} clientes")
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error al obtener todos los clientes: {e}")
            raise RepositoryError(
                message=f"Error al obtener todos los clientes: {e}",
                operation="get_all_clients",
                entity_type="Client",
                original_error=e
            )

    async def bulk_update_clients(
        self,
        updates: Dict[UUID, ClientUpdate],
        validate_business_rules: bool = True
    ) -> List[Client]:
        """
        Actualiza múltiples clientes en una operación transaccional.
        
        Args:
            updates: Diccionario con ID del cliente y datos de actualización
            validate_business_rules: Si aplicar validaciones de negocio
            
        Returns:
            List[Client]: Lista de clientes actualizados
            
        Raises:
            ValidationError: Si alguna actualización no cumple las reglas
            TransactionError: Si falla la operación transaccional
        """
        try:
            self._logger.debug(f"Actualizando {len(updates)} clientes en lote")
            
            updated_clients = []
            
            for client_id, client_data in updates.items():
                if validate_business_rules:
                    await self._validate_client_update(client_id, client_data)
                
                updated_client = await self.update_client(
                    client_id=client_id,
                    client_data=client_data,
                    validate_business_rules=False  # Ya validado arriba
                )
                updated_clients.append(updated_client)
            
            self._logger.info(f"✅ {len(updated_clients)} clientes actualizados en lote")
            return updated_clients
            
        except Exception as e:
            self._logger.error(f"Error en actualización en lote: {e}")
            raise RepositoryError(
                message=f"Error en actualización en lote: {e}",
                operation="bulk_update_clients",
                entity_type="Client",
                original_error=e
            )

    async def delete_client(self, client_id: int) -> bool:
        """Elimina un cliente por su ID aplicando validaciones de negocio."""
        try:
            self._logger.info(f"Iniciando eliminación de cliente ID: {client_id}")
            
            # Verificar que el cliente existe
            existing_client = await self._client_repository.get_client_by_id(client_id)
            if not existing_client:
                raise NotFoundError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    entity_type="Client",
                    entity_id=str(client_id)
                )
            
            # Validar que se puede eliminar
            await self._validate_client_deletion(client_id)
            
            # Eliminar cliente a través del repositorio
            deleted = await self._client_repository.delete_client(client_id)
            
            if deleted:
                self._logger.info(f"Cliente eliminado exitosamente: ID {client_id}")
            else:
                self._logger.warning(f"No se pudo eliminar cliente ID: {client_id}")
            
            return deleted
            
        except Exception as e:
            self._logger.error(f"Error al eliminar cliente ID {client_id}: {e}")
            if isinstance(e, (NotFoundError, BusinessLogicError)):
                raise
            raise RepositoryError(
                message=f"Error inesperado al eliminar cliente: {e}",
                operation="delete_client",
                entity_type="Client",
                original_error=e
            )

    async def bulk_create_clients(
        self,
        clients_data: List[ClientCreate],
        validate_business_rules: bool = True
    ) -> List[Client]:
        """Crea múltiples clientes en una sola operación transaccional."""
        try:
            self._logger.info(f"Iniciando creación en lote de {len(clients_data)} clientes")
            
            created_clients = []
            
            for i, client_data in enumerate(clients_data):
                try:
                    # Validaciones de dominio para cada cliente
                    if validate_business_rules:
                        await self._validate_client_creation(client_data)
                    
                    # Crear cliente
                    created_client = await self._client_repository.create_client(client_data)
                    created_clients.append(Client.model_validate(created_client))
                    
                except Exception as e:
                    self._logger.error(f"Error al crear cliente {i+1}/{len(clients_data)}: {e}")
                    raise ValidationError(
                        message=f"Error en cliente {i+1}: {e}",
                        field=f"clients_data[{i}]",
                        value=client_data.model_dump()
                    )
            
            self._logger.info(f"Creación en lote completada: {len(created_clients)} clientes")
            return created_clients
            
        except Exception as e:
            self._logger.error(f"Error en creación en lote: {e}")
            if isinstance(e, ValidationError):
                raise
            raise RepositoryError(
                message=f"Error inesperado en creación en lote: {e}",
                operation="bulk_create_clients",
                entity_type="Client",
                original_error=e
            )

    async def get_by_unique_field(self, field_name: str, field_value: Any) -> Optional[Client]:
        """
        Obtiene un cliente por un campo único específico.
        
        Args:
            field_name: Nombre del campo único
            field_value: Valor del campo único
            
        Returns:
            Optional[Client]: Cliente encontrado o None
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        try:
            self._logger.debug(f"Buscando cliente por {field_name}={field_value}")
            
            client = await self._client_repository.get_by_unique_field(field_name, field_value)
            
            if client:
                return Client.model_validate(client)
            return None
            
        except Exception as e:
            self._logger.error(f"Error al buscar cliente por {field_name}={field_value}: {e}")
            raise RepositoryError(
                message=f"Error al buscar cliente por campo único: {e}",
                operation="get_by_unique_field",
                entity_type="Client",
                original_error=e
            )

    # Métodos privados de validación

    async def _validate_client_creation(self, client_data: ClientCreate) -> None:
        """Valida las reglas de negocio para la creación de un cliente."""
        # Validar unicidad de nombre
        if await self._client_repository.get_client_by_name(client_data.name):
            raise BusinessLogicError(
                message=f"Ya existe un cliente con el nombre '{client_data.name}'",
                operation="validate_client_creation",
                entity_type="Client"
            )
        
        # Validar unicidad de código si se proporciona
        if client_data.code:
            if await self._client_repository.get_client_by_code(client_data.code):
                raise BusinessLogicError(
                message=f"Ya existe un cliente con el código '{client_data.code}'",
                operation="validate_client_creation",
                entity_type="Client"
            )
        
        # Validar unicidad de email si se proporciona
        if client_data.email:
            if await self._client_repository.get_client_by_email(client_data.email):
                raise BusinessLogicError(
                message=f"Ya existe un cliente con el email '{client_data.email}'",
                operation="validate_client_creation",
                entity_type="Client"
            )

    async def _validate_client_update(self, client_id: int, client_data: ClientUpdate) -> None:
        """Valida las reglas de negocio para la actualización de un cliente."""
        # Validar unicidad de nombre si se está actualizando
        if client_data.name:
            existing_client = await self._client_repository.get_client_by_name(client_data.name)
            if existing_client and existing_client.id != client_id:
                raise BusinessLogicError(
                    message=f"Ya existe otro cliente con el nombre '{client_data.name}'",
                    operation="validate_client_update",
                    entity_type="Client"
                )
        
        # Validar unicidad de código si se está actualizando
        if client_data.code:
            existing_client = await self._client_repository.get_client_by_code(client_data.code)
            if existing_client and existing_client.id != client_id:
                raise BusinessLogicError(
                    message=f"Ya existe otro cliente con el código '{client_data.code}'",
                    operation="validate_client_update",
                    entity_type="Client"
                )
        
        # Validar unicidad de email si se está actualizando
        if client_data.email:
            existing_client = await self._client_repository.get_client_by_email(client_data.email)
            if existing_client and existing_client.id != client_id:
                raise BusinessLogicError(
                    message=f"Ya existe otro cliente con el email '{client_data.email}'",
                    operation="validate_client_update",
                    entity_type="Client"
                )

    async def _validate_client_deletion(self, client_id: int) -> None:
        """Valida si un cliente puede ser eliminado según las reglas de negocio."""
        # Verificar si el cliente tiene proyectos asociados
        project_count = await self._client_repository.get_client_project_count(client_id)
        if project_count > 0:
            raise BusinessLogicError(
                message=f"No se puede eliminar el cliente porque tiene {project_count} proyecto(s) asociado(s)",
                operation="validate_client_deletion",
                entity_type="Client"
            )