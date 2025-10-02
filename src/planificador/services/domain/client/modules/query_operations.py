# src/planificador/services/domain/client/modules/query_operations.py

"""
Módulo de operaciones de consulta básica para el servicio de dominio de cliente.

Este módulo implementa las consultas básicas y comunes para la entidad Cliente,
proporcionando métodos optimizados para búsquedas frecuentes.
"""

from typing import List, Optional

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

    async def get_clients_by_status(self, is_active: bool) -> List[Client]:
        """
        Obtiene clientes filtrados por su estado activo/inactivo.
        
        Args:
            is_active: True para clientes activos, False para inactivos
            
        Returns:
            List[Client]: Lista de clientes que coinciden con el estado
        """
        try:
            self._logger.debug(f"Buscando clientes por estado activo: {is_active}")
            
            filters = {"is_active": is_active}
            clients = await self._client_repository.get_clients_by_filters(filters)
            
            return [Client.model_validate(client) for client in clients]
            
        except Exception as e:
            self._logger.error(f"Error al buscar clientes por estado {is_active}: {e}")
            raise RepositoryError(
                message=f"Error al buscar clientes por estado: {e}",
                operation="get_clients_by_status",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_by_ids(self, client_ids: List[int]) -> List[Client]:
        """
        Obtiene múltiples clientes por sus IDs.
        
        Args:
            client_ids: Lista de IDs de clientes a buscar
            
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

    async def search_clients_basic(
        self,
        search_term: str,
        fields: Optional[List[str]] = None
    ) -> List[Client]:
        """
        Realiza una búsqueda básica de clientes en campos específicos.
        
        Args:
            search_term: Término de búsqueda
            fields: Lista de campos donde buscar (por defecto: name, email, contact_person)
            
        Returns:
            List[Client]: Lista de clientes que coinciden con la búsqueda
        """
        try:
            self._logger.debug(f"Búsqueda básica de clientes: '{search_term}'")
            
            # Campos por defecto si no se especifican
            if fields is None:
                fields = ["name", "email", "contact_person"]
            
            clients = await self._client_repository.search_clients_by_text(
                search_text=search_term,
                fields=fields
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

    async def get_active_clients(self) -> List[Client]:
        """
        Obtiene todos los clientes activos.
        
        Returns:
            List[Client]: Lista de clientes activos
        """
        try:
            self._logger.debug("Obteniendo clientes activos")
            
            return await self.get_clients_by_status(is_active=True)
            
        except Exception as e:
            self._logger.error(f"Error al obtener clientes activos: {e}")
            raise RepositoryError(
                message=f"Error al obtener clientes activos: {e}",
                operation="get_active_clients",
                entity_type="Client",
                original_error=e
            )

    async def get_inactive_clients(self) -> List[Client]:
        """
        Obtiene todos los clientes inactivos.
        
        Returns:
            List[Client]: Lista de clientes inactivos
        """
        try:
            self._logger.debug("Obteniendo clientes inactivos")
            
            return await self.get_clients_by_status(is_active=False)
            
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