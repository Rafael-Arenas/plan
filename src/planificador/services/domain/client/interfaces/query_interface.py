# -*- coding: utf-8 -*-
"""
Query Operations Interface for Client Domain Service

Define las operaciones básicas de consulta para la entidad Client
a nivel de dominio con lógica de negocio aplicada.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from planificador.schemas.client import Client


class IQueryOperations(ABC):
    """
    Interfaz para operaciones de consulta básica del dominio Client.
    
    Define métodos para búsquedas simples y filtros básicos
    con aplicación de reglas de negocio.
    """

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass