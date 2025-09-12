"""Módulo de operaciones de búsqueda para clientes.

Este módulo implementa la interfaz ISearchOperations y proporciona
funcionalidades especializadas para búsqueda y filtrado de clientes.

Clases:
    SearchOperations: Implementación de operaciones de búsqueda

Ejemplo:
    ```python
    search_ops = SearchOperations(session, query_builder, exception_handler)
    clients = await search_ops.search_clients_by_text("empresa")
    ```
"""

from typing import Any
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from planificador.models.client import Client
from ..interfaces.search_interface import ISearchOperations
from ..client_query_builder import ClientQueryBuilder
from ..client_exception_handler import ClientExceptionHandler


class SearchOperations(ISearchOperations):
    """Implementación de operaciones de búsqueda para clientes.
    
    Esta clase proporciona métodos especializados para búsqueda y filtrado
    de clientes, delegando las consultas complejas al query builder.
    
    Attributes:
        session: Sesión de base de datos SQLAlchemy
        query_builder: Constructor de consultas especializado
        exception_handler: Manejador de excepciones del repositorio
    """
    
    def __init__(
        self,
        session: AsyncSession,
        query_builder: ClientQueryBuilder,
        exception_handler: ClientExceptionHandler,
    ) -> None:
        """Inicializa las operaciones de búsqueda.
        
        Args:
            session: Sesión de base de datos activa
            query_builder: Constructor de consultas para clientes
            exception_handler: Manejador de excepciones
        """
        self.session = session
        self.query_builder = query_builder
        self.exception_handler = exception_handler
        self._logger = logger.bind(module="SearchOperations")
    
    async def search_clients_by_text(self, search_text: str) -> list[Client]:
        """Busca clientes por texto en múltiples campos.
        
        Args:
            search_text: Texto a buscar en nombre, código y otros campos
            
        Returns:
            Lista de clientes que coinciden con el texto
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la búsqueda
        """
        self._logger.info(f"Buscando clientes por texto: {search_text}")
        
        try:
            return await self.query_builder.search_clients_by_text(search_text)
        except Exception as e:
            self._logger.error(f"Error en búsqueda por texto: {e}")
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="search_clients_by_text",
                additional_context={"search_text": search_text},
            )
    
    async def get_clients_by_filters(
        self, filters: dict[str, Any]
    ) -> list[Client]:
        """Obtiene clientes aplicando múltiples filtros.
        
        Args:
            filters: Diccionario con criterios de filtrado
            
        Returns:
            Lista de clientes que cumplen los filtros
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        self._logger.info(f"Aplicando filtros: {filters}")
        
        try:
            return await self.query_builder.find_by_criteria(**filters)
        except Exception as e:
            self._logger.error(f"Error aplicando filtros: {e}")
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_by_filters",
                additional_context={"filters": filters},
            )
    
    async def get_clients_with_contact_info(
        self, include_inactive: bool = False
    ) -> list[Client]:
        """Obtiene clientes que tienen información de contacto.
        
        Args:
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            Lista de clientes con información de contacto
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        self._logger.info(
            f"Obteniendo clientes con contacto (incluir inactivos: {include_inactive})"
        )
        
        try:
            return await self.query_builder.find_clients_with_contact_info(
                include_inactive
            )
        except Exception as e:
            self._logger.error(f"Error obteniendo clientes con contacto: {e}")
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_with_contact_info",
                additional_context={"include_inactive": include_inactive},
            )
    
    async def get_clients_without_contact_info(
        self, include_inactive: bool = False
    ) -> list[Client]:
        """Obtiene clientes que no tienen información de contacto.
        
        Args:
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            Lista de clientes sin información de contacto
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        self._logger.info(
            f"Obteniendo clientes sin contacto (incluir inactivos: {include_inactive})"
        )
        
        try:
            return await self.query_builder.find_clients_without_contact_info(
                include_inactive
            )
        except Exception as e:
            self._logger.error(f"Error obteniendo clientes sin contacto: {e}")
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_without_contact_info",
                additional_context={"include_inactive": include_inactive},
            )
    
    async def search_clients_by_name(self, name_pattern: str) -> list[Client]:
        """Busca clientes por patrón de nombre.
        
        Args:
            name_pattern: Patrón de búsqueda en el nombre
            
        Returns:
            Lista de clientes que coinciden con el patrón
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la búsqueda
        """
        self._logger.info(f"Buscando clientes por nombre: {name_pattern}")
        
        try:
            return await self.query_builder.search_by_name(name_pattern)
        except Exception as e:
            self._logger.error(f"Error en búsqueda por nombre: {e}")
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="search_clients_by_name",
                additional_context={"name_pattern": name_pattern},
            )
    
    async def get_active_clients(self) -> list[Client]:
        """Obtiene todos los clientes activos.
        
        Returns:
            Lista de clientes activos
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        self._logger.info("Obteniendo clientes activos")
        
        try:
            return await self.query_builder.get_active_clients()
        except Exception as e:
            self._logger.error(f"Error obteniendo clientes activos: {e}")
            return await self.exception_handler.handle_unexpected_error(
                error=e, operation="get_active_clients", additional_context={}
            )
    
    async def search_with_advanced_filters(
        self,
        name_pattern: str | None = None,
        code_pattern: str | None = None,
        has_email: bool | None = None,
        has_phone: bool | None = None,
        has_contact_person: bool | None = None,
        is_active: bool | None = None,
        min_projects: int | None = None,
        max_projects: int | None = None,
        created_after: date | None = None,
        created_before: date | None = None,
        order_by: str = "name",
        order_direction: str = "asc",
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Client]:
        """Búsqueda avanzada de clientes con múltiples filtros.
        
        Args:
            name_pattern: Patrón de búsqueda en nombre
            code_pattern: Patrón de búsqueda en código
            has_email: Filtrar por presencia de email
            has_phone: Filtrar por presencia de teléfono
            has_contact_person: Filtrar por presencia de persona de contacto
            is_active: Filtrar por estado activo
            min_projects: Número mínimo de proyectos
            max_projects: Número máximo de proyectos
            created_after: Fecha de creación posterior a
            created_before: Fecha de creación anterior a
            order_by: Campo de ordenamiento
            order_direction: Dirección de ordenamiento
            limit: Límite de resultados
            offset: Desplazamiento de resultados
            
        Returns:
            Lista de clientes que coinciden con los filtros
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la búsqueda
        """
        self._logger.info("Ejecutando búsqueda avanzada con filtros")
        
        try:
            return await self.query_builder.search_with_advanced_filters(
                name_pattern=name_pattern,
                code_pattern=code_pattern,
                has_email=has_email,
                has_phone=has_phone,
                has_contact_person=has_contact_person,
                is_active=is_active,
                min_projects=min_projects,
                max_projects=max_projects,
                created_after=created_after,
                created_before=created_before,
                order_by=order_by,
                order_direction=order_direction,
                limit=limit,
                offset=offset,
            )
        except Exception as e:
            self._logger.error(f"Error en búsqueda avanzada: {e}")
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="search_with_advanced_filters",
                additional_context={
                    "name_pattern": name_pattern,
                    "code_pattern": code_pattern,
                    "has_email": has_email,
                    "has_phone": has_phone,
                    "has_contact_person": has_contact_person,
                    "is_active": is_active,
                    "min_projects": min_projects,
                    "max_projects": max_projects,
                    "created_after": created_after,
                    "created_before": created_before,
                    "order_by": order_by,
                    "order_direction": order_direction,
                    "limit": limit,
                    "offset": offset,
                },
            )