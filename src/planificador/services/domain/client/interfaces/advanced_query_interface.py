# -*- coding: utf-8 -*-
"""
Advanced Query Operations Interface for Client Domain Service

Define las operaciones avanzadas de consulta para la entidad Client
con filtros complejos, paginación y ordenamiento.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime

from planificador.schemas.client import Client


class IAdvancedQueryOperations(ABC):
    """
    Interfaz para operaciones de consulta avanzada del dominio Client.
    
    Define métodos para búsquedas complejas, filtros dinámicos,
    paginación y ordenamiento con lógica de negocio aplicada.
    """

    @abstractmethod
    async def search_clients_advanced(
        self,
        filters: Dict[str, Any],
        pagination: Optional[Dict[str, Any]] = None,
        sorting: Optional[List[Dict[str, Any]]] = None,
        include_relationships: bool = False
    ) -> Tuple[List[Client], int]:
        """
        Búsqueda avanzada de clientes con filtros dinámicos.
        
        Args:
            filters: Diccionario de filtros dinámicos
            pagination: Parámetros de paginación
            sorting: Lista de parámetros de ordenamiento
            include_relationships: Si incluir relaciones
            
        Returns:
            Tuple[List[Client], int]: (clientes, total_count)
        """
        pass

    @abstractmethod
    async def filter_clients_by_criteria(
        self,
        criteria: Dict[str, Any],
        operator: str = "AND",
        limit: Optional[int] = None
    ) -> List[Client]:
        """
        Filtra clientes usando criterios complejos.
        
        Args:
            criteria: Criterios de filtrado
            operator: Operador lógico (AND, OR)
            limit: Límite de resultados
            
        Returns:
            List[Client]: Lista de clientes filtrados
        """
        pass

    @abstractmethod
    async def get_clients_with_pagination(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sorting: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[List[Client], int, int]:
        """
        Obtiene clientes con paginación.
        
        Args:
            page: Número de página (base 1)
            page_size: Tamaño de página
            filters: Filtros opcionales
            sorting: Ordenamiento opcional
            
        Returns:
            Tuple[List[Client], int, int]: (clientes, total_count, total_pages)
        """
        pass

    @abstractmethod
    async def search_clients_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        date_field: str = "created_at",
        include_inactive: bool = False
    ) -> List[Client]:
        """
        Busca clientes por rango de fechas.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            date_field: Campo de fecha a usar
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes en el rango
        """
        pass

    @abstractmethod
    async def get_clients_by_multiple_filters(
        self,
        name_filter: Optional[str] = None,
        email_filter: Optional[str] = None,
        phone_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
        combine_with_and: bool = True
    ) -> List[Client]:
        """
        Obtiene clientes aplicando múltiples filtros.
        
        Args:
            name_filter: Filtro por nombre
            email_filter: Filtro por email
            phone_filter: Filtro por teléfono
            status_filter: Filtro por estado
            type_filter: Filtro por tipo
            combine_with_and: Si combinar filtros con AND (True) o OR (False)
            
        Returns:
            List[Client]: Lista de clientes filtrados
        """
        pass

    @abstractmethod
    async def search_clients_fuzzy(
        self,
        search_term: str,
        similarity_threshold: float = 0.7,
        max_results: int = 50
    ) -> List[Client]:
        """
        Búsqueda difusa de clientes.
        
        Args:
            search_term: Término de búsqueda
            similarity_threshold: Umbral de similitud (0.0 - 1.0)
            max_results: Máximo número de resultados
            
        Returns:
            List[Client]: Lista de clientes con coincidencias difusas
        """
        pass

    @abstractmethod
    async def get_clients_sorted(
        self,
        sort_by: str,
        sort_order: str = "asc",
        include_inactive: bool = False,
        limit: Optional[int] = None
    ) -> List[Client]:
        """
        Obtiene clientes ordenados por un campo específico.
        
        Args:
            sort_by: Campo por el cual ordenar
            sort_order: Orden (asc, desc)
            include_inactive: Si incluir clientes inactivos
            limit: Límite de resultados
            
        Returns:
            List[Client]: Lista de clientes ordenados
        """
        pass

    @abstractmethod
    async def count_clients_by_criteria(
        self,
        criteria: Dict[str, Any],
        operator: str = "AND"
    ) -> int:
        """
        Cuenta clientes que cumplen criterios específicos.
        
        Args:
            criteria: Criterios de filtrado
            operator: Operador lógico (AND, OR)
            
        Returns:
            int: Número de clientes que cumplen los criterios
        """
        pass

    @abstractmethod
    async def get_clients_with_complex_joins(
        self,
        include_projects: bool = False,
        include_teams: bool = False,
        include_assignments: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Client]:
        """
        Obtiene clientes con joins complejos a entidades relacionadas.
        
        Args:
            include_projects: Si incluir proyectos del cliente
            include_teams: Si incluir equipos del cliente
            include_assignments: Si incluir asignaciones del cliente
            filters: Filtros adicionales
            
        Returns:
            List[Client]: Lista de clientes con relaciones cargadas
        """
        pass
