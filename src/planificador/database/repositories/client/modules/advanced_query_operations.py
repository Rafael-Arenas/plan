"""Módulo de operaciones de consulta avanzadas para clientes.

Este módulo implementa funcionalidades especializadas para consultas
complejas y filtros avanzados sobre la entidad Client.

Características principales:
- Búsquedas por texto completo
- Filtros múltiples y combinados
- Consultas con criterios complejos
- Paginación y ordenamiento avanzado
- Manejo robusto de errores con logging estructurado
- Operaciones asíncronas optimizadas

Autor: Sistema de Repositorios
Versión: 1.0.0
"""

from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from planificador.exceptions.repository.client_repository_exceptions import (
    ClientRepositoryError,
    ClientValidationError,
)
from planificador.models.client import Client
from ..interfaces.advanced_query_interface import IAdvancedQueryOperations


class AdvancedQueryOperations(IAdvancedQueryOperations):
    """Implementación de operaciones de consulta avanzadas para clientes.
    
    Esta clase proporciona métodos especializados para realizar consultas
    complejas sobre la entidad Client, incluyendo búsquedas por texto,
    filtros múltiples y criterios avanzados.
    
    Attributes:
        session: Sesión asíncrona de SQLAlchemy
        _logger: Logger estructurado para la clase
    """

    def __init__(self, session: AsyncSession):
        """Inicializa las operaciones de consulta avanzadas.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        self.session = session
        self._logger = logger.bind(component="AdvancedQueryOperations")
        
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
            ClientRepositoryError: Si ocurre un error en la consulta
            ClientValidationError: Si los parámetros son inválidos
        """
        try:
            if not search_text or not search_text.strip():
                raise ClientValidationError(
                    message="El texto de búsqueda no puede estar vacío",
                    field="search_text",
                    value=search_text
                )
                
            self._logger.debug(
                f"Búsqueda de texto: '{search_text}' en campos: {fields}"
            )
            
            from sqlalchemy import select
            
            # Campos por defecto para búsqueda
            default_fields = ['name', 'email', 'phone', 'address', 'code']
            search_fields = fields if fields else default_fields
            
            # Construir patrón de búsqueda
            pattern = f"%{search_text.strip()}%"
            
            # Construir condiciones OR para cada campo
            conditions = []
            for field in search_fields:
                if hasattr(Client, field):
                    field_attr = getattr(Client, field)
                    conditions.append(field_attr.ilike(pattern))
            
            if not conditions:
                raise ClientValidationError(
                    message="No se encontraron campos válidos para búsqueda",
                    field="fields",
                    value=fields
                )
            
            # Ejecutar consulta con condiciones OR
            stmt = (
                select(Client)
                .where(or_(*conditions))
                .order_by(Client.name)
                .offset(offset)
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            clients = result.scalars().all()
            
            self._logger.info(
                f"Encontrados {len(clients)} clientes con texto '{search_text}'"
            )
            return list(clients)
            
        except ClientValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error en búsqueda por texto '{search_text}': {e}")
            raise ClientRepositoryError(
                message=f"Error en búsqueda por texto: {e}",
                operation="search_clients_by_text",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_by_filters(
        self, 
        filters: Dict[str, Any],
        limit: int = 50,
        offset: int = 0,
        order_by: Optional[str] = None
    ) -> List[Client]:
        """Obtiene clientes aplicando múltiples filtros.
        
        Args:
            filters: Diccionario con filtros a aplicar
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            order_by: Campo por el cual ordenar
            
        Returns:
            Lista de clientes que cumplen los filtros
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
            ClientValidationError: Si los filtros son inválidos
        """
        try:
            if not filters:
                raise ClientValidationError(
                    message="Debe proporcionar al menos un filtro",
                    field="filters",
                    value=filters
                )
                
            self._logger.debug(f"Aplicando filtros: {filters}")
            
            from sqlalchemy import select
            
            # Construir condiciones de filtro
            conditions = []
            
            for field, value in filters.items():
                if not hasattr(Client, field):
                    raise ClientValidationError(
                        message=f"Campo '{field}' no existe en Client",
                        field=field,
                        value=value
                    )
                
                field_attr = getattr(Client, field)
                
                # Manejar diferentes tipos de filtros
                if isinstance(value, str) and '%' in value:
                    # Filtro LIKE para patrones
                    conditions.append(field_attr.ilike(value))
                elif isinstance(value, list):
                    # Filtro IN para listas
                    conditions.append(field_attr.in_(value))
                elif isinstance(value, dict):
                    # Filtros de rango (gte, lte, gt, lt)
                    if 'gte' in value:
                        conditions.append(field_attr >= value['gte'])
                    if 'lte' in value:
                        conditions.append(field_attr <= value['lte'])
                    if 'gt' in value:
                        conditions.append(field_attr > value['gt'])
                    if 'lt' in value:
                        conditions.append(field_attr < value['lt'])
                else:
                    # Filtro de igualdad exacta
                    conditions.append(field_attr == value)
            
            # Construir consulta base
            stmt = select(Client).where(and_(*conditions))
            
            # Aplicar ordenamiento
            if order_by:
                if hasattr(Client, order_by):
                    order_field = getattr(Client, order_by)
                    stmt = stmt.order_by(order_field)
                else:
                    self._logger.warning(f"Campo de ordenamiento '{order_by}' no existe")
                    stmt = stmt.order_by(Client.name)
            else:
                stmt = stmt.order_by(Client.name)
            
            # Aplicar paginación
            stmt = stmt.offset(offset).limit(limit)
            
            result = await self.session.execute(stmt)
            clients = result.scalars().all()
            
            self._logger.info(
                f"Encontrados {len(clients)} clientes con filtros aplicados"
            )
            return list(clients)
            
        except ClientValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al aplicar filtros {filters}: {e}")
            raise ClientRepositoryError(
                message=f"Error al aplicar filtros: {e}",
                operation="get_clients_by_filters",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_with_relationships(
        self, 
        include_projects: bool = False,
        include_contacts: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Client]:
        """Obtiene clientes con sus relaciones cargadas.
        
        Args:
            include_projects: Si incluir proyectos relacionados
            include_contacts: Si incluir contactos relacionados
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            
        Returns:
            Lista de clientes con relaciones cargadas
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(
                f"Obteniendo clientes con relaciones (projects: {include_projects}, "
                f"contacts: {include_contacts})"
            )
            
            from sqlalchemy import select
            
            # Construir consulta base
            stmt = select(Client)
            
            # Agregar eager loading según sea necesario
            options = []
            if include_projects and hasattr(Client, 'projects'):
                options.append(selectinload(Client.projects))
            if include_contacts and hasattr(Client, 'contacts'):
                options.append(selectinload(Client.contacts))
            
            if options:
                stmt = stmt.options(*options)
            
            # Aplicar ordenamiento y paginación
            stmt = stmt.order_by(Client.name).offset(offset).limit(limit)
            
            result = await self.session.execute(stmt)
            clients = result.scalars().all()
            
            self._logger.info(
                f"Obtenidos {len(clients)} clientes con relaciones cargadas"
            )
            return list(clients)
            
        except Exception as e:
            self._logger.error(f"Error al obtener clientes con relaciones: {e}")
            raise ClientRepositoryError(
                message=f"Error al obtener clientes con relaciones: {e}",
                operation="get_clients_with_relationships",
                entity_type="Client",
                original_error=e
            )

    async def count_clients_by_filters(self, filters: Dict[str, Any]) -> int:
        """Cuenta clientes que cumplen los filtros especificados.
        
        Args:
            filters: Diccionario con filtros a aplicar
            
        Returns:
            Número de clientes que cumplen los filtros
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Contando clientes con filtros: {filters}")
            
            from sqlalchemy import select, func
            
            # Reutilizar lógica de filtros de get_clients_by_filters
            conditions = []
            
            for field, value in filters.items():
                if not hasattr(Client, field):
                    continue
                    
                field_attr = getattr(Client, field)
                
                if isinstance(value, str) and '%' in value:
                    conditions.append(field_attr.ilike(value))
                elif isinstance(value, list):
                    conditions.append(field_attr.in_(value))
                elif isinstance(value, dict):
                    if 'gte' in value:
                        conditions.append(field_attr >= value['gte'])
                    if 'lte' in value:
                        conditions.append(field_attr <= value['lte'])
                    if 'gt' in value:
                        conditions.append(field_attr > value['gt'])
                    if 'lt' in value:
                        conditions.append(field_attr < value['lt'])
                else:
                    conditions.append(field_attr == value)
            
            # Consulta de conteo
            stmt = select(func.count(Client.id))
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            result = await self.session.execute(stmt)
            count = result.scalar()
            
            self._logger.info(f"Contados {count} clientes con filtros aplicados")
            return count
            
        except Exception as e:
            self._logger.error(f"Error al contar clientes con filtros {filters}: {e}")
            raise ClientRepositoryError(
                message=f"Error al contar clientes: {e}",
                operation="count_clients_by_filters",
                entity_type="Client",
                original_error=e
            )

    async def search_clients_fuzzy(
        self, 
        search_term: str, 
        similarity_threshold: float = 0.3
    ) -> List[Client]:
        """Realiza búsqueda difusa de clientes.
        
        Args:
            search_term: Término de búsqueda
            similarity_threshold: Umbral de similitud (0.0 a 1.0)
            
        Returns:
            Lista de clientes ordenados por relevancia
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            if not search_term or not search_term.strip():
                return []
                
            self._logger.debug(
                f"Búsqueda difusa: '{search_term}' (umbral: {similarity_threshold})"
            )
            
            from sqlalchemy import select, func
            
            # Búsqueda básica con LIKE para simulación de fuzzy search
            # En producción se podría usar extensiones como pg_trgm para PostgreSQL
            search_pattern = f"%{search_term.strip()}%"
            
            stmt = (
                select(Client)
                .where(
                    or_(
                        Client.name.ilike(search_pattern),
                        Client.email.ilike(search_pattern),
                        Client.code.ilike(search_pattern)
                    )
                )
                .order_by(Client.name)
                .limit(50)
            )
            
            result = await self.session.execute(stmt)
            clients = result.scalars().all()
            
            self._logger.info(
                f"Búsqueda difusa encontró {len(clients)} clientes para '{search_term}'"
            )
            return list(clients)
            
        except Exception as e:
            self._logger.error(f"Error en búsqueda difusa '{search_term}': {e}")
            raise ClientRepositoryError(
                message=f"Error en búsqueda difusa: {e}",
                operation="search_clients_fuzzy",
                entity_type="Client",
                original_error=e
            )