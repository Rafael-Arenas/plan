# src/planificador/services/domain/team/interfaces/search_operations.py

"""
Interfaz para operaciones de búsqueda del servicio de dominio de Team.

Define los métodos para búsquedas básicas y avanzadas de equipos,
incluyendo filtros por criterios múltiples y ordenamiento personalizado.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from enum import Enum

from .....schemas.team.team import TeamSchema
from .....schemas.common.pagination import PaginatedResponse
from .....schemas.team.search import TeamSearchCriteria


class TeamStatus(str, Enum):
    """Estados posibles de un equipo."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class ITeamDomainSearchOperations(ABC):
    """
    Interfaz para operaciones de búsqueda del servicio de dominio de Team.
    
    Define los métodos para realizar búsquedas básicas y avanzadas de equipos
    con múltiples criterios de filtrado y ordenamiento.
    """

    @abstractmethod
    async def find_teams_by_name(
        self,
        name_pattern: str,
        skip: int = 0,
        limit: int = 100
    ) -> PaginatedResponse[TeamSchema]:
        """
        Busca equipos por nombre con coincidencia parcial.
        
        Args:
            name_pattern: Patrón de nombre a buscar
            skip: Número de registros a omitir
            limit: Número máximo de registros a retornar
            
        Returns:
            PaginatedResponse[TeamSchema]: Respuesta paginada con equipos encontrados
            
        Raises:
            ValidationError: Si el patrón de búsqueda es inválido
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_teams_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> PaginatedResponse[TeamSchema]:
        """
        Obtiene equipos filtrados por su estado actual.
        
        Args:
            status: Estado de los equipos a buscar
            skip: Número de registros a omitir
            limit: Número máximo de registros a retornar
            
        Returns:
            PaginatedResponse[TeamSchema]: Respuesta paginada con equipos del estado especificado
            
        Raises:
            ValidationError: Si el estado no es válido
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_teams_by_department(
        self,
        department_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> PaginatedResponse[TeamSchema]:
        """
        Obtiene equipos asociados a un departamento específico.
        
        Args:
            department_id: Identificador único del departamento
            skip: Número de registros a omitir
            limit: Número máximo de registros a retornar
            
        Returns:
            PaginatedResponse[TeamSchema]: Respuesta paginada con equipos del departamento
            
        Raises:
            NotFoundError: Si el departamento no existe
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def search_teams_advanced(
        self,
        criteria: TeamSearchCriteria,
        skip: int = 0,
        limit: int = 100
    ) -> PaginatedResponse[TeamSchema]:
        """
        Búsqueda avanzada con múltiples criterios complejos.
        
        Args:
            criteria: Criterios de búsqueda avanzada
            skip: Número de registros a omitir
            limit: Número máximo de registros a retornar
            
        Returns:
            PaginatedResponse[TeamSchema]: Respuesta paginada con equipos que cumplen los criterios
            
        Raises:
            ValidationError: Si los criterios de búsqueda son inválidos
            RepositoryError: Si hay error en la consulta
        """
        pass