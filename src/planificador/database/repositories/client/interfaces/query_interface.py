"""Interfaz para operaciones de consulta básicas de clientes.

Esta interfaz define los métodos estándar para realizar consultas
básicas sobre la entidad Client.

Autor: Sistema de Repositorios
Versión: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from planificador.models.client import Client


class IQueryOperations(ABC):
    """Interfaz para operaciones de consulta básicas de clientes.
    
    Define los métodos estándar para realizar consultas simples
    y directas sobre la entidad Client.
    """

    @abstractmethod
    async def get_client_by_id(self, client_id: int) -> Optional[Client]:
        """Obtiene un cliente por su ID.
        
        Args:
            client_id: ID del cliente a buscar
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def get_client_by_name(self, name: str) -> Optional[Client]:
        """Busca un cliente por nombre exacto.
        
        Args:
            name: Nombre exacto del cliente
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def get_client_by_code(self, code: str) -> Optional[Client]:
        """Busca un cliente por código único.
        
        Args:
            code: Código único del cliente
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def get_client_by_email(self, email: str) -> Optional[Client]:
        """Busca un cliente por email.
        
        Args:
            email: Email del cliente
            
        Returns:
            Cliente encontrado o None si no existe
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def search_clients_by_name(self, name_pattern: str) -> List[Client]:
        """Busca clientes por patrón de nombre.
        
        Args:
            name_pattern: Patrón de búsqueda para el nombre
            
        Returns:
            Lista de clientes que coinciden con el patrón
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass

    @abstractmethod
    async def get_all_clients(
        self, 
        limit: Optional[int] = None, 
        offset: int = 0
    ) -> List[Client]:
        """Obtiene todos los clientes con paginación opcional.
        
        Args:
            limit: Número máximo de clientes a retornar (None para todos)
            offset: Número de clientes a omitir desde el inicio
            
        Returns:
            Lista de clientes
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        pass