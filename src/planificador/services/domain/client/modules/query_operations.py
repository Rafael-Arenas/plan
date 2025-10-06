# src/planificador/services/domain/client/modules/query_operations.py

"""
Módulo de operaciones de consulta básica para el servicio de dominio de cliente.

Este módulo implementa las consultas básicas y comunes para la entidad Cliente,
proporcionando métodos optimizados para búsquedas frecuentes.
"""

from typing import List, Optional
from uuid import UUID

from loguru import logger

from planificador.exceptions import RepositoryError
from planificador.repositories.client.client_repository_facade import ClientRepositoryFacade
from planificador.schemas import Client
from planificador.services.domain.client.interfaces.query_interface import IQueryOperations


class QueryOperations(IQueryOperations):
    """
    Implementación de operaciones de consulta básica para el dominio de cliente.
    
    Esta clase encapsula las consultas más comunes y frecuentes para clientes,
    optimizando el acceso a datos y proporcionando una interfaz consistente.
    """

    def __init__(self, client_repository: ClientRepositoryFacade):
        """
        Inicializa el módulo de operaciones de consulta.
        
        Args:
            client_repository: Facade del repositorio de cliente
        """
        self._client_repository = client_repository
        self._logger = logger

    # ========== Implementación de métodos abstractos faltantes ==========

    async def find_clients_by_name(
        self,
        name: str,
        exact_match: bool = False,
        include_inactive: bool = False
    ) -> List[Client]:
        """
        Busca clientes por nombre.
        
        Args:
            name: Nombre o parte del nombre a buscar
            exact_match: Si buscar coincidencia exacta
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes encontrados
        """
        try:
            self._logger.debug(f"Buscando clientes por nombre: '{name}' (exact={exact_match}, include_inactive={include_inactive})")
            
            if exact_match:
                client = await self._client_repository.get_client_by_name(name)
                if client and (include_inactive or client.is_active):
                    return [Client.model_validate(client)]
                return []
            else:
                clients = await self._client_repository.search_clients_by_name(name)
                if not include_inactive:
                    clients = [c for c in clients if c.is_active]
                return [Client.model_validate(client) for client in clients]
                
        except Exception as e:
            self._logger.error(f"Error al buscar clientes por nombre '{name}': {e}")
            raise RepositoryError(
                message=f"Error al buscar clientes por nombre: {e}",
                operation="find_clients_by_name",
                entity_type="Client",
                original_error=e
            )

    async def find_clients_by_email(
        self,
        email: str,
        exact_match: bool = True
    ) -> List[Client]:
        """
        Busca clientes por email.
        
        Args:
            email: Email o parte del email a buscar
            exact_match: Si buscar coincidencia exacta
            
        Returns:
            List[Client]: Lista de clientes encontrados
        """
        try:
            self._logger.debug(f"Buscando clientes por email: '{email}' (exact={exact_match})")
            
            if exact_match:
                client = await self._client_repository.get_client_by_email(email)
                return [Client.model_validate(client)] if client else []
            else:
                # Para búsqueda parcial, usar filtros con patrón
                filters = {"email__icontains": email}
                clients = await self._client_repository.get_clients_by_filters(filters)
                return [Client.model_validate(client) for client in clients]
                
        except Exception as e:
            self._logger.error(f"Error al buscar clientes por email '{email}': {e}")
            raise RepositoryError(
                message=f"Error al buscar clientes por email: {e}",
                operation="find_clients_by_email",
                entity_type="Client",
                original_error=e
            )

    async def find_clients_by_phone(
        self,
        phone: str,
        exact_match: bool = False
    ) -> List[Client]:
        """
        Busca clientes por teléfono.
        
        Args:
            phone: Teléfono o parte del teléfono a buscar
            exact_match: Si buscar coincidencia exacta
            
        Returns:
            List[Client]: Lista de clientes encontrados
        """
        try:
            self._logger.debug(f"Buscando clientes por teléfono: '{phone}' (exact={exact_match})")
            
            if exact_match:
                filters = {"phone": phone}
                clients = await self._client_repository.get_clients_by_filters(filters, limit=1)
                return [Client.model_validate(clients[0])] if clients else []
            else:
                # Para búsqueda parcial, usar filtros con patrón
                filters = {"phone__icontains": phone}
                clients = await self._client_repository.get_clients_by_filters(filters)
                return [Client.model_validate(client) for client in clients]
                
        except Exception as e:
            self._logger.error(f"Error al buscar clientes por teléfono '{phone}': {e}")
            raise RepositoryError(
                message=f"Error al buscar clientes por teléfono: {e}",
                operation="find_clients_by_phone",
                entity_type="Client",
                original_error=e
            )

    async def check_client_exists(
        self,
        client_id: UUID
    ) -> bool:
        """
        Verifica si un cliente existe.
        
        Args:
            client_id: ID del cliente a verificar
            
        Returns:
            bool: True si el cliente existe
        """
        try:
            self._logger.debug(f"Verificando existencia de cliente ID: {client_id}")
            
            client = await self._client_repository.get_client_by_id(client_id)
            exists = client is not None
            
            self._logger.debug(f"Cliente ID {client_id} {'existe' if exists else 'no existe'}")
            return exists
            
        except Exception as e:
            self._logger.error(f"Error al verificar existencia de cliente ID {client_id}: {e}")
            raise RepositoryError(
                message=f"Error al verificar existencia: {e}",
                operation="check_client_exists",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )

    async def get_clients_by_type(
        self,
        client_type: str,
        include_inactive: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes por tipo.
        
        Args:
            client_type: Tipo de cliente (individual, corporate, etc.)
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes del tipo especificado
        """
        try:
            self._logger.debug(f"Buscando clientes por tipo: {client_type} (include_inactive={include_inactive})")
            
            filters = {"client_type": client_type}
            if not include_inactive:
                filters["is_active"] = True
                
            clients = await self._client_repository.get_clients_by_filters(filters)
            return [Client.model_validate(client) for client in clients]
                
        except Exception as e:
            self._logger.error(f"Error al buscar clientes por tipo '{client_type}': {e}")
            raise RepositoryError(
                message=f"Error al buscar clientes por tipo: {e}",
                operation="get_clients_by_type",
                entity_type="Client",
                original_error=e
            )

    # ========== Métodos existentes ==========

    async def get_client_by_name(self, name: str) -> Optional[Client]:
        """
        Obtiene un cliente por su nombre exacto.
        
        Args:
            name: Nombre del cliente a buscar
            
        Returns:
            Optional[Client]: Cliente encontrado o None
        """
        try:
            self._logger.debug(f"Buscando cliente por nombre: {name}")
            
            client = await self._client_repository.get_client_by_name(name)
            
            if client:
                return Client.model_validate(client)
            return None
            
        except Exception as e:
            self._logger.error(f"Error al buscar cliente por nombre '{name}': {e}")
            raise RepositoryError(
                message=f"Error al buscar cliente por nombre: {e}",
                operation="get_client_by_name",
                entity_type="Client",
                original_error=e
            )

    async def get_client_by_email(self, email: str) -> Optional[Client]:
        """
        Obtiene un cliente por su dirección de email.
        
        Args:
            email: Email del cliente a buscar
            
        Returns:
            Optional[Client]: Cliente encontrado o None
        """
        try:
            self._logger.debug(f"Buscando cliente por email: {email}")
            
            client = await self._client_repository.get_client_by_email(email)
            
            if client:
                return Client.model_validate(client)
            return None
            
        except Exception as e:
            self._logger.error(f"Error al buscar cliente por email '{email}': {e}")
            raise RepositoryError(
                message=f"Error al buscar cliente por email: {e}",
                operation="get_client_by_email",
                entity_type="Client",
                original_error=e
            )

    async def get_client_by_phone(self, phone: str) -> Optional[Client]:
        """
        Obtiene un cliente por su número de teléfono.
        
        Args:
            phone: Teléfono del cliente a buscar
            
        Returns:
            Optional[Client]: Cliente encontrado o None
        """
        try:
            self._logger.debug(f"Buscando cliente por teléfono: {phone}")
            
            # Nota: Esta funcionalidad requiere implementación en el repositorio
            # Por ahora, usamos búsqueda por filtros
            filters = {"phone": phone}
            clients = await self._client_repository.get_clients_by_filters(filters, limit=1)
            
            if clients:
                return Client.model_validate(clients[0])
            return None
            
        except Exception as e:
            self._logger.error(f"Error al buscar cliente por teléfono '{phone}': {e}")
            raise RepositoryError(
                message=f"Error al buscar cliente por teléfono: {e}",
                operation="get_client_by_phone",
                entity_type="Client",
                original_error=e
            )

    async def get_client_by_code(self, code: str) -> Optional[Client]:
        """
        Obtiene un cliente por su código único.
        
        Args:
            code: Código del cliente a buscar
            
        Returns:
            Optional[Client]: Cliente encontrado o None
        """
        try:
            self._logger.debug(f"Buscando cliente por código: {code}")
            
            client = await self._client_repository.get_client_by_code(code)
            
            if client:
                return Client.model_validate(client)
            return None
            
        except Exception as e:
            self._logger.error(f"Error al buscar cliente por código '{code}': {e}")
            raise RepositoryError(
                message=f"Error al buscar cliente por código: {e}",
                operation="get_client_by_code",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_by_status(
        self,
        status: str,
        include_relationships: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes por estado.
        
        Args:
            status: Estado del cliente (active, inactive, suspended, etc.)
            include_relationships: Si incluir relaciones del cliente
            
        Returns:
            List[Client]: Lista de clientes con el estado especificado
        """
        try:
            self._logger.debug(f"Buscando clientes por estado: '{status}' (include_relationships={include_relationships})")
            
            # Mapear estados de string a boolean para is_active
            status_mapping = {
                "active": True,
                "inactive": False,
                "suspended": False
            }
            
            if status in status_mapping:
                is_active = status_mapping[status]
                filters = {"is_active": is_active}
            else:
                # Si no es un estado conocido, buscar por el campo status directamente
                filters = {"status": status}
            
            clients = await self._client_repository.get_clients_by_filters(filters)
            
            # TODO: Implementar include_relationships cuando sea necesario
            if include_relationships:
                self._logger.warning("include_relationships no implementado aún")
            
            return [Client.model_validate(client) for client in clients]
            
        except Exception as e:
            self._logger.error(f"Error al buscar clientes por estado '{status}': {e}")
            raise RepositoryError(
                message=f"Error al buscar clientes por estado: {e}",
                operation="get_clients_by_status",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_by_ids(
        self,
        client_ids: List[UUID],
        include_relationships: bool = False
    ) -> List[Client]:
        """
        Obtiene múltiples clientes por sus IDs.
        
        Args:
            client_ids: Lista de IDs de clientes
            include_relationships: Si incluir relaciones
            
        Returns:
            List[Client]: Lista de clientes encontrados
        """
        try:
            self._logger.debug(f"Buscando {len(client_ids)} clientes por IDs")
            
            clients = []
            for client_id in client_ids:
                client = await self._client_repository.get_client_by_id(client_id)
                if client:
                    clients.append(Client.model_validate(client))
            
            # TODO: Implementar include_relationships cuando sea necesario
            if include_relationships:
                self._logger.warning("include_relationships no implementado aún")
            
            self._logger.debug(f"Encontrados {len(clients)} de {len(client_ids)} clientes")
            return clients
            
        except Exception as e:
            self._logger.error(f"Error al buscar clientes por IDs: {e}")
            raise RepositoryError(
                message=f"Error al buscar clientes por IDs: {e}",
                operation="get_clients_by_ids",
                entity_type="Client",
                original_error=e
            )
            self._logger.error(f"Error al buscar clientes por IDs: {e}")
            raise RepositoryError(
                message=f"Error al buscar clientes por IDs: {e}",
                operation="get_clients_by_ids",
                entity_type="Client",
                original_error=e
            )

    async def search_clients_basic(
        self,
        search_term: str,
        search_fields: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Client]:
        """
        Búsqueda básica de clientes en múltiples campos.
        
        Args:
            search_term: Término de búsqueda
            search_fields: Campos específicos donde buscar (None = todos)
            limit: Límite de resultados
            
        Returns:
            List[Client]: Lista de clientes que coinciden
        """
        try:
            self._logger.debug(f"Búsqueda básica de clientes: '{search_term}' (limit={limit})")
            
            # Campos por defecto si no se especifican
            if search_fields is None:
                search_fields = ["name", "email", "contact_person"]
            
            clients = await self._client_repository.search_clients_by_text(
                search_text=search_term,
                fields=search_fields,
                limit=limit
            )
            
            result = [Client.model_validate(client) for client in clients]
            self._logger.debug(f"Encontrados {len(result)} clientes en búsqueda básica")
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error en búsqueda básica de clientes: {e}")
            raise RepositoryError(
                message=f"Error en búsqueda básica: {e}",
                operation="search_clients_basic",
                entity_type="Client",
                original_error=e
            )

    async def get_all_clients(
        self,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Client]:
        """
        Obtiene todos los clientes con paginación opcional.
        
        Args:
            limit: Número máximo de clientes a retornar
            offset: Número de clientes a omitir
            
        Returns:
            List[Client]: Lista de clientes
        """
        try:
            self._logger.debug(f"Obteniendo todos los clientes (limit={limit}, offset={offset})")
            
            clients = await self._client_repository.get_all_clients(
                limit=limit,
                offset=offset
            )
            
            result = [Client.model_validate(client) for client in clients]
            self._logger.debug(f"Obtenidos {len(result)} clientes")
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error al obtener todos los clientes: {e}")
            raise RepositoryError(
                message=f"Error al obtener clientes: {e}",
                operation="get_all_clients",
                entity_type="Client",
                original_error=e
            )

    async def search_clients_by_name_pattern(self, name_pattern: str) -> List[Client]:
        """
        Busca clientes que coincidan con un patrón de nombre.
        
        Args:
            name_pattern: Patrón de nombre a buscar
            
        Returns:
            List[Client]: Lista de clientes que coinciden con el patrón
        """
        try:
            self._logger.debug(f"Buscando clientes por patrón de nombre: '{name_pattern}'")
            
            clients = await self._client_repository.search_clients_by_name(name_pattern)
            
            result = [Client.model_validate(client) for client in clients]
            self._logger.debug(f"Encontrados {len(result)} clientes con patrón de nombre")
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error al buscar por patrón de nombre: {e}")
            raise RepositoryError(
                message=f"Error en búsqueda por patrón: {e}",
                operation="search_clients_by_name_pattern",
                entity_type="Client",
                original_error=e
            )

    async def get_active_clients(
        self,
        include_relationships: bool = False
    ) -> List[Client]:
        """
        Obtiene todos los clientes activos.
        
        Args:
            include_relationships: Si incluir relaciones del cliente
            
        Returns:
            List[Client]: Lista de clientes activos
        """
        try:
            self._logger.debug(f"Obteniendo clientes activos (include_relationships={include_relationships})")
            
            return await self.get_clients_by_status("active", include_relationships)
            
        except Exception as e:
            self._logger.error(f"Error al obtener clientes activos: {e}")
            raise RepositoryError(
                message=f"Error al obtener clientes activos: {e}",
                operation="get_active_clients",
                entity_type="Client",
                original_error=e
            )

    async def get_inactive_clients(
        self,
        include_relationships: bool = False
    ) -> List[Client]:
        """
        Obtiene todos los clientes inactivos.
        
        Args:
            include_relationships: Si incluir relaciones del cliente
            
        Returns:
            List[Client]: Lista de clientes inactivos
        """
        try:
            self._logger.debug(f"Obteniendo clientes inactivos (include_relationships={include_relationships})")
            
            return await self.get_clients_by_status("inactive", include_relationships)
            
        except Exception as e:
            self._logger.error(f"Error al obtener clientes inactivos: {e}")
            raise RepositoryError(
                message=f"Error al obtener clientes inactivos: {e}",
                operation="get_inactive_clients",
                entity_type="Client",
                original_error=e
            )

    async def client_exists(self, client_id: int) -> bool:
        """
        Verifica si existe un cliente con el ID especificado.
        
        Args:
            client_id: ID del cliente a verificar
            
        Returns:
            bool: True si el cliente existe, False en caso contrario
        """
        try:
            self._logger.debug(f"Verificando existencia de cliente ID: {client_id}")
            
            client = await self._client_repository.get_client_by_id(client_id)
            exists = client is not None
            
            self._logger.debug(f"Cliente ID {client_id} {'existe' if exists else 'no existe'}")
            return exists
            
        except Exception as e:
            self._logger.error(f"Error al verificar existencia de cliente ID {client_id}: {e}")
            raise RepositoryError(
                message=f"Error al verificar existencia: {e}",
                operation="client_exists",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )