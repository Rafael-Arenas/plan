# src/planificador/services/domain/team/interfaces/crud_operations.py

"""
Interfaz para operaciones CRUD del servicio de dominio de Team.

Define los métodos básicos para crear, leer, actualizar y eliminar equipos,
incluyendo operaciones en lote y validaciones de negocio.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .....schemas.team.team_advanced_schemas import (
    TeamCreateSchema,
    TeamUpdateSchema,
    TeamSchema,
    PaginatedResponse
)


class ITeamDomainCrudOperations(ABC):
    """
    Interfaz para operaciones CRUD del servicio de dominio de Team.
    
    Define los métodos fundamentales para la gestión básica de equipos,
    incluyendo validaciones de negocio y operaciones transaccionales.
    """

    @abstractmethod
    async def create_team(
        self,
        team_data: TeamCreateSchema,
        validate_business_rules: bool = True
    ) -> TeamSchema:
        """
        Crea un nuevo equipo con validación completa de datos de negocio.
        
        Args:
            team_data: Datos del equipo a crear
            validate_business_rules: Si aplicar validaciones de reglas de negocio
            
        Returns:
            TeamSchema: El equipo creado con su información completa
            
        Raises:
            ValidationError: Si los datos no son válidos
            BusinessRuleViolationError: Si viola reglas de negocio
            RepositoryError: Si hay error en la persistencia
        """
        pass

    @abstractmethod
    async def get_team_by_id(
        self,
        team_id: int,
        include_members: bool = False
    ) -> Optional[TeamSchema]:
        """
        Obtiene un equipo específico por su identificador único.
        
        Args:
            team_id: Identificador único del equipo
            include_members: Si incluir información detallada de miembros
            
        Returns:
            Optional[TeamSchema]: El equipo encontrado o None si no existe
            
        Raises:
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def update_team(
        self,
        team_id: int,
        update_data: TeamUpdateSchema,
        validate_changes: bool = True
    ) -> TeamSchema:
        """
        Actualiza la información de un equipo existente.
        
        Args:
            team_id: Identificador único del equipo
            update_data: Datos de actualización del equipo
            validate_changes: Si validar el impacto de los cambios
            
        Returns:
            TeamSchema: El equipo actualizado
            
        Raises:
            NotFoundError: Si el equipo no existe
            ValidationError: Si los datos de actualización no son válidos
            BusinessRuleViolationError: Si los cambios violan reglas de negocio
            RepositoryError: Si hay error en la persistencia
        """
        pass

    @abstractmethod
    async def delete_team(
        self,
        team_id: int,
        force_delete: bool = False
    ) -> bool:
        """
        Elimina un equipo del sistema después de validar dependencias.
        
        Args:
            team_id: Identificador único del equipo
            force_delete: Si forzar eliminación ignorando dependencias
            
        Returns:
            bool: True si se eliminó exitosamente
            
        Raises:
            NotFoundError: Si el equipo no existe
            BusinessRuleViolationError: Si tiene dependencias activas
            RepositoryError: Si hay error en la eliminación
        """
        pass

    @abstractmethod
    async def get_all_teams(
        self,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False
    ) -> PaginatedResponse[TeamSchema]:
        """
        Obtiene todos los equipos con paginación y filtros opcionales.
        
        Args:
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a retornar
            include_inactive: Si incluir equipos inactivos
            
        Returns:
            PaginatedResponse[TeamSchema]: Lista paginada de equipos
            
        Raises:
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def bulk_create_teams(
        self,
        teams_data: List[TeamCreateSchema],
        validate_each: bool = True,
        stop_on_error: bool = False
    ) -> List[TeamSchema]:
        """
        Crea múltiples equipos en una operación en lote.
        
        Args:
            teams_data: Lista de datos de equipos a crear
            validate_each: Si validar cada equipo individualmente
            stop_on_error: Si detener el proceso al encontrar un error
            
        Returns:
            List[TeamSchema]: Lista de equipos creados exitosamente
            
        Raises:
            ValidationError: Si algún equipo no es válido
            BusinessRuleViolationError: Si algún equipo viola reglas de negocio
            RepositoryError: Si hay error en la persistencia
        """
        pass