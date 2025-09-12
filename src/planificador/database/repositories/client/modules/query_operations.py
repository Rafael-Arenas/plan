"""Módulo de operaciones de consulta para clientes.

Este módulo implementa la interfaz IQueryOperations y proporciona
funcionalidades especializadas para consultas básicas de clientes.

Características principales:
- Consultas por ID, nombre, código y email
- Búsquedas por patrones de texto
- Manejo robusto de errores con logging estructurado
- Operaciones asíncronas optimizadas
- Integración con el sistema de excepciones del repositorio

Autor: Sistema de Repositorios
Versión: 1.0.0
"""

from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.exceptions.repository.client_repository_exceptions import (
    ClientRepositoryError,
    ClientNotFoundError,
)
from planificador.models.client import Client
from ..interfaces.query_interface import IQueryOperations


class QueryOperations(IQueryOperations):
    """Implementación de operaciones de consulta para clientes.
    
    Esta clase proporciona métodos especializados para realizar consultas
    básicas sobre la entidad Client, incluyendo búsquedas por diferentes
    criterios y patrones de texto.
    
    Attributes:
        session: Sesión asíncrona de SQLAlchemy
        _logger: Logger estructurado para la clase
    """

    def __init__(self, session: AsyncSession):
        """Inicializa las operaciones de consulta.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        self.session = session
        self._logger = logger.bind(component="QueryOperations")
        
        self._logger.debug("QueryOperations inicializado")

    async def get_client_by_id(self, client_id: int) -> Client | None:
        """Obtiene un cliente por su ID.
        
        Args:
            client_id: ID del cliente a buscar
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Buscando cliente por ID: {client_id}")
            
            # Realizar consulta directa por ID
            result = await self.session.get(Client, client_id)
            
            if result:
                self._logger.info(f"Cliente encontrado: {result.name} (ID: {client_id})")
            else:
                self._logger.debug(f"Cliente no encontrado con ID: {client_id}")
                
            return result
            
        except Exception as e:
            self._logger.error(f"Error al buscar cliente por ID {client_id}: {e}")
            raise ClientRepositoryError(
                message=f"Error al buscar cliente por ID: {e}",
                operation="get_client_by_id",
                entity_type="Client",
                entity_id=client_id,
                original_error=e
            )

    async def get_client_by_name(self, name: str) -> Client | None:
        """Busca un cliente por nombre exacto.
        
        Args:
            name: Nombre exacto del cliente
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Buscando cliente por nombre: {name}")
            
            from sqlalchemy import select
            
            # Consulta por nombre exacto (case-insensitive)
            stmt = select(Client).where(Client.name.ilike(name))
            result = await self.session.execute(stmt)
            client = result.scalar_one_or_none()
            
            if client:
                self._logger.info(f"Cliente encontrado por nombre: {client.name} (ID: {client.id})")
            else:
                self._logger.debug(f"Cliente no encontrado con nombre: {name}")
                
            return client
            
        except Exception as e:
            self._logger.error(f"Error al buscar cliente por nombre '{name}': {e}")
            raise ClientRepositoryError(
                message=f"Error al buscar cliente por nombre: {e}",
                operation="get_client_by_name",
                entity_type="Client",
                original_error=e
            )

    async def get_client_by_code(self, code: str) -> Client | None:
        """Busca un cliente por código único.
        
        Args:
            code: Código único del cliente
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Buscando cliente por código: {code}")
            
            from sqlalchemy import select
            
            # Consulta por código exacto
            stmt = select(Client).where(Client.code == code)
            result = await self.session.execute(stmt)
            client = result.scalar_one_or_none()
            
            if client:
                self._logger.info(f"Cliente encontrado por código: {client.name} (código: {code})")
            else:
                self._logger.debug(f"Cliente no encontrado con código: {code}")
                
            return client
            
        except Exception as e:
            self._logger.error(f"Error al buscar cliente por código '{code}': {e}")
            raise ClientRepositoryError(
                message=f"Error al buscar cliente por código: {e}",
                operation="get_client_by_code",
                entity_type="Client",
                original_error=e
            )

    async def get_client_by_email(self, email: str) -> Client | None:
        """Busca un cliente por email.
        
        Args:
            email: Email del cliente
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Buscando cliente por email: {email}")
            
            from sqlalchemy import select
            
            # Consulta por email (case-insensitive)
            stmt = select(Client).where(Client.email.ilike(email))
            result = await self.session.execute(stmt)
            client = result.scalar_one_or_none()
            
            if client:
                self._logger.info(f"Cliente encontrado por email: {client.name} (email: {email})")
            else:
                self._logger.debug(f"Cliente no encontrado con email: {email}")
                
            return client
            
        except Exception as e:
            self._logger.error(f"Error al buscar cliente por email '{email}': {e}")
            raise ClientRepositoryError(
                message=f"Error al buscar cliente por email: {e}",
                operation="get_client_by_email",
                entity_type="Client",
                original_error=e
            )

    async def search_clients_by_name(self, name_pattern: str) -> list[Client]:
        """Busca clientes por patrón de nombre.
        
        Args:
            name_pattern: Patrón de búsqueda para el nombre
            
        Returns:
            Lista de clientes que coinciden con el patrón
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Buscando clientes por patrón de nombre: {name_pattern}")
            
            from sqlalchemy import select
            
            # Búsqueda con patrón LIKE (case-insensitive)
            pattern = f"%{name_pattern}%"
            stmt = select(Client).where(Client.name.ilike(pattern)).order_by(Client.name)
            result = await self.session.execute(stmt)
            clients = result.scalars().all()
            
            self._logger.info(f"Encontrados {len(clients)} clientes con patrón '{name_pattern}'")
            return list(clients)
            
        except Exception as e:
            self._logger.error(f"Error al buscar clientes por patrón '{name_pattern}': {e}")
            raise ClientRepositoryError(
                message=f"Error al buscar clientes por patrón de nombre: {e}",
                operation="search_clients_by_name",
                entity_type="Client",
                original_error=e
            )

    async def get_all_clients(self, limit: int | None = None, offset: int = 0) -> list[Client]:
        """Obtiene todos los clientes con paginación opcional.
        
        Args:
            limit: Número máximo de clientes a retornar (None para todos)
            offset: Número de clientes a omitir desde el inicio
            
        Returns:
            Lista de clientes
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo todos los clientes (limit: {limit}, offset: {offset})")
            
            from sqlalchemy import select
            
            # Consulta base ordenada por nombre
            stmt = select(Client).order_by(Client.name)
            
            # Aplicar paginación si se especifica
            if offset > 0:
                stmt = stmt.offset(offset)
            if limit is not None:
                stmt = stmt.limit(limit)
                
            result = await self.session.execute(stmt)
            clients = result.scalars().all()
            
            self._logger.info(f"Obtenidos {len(clients)} clientes")
            return list(clients)
            
        except Exception as e:
            self._logger.error(f"Error al obtener todos los clientes: {e}")
            raise ClientRepositoryError(
                message=f"Error al obtener todos los clientes: {e}",
                operation="get_all_clients",
                entity_type="Client",
                original_error=e
            )