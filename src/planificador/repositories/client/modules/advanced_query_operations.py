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

from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.client import Client
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions import (
    RepositoryError,
    ValidationError,
)
from ..interfaces.query_interface import IQueryOperations


class AdvancedQueryOperations(BaseRepository[Client], IQueryOperations):
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