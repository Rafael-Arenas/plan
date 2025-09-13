"""Interfaz para operaciones de consulta avanzadas de clientes.

Esta interfaz define los métodos para realizar consultas complejas,
filtros múltiples y búsquedas especializadas sobre la entidad Client.

Autor: Sistema de Repositorios
Versión: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from planificador.models.client import Client


class IAdvancedQueryOperations(ABC):
    """Interfaz para operaciones de consulta avanzadas de clientes.
    
    Define los métodos para realizar consultas complejas, filtros
    múltiples y búsquedas especializadas sobre la entidad Client.
    """

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def count_clients_by_filters(self, filters: Dict[str, Any]) -> int:
        """Cuenta clientes que cumplen los filtros especificados.
        
        Args:
            filters: Diccionario con filtros a aplicar
            
        Returns:
            Número de clientes que cumplen los filtros
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
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
        pass