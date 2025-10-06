"""Módulo de operaciones de consulta avanzadas para clientes.

Este módulo implementa funcionalidades especializadas para consultas
complejas y filtros avanzados sobre la entidad Client, aprovechando
las capacidades del BaseRepository.

Características principales:
- Búsquedas por texto completo
- Filtros múltiples y combinados
- Consultas con criterios complejos
- Paginación y ordenamiento avanzado
- Manejo robusto de errores con logging estructurado
- Operaciones asíncronas optimizadas

Autor: Sistema de Repositorios
Versión: 2.0.0
"""

from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.exceptions.validation import ValidationError
from planificador.exceptions.repository.client_repository_exceptions import ClientRepositoryError
from planificador.exceptions.repository.base_repository_exceptions import convert_sqlalchemy_error
from planificador.models.client import Client
from planificador.repositories.base_repository import BaseRepository
from planificador.repositories.client.interfaces.query_interface import (
    IAdvancedQueryOperations,
    IQueryOperations,
)


class AdvancedQueryOperations(BaseRepository[Client], IAdvancedQueryOperations, IQueryOperations):
    """Implementación de operaciones de consulta avanzadas para clientes.
    
    Hereda de BaseRepository para reutilizar la lógica CRUD y de consulta
    básica, y se especializa en búsquedas complejas para la entidad Client.
    """

    def __init__(self, session: AsyncSession):
        """Inicializa las operaciones de consulta avanzadas.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        super().__init__(session, Client)
        self._logger = self._logger.bind(component="AdvancedQueryOperations")
        self._logger.debug("AdvancedQueryOperations inicializado")

    async def search_clients_by_text(
        self, 
        search_text: str, 
        fields: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Client]:
        """Busca clientes por texto en múltiples campos.
        
        Args:
            search_text: Texto a buscar
            fields: Lista de campos donde buscar (None para todos)
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            
        Returns:
            Lista de clientes que coinciden con el texto
            
        Raises:
            ValidationError: Si los parámetros son inválidos
            RepositoryError: Si ocurre un error en la consulta
        """
        if not search_text or not search_text.strip():
            raise ValidationError(
                message="El texto de búsqueda no puede estar vacío",
                field="search_text",
                value=search_text
            )
            
        self._logger.debug(
            f"Búsqueda de texto: '{search_text}' en campos: {fields}"
        )
        
        default_fields = ['name', 'email', 'phone', 'address', 'code']
        search_fields = fields if fields else default_fields
        
        pattern = f"%{search_text.strip()}%"
        
        # Usamos un OR para buscar en múltiples campos
        criteria = {
            "or": [
                {field: {"operator": "ilike", "value": pattern}}
                for field in search_fields if hasattr(self.model_class, field)
            ]
        }
        
        if not criteria["or"]:
            raise ValidationError(
                message="No se encontraron campos válidos para búsqueda",
                field="fields",
                value=fields
            )

        return await self.find_by_criteria(
            criteria=criteria,
            limit=limit,
            offset=offset,
            order_by="name"
        )

    async def get_clients_by_filters(
        self, 
        filters: Dict[str, Any],
        limit: int = 50,
        offset: int = 0,
        order_by: Optional[str] = "name"
    ) -> List[Client]:
        """Obtiene clientes aplicando múltiples filtros.
        
        Este método actúa como un alias para find_by_criteria, garantizando
        la compatibilidad con la interfaz anterior.
        
        Args:
            filters: Diccionario con filtros a aplicar
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            order_by: Campo por el cual ordenar
            
        Returns:
            Lista de clientes que cumplen los filtros
            
        Raises:
            RepositoryError: Si ocurre un error en la consulta
            ValidationError: Si los filtros son inválidos
        """
        if not filters:
            raise ValidationError(
                message="Debe proporcionar al menos un filtro",
                field="filters",
                value=filters
            )
            
        self._logger.debug(f"Aplicando filtros: {filters}")
        
        return await self.find_by_criteria(
            criteria=filters,
            limit=limit,
            offset=offset,
            order_by=order_by
        )

    async def get_clients_with_relationships(
        self, 
        include_projects: bool = False,
        include_contacts: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Client]:
        """Obtiene clientes con sus relaciones cargadas (eager loading).
        
        Args:
            include_projects: Si incluir proyectos relacionados
            include_contacts: Si incluir contactos relacionados
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            
        Returns:
            Lista de clientes con relaciones cargadas
            
        Raises:
            RepositoryError: Si ocurre un error en la consulta
        """
        self._logger.debug(
            f"Obteniendo clientes con relaciones (projects: {include_projects}, "
            f"contacts: {include_contacts})"
        )
        
        relationships_to_load = []
        if include_projects and hasattr(self.model_class, 'projects'):
            relationships_to_load.append('projects')
        if include_contacts and hasattr(self.model_class, 'contacts'):
            relationships_to_load.append('contacts')
        
        return await self.get_all_with_relationships(
            relationships=relationships_to_load,
            limit=limit,
            offset=offset,
            order_by="name"
        )

    async def count_clients_by_filters(self, filters: Dict[str, Any]) -> int:
        """Cuenta clientes que cumplen los filtros especificados.
        
        Este método actúa como un alias para el método `count` del
        repositorio base.
        
        Args:
            filters: Diccionario con filtros a aplicar
            
        Returns:
            Número de clientes que cumplen los filtros
            
        Raises:
            RepositoryError: Si ocurre un error en la consulta
        """
        self._logger.debug(f"Contando clientes con filtros: {filters}")
        return await self.count(filters=filters)

    async def search_clients_fuzzy(
        self, 
        search_term: str, 
        similarity_threshold: float = 0.3
    ) -> List[Client]:
        """Realiza búsqueda difusa de clientes.
        
        En esta implementación, se simula una búsqueda difusa usando ILIKE.
        Para una búsqueda más avanzada, se recomienda usar extensiones de
        base de datos como pg_trgm en PostgreSQL.
        
        Args:
            search_term: Término de búsqueda
            similarity_threshold: Umbral de similitud (no utilizado en esta simulación)
            
        Returns:
            Lista de clientes ordenados por relevancia
            
        Raises:
            RepositoryError: Si ocurre un error en la consulta
        """
        if not search_term or not search_term.strip():
            return []
            
        self._logger.debug(
            f"Búsqueda difusa (simulada): '{search_term}'"
        )
        
        search_pattern = f"%{search_term.strip()}%"
        
        criteria = {
            "or": [
                {"name": {"operator": "ilike", "value": search_pattern}},
                {"email": {"operator": "ilike", "value": search_pattern}},
                {"code": {"operator": "ilike", "value": search_pattern}},
            ]
        }
        
        return await self.find_by_criteria(
            criteria=criteria,
            limit=50,
            order_by="name"
        )

    # Implementación de métodos de IQueryOperations
    async def get_client_by_id(self, client_id: int) -> Client | None:
        """Obtiene un cliente por su ID."""
        self._logger.debug(f"Obteniendo cliente por ID: {client_id}")
        
        try:
            async with self.get_session() as session:
                query = select(self.model_class).where(self.model_class.id == client_id)
                result = await session.execute(query)
                client = result.scalar_one_or_none()
                
                if client:
                    self._logger.debug(f"Cliente encontrado: {client.name}")
                else:
                    self._logger.debug(f"No se encontró cliente con ID: {client_id}")
                
                return client
                
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo cliente por ID {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_by_id",
                entity_type=self.model_class.__name__,
                entity_id=client_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo cliente: {e}")
            raise ClientRepositoryError(
                message=f"Error inesperado obteniendo cliente con ID {client_id}",
                operation="get_client_by_id",
                entity_type=self.model_class.__name__,
                entity_id=client_id,
                original_error=e
            )

    async def get_client_by_name(self, name: str) -> Client | None:
        """Busca un cliente por nombre exacto (case-insensitive)."""
        self._logger.debug(f"Buscando cliente por nombre: {name}")
        
        try:
            async with self.get_session() as session:
                query = select(self.model_class).where(
                    self.model_class.name.ilike(name)
                )
                result = await session.execute(query)
                client = result.scalar_one_or_none()
                
                if client:
                    self._logger.debug(f"Cliente encontrado: {client.id}")
                else:
                    self._logger.debug(f"No se encontró cliente con nombre: {name}")
                
                return client
                
        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando cliente por nombre {name}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_by_name",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando cliente: {e}")
            raise ClientRepositoryError(
                message=f"Error inesperado buscando cliente por nombre {name}",
                operation="get_client_by_name",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_client_by_code(self, code: str) -> Client | None:
        """Busca un cliente por código único."""
        self._logger.debug(f"Buscando cliente por código: {code}")
        
        try:
            async with self.get_session() as session:
                query = select(self.model_class).where(self.model_class.code == code)
                result = await session.execute(query)
                client = result.scalar_one_or_none()
                
                if client:
                    self._logger.debug(f"Cliente encontrado: {client.name}")
                else:
                    self._logger.debug(f"No se encontró cliente con código: {code}")
                
                return client
                
        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando cliente por código {code}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_by_code",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando cliente: {e}")
            raise ClientRepositoryError(
                message=f"Error inesperado buscando cliente por código {code}",
                operation="get_client_by_code",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_client_by_email(self, email: str) -> Client | None:
        """Busca un cliente por email (case-insensitive)."""
        self._logger.debug(f"Buscando cliente por email: {email}")
        
        try:
            async with self.get_session() as session:
                query = select(self.model_class).where(
                    self.model_class.email.ilike(email)
                )
                result = await session.execute(query)
                client = result.scalar_one_or_none()
                
                if client:
                    self._logger.debug(f"Cliente encontrado: {client.name}")
                else:
                    self._logger.debug(f"No se encontró cliente con email: {email}")
                
                return client
                
        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando cliente por email {email}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_by_email",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando cliente: {e}")
            raise ClientRepositoryError(
                message=f"Error inesperado buscando cliente por email {email}",
                operation="get_client_by_email",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def search_clients_by_name(self, name_pattern: str) -> list[Client]:
        """Busca clientes por patrón de nombre (case-insensitive)."""
        self._logger.debug(f"Buscando clientes por patrón de nombre: {name_pattern}")
        
        try:
            async with self.get_session() as session:
                pattern = f"%{name_pattern}%"
                query = select(self.model_class).where(
                    self.model_class.name.ilike(pattern)
                ).order_by(self.model_class.name)
                
                result = await session.execute(query)
                clients = result.scalars().all()
                
                self._logger.debug(f"Encontrados {len(clients)} clientes con patrón: {name_pattern}")
                return list(clients)
                
        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando clientes por patrón {name_pattern}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="search_clients_by_name",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando clientes: {e}")
            raise ClientRepositoryError(
                message=f"Error inesperado buscando clientes por patrón {name_pattern}",
                operation="search_clients_by_name",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_all_clients(
        self, limit: int | None = None, offset: int = 0
    ) -> list[Client]:
        """Obtiene todos los clientes con paginación opcional."""
        self._logger.debug(f"Obteniendo todos los clientes (limit: {limit}, offset: {offset})")
        
        try:
            async with self.get_session() as session:
                query = select(self.model_class).order_by(self.model_class.name)
                
                if offset > 0:
                    query = query.offset(offset)
                if limit is not None:
                    query = query.limit(limit)
                
                result = await session.execute(query)
                clients = result.scalars().all()
                
                self._logger.debug(f"Obtenidos {len(clients)} clientes")
                return list(clients)
                
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo todos los clientes: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_all_clients",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo clientes: {e}")
            raise ClientRepositoryError(
                message="Error inesperado obteniendo todos los clientes",
                operation="get_all_clients",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    # Implementación del método abstracto de BaseRepository
    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[Client]:
        """
        Obtiene un cliente por un campo único específico.
        
        Args:
            field_name: Nombre del campo único (email, code, etc.)
            value: Valor a buscar
            
        Returns:
            Cliente encontrado o None si no existe
        """
        self._logger.debug(f"Buscando cliente por {field_name} = {value}")
        
        try:
            async with self.get_session() as session:
                # Obtener el atributo del modelo dinámicamente
                if not hasattr(self.model_class, field_name):
                    raise ValueError(f"El campo '{field_name}' no existe en el modelo Client")
                
                field_attr = getattr(self.model_class, field_name)
                query = select(self.model_class).where(field_attr == value)
                result = await session.execute(query)
                client = result.scalar_one_or_none()
                
                if client:
                    self._logger.debug(f"Cliente encontrado: {client.id}")
                else:
                    self._logger.debug(f"No se encontró cliente con {field_name} = {value}")
                
                return client
                
        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando cliente por {field_name}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_unique_field",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando cliente: {e}")
            raise ClientRepositoryError(
                message=f"Error inesperado buscando cliente por {field_name} = {value}",
                operation="get_by_unique_field",
                entity_type=self.model_class.__name__,
                original_error=e
            )